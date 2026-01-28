from agent.state import AgentState


async def execute_plan(agent, state: AgentState, max_steps: int = 10):
    """
    Execute the plan with context awareness.

    Args:
        agent: The AI agent
        state: AgentState containing plan and context
        max_steps: Maximum number of steps to execute
    """
    while (
        not state.completed
        and state.current_step < len(state.plan)
        and state.current_step < max_steps
    ):
        step = state.plan[state.current_step]

        # Build context-aware prompt
        context_info = ""
        if state.current_step == 0 and state.context:
            # Include context only in the first step to avoid repetition
            context_info = f"""

RELEVANT CONTEXT FROM PAST INTERACTIONS:
{state.get_context_summary()}

Use this context to inform your execution approach.
"""

        prompt = f"""
You are executing step {state.current_step + 1} of {len(state.plan)}.

Goal: {state.goal}

Current Step:
{step}

Previous observations from current execution:
{state.observations if state.observations else "None yet"}
{context_info}

Execute this step using available tools. Be concise in your response.
"""

        result = await agent.run(prompt)
        state.observations.append(result.output)
        state.current_step += 1

    state.completed = True
