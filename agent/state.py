from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid


@dataclass
class AgentState:
    goal: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    plan: List[str] = field(default_factory=list)
    current_step: int = 0
    observations: List[str] = field(default_factory=list)
    completed: bool = False
    context: Optional[Dict] = None  # Stores retrieved context from memory
    metadata: Dict = field(default_factory=dict)  # Additional metadata

    def add_metadata(self, key: str, value):
        """Add metadata to the state."""
        self.metadata[key] = value

    def get_context_summary(self) -> str:
        """Get a formatted summary of the context."""
        if not self.context:
            return "No previous context available."

        summary = []

        # Recent history
        if self.context.get("recent_history"):
            summary.append("=== Recent Conversation History ===")
            for idx, item in enumerate(self.context["recent_history"], 1):
                summary.append(f"\n{idx}. Goal: {item['goal']}")
                summary.append(f"   Result: {item['result']}")

        # Similar interactions
        if self.context.get("similar_interactions"):
            summary.append("\n\n=== Similar Past Interactions ===")
            for idx, item in enumerate(self.context["similar_interactions"], 1):
                summary.append(f"\n{idx}. Goal: {item['goal']}")
                summary.append(f"   Result: {item['result']}")

        return "\n".join(summary) if summary else "No previous context available."
