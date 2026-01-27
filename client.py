import asyncio
from agent.autonomous import run_autonomous_agent
from dotenv import load_dotenv

load_dotenv()


async def main():
    print("Autonomous Agent (type 'exit' to quit)")

    while True:
        goal = input("\nYou: ")
        if goal.lower() in {"exit", "quit"}:
            break

        result = await run_autonomous_agent(goal)
        print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())
