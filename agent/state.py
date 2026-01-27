from dataclasses import dataclass, field
from typing import List


@dataclass
class AgentState:
    goal: str
    plan: List[str] = field(default_factory=list)
    current_step: int = 0
    observations: List[str] = field(default_factory=list)
    completed: bool = False
