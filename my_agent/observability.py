from dotenv import load_dotenv
load_dotenv()

import logging
import time
import json
from datetime import datetime
from typing import Optional
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
import asyncio


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent_logs.txt", mode="a"),
    ]
)
logger = logging.getLogger("agent.observability")

class AgentMetrics:
    """Tracks key performance metrics for the agent."""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.tool_calls = {}
        self.response_times = []
        self.start_time = datetime.now()
    
    def record_request(self, success: bool, duration_ms: float):
        self.total_requests += 1
        self.response_times.append(duration_ms)
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
    
    def record_tool_call(self, tool_name: str):
        self.tool_calls[tool_name] = self.tool_calls.get(tool_name, 0) + 1
    
    def report(self) -> dict:
        avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        return {
            "total_requests": self.total_requests,
            "success_rate": f"{(self.successful_requests / max(self.total_requests, 1)) * 100:.1f}%",
            "failed_requests": self.failed_requests,
            "avg_response_time_ms": round(avg_time, 2),
            "tool_usage": self.tool_calls,
            "uptime_seconds": (datetime.now() - self.start_time).seconds,
        }

metrics = AgentMetrics()

def on_before_llm_call(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    """Fires before every LLM call — logs the request."""
    logger.info(f"[TRACE] LLM called | agent={callback_context.agent_name} | turn={callback_context.invocation_id[:8]}")
    
    if llm_request.contents:
        for content in llm_request.contents:
            if content.role == "user" and content.parts:
                text = content.parts[0].text if content.parts[0].text else "[tool result]"
                logger.info(f"[TRACE] User input: {text[:100]}")
    
    return None  

def on_after_llm_call(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """Fires after every LLM call — logs the response."""
    if llm_response.content and llm_response.content.parts:
        part = llm_response.content.parts[0]
        if hasattr(part, 'text') and part.text:
            logger.info(f"[TRACE] Agent response: {part.text[:100]}")
        elif hasattr(part, 'function_call') and part.function_call:
            logger.info(f"[TRACE] Tool call decided: {part.function_call.name}")
    return None

def on_before_tool_call(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
    """Fires before every tool call — logs and tracks metrics."""
    logger.info(f"[TRACE] Tool firing: {tool.name} | args={json.dumps(args)[:100]}")
    metrics.record_tool_call(tool.name)
    tool_context.state["tool_start_time"] = time.time()
    return None 

def on_after_tool_call(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict) -> Optional[dict]:
    """Fires after every tool call — logs result and timing."""
    start = tool_context.state.get("tool_start_time", time.time())
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"[TRACE] Tool done: {tool.name} | duration={duration}ms | result={str(tool_response)[:80]}")
    return None


def get_current_time() -> dict:
    """Returns the current date and time.
    
    Returns:
        A dict with current time and date.
    """
    from datetime import datetime
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

observable_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="observable_agent",
    description="An agent with full observability — logs, traces and metrics.",
    instruction="""
    You are a helpful assistant.
    Use get_current_time for time questions.
    Use calculate for math questions.
    Always use tools — never guess.
    """,
    tools=[get_current_time, calculate],
    before_model_callback=on_before_llm_call,
    after_model_callback=on_after_llm_call,
    before_tool_callback=on_before_tool_call,
    after_tool_callback=on_after_tool_call,
)

APP_NAME = "observable_app"
USER_ID = "user_jon"
session_service = InMemorySessionService()

async def run_with_observability():
    """Runs test queries and shows full observability output."""
    
    session_id = "obs_session_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )
    
    runner = Runner(
        agent=observable_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    
    test_queries = [
        "What time is it?",
        "What is 15 * 24 + 100?",
        "What is sqrt(256)?",
        "What day is today?",
    ]
    
    print("\n" + "="*60)
    print("DAY 4A — OBSERVABILITY DEMO")
    print("Logs, Traces and Metrics in action")
    print("="*60)
    
    for query in test_queries:
        print(f"\n{'─'*40}")
        print(f"USER: {query}")
        
        start = time.time()
        success = True
        
        try:
            message = Content(parts=[Part(text=query)], role="user")
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session_id,
                new_message=message
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        print(f"AGENT: {event.content.parts[0].text}")
        except Exception as e:
            logger.error(f"[ERROR] Request failed: {e}")
            success = False
        
        duration = round((time.time() - start) * 1000, 2)
        metrics.record_request(success, duration)
    
    print("\n" + "="*60)
    print("METRICS REPORT")
    print("="*60)
    report = metrics.report()
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    print("\n[Logs also saved to agent_logs.txt]")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_with_observability())