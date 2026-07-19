import os
import anthropic
from agent.providers.base import ModelResponse, ToolCall

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


class AnthropicProvider:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model

    def call(self, messages: list[dict], tools: list[dict], system: str) -> ModelResponse:
        resp = _client.messages.create(
            model=self.model, max_tokens=1024, system=system, messages=messages, tools=tools
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        tool_calls = [
            ToolCall(id=b.id, name=b.name, input=b.input)
            for b in resp.content
            if b.type == "tool_use"
        ]
        return ModelResponse(text=text, tool_calls=tool_calls, raw=resp.model_dump(), stop_reason=resp.stop_reason)
