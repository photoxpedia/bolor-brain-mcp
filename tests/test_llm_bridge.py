"""
Tests for the LLM Bridge module.

TDD: These tests are written BEFORE the implementation.
The LLM bridge must support:
- Disabled mode (pure symbolic, no LLM dependency)
- Enabled mode with lazy-loaded LLM client
- Fallback to symbolic formatting on LLM error
- Three use cases: synthesis, creative, ambiguous
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestLLMBridgeDisabled:
    """Test LLMBridge behavior when LLM is disabled."""

    def test_bridge_creation_when_disabled(self):
        """LLMBridge should be creatable even when LLM is disabled."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(llm_enabled=False)
        bridge = LLMBridge(config)

        assert bridge.enabled is False
        assert bridge.config == config

    @pytest.mark.asyncio
    async def test_synthesize_without_llm(self):
        """synthesize() should use template formatting when LLM is disabled."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(llm_enabled=False)
        bridge = LLMBridge(config)

        # Create a structured result to synthesize
        structured_result = {
            "conclusion": "The evidence supports conclusion X",
            "confidence": 0.85,
            "reasoning_steps": ["Step 1", "Step 2", "Step 3"]
        }

        response = await bridge.synthesize(structured_result, output_style="detailed")

        # Should return an LLMResponse with formatted text
        assert response.success is True
        assert response.used_llm is False
        assert "conclusion" in response.content.lower() or "The evidence" in response.content
        assert response.fallback_reason == "llm_disabled"

    @pytest.mark.asyncio
    async def test_enhance_creativity_returns_base_ideas(self):
        """enhance_creativity() should return base ideas when LLM is disabled."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(llm_enabled=False)
        bridge = LLMBridge(config)

        base_ideas = ["Idea 1", "Idea 2", "Idea 3"]
        challenge = "How to improve system performance"
        constraints = ["Limited budget", "Short timeline"]

        response = await bridge.enhance_creativity(base_ideas, challenge, constraints)

        # Should return the base ideas without LLM enhancement
        assert response.success is True
        assert response.used_llm is False
        # The content should contain all base ideas
        for idea in base_ideas:
            assert idea in response.content or idea in str(response.ideas)


class TestLLMBridgeEnabled:
    """Test LLMBridge behavior when LLM is enabled."""

    def test_bridge_creation_requires_no_key_until_use(self):
        """LLMBridge should be creatable without API key; key only needed on first use."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key=None  # No key provided
        )
        bridge = LLMBridge(config)

        # Bridge should be created successfully (lazy loading)
        assert bridge.enabled is True
        assert bridge._client is None  # Client not initialized yet

    def test_client_lazy_loaded(self):
        """Client should not be initialized until first access."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key"
        )
        bridge = LLMBridge(config)

        # _client should be None before first use
        assert bridge._client is None

    @pytest.mark.asyncio
    async def test_synthesize_with_mock_llm(self):
        """synthesize() should use LLM when enabled and synthesis is in use_for."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_use_for=["synthesis"]
        )
        bridge = LLMBridge(config)

        # Mock the _call_llm method
        bridge._call_llm = AsyncMock(return_value="LLM synthesized output")

        structured_result = {
            "conclusion": "Test conclusion",
            "confidence": 0.9
        }

        response = await bridge.synthesize(structured_result, output_style="detailed")

        # Should have used LLM
        assert response.success is True
        assert response.used_llm is True
        assert "LLM synthesized output" in response.content
        bridge._call_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesize_skips_llm_when_not_in_use_for(self):
        """synthesize() should use template when synthesis is not in use_for."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_use_for=["creative"]  # synthesis not included
        )
        bridge = LLMBridge(config)

        structured_result = {
            "conclusion": "Test conclusion",
            "confidence": 0.9
        }

        response = await bridge.synthesize(structured_result, output_style="detailed")

        # Should NOT have used LLM (synthesis not in use_for)
        assert response.success is True
        assert response.used_llm is False
        assert response.fallback_reason == "use_case_not_enabled"


