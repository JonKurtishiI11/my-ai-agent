from dotenv import load_dotenv
load_dotenv()

import json
import asyncio
from datetime import datetime
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
import anthropic

APP_NAME = "eval_app"
USER_ID = "user_jon"

def get_current_time() -> dict:
    """Returns the current date and time.
    
    Returns:
        A dict with current time and date.
    """
    now = datetime.now()
    return {"time": now.strftime("%H:%M:%S"), "date": now.strftime("%Y-%m-%d"), "day": now.strftime("%A")}

def calculate(expression: str) -> dict:
    """Evaluates a math expression.
    
    Args:
        expression: A math expression like '10 * 5'.
    
    Returns:
        A dict with the result.
    """
    try:
        import math
        result = eval(expression, {"__builtins__": {}}, {k: v for k, v in math.__dict__.items() if not k.startswith("__")})
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e)}

def get_weather(city: str) -> dict:
    """Gets current weather for a city.
    
    Args:
        city: Name of the city.
    
    Returns:
        A dict with temperature and description.
    """
    import urllib.request, urllib.parse
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        c = data["current_condition"][0]
        return {"city": city, "temp_c": c["temp_C"], "description": c["weatherDesc"][0]["value"]}
    except Exception as e:
        return {"error": str(e)}

agent_under_test = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="agent_under_test",
    description="Agent being evaluated for quality.",
    instruction="""
    You are a helpful assistant.
    Use tools for time, math and weather — never guess.
    Be concise — one sentence answers when possible.
    """,
    tools=[get_current_time, calculate, get_weather],
)


GOLDEN_DATASET = [
    {
        "id": "T001",
        "query": "What is 25 multiplied by 4?",
        "expected_tool": "calculate",
        "expected_contains": ["100"],
        "category": "math",
    },
    {
        "id": "T002",
        "query": "What is the square root of 144?",
        "expected_tool": "calculate",
        "expected_contains": ["12"],
        "category": "math",
    },
    {
        "id": "T003",
        "query": "What day is today?",
        "expected_tool": "get_current_time",
        "expected_contains": ["Wednesday", "Thursday", "Friday", "Monday", "Tuesday", "Saturday", "Sunday"],
        "category": "time",
    },
    {
        "id": "T004",
        "query": "What is the weather in London?",
        "expected_tool": "get_weather",
        "expected_contains": ["London", "°C", "temperature", "temp"],
        "category": "weather",
    },
    {
        "id": "T005",
        "query": "Calculate 1000 divided by 8",
        "expected_tool": "calculate",
        "expected_contains": ["125"],
        "category": "math",
    },
]

class LLMJudge:
    """Uses Claude to evaluate agent response quality."""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
    
    def score_response(self, query: str, response: str, expected_contains: list) -> dict:
        """Asks Claude to score the agent's response on 3 dimensions."""
        
        prompt = f"""You are evaluating an AI agent's response. Score it on these 3 dimensions from 1-5:

QUERY: {query}
AGENT RESPONSE: {response}
EXPECTED TO CONTAIN ONE OF: {expected_contains}

Score each dimension 1-5 where 5 is perfect:
1. CORRECTNESS: Is the answer factually correct and does it contain the expected information?
2. CONCISENESS: Is the response appropriately brief without missing key info?
3. HELPFULNESS: Does it directly address what the user asked?

Respond ONLY with valid JSON like this:
{{"correctness": 4, "conciseness": 5, "helpfulness": 4, "overall": 4.3, "reason": "one sentence explanation"}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            raw = message.content[0].text.strip()
            if "```" in raw:
                raw = raw.split("```")[1].replace("json", "").strip()
            return json.loads(raw)
        except Exception as e:
            return {"correctness": 0, "conciseness": 0, "helpfulness": 0, "overall": 0, "reason": f"Parse error: {e}"}

async def run_evaluation():
    """Runs the full evaluation pipeline on the golden dataset."""
    
    session_service = InMemorySessionService()
    judge = LLMJudge()
    results = []
    
    print("\n" + "="*60)
    print("DAY 4B — AGENT EVALUATION")
    print("LLM-as-a-Judge scoring on golden dataset")
    print("="*60)
    
    for test_case in GOLDEN_DATASET:
        session_id = f"eval_session_{test_case['id']}"
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id
        )
        
        runner = Runner(
            agent=agent_under_test,
            app_name=APP_NAME,
            session_service=session_service,
        )
        
        print(f"\n{'─'*40}")
        print(f"Test {test_case['id']} [{test_case['category']}]: {test_case['query']}")
        
        agent_response = ""
        tool_used = None
        
        try:
            message = Content(parts=[Part(text=test_case["query"])], role="user")
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session_id,
                new_message=message
            ):
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts or []:
                        if hasattr(part, 'function_call') and part.function_call:
                            tool_used = part.function_call.name
                
                if event.is_final_response():
                    if event.content and event.content.parts:
                        agent_response = event.content.parts[0].text
        
        except Exception as e:
            agent_response = f"ERROR: {e}"
        
        print(f"AGENT: {agent_response[:120]}")
        
        tool_correct = tool_used == test_case["expected_tool"]
        
        content_found = any(
            expected.lower() in agent_response.lower() 
            for expected in test_case["expected_contains"]
        )
        
        scores = judge.score_response(
            test_case["query"],
            agent_response,
            test_case["expected_contains"]
        )
        
        result = {
            "id": test_case["id"],
            "category": test_case["category"],
            "tool_used": tool_used,
            "expected_tool": test_case["expected_tool"],
            "tool_correct": tool_correct,
            "content_found": content_found,
            "scores": scores,
        }
        results.append(result)
        
        print(f"Tool: {tool_used} ({'✓' if tool_correct else '✗'} expected {test_case['expected_tool']})")
        print(f"Content check: {'✓' if content_found else '✗'}")
        print(f"Judge scores → Correctness: {scores.get('correctness')}/5 | "
              f"Conciseness: {scores.get('conciseness')}/5 | "
              f"Helpfulness: {scores.get('helpfulness')}/5 | "
              f"Overall: {scores.get('overall')}/5")
        print(f"Reason: {scores.get('reason', '')}")
    
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    tool_accuracy = sum(1 for r in results if r["tool_correct"]) / len(results) * 100
    content_accuracy = sum(1 for r in results if r["content_found"]) / len(results) * 100
    avg_overall = sum(r["scores"].get("overall", 0) for r in results) / len(results)
    avg_correctness = sum(r["scores"].get("correctness", 0) for r in results) / len(results)
    
    print(f"  Tests run:          {len(results)}")
    print(f"  Tool accuracy:      {tool_accuracy:.0f}%")
    print(f"  Content accuracy:   {content_accuracy:.0f}%")
    print(f"  Avg overall score:  {avg_overall:.2f}/5")
    print(f"  Avg correctness:    {avg_correctness:.2f}/5")
    
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Full results saved to eval_results.json")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_evaluation())