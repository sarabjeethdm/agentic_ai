from agent.state import AgentState


async def execute_plan(agent, state: AgentState, max_steps: int = 10):
    while (
        not state.completed
        and state.current_step < len(state.plan)
        and state.current_step < max_steps
    ):
        step = state.plan[state.current_step]

        prompt = f"""
        You are executing step {state.current_step + 1}.

        Step:
        {step}

        Previous observations:
        {state.observations}

        Execute this step using available tools.
        """

        result = await agent.run(prompt)
        state.observations.append(result.output)
        state.current_step += 1

    state.completed = True
