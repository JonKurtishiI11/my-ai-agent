from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import load_memory
from my_agent.tools.advanced_tools import (
    get_weather,
    save_note,
    list_notes,
    calculate_advanced,
    convert_units,
)

def get_current_time() -> dict:
    """Returns the current date and time.
    
    Returns:
        A dict with current time, date and day of week.
    """
    from datetime import datetime
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
    }

def save_task(title: str, priority: str, due_date: str) -> dict:
    """Saves a task to the task list.
    
    Args:
        title: Task title.
        priority: Priority - 'high', 'medium', or 'low'.
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

math_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="math_specialist",
    description="Expert at all math and calculations.",
    instruction="Use calculate_advanced for all math. Be precise and brief.",
    tools=[calculate_advanced],
)

weather_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="weather_specialist",
    description="Expert at weather for any city worldwide.",
    instruction="Use get_weather always. Give temp in C and F with a brief summary.",
    tools=[get_weather],
)

productivity_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="productivity_specialist",
    description="Expert at time, scheduling and task management.",
    instruction="Use get_current_time for time questions. Use save_task to save tasks.",
    tools=[get_current_time, save_task],
)

notes_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="notes_specialist",
    description="Expert at saving and retrieving notes.",
    instruction="Use save_note to save notes. Use list_notes to list them.",
    tools=[save_note, list_notes],
)

root_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="my_first_agent",
    description="Master coordinator with specialist agents and long-term memory.",
    instruction="""
    You are a smart coordinator with a team of specialists and long-term memory.
    
    Your specialists:
    - math_specialist: ALL math, calculations, sqrt, percentages
    - weather_specialist: ALL weather for any city
    - productivity_specialist: time, date, saving tasks
    - notes_specialist: saving and listing notes
    
    Your memory tool:
    - load_memory: search past conversations for things the user told you before
    
    RULES:
    - Delegate to the right specialist for every request
    - Use load_memory if the user asks about something from a past conversation
    - For mixed questions use multiple specialists
    - Always summarize results clearly
    - Convert units using calculate_advanced via math_specialist
    """,
    tools=[
        AgentTool(agent=math_agent),
        AgentTool(agent=weather_agent),
        AgentTool(agent=productivity_agent),
        AgentTool(agent=notes_agent),
        load_memory,
        convert_units,
    ],
)