REFLECT_PROMPT = """
Analyze the execution so far.

Respond with ONLY one word:
- CONTINUE
- RETRY
- FAIL
"""


async def reflect(agent, state) -> str:
    prompt = f"""
    {REFLECT_PROMPT}

    Goal:
    {state.goal}

    Plan:
    {state.plan}

    Observations:
    {state.observations}
    """
    result = await agent.run(prompt)
    return result.output.strip()
