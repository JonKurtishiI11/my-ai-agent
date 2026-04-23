from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
import asyncio

APP_NAME = "my_ai_agent"
USER_ID = "user_jon"

def remember_preference(key: str, value: str) -> dict:
    """Stores a user preference in the current session state.
    
    Args:
        key: The preference name e.g. 'favorite_city' or 'name'.
        value: The preference value e.g. 'London' or 'Jon'.
    
    Returns:
        A dict confirming the preference was stored.
    """
    return {
        "stored": True,
        "key": key,
        "value": value,
        "message": f"Got it! I'll remember that your {key} is {value}."
    }

def get_current_time() -> dict:
    """Returns the current date and time.
    
    Returns:
        A dict with current time and date.
    """
    from datetime import datetime
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A")
    }

session_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="session_agent",
    description="A stateful agent that remembers things within a conversation.",
    instruction="""
    You are a friendly assistant with short-term memory.
    
    During our conversation you will remember:
    - The user's name if they tell you
    - Their preferences (favorite city, food, etc.)
    - Anything they explicitly ask you to remember
    
    Use the remember_preference tool to store any personal info the user shares.
    Always greet the user by name if you know it.
    Reference earlier parts of the conversation naturally.
    
    You also know the current time via get_current_time.
    """,
    tools=[remember_preference, get_current_time],
)

session_service = InMemorySessionService()

async def run_conversation():
    """Runs a multi-turn conversation demonstrating session memory."""
    
    session_id = "demo_session_001"
    
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )
    
    runner = Runner(
        agent=session_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    
    turns = [
        "Hi! My name is Jon and I am learning ADK.",
        "My favorite city is Tetovo.",
        "What is my name and favorite city?",
        "What time is it right now?",
        "Summarize what you know about me so far.",
    ]
    
    print("\n" + "="*60)
    print("DAY 3A — SESSION DEMO (multi-turn conversation)")
    print("="*60)
    
    for user_input in turns:
        print(f"\nUSER: {user_input}")
        
        message = Content(
            parts=[Part(text=user_input)],
            role="user"
        )
        
        response_text = ""
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
        
        print(f"AGENT: {response_text}")
    
    print("\n" + "="*60)
    print("Session complete — agent remembered context across all turns!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_conversation())