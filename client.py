import asyncio
import uuid
import logging
from agent.autonomous import run_autonomous_agent
from dotenv import load_dotenv

load_dotenv()

# Configure logging to only show errors by default
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")


async def main():
    print("=" * 60)
    print("Autonomous Agent with Long-Term Memory")
    print("=" * 60)
    print("\nCommands:")
    print("  - Type your goal to interact with the agent")
    print("  - 'new' or 'reset' to start a new session")
    print("  - 'session' to see current session ID")
    print("  - 'exit' or 'quit' to quit")
    print("=" * 60)

    # Create a session ID for this conversation
    session_id = str(uuid.uuid4())
    print(f"\nSession ID: {session_id}")

    while True:
        goal = input("\nYou: ").strip()

        if not goal:
            continue

        if goal.lower() in {"exit", "quit"}:
            print("\nGoodbye! 👋")
            break

        if goal.lower() in {"new", "reset"}:
            session_id = str(uuid.uuid4())
            print(f"Started new session: {session_id}")
            continue

        if goal.lower() == "session":
            print(f"Current session ID: {session_id}")
            continue

        try:
            print("\nAgent: ", end="", flush=True)
            result = await run_autonomous_agent(goal, session_id=session_id)
            print(result)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try rephrasing your goal or start a new session with 'new'")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")