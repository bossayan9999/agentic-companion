"""
Approval queue: when the rules engine flags a tool call as needing approval,
it lands here instead of executing. A human (you, via API/dashboard/push
notification) approves or rejects it. Only on approval does agent/brain.py
actually invoke the tool handler.
"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class PendingAction:
    id: str
    tenant_id: str
    tool_name: str
    tool_input: dict
    status: str = "pending"  # pending | approved | rejected
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ApprovalQueue:
    """In-memory for the scaffold — swap for a DB table for persistence across restarts."""

    def __init__(self):
        self._pending: dict[str, PendingAction] = {}

    def enqueue(self, tenant_id: str, tool_name: str, tool_input: dict) -> PendingAction:
        action = PendingAction(
            id=str(uuid.uuid4()), tenant_id=tenant_id, tool_name=tool_name, tool_input=tool_input
        )
        self._pending[action.id] = action
        return action

    def list_pending(self, tenant_id: str) -> list[PendingAction]:
        return [a for a in self._pending.values() if a.tenant_id == tenant_id and a.status == "pending"]

    def decide(self, action_id: str, tenant_id: str, approve: bool) -> PendingAction | None:
        action = self._pending.get(action_id)
        if not action or action.tenant_id != tenant_id or action.status != "pending":
            return None
        action.status = "approved" if approve else "rejected"
        return action

    def get(self, action_id: str) -> PendingAction | None:
        return self._pending.get(action_id)


approval_queue = ApprovalQueue()
