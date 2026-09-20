"""Unified Model Gateway and Router.

Supports multi-provider dispatch and automatic fallback across:
- Google Gemini
- OpenAI
- Anthropic Claude
- DeepSeek
- Groq
- OpenRouter
- Local Ollama
- Local Mock
"""

import os
import logging
from typing import Dict, Any, Optional, List
from models.base import BaseModelProvider
from models.mock import MockModelProvider
from models.gemini import GeminiProvider
from models.ollama import OllamaProvider
from models.openai_compatible import OpenAICompatibleProvider
from models.anthropic import AnthropicProvider

logger = logging.getLogger("model_router")

PROVIDER_REGISTRY = {
    "gemini": {
        "class": GeminiProvider,
        "default_model": "gemini-2.5-flash",
        "env_key": "GEMINI_API_KEY",
        "multimodal": True
    },
    "openai": {
        "class": lambda m, k: OpenAICompatibleProvider(flavor="openai", model_name=m or "gpt-4o-mini", api_key=k),
        "default_model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
        "multimodal": True
    },
    "anthropic": {
        "class": AnthropicProvider,
        "default_model": "claude-3-5-sonnet-20241022",
        "env_key": "ANTHROPIC_API_KEY",
        "multimodal": True
    },
    "deepseek": {
        "class": lambda m, k: OpenAICompatibleProvider(flavor="deepseek", model_name=m or "deepseek-chat", api_key=k),
        "default_model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
        "multimodal": False
    },
    "groq": {
        "class": lambda m, k: OpenAICompatibleProvider(flavor="groq", model_name=m or "llama-3.3-70b-versatile", api_key=k),
        "default_model": "llama-3.3-70b-versatile",
        "env_key": "GROQ_API_KEY",
        "multimodal": False
    },
    "openrouter": {
        "class": lambda m, k: OpenAICompatibleProvider(flavor="openrouter", model_name=m or "google/gemini-2.5-flash", api_key=k),
        "default_model": "google/gemini-2.5-flash",
        "env_key": "OPENROUTER_API_KEY",
        "multimodal": True
    },
    "ollama": {
        "class": OllamaProvider,
        "default_model": "llama3.2",
        "env_key": None,
        "multimodal": False
    },
    "mock": {
        "class": MockModelProvider,
        "default_model": "mock-v1",
        "env_key": None,
        "multimodal": True
    }
}

class UnifiedFallbackProvider(BaseModelProvider):
    """Wraps a primary model provider with an ordered chain of fallbacks."""
    def __init__(self, primary: BaseModelProvider, fallbacks: Optional[List[BaseModelProvider]] = None):
        super().__init__(model_name=primary.model_name, api_key=primary.api_key)
        self.primary = primary
        self.fallbacks = fallbacks or []

    def predict_action(
        self,
        goal: str,
        screen_state_text: str,
        screenshot_bytes: Optional[bytes] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        all_providers = [self.primary] + self.fallbacks
        last_err = None

        for idx, provider in enumerate(all_providers):
            try:
                # If provider doesn't support multimodal vision, pass text only
                prov_name = getattr(provider, "flavor", getattr(provider, "__class__", type(provider)).__name__)
                use_screenshot = screenshot_bytes if getattr(provider, "multimodal", True) else None
                return provider.predict_action(goal, screen_state_text, use_screenshot, history)
            except Exception as e:
                last_err = e
                print(f"[MODEL FAILOVER] Provider #{idx} ({provider.model_name}) failed: {e}. Trying fallback...")

        raise RuntimeError(f"All model providers in failover chain failed. Last error: {last_err}")

def get_model_provider(
    provider_name: str = "gemini",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    enable_fallback: bool = True
) -> BaseModelProvider:
    name = (provider_name or "gemini").lower()
    if name not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {list(PROVIDER_REGISTRY.keys())}")

    meta = PROVIDER_REGISTRY[name]
    # Guard against passing mismatched model names to providers (e.g. from stale env vars or default fallbacks)
    if model_name and "gemini" in model_name.lower() and name not in ("gemini", "openrouter"):
        target_model = meta["default_model"]
    elif model_name and "claude" in model_name.lower() and name not in ("anthropic", "openrouter"):
        target_model = meta["default_model"]
    elif model_name and "gpt" in model_name.lower() and name not in ("openai", "openrouter"):
        target_model = meta["default_model"]
    elif model_name and "llama" in model_name.lower() and name not in ("groq", "ollama", "openrouter"):
        target_model = meta["default_model"]
    else:
        target_model = model_name or meta["default_model"]

    creator = meta["class"]
    primary = creator(target_model, api_key)


    if not enable_fallback:
        return primary

    # Construct safe fallbacks (e.g. fallback to mock or secondary key)
    fallbacks = []

    return UnifiedFallbackProvider(primary=primary, fallbacks=fallbacks)

def get_all_configured_keys() -> Dict[str, str]:
    keys = {}
    for name, meta in PROVIDER_REGISTRY.items():
        env_var = meta.get("env_key")
        if env_var:
            val = os.environ.get(env_var, "")
            keys[name] = val
    return keys
