import json
import re

PLANNER_PROMPT = """
You are an autonomous planning agent.

Given a user goal, produce an ordered list of minimal steps.

Rules:
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


async def generate_plan(agent, goal: str) -> list[str]:
    result = await agent.run(f"{PLANNER_PROMPT}\nGoal: {goal}")

    try:
        data = extract_json(result.output)
        return data["steps"]
    except Exception as e:
        raise RuntimeError(
            f"Planner failed to return valid JSON.\nOutput was:\n{result.output}"
        ) from e
