from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

from agent.state import AgentState
from agent.planner import generate_plan
from agent.executor import execute_plan
from agent.reflector import reflect

MCP_SERVER_URL = "http://localhost:8000/sse"


async def run_autonomous_agent(goal: str):
    server = MCPServerSSE(url=MCP_SERVER_URL)

    agent = Agent(
        model="openai:gpt-4o-mini",
        mcp_servers=[server],
    )

    async with agent.run_mcp_servers():
        state = AgentState(goal=goal)

        # 1. Plan
        state.plan = await generate_plan(agent, goal)

        # 2. Execute + Reflect
        await execute_plan(agent, state)
        decision = await reflect(agent, state)

        if decision == "FAIL":
            return "Agent failed to complete the task."

        return state.observations[-1]
