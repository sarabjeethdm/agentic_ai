REFLECT_PROMPT = """
Analyze the execution so far, considering both current execution and historical context.

Respond with ONLY one word:
- CONTINUE (if task is complete and successful)
- RETRY (if task needs another attempt with different approach)
- FAIL (if task is impossible or has critical errors)
"""


async def reflect(agent, state) -> str:
    """
    Reflect on the execution and decide next action.

    Args:
        agent: The AI agent
        state: AgentState containing execution results and context

    Returns:
        Decision: CONTINUE, RETRY, or FAIL
    """
    # Build context-aware reflection prompt
    context_info = ""
    if state.context and state.context.get("similar_interactions"):
        context_info = """

HISTORICAL CONTEXT:
Similar past interactions show successful patterns. Consider if current execution aligns with past successes.
"""

    prompt = f"""
{REFLECT_PROMPT}

Goal:
{state.goal}

Plan:
{state.plan}

Observations:
{state.observations}
{context_info}
"""
    result = await agent.run(prompt)
    decision = result.output.strip().upper()

    # Ensure valid response
    valid_decisions = ["CONTINUE", "RETRY", "FAIL"]
    if decision not in valid_decisions:
        # Try to extract a valid decision
        for valid in valid_decisions:
            if valid in decision:
                return valid
        # Default to CONTINUE if we can't determine
        return "CONTINUE"

    return decision