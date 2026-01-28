import logging
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE

from agent.state import AgentState
from agent.planner import generate_plan
from agent.executor import execute_plan
from agent.reflector import reflect
from agent.memory import MemoryStore

logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8000/sse"


async def run_autonomous_agent(
    goal: str, session_id: str = None, use_memory: bool = True
):
    """
    Run the autonomous agent with long-term memory capabilities.

    Args:
        goal: User's goal/query
        session_id: Session identifier for conversation tracking
        use_memory: Whether to use memory storage and retrieval

    Returns:
        Final result from the agent
    """
    server = MCPServerSSE(url=MCP_SERVER_URL)

    agent = Agent(
        model="openai:gpt-4o-mini",
        mcp_servers=[server],
    )

    # Initialize memory store if enabled
    memory = None
    if use_memory:
        try:
            memory = MemoryStore()
        except Exception as e:
            logger.warning(f"Failed to initialize memory store: {e}")
            logger.warning("Continuing without memory capabilities")

    async with agent.run_mcp_servers():
        # Initialize state
        state = AgentState(goal=goal)
        if session_id:
            state.session_id = session_id

        # Retrieve relevant context from memory
        if memory:
            try:
                context = await memory.get_relevant_context(
                    goal=goal,
                    session_id=state.session_id,
                    history_limit=5,
                    similar_limit=3,
                )
                state.context = context
                logger.info("Retrieved context from memory")
            except Exception as e:
                logger.warning(f"Failed to retrieve context: {e}")

        try:
            # 1. Plan with context
            state.plan = await generate_plan(agent, state)
            logger.info(f"Generated plan: {state.plan}")

            # 2. Execute plan with context
            await execute_plan(agent, state)

            # 3. Reflect on execution
            decision = await reflect(agent, state)
            logger.info(f"Reflection decision: {decision}")

            # Handle reflection decision
            if decision == "FAIL":
                result = "Agent failed to complete the task."
            elif decision == "RETRY":
                result = "Task needs refinement. Consider rephrasing or breaking into smaller goals."
            else:
                # Get the final result
                if state.observations:
                    result = state.observations[-1]
                else:
                    result = "Task completed but no observations recorded."

            # Store interaction in memory
            if memory:
                try:
                    await memory.store_interaction(
                        session_id=state.session_id,
                        goal=goal,
                        plan=state.plan,
                        observations=state.observations,
                        result=result,
                        metadata={
                            "decision": decision,
                            "steps_executed": state.current_step,
                        },
                    )
                    logger.info("Stored interaction in memory")
                except Exception as e:
                    logger.warning(f"Failed to store interaction: {e}")

            return result

        except Exception as e:
            logger.error(f"Error during agent execution: {e}")
            error_result = f"Error during execution: {str(e)}"

            # Try to store the error in memory
            if memory:
                try:
                    await memory.store_interaction(
                        session_id=state.session_id,
                        goal=goal,
                        plan=state.plan,
                        observations=state.observations + [error_result],
                        result=error_result,
                        metadata={"error": True, "error_message": str(e)},
                    )
                except Exception as store_error:
                    logger.warning(f"Failed to store error interaction: {store_error}")

            raise

        finally:
            # Close memory connection
            if memory:
                memory.close()
