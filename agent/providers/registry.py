"""
Single place to resolve a model choice to a working provider instance.
Add entries as you want them available; OpenRouter slugs work for basically
any model without writing new provider code.

Quick reference (OpenRouter slugs — copy-paste ready):
  https://openrouter.ai/models  <- browse full catalog + live pricing
  - "openai/gpt-4o"
  - "openai/o3"
  - "google/gemini-2.5-pro"
  - "meta-llama/llama-3.3-70b-instruct"
  - "deepseek/deepseek-r1"
  - "x-ai/grok-4"
  - "anthropic/claude-sonnet-4.6"   (Claude via OpenRouter, if you want one billing account)
"""
from agent.providers.anthropic_provider import AnthropicProvider
from agent.providers.openrouter_provider import OpenRouterProvider

# Friendly aliases -> (provider_class, model_id)
MODEL_ALIASES = {
    "claude": ("anthropic", "claude-sonnet-4-6"),
    "gpt4o": ("openrouter", "openai/gpt-4o"),
    "gemini": ("openrouter", "google/gemini-2.5-pro"),
    "llama": ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
    "deepseek": ("openrouter", "deepseek/deepseek-r1"),
    "grok": ("openrouter", "x-ai/grok-4"),
}


def get_provider(model_alias: str = "claude"):
    backend, model_id = MODEL_ALIASES.get(model_alias, ("anthropic", "claude-sonnet-4-6"))
    if backend == "openrouter":
        return OpenRouterProvider(model=model_id)
    return AnthropicProvider(model=model_id)
