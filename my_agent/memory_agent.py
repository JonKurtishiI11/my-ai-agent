from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.tools import load_memory
from google.genai.types import Content, Part
import asyncio

APP_NAME = "my_ai_agent"
USER_ID = "user_jon"


info_capture_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="info_capture_agent",
    description="Captures and acknowledges information from the user.",
    instruction="""
    You are a helpful assistant. 
    Listen carefully to what the user tells you and acknowledge it clearly.
    Confirm you have noted every detail they share.
    """,
)


memory_recall_agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="memory_recall_agent",
    description="Recalls information from past conversations using memory.",
    instruction="""
    You are a helpful assistant with long-term memory.
    
    When the user asks about something, ALWAYS use the load_memory tool 
    first to check if the answer is in past conversations.
    
    If you find relevant memories, use them to answer.
    If you don't find anything, say so honestly.
    """,
    tools=[load_memory],
)


session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

async def run_memory_demo():
    """Demonstrates long-term memory across two separate sessions."""
    
    print("\n" + "="*60)
    print("DAY 3B — LONG-TERM MEMORY DEMO")
    print("="*60)
    
    print("\n--- SESSION 1: Sharing information ---")
    
    session1_id = "session_capture_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session1_id
    )
    
    runner1 = Runner(
        agent=info_capture_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )
    
    facts = [
        "My name is Jon and I am from Tetovo, Macedonia.",
        "I am building an AI agent for my master thesis about land parcels.",
        "My favorite programming language is Python.",
    ]
    
    for fact in facts:
        print(f"\nUSER: {fact}")
        message = Content(parts=[Part(text=fact)], role="user")
        
        async for event in runner1.run_async(
            user_id=USER_ID,
            session_id=session1_id,
            new_message=message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(f"AGENT: {event.content.parts[0].text}")
    
    session1 = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session1_id
    )
    await memory_service.add_session_to_memory(session1)
    print("\n[Memory saved from Session 1]")
    
    print("\n--- SESSION 2: New session, recalling from memory ---")
    
    session2_id = "session_recall_001"
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session2_id
    )
    
    runner2 = Runner(
        agent=memory_recall_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )
    
    questions = [
        "What is my name and where am I from?",
        "What is my thesis about?",
        "What programming language do I prefer?",
    ]
    
    for question in questions:
        print(f"\nUSER: {question}")
        message = Content(parts=[Part(text=question)], role="user")
        
        async for event in runner2.run_async(
            user_id=USER_ID,
            session_id=session2_id,
            new_message=message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    print(f"AGENT: {event.content.parts[0].text}")
    
    print("\n" + "="*60)
    print("Memory demo complete!")
    print("Agent recalled facts from a completely different session!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_memory_demo())