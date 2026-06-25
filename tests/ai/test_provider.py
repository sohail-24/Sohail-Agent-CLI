import pytest

from src.ai.exceptions import AIProviderError
from src.ai.provider import AIProviderFactory, ProviderSpec
from src.providers import MockProvider, OllamaProvider


def test_provider_factory_creates_mock_provider():
    provider = AIProviderFactory().create(ProviderSpec(name="mock"))
    assert isinstance(provider, MockProvider)


def test_provider_factory_creates_ollama_provider():
    provider = AIProviderFactory().create(ProviderSpec(name="ollama"))
    assert isinstance(provider, OllamaProvider)


def test_provider_factory_rejects_cloud_placeholders():
    with pytest.raises(AIProviderError, match="placeholder"):
        AIProviderFactory().create(ProviderSpec(name="openai"))


def test_provider_factory_uses_explicit_provider():
    provider = MockProvider()
    assert AIProviderFactory().create(provider=provider) is provider
