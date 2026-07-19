"""
Common interface so the brain doesn't care whether it's talking to Claude
directly, or to any model via OpenRouter. Every provider takes the same
messages/tools shape and returns the same normalized response shape.
"""
from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class ModelResponse:
    text: str
    tool_calls: list[ToolCall]
    raw: dict
    stop_reason: str  # "tool_use" or "end_turn"


class Provider(Protocol):
    def call(self, messages: list[dict], tools: list[dict], system: str) -> ModelResponse: ...
