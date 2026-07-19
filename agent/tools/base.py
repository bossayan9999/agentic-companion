"""
Tool registry: every connector/skill the agent can call registers itself here.
This gives the brain a single source of truth for what it's allowed to do,
and makes adding a new tool a matter of writing one function + one decorator.
"""
from __future__ import annotations
from typing import Callable, Any
from dataclasses import dataclass, field


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict  # JSON schema, same shape Claude/OpenAI tool-calling expects
    handler: Callable[..., Any]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, parameters: dict):
        def decorator(fn: Callable[..., Any]):
            self._tools[name] = Tool(name, description, parameters, fn)
            return fn
        return decorator

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def as_schema(self) -> list[dict]:
        """Return tool definitions in the shape the LLM tool-calling API expects."""
        return [
            {"name": t.name, "description": t.description, "input_schema": t.parameters}
            for t in self._tools.values()
        ]

    def call(self, name: str, **kwargs) -> Any:
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return tool.handler(**kwargs)


registry = ToolRegistry()
