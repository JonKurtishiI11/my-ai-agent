from dotenv import load_dotenv
load_dotenv()

import asyncio
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.genai.types import Content, Part

APP_NAME = "multi_agent_app"
USER_ID = "user_jon"

def calculate_advanced(expression: str) -> dict:
    """Evaluates advanced math expressions including sqrt, pow, etc.
    
    Args:
        expression: Math expression e.g. 'sqrt(144)' or '2**10'.
    
    Returns:
        A dict with the result.
    """
    import math
    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        )
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e)}

math_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="math_specialist",
    description="Expert at mathematical calculations and equations.",
    instruction="""
    You are a math specialist.
    Always use calculate_advanced for any computation.
    Return only the numerical answer with a brief explanation.
    """,
    tools=[calculate_advanced],
)

def get_weather(city: str) -> dict:
    """Gets current weather for any city.
    
    Args:
        city: Name of the city.
    
    Returns:
        A dict with temperature and weather description.
    """
    import urllib.request, urllib.parse, json
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        c = data["current_condition"][0]
        return {
            "city": city,
            "temp_c": c["temp_C"],
            "temp_f": c["temp_F"],
            "description": c["weatherDesc"][0]["value"],
            "humidity": c["humidity"],
        }
    except Exception as e:
        return {"error": str(e), "city": city}

weather_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="weather_specialist",
    description="Expert at fetching and interpreting weather data for any city.",
    instruction="""
    You are a weather specialist.
    Always use get_weather for weather queries.
    Give a friendly concise weather summary including both C and F.
    """,
    tools=[get_weather],
)

def get_current_time() -> dict:
    """Returns the current date, time and day.
    
    Returns:
        A dict with full time details.
    """
    from datetime import datetime
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
        "week_number": now.strftime("%W"),
    }

def save_task(title: str, priority: str, due_date: str) -> dict:
    """Saves a task to the task list.
    
    Args:
        title: Task title.
        priority: Priority level - 'high', 'medium', or 'low'.
        due_date: Due date in YYYY-MM-DD format.
    
    Returns:
        A dict confirming the task was saved.
    """
    import json, os
    from datetime import datetime
    file = "tasks.json"
    tasks = json.load(open(file)) if os.path.exists(file) else []
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "priority": priority,
        "due_date": due_date,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "done": False,
    }
    tasks.append(task)
    json.dump(tasks, open(file, "w"), indent=2)
    return {"saved": True, "task_id": task["id"], "title": title}

productivity_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="productivity_specialist",
    description="Expert at time management, scheduling and task tracking.",
    instruction="""
    You are a productivity specialist.
    Use get_current_time for time and date queries.
    Use save_task to create and track tasks.
    Be encouraging and action-oriented.
    """,
    tools=[get_current_time, save_task],
)

math_tool = AgentTool(agent=math_agent)
weather_tool = AgentTool(agent=weather_agent)
productivity_tool = AgentTool(agent=productivity_agent)

coordinator_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="coordinator",
    description="Master coordinator that routes tasks to specialist agents.",
    instruction="""
    You are a coordinator managing a team of specialist agents.
    
    Your team:
    - math_specialist: handles ALL math and calculations
    - weather_specialist: handles ALL weather queries
    - productivity_specialist: handles time, scheduling, task saving
    
    RULES:
    - ALWAYS delegate to the right specialist — never answer directly
    - For math → use math_specialist tool
    - For weather → use weather_specialist tool
    - For time/tasks → use productivity_specialist tool
    - For mixed questions → use multiple specialists in sequence
    - Summarize specialist results clearly for the user
    """,
    tools=[math_tool, weather_tool, productivity_tool],
)

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

async def run_multi_agent():
    session_id = "multi_agent_session_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )
    
    runner = Runner(
        agent=coordinator_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )
    
    queries = [
        "What is the square root of 1024 plus 200?",
        "What is the weather like in Tetovo, Macedonia?",
        "What day is today and save a task: 'Finish ADK course' high priority due 2026-04-30",
        "What is 15% of 2500 and what is the weather in London?",
    ]
    
    print("\n" + "="*60)
    print("DAY 5 — MULTI-AGENT SYSTEM")
    print("Coordinator delegating to specialist agents")
    print("="*60)
    
    for query in queries:
        print(f"\n{'─'*50}")
        print(f"USER: {query}")
        print(f"{'─'*50}")
        
        message = Content(parts=[Part(text=query)], role="user")
        
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(f"COORDINATOR: {event.content.parts[0].text}")
    
    print("\n" + "="*60)
    print("Multi-agent demo complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_multi_agent())