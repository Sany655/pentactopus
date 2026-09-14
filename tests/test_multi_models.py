"""Unit and integration tests for Unified Multi-Model Gateway."""

import pytest
import json
from models.router import get_model_provider, PROVIDER_REGISTRY, UnifiedFallbackProvider
from models.openai_compatible import OpenAICompatibleProvider
from models.anthropic import AnthropicProvider
from models.mock import MockModelProvider

def test_all_providers_registered():
    expected = {"gemini", "openai", "anthropic", "deepseek", "groq", "openrouter", "ollama", "mock"}
    assert expected.issubset(set(PROVIDER_REGISTRY.keys()))

def test_openai_compatible_initialization():
    provider = OpenAICompatibleProvider(flavor="deepseek", api_key="test-key-123")
    assert provider.flavor == "deepseek"
    assert provider.model_name == "deepseek-chat"
    assert provider.endpoint == "https://api.deepseek.com/chat/completions"
    assert provider.api_key == "test-key-123"

def test_groq_initialization():
    provider = OpenAICompatibleProvider(flavor="groq", api_key="gsk_test")
    assert provider.flavor == "groq"
    assert provider.model_name == "llama-3.3-70b-versatile"
    assert provider.endpoint == "https://api.groq.com/openai/v1/chat/completions"

def test_anthropic_initialization():
    provider = AnthropicProvider(api_key="sk-ant-test")
    assert provider.model_name == "claude-3-5-sonnet-20241022"
    assert provider.endpoint == "https://api.anthropic.com/v1/messages"
    assert provider.api_key == "sk-ant-test"

def test_json_extraction_from_markdown():
    provider = OpenAICompatibleProvider(flavor="openai", api_key="dummy")
    raw_markdown = """```json
{"action": "tap", "x": 300, "y": 700}
```"""
    parsed = provider._extract_json(raw_markdown)
    assert parsed["action"] == "tap"
    assert parsed["x"] == 300
    assert parsed["y"] == 700

def test_fallback_mechanism():
    class FailingProvider:
        model_name = "failing-model"
        api_key = "dummy"
        def predict_action(self, *args, **kwargs):
            raise ConnectionError("Rate limit 429: quota exceeded")

    mock_backup = MockModelProvider("mock-v1")
    fallback_chain = UnifiedFallbackProvider(primary=FailingProvider(), fallbacks=[mock_backup])
    
    # Should not raise exception; should seamlessly fallback to mock
    res = fallback_chain.predict_action(goal="Open Settings", screen_state_text="Elements: [Settings]")
    assert "action" in res
