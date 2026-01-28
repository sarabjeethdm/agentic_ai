import json
import re

PLANNER_PROMPT = """
You are an autonomous planning agent with access to conversation history and similar past interactions.

Given a user goal and relevant context, produce an ordered list of minimal steps.

Rules:
- Consider the conversation history and similar past interactions when planning
- Learn from successful past strategies
- Avoid repeating failed approaches from history
- Do NOT execute anything
- Do NOT explain
- Output JSON only in this exact format:

{
  "steps": ["step 1", "step 2"]
}
"""


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in planner output:\n{text}")
    return json.loads(match.group())


async def generate_plan(agent, state) -> list[str]:
    """
    Generate a plan using the agent, considering historical context.

    Args:
        agent: The AI agent
        state: AgentState containing goal and context

    Returns:
        List of plan steps
    """
    # Build context-aware prompt
    context_info = ""
    if state.context:
        context_info = f"""

RELEVANT CONTEXT:
{state.get_context_summary()}

Use this context to inform your planning. Learn from successful past approaches and avoid repeating failures.
"""

    prompt = f"""{PLANNER_PROMPT}

Goal: {state.goal}
{context_info}
"""

    result = await agent.run(prompt)

    try:
        data = extract_json(result.output)
        return data["steps"]
    except Exception as e:
        raise RuntimeError(
            f"Planner failed to return valid JSON.\nOutput was:\n{result.output}"
        ) from e
