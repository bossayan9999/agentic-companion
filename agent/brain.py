"""
The Brain: the agentic loop. On every turn it:
1. Pulls relevant memory (semantic recall + known facts)
2. Calls the chosen model (any provider — see agent/providers/registry.py)
3. For each tool call the model makes, checks the rules engine:
   - "auto"    -> execute immediately
   - "approve" -> queue it and tell the user it's waiting on them
   - "block"   -> refuse, tell the user why
4. Feeds executed-tool results back until the model produces a final answer
5. Writes anything worth remembering back to memory

Model-agnostic by design: pass model_alias="gpt4o" / "gemini" / "llama" / etc.
and the same loop runs against a completely different backend via OpenRouter.
See agent/providers/registry.py for available aliases and links.
"""
from __future__ import annotations
import os
from memory.store import MemoryStore
from agent.tools.base import registry
from agent.providers.registry import get_provider
from agent.rules import get_tier
from agent.approval import approval_queue
import agent.tools.calendar_tool  # noqa: F401
import agent.osint.recon  # noqa: F401

SYSTEM_PROMPT = """You are an autonomous personal agent. You have memory of the user's
ongoing projects and preferences, and access to tools for taking real action.
Use recalled memory to stay consistent with what the user has told you before.
Some of your tools require human approval before they run — if a tool call is
queued for approval, tell the user clearly what's pending and why."""


def run_turn(tenant_id: str, user_message: str, model_alias: str = "claude") -> str:
    memory = MemoryStore(tenant_id)
    recalled = memory.recall(user_message, n_results=5)
    context_block = "\n".join(recalled) if recalled else "(no relevant memory yet)"

    messages = [
        {
            "role": "user",
            "content": f"Relevant memory:\n{context_block}\n\nUser message:\n{user_message}",
        }
    ]

    provider = get_provider(model_alias)
    tools_schema = registry.as_schema()
    response = provider.call(messages, tools_schema, SYSTEM_PROMPT)

    notes = []  # collects approval/block notices to surface to the user
    while response.stop_reason == "tool_use":
        tool_results = []
        for call in response.tool_calls:
            tier = get_tier(call.name)

            if tier == "block":
                notes.append(f"Blocked: '{call.name}' is not permitted to run from this agent.")
                tool_results.append({"tool_use_id": call.id, "content": "BLOCKED by policy."})
                continue

            if tier == "approve":
                pending = approval_queue.enqueue(tenant_id, call.name, call.input)
                notes.append(
                    f"Waiting on your approval to run '{call.name}' "
                    f"(request id: {pending.id}). Approve via POST /approvals/{pending.id}/approve."
                )
                tool_results.append(
                    {"tool_use_id": call.id, "content": f"PENDING_APPROVAL id={pending.id}"}
                )
                continue

            # tier == "auto"
            result = registry.call(call.name, **call.input)
            tool_results.append({"tool_use_id": call.id, "content": str(result)})

        messages.append({"role": "assistant", "content": response.text or "(tool calls)"})
        messages.append(
            {"role": "user", "content": "Tool results:\n" + "\n".join(str(r) for r in tool_results)}
        )
        response = provider.call(messages, tools_schema, SYSTEM_PROMPT)

    final_text = response.text
    if notes:
        final_text = final_text + "\n\n" + "\n".join(notes)

    memory.remember(
        text=f"User said: {user_message}\nAgent replied: {final_text}",
        doc_id=f"turn-{os.urandom(4).hex()}",
    )
    return final_text


def execute_approved_action(tenant_id: str, action_id: str):
    """Call this after a human approves a pending action (see api/main.py)."""
    action = approval_queue.get(action_id)
    if not action or action.tenant_id != tenant_id:
        raise ValueError("Unknown or mismatched approval request")
    if action.status != "approved":
        raise ValueError(f"Action is not approved (status: {action.status})")
    return registry.call(action.tool_name, **action.tool_input)