class TestLLMBridgeFallback:
    """Test LLMBridge fallback behavior on errors."""

    @pytest.mark.asyncio
    async def test_fallback_to_symbolic_on_llm_error(self):
        """Should fallback to symbolic formatting when LLM call fails."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_use_for=["synthesis"],
            llm_fallback_to_symbolic=True
        )
        bridge = LLMBridge(config)

        # Mock _call_llm to raise an exception
        bridge._call_llm = AsyncMock(side_effect=Exception("API Error"))

        structured_result = {
            "conclusion": "Test conclusion",
            "confidence": 0.9
        }

        response = await bridge.synthesize(structured_result, output_style="detailed")

        # Should fallback to symbolic formatting
        assert response.success is True
        assert response.used_llm is False
        assert response.fallback_reason == "llm_error"
        assert "Test conclusion" in response.content or "conclusion" in response.content.lower()

    @pytest.mark.asyncio
    async def test_no_fallback_when_disabled(self):
        """Should raise error when LLM fails and fallback is disabled."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge, LLMBridgeError

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_use_for=["synthesis"],
            llm_fallback_to_symbolic=False
        )
        bridge = LLMBridge(config)

        # Mock _call_llm to raise an exception
        bridge._call_llm = AsyncMock(side_effect=Exception("API Error"))

        structured_result = {
            "conclusion": "Test conclusion",
            "confidence": 0.9
        }

        with pytest.raises(LLMBridgeError, match="LLM call failed"):
            await bridge.synthesize(structured_result, output_style="detailed")


class TestLLMBridgeResolveAmbiguity:
    """Test resolve_ambiguity method."""

    @pytest.mark.asyncio
    async def test_resolve_ambiguity_when_disabled(self):
        """resolve_ambiguity() should return symbolic result when LLM disabled."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(llm_enabled=False)
        bridge = LLMBridge(config)

        symbolic_result = {
            "interpretation_1": {"meaning": "A", "score": 0.6},
            "interpretation_2": {"meaning": "B", "score": 0.4}
        }

        response = await bridge.resolve_ambiguity(symbolic_result, confidence=0.5)

        assert response.success is True
        assert response.used_llm is False
        # Should return highest scoring interpretation
        assert "A" in response.content or "interpretation_1" in response.content

    @pytest.mark.asyncio
    async def test_resolve_ambiguity_with_llm(self):
        """resolve_ambiguity() should use LLM when enabled."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_use_for=["ambiguous"]
        )
        bridge = LLMBridge(config)

        # Mock the _call_llm method
        bridge._call_llm = AsyncMock(return_value="The most likely interpretation is A because...")

        symbolic_result = {
            "interpretation_1": {"meaning": "A", "score": 0.6},
            "interpretation_2": {"meaning": "B", "score": 0.4}
        }

        response = await bridge.resolve_ambiguity(symbolic_result, confidence=0.5)

        assert response.success is True
        assert response.used_llm is True
        assert "interpretation is A" in response.content


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """LLMResponse should be creatable with all fields."""
        from modules.llm_bridge import LLMResponse

        response = LLMResponse(
            success=True,
            content="Test content",
            used_llm=False,
            fallback_reason="llm_disabled"
        )

        assert response.success is True
        assert response.content == "Test content"
        assert response.used_llm is False
        assert response.fallback_reason == "llm_disabled"

    def test_llm_response_with_ideas(self):
        """LLMResponse should support optional ideas list."""
        from modules.llm_bridge import LLMResponse

        response = LLMResponse(
            success=True,
            content="Generated ideas",
            used_llm=True,
            ideas=["Idea 1", "Idea 2"]
        )

        assert response.ideas == ["Idea 1", "Idea 2"]


class TestLLMBridgeProviders:
    """Test LLM client initialization for different providers."""

    def test_openai_provider_init(self):
        """OpenAI provider should initialize correctly."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_model="gpt-4"
        )
        bridge = LLMBridge(config)

        # Verify config is stored
        assert bridge.config.llm_provider == "openai"
        assert bridge.config.llm_model == "gpt-4"

    def test_anthropic_provider_init(self):
        """Anthropic provider should initialize correctly."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="anthropic",
            llm_api_key="test-key",
            llm_model="claude-3-opus"
        )
        bridge = LLMBridge(config)

        assert bridge.config.llm_provider == "anthropic"
        assert bridge.config.llm_model == "claude-3-opus"

    def test_ollama_provider_init(self):
        """Ollama provider should initialize correctly."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="ollama",
            llm_base_url="http://localhost:11434",
            llm_model="llama3"
        )
        bridge = LLMBridge(config)

        assert bridge.config.llm_provider == "ollama"
        assert bridge.config.llm_base_url == "http://localhost:11434"

    def test_custom_provider_init(self):
        """Custom provider should initialize correctly."""
        from modules.config import Config
        from modules.llm_bridge import LLMBridge

        config = Config(
            llm_enabled=True,
            llm_provider="custom",
            llm_base_url="https://custom-api.example.com",
            llm_api_key="custom-key",
            llm_model="custom-model"
        )
        bridge = LLMBridge(config)

        assert bridge.config.llm_provider == "custom"
        assert bridge.config.llm_base_url == "https://custom-api.example.com"
