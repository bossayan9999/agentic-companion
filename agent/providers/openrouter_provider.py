"""
OpenRouter gives you one API key and one endpoint for basically every model
worth using (GPT, Gemini, Llama, Mistral, DeepSeek, Grok, Claude, etc.).
Pick a model by its OpenRouter slug, e.g. "openai/gpt-4o", "google/gemini-2.5-pro",
"meta-llama/llama-3.3-70b-instruct", "deepseek/deepseek-r1".

Quick links:
- Sign up / get API key: https://openrouter.ai/keys
- Full model list + live pricing: https://openrouter.ai/models
- API docs: https://openrouter.ai/docs

Set OPENROUTER_API_KEY in your environment. That's the only setup needed —
no per-provider accounts.
"""
import os
import httpx
from agent.providers.base import ModelResponse, ToolCall

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def _to_openai_tools(anthropic_style_tools: list[dict]) -> list[dict]:
    """Convert our internal (Anthropic-shaped) tool schema to OpenAI function format,
    which is what OpenRouter's unified endpoint expects."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in anthropic_style_tools
    ]


class OpenRouterProvider:
    def __init__(self, model: str):
        """model: any OpenRouter slug, e.g. 'openai/gpt-4o', 'anthropic/claude-sonnet-4.6',
        'google/gemini-2.5-pro', 'deepseek/deepseek-r1'. Full list: https://openrouter.ai/models"""
        self.model = model
        self.api_key = os.environ.get("OPENROUTER_API_KEY")

    def call(self, messages: list[dict], tools: list[dict], system: str) -> ModelResponse:
        oa_messages = [{"role": "system", "content": system}] + messages
        payload = {"model": self.model, "messages": oa_messages}
        if tools:
            payload["tools"] = _to_openai_tools(tools)

        resp = httpx.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                # Optional but recommended by OpenRouter for their leaderboards:
                "HTTP-Referer": "https://your-app-domain.example",
                "X-Title": "Agentic AI Companion",
            },
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]["message"]

        tool_calls = [
            ToolCall(
                id=tc["id"],
                name=tc["function"]["name"],
                input=_safe_json(tc["function"]["arguments"]),
            )
            for tc in choice.get("tool_calls", []) or []
        ]
        stop_reason = "tool_use" if tool_calls else "end_turn"
        return ModelResponse(
            text=choice.get("content") or "", tool_calls=tool_calls, raw=data, stop_reason=stop_reason
        )


def _safe_json(s):
    import json
    try:
        return json.loads(s)
    except Exception:
        return {}
