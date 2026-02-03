# Phase 1: Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Set up the foundation for Universal Thinking MCP - config system, LLM bridge, and cognitive genome.

**Architecture:** Extend existing Bolor-Brain-MCP with new modules. Config controls all behavior. LLM bridge is optional (system works without it). Genome provides 60+ evolvable parameters that control cognition.

**Tech Stack:** Python 3.11+, dataclasses, asyncio, optional openai/anthropic/ollama clients

---

## Task 1: Create Config System

**Files:**
- Create: `modules/config.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
import pytest
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config, validate_python_version


class TestConfig:
    def test_default_config_has_llm_disabled(self):
        """Default config should have LLM disabled (standalone mode)."""
        config = Config()
        assert config.llm_enabled is False

    def test_config_accepts_llm_settings(self):
        """Config should accept LLM provider settings."""
        config = Config(
            llm_enabled=True,
            llm_provider="anthropic",
            llm_model="claude-sonnet-4-20250514"
        )
        assert config.llm_enabled is True
        assert config.llm_provider == "anthropic"
        assert config.llm_model == "claude-sonnet-4-20250514"

    def test_config_from_env(self):
        """Config should load from environment variables."""
        os.environ["BOLOR_LLM_ENABLED"] = "true"
        os.environ["BOLOR_LLM_PROVIDER"] = "ollama"
        config = Config.from_env()
        assert config.llm_enabled is True
        assert config.llm_provider == "ollama"
        # Cleanup
        del os.environ["BOLOR_LLM_ENABLED"]
        del os.environ["BOLOR_LLM_PROVIDER"]

    def test_python_version_check(self):
        """Should validate Python version is 3.11+."""
        # This should not raise since we're running on valid Python
        validate_python_version()  # No exception = pass


class TestConfigValidation:
    def test_invalid_provider_raises(self):
        """Invalid LLM provider should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            Config(llm_enabled=True, llm_provider="invalid_provider")

    def test_enabled_without_provider_uses_default(self):
        """Enabling LLM without provider should use default."""
        config = Config(llm_enabled=True)
        assert config.llm_provider == "openai"  # default
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'modules.config'"

**Step 3: Write the implementation**

```python
# modules/config.py
"""
Configuration system for Bolor-Brain-MCP.

Supports:
- Standalone mode (no LLM, pure symbolic reasoning)
- LLM-enhanced mode (symbolic + LLM synthesis)
- Environment variable configuration
- Runtime mode switching
"""

from dataclasses import dataclass, field
from typing import Optional, List
import os
import sys


# Valid LLM providers
VALID_PROVIDERS = {"openai", "anthropic", "ollama", "custom"}

# Minimum Python version
MIN_PYTHON = (3, 11)
MAX_PYTHON = (3, 13)


def validate_python_version() -> None:
    """Ensure Python version is compatible."""
    if sys.version_info < MIN_PYTHON:
        sys.exit(
            f"Bolor-Brain-MCP requires Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+. "
            f"You have Python {sys.version_info[0]}.{sys.version_info[1]}"
        )
    if sys.version_info >= MAX_PYTHON:
        import warnings
        warnings.warn(
            f"Python {sys.version_info[0]}.{sys.version_info[1]} is untested. "
            f"Python 3.11-3.12 recommended.",
            UserWarning
        )


@dataclass
class Config:
    """
    Central configuration for Bolor-Brain-MCP.

    Two modes:
    - Standalone (llm_enabled=False): Pure symbolic + case-based reasoning
    - LLM-Enhanced (llm_enabled=True): Symbolic first, LLM synthesizes output

    Example:
        # Standalone mode (default)
        config = Config()

        # LLM-enhanced mode
        config = Config(
            llm_enabled=True,
            llm_provider="anthropic",
            llm_model="claude-sonnet-4-20250514"
        )

        # From environment
        config = Config.from_env()
    """

    # === LLM Configuration ===
    llm_enabled: bool = False
    llm_provider: str = "openai"  # openai, anthropic, ollama, custom
    llm_model: str = "gpt-4o"
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None  # For ollama/custom endpoints
    llm_timeout: float = 30.0
    llm_fallback_to_symbolic: bool = True  # If LLM fails, use symbolic
    llm_use_for: List[str] = field(default_factory=lambda: [
        "synthesis",    # Combine insights into natural language
        "creative",     # Novel idea generation
        "ambiguous",    # When symbolic reasoning is uncertain
    ])

    # === Database Configuration ===
    db_path: str = "brain.db"

    # === Embedding Configuration ===
    embedding_model: str = "all-mpnet-base-v2"
    embedding_device: str = "cpu"  # cpu, cuda, mps
    embedding_cache_enabled: bool = True
    embedding_cache_size: int = 1000

    # === Reasoning Configuration ===
    reasoning_default_mode: str = "hybrid"  # symbolic, case_based, hybrid
    reasoning_confidence_threshold: float = 0.3  # Below this, try LLM if enabled
    reasoning_max_steps: int = 10  # Max inference steps

    # === Framework Configuration ===
    framework_auto_select: bool = True  # Auto-select best framework
    framework_max_parallel: int = 3  # Max frameworks to apply in parallel

    # === Learning Configuration ===
    learning_enabled: bool = True
    learning_min_confidence: float = 0.3  # Min confidence to store pattern

    # === Debug Configuration ===
    debug: bool = False
    log_level: str = "INFO"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.llm_enabled and self.llm_provider not in VALID_PROVIDERS:
            raise ValueError(
                f"Unknown LLM provider: {self.llm_provider}. "
                f"Valid providers: {VALID_PROVIDERS}"
            )

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create config from environment variables.

        Environment variables (all prefixed with BOLOR_):
        - BOLOR_LLM_ENABLED: true/false
        - BOLOR_LLM_PROVIDER: openai/anthropic/ollama/custom
        - BOLOR_LLM_MODEL: model name
        - BOLOR_LLM_API_KEY: API key
        - BOLOR_LLM_BASE_URL: Base URL for custom/ollama
        - BOLOR_DB_PATH: Database path
        - BOLOR_DEBUG: true/false
        - BOLOR_LOG_LEVEL: DEBUG/INFO/WARNING/ERROR
        """
        def get_bool(key: str, default: bool) -> bool:
            val = os.environ.get(key, "").lower()
            if val in ("true", "1", "yes"):
                return True
            elif val in ("false", "0", "no"):
                return False
            return default

        def get_float(key: str, default: float) -> float:
            val = os.environ.get(key)
            if val:
                try:
                    return float(val)
                except ValueError:
                    pass
            return default

        def get_int(key: str, default: int) -> int:
            val = os.environ.get(key)
            if val:
                try:
                    return int(val)
                except ValueError:
                    pass
            return default

        return cls(
            llm_enabled=get_bool("BOLOR_LLM_ENABLED", False),
            llm_provider=os.environ.get("BOLOR_LLM_PROVIDER", "openai"),
            llm_model=os.environ.get("BOLOR_LLM_MODEL", "gpt-4o"),
            llm_api_key=os.environ.get("BOLOR_LLM_API_KEY"),
            llm_base_url=os.environ.get("BOLOR_LLM_BASE_URL"),
            llm_timeout=get_float("BOLOR_LLM_TIMEOUT", 30.0),
            llm_fallback_to_symbolic=get_bool("BOLOR_LLM_FALLBACK", True),
            db_path=os.environ.get("BOLOR_DB_PATH", "brain.db"),
            embedding_model=os.environ.get("BOLOR_EMBEDDING_MODEL", "all-mpnet-base-v2"),
            embedding_device=os.environ.get("BOLOR_EMBEDDING_DEVICE", "cpu"),
            debug=get_bool("BOLOR_DEBUG", False),
            log_level=os.environ.get("BOLOR_LOG_LEVEL", "INFO"),
        )

    def to_dict(self) -> dict:
        """Convert config to dictionary (for serialization)."""
        return {
            "llm_enabled": self.llm_enabled,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_base_url": self.llm_base_url,
            "llm_timeout": self.llm_timeout,
            "llm_fallback_to_symbolic": self.llm_fallback_to_symbolic,
            "llm_use_for": self.llm_use_for,
            "db_path": self.db_path,
            "embedding_model": self.embedding_model,
            "embedding_device": self.embedding_device,
            "reasoning_default_mode": self.reasoning_default_mode,
            "reasoning_confidence_threshold": self.reasoning_confidence_threshold,
            "framework_auto_select": self.framework_auto_select,
            "learning_enabled": self.learning_enabled,
            "debug": self.debug,
            "log_level": self.log_level,
        }


# Global config instance (can be overridden)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global config instance."""
    global _config
    _config = config
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/test_config.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add modules/config.py tests/test_config.py
git commit -m "feat(config): add configuration system with LLM toggle

- Standalone mode (default): pure symbolic reasoning
- LLM-enhanced mode: symbolic + LLM synthesis
- Environment variable support (BOLOR_* prefix)
- Python version validation (3.11+)
- Runtime mode switching"
```

---

## Task 2: Create LLM Bridge

**Files:**
- Create: `modules/llm_bridge.py`
- Create: `tests/test_llm_bridge.py`

**Step 1: Write the failing test**

```python
# tests/test_llm_bridge.py
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config
from modules.llm_bridge import LLMBridge


class TestLLMBridgeDisabled:
    """Test LLM bridge when disabled (standalone mode)."""

    def test_bridge_creation_when_disabled(self):
        """Bridge should create successfully when LLM disabled."""
        config = Config(llm_enabled=False)
        bridge = LLMBridge(config)
        assert bridge.enabled is False
        assert bridge.client is None

    @pytest.mark.asyncio
    async def test_synthesize_without_llm(self):
        """Synthesize should return formatted text without LLM."""
        config = Config(llm_enabled=False)
        bridge = LLMBridge(config)

        result = await bridge.synthesize({
            "conclusion": "Test conclusion",
            "confidence": 0.85,
            "reasoning_chain": ["Step 1", "Step 2"],
            "evidence": ["Fact A", "Fact B"]
        })

        assert "Test conclusion" in result
        assert "85%" in result or "0.85" in result
        assert "Step 1" in result

    @pytest.mark.asyncio
    async def test_enhance_creativity_returns_base_ideas(self):
        """Without LLM, should return base ideas unchanged."""
        config = Config(llm_enabled=False)
        bridge = LLMBridge(config)

        base_ideas = ["Idea 1", "Idea 2"]
        result = await bridge.enhance_creativity(
            base_ideas=base_ideas,
            challenge="Test challenge",
            constraints={}
        )

        assert result == base_ideas


class TestLLMBridgeEnabled:
    """Test LLM bridge when enabled."""

    def test_bridge_creation_requires_no_key_until_use(self):
        """Bridge should create without API key (lazy loading)."""
        config = Config(llm_enabled=True, llm_provider="openai")
        bridge = LLMBridge(config)
        assert bridge.enabled is True
        # Client not created until first use (lazy)

    @pytest.mark.asyncio
    async def test_synthesize_with_mock_llm(self):
        """Synthesize should call LLM when enabled."""
        config = Config(llm_enabled=True, llm_provider="openai", llm_api_key="test-key")
        bridge = LLMBridge(config)

        # Mock the LLM call
        bridge._call_llm = AsyncMock(return_value="LLM synthesized response")

        result = await bridge.synthesize({
            "conclusion": "Test",
            "confidence": 0.8,
            "reasoning_chain": [],
            "evidence": []
        })

        assert result == "LLM synthesized response"
        bridge._call_llm.assert_called_once()


class TestLLMBridgeFallback:
    """Test fallback behavior."""

    @pytest.mark.asyncio
    async def test_fallback_to_symbolic_on_llm_error(self):
        """Should fallback to symbolic formatting on LLM error."""
        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_fallback_to_symbolic=True
        )
        bridge = LLMBridge(config)

        # Mock LLM to raise error
        bridge._call_llm = AsyncMock(side_effect=Exception("API Error"))

        result = await bridge.synthesize({
            "conclusion": "Fallback test",
            "confidence": 0.75,
            "reasoning_chain": ["Step 1"],
            "evidence": []
        })

        # Should get formatted output, not error
        assert "Fallback test" in result
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/test_llm_bridge.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'modules.llm_bridge'"

**Step 3: Write the implementation**

```python
# modules/llm_bridge.py
"""
LLM Bridge - Optional LLM integration for Bolor-Brain-MCP.

The system works WITHOUT this - all logic is symbolic-verified first.
LLM enhances output (natural language synthesis, creativity boost) when enabled.

Supports:
- OpenAI (gpt-4o, gpt-4-turbo, etc.)
- Anthropic (claude-sonnet-4-20250514, claude-opus-4-20250514, etc.)
- Ollama (local models)
- Custom endpoints

Key principle: LLM enhances, never replaces. All logic is symbolic-verified first.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
import asyncio
import logging

from .config import Config


logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM call."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    raw: Optional[Any] = None


class LLMBridge:
    """
    Optional LLM integration. System works without it.

    When disabled: Returns template-formatted output
    When enabled: Symbolic reasoning first, then LLM synthesizes

    Example:
        bridge = LLMBridge(config)

        # With LLM (if enabled) or formatted text (if disabled)
        result = await bridge.synthesize({
            "conclusion": "...",
            "confidence": 0.8,
            "reasoning_chain": [...],
            "evidence": [...]
        })
    """

    def __init__(self, config: Config):
        self.config = config
        self.enabled = config.llm_enabled
        self.provider = config.llm_provider
        self.model = config.llm_model
        self.timeout = config.llm_timeout
        self.fallback_to_symbolic = config.llm_fallback_to_symbolic
        self.use_for = config.llm_use_for

        # Lazy-loaded client
        self._client = None

    @property
    def client(self):
        """Lazy-load LLM client on first use."""
        if not self.enabled:
            return None

        if self._client is None:
            self._client = self._init_client()

        return self._client

    def _init_client(self):
        """Initialize LLM client based on provider."""
        if not self.enabled:
            return None

        try:
            if self.provider == "openai":
                from openai import AsyncOpenAI
                return AsyncOpenAI(
                    api_key=self.config.llm_api_key,
                    base_url=self.config.llm_base_url,
                    timeout=self.timeout
                )
            elif self.provider == "anthropic":
                from anthropic import AsyncAnthropic
                return AsyncAnthropic(
                    api_key=self.config.llm_api_key,
                    timeout=self.timeout
                )
            elif self.provider == "ollama":
                from ollama import AsyncClient
                return AsyncClient(
                    host=self.config.llm_base_url or "http://localhost:11434"
                )
            elif self.provider == "custom":
                # Custom provider uses OpenAI-compatible API
                from openai import AsyncOpenAI
                return AsyncOpenAI(
                    api_key=self.config.llm_api_key or "not-needed",
                    base_url=self.config.llm_base_url,
                    timeout=self.timeout
                )
            else:
                logger.warning(f"Unknown provider {self.provider}, disabling LLM")
                self.enabled = False
                return None
        except ImportError as e:
            logger.warning(f"LLM client library not installed: {e}. Disabling LLM.")
            self.enabled = False
            return None

    async def _call_llm(self, prompt: str, system: Optional[str] = None) -> str:
        """Make LLM API call."""
        if not self.enabled or self.client is None:
            raise RuntimeError("LLM not enabled")

        try:
            if self.provider == "openai" or self.provider == "custom":
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=system or "You are a helpful assistant.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif self.provider == "ollama":
                response = await self.client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system or "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response["message"]["content"]

            else:
                raise ValueError(f"Unknown provider: {self.provider}")

        except asyncio.TimeoutError:
            logger.error(f"LLM call timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    async def synthesize(
        self,
        structured_result: Dict[str, Any],
        output_style: str = "concise"
    ) -> str:
        """
        Convert structured reasoning to natural language.

        Args:
            structured_result: Dict with conclusion, confidence, reasoning_chain, evidence
            output_style: "concise", "detailed", or "technical"

        Returns:
            Natural language synthesis (from LLM if enabled, template if not)
        """
        if not self.enabled or "synthesis" not in self.use_for:
            return self._format_without_llm(structured_result, output_style)

        try:
            prompt = self._build_synthesis_prompt(structured_result, output_style)
            system = (
                "You are a clear, concise communicator. Transform structured reasoning "
                "into natural language. Preserve the logic chain but make it readable. "
                "Do not add information beyond what's provided."
            )
            return await self._call_llm(prompt, system)
        except Exception as e:
            if self.fallback_to_symbolic:
                logger.warning(f"LLM synthesis failed, falling back to template: {e}")
                return self._format_without_llm(structured_result, output_style)
            raise

    async def enhance_creativity(
        self,
        base_ideas: List[str],
        challenge: str,
        constraints: Dict[str, Any]
    ) -> List[str]:
        """
        Generate additional creative ideas (LLM optional).

        Args:
            base_ideas: Ideas from symbolic/case-based reasoning
            challenge: The creative challenge
            constraints: Constraints to respect

        Returns:
            Combined list of base + LLM-generated ideas
        """
        if not self.enabled or "creative" not in self.use_for:
            return base_ideas

        try:
            prompt = self._build_creativity_prompt(base_ideas, challenge, constraints)
            system = (
                "You are a creative problem solver. Generate novel ideas that are "
                "distinct from the provided base ideas. Respect all constraints. "
                "Return only new ideas, one per line."
            )
            response = await self._call_llm(prompt, system)
            new_ideas = [line.strip() for line in response.split("\n") if line.strip()]
            return base_ideas + new_ideas
        except Exception as e:
            if self.fallback_to_symbolic:
                logger.warning(f"LLM creativity enhancement failed: {e}")
                return base_ideas
            raise

    async def resolve_ambiguity(
        self,
        symbolic_result: Dict[str, Any],
        confidence: float
    ) -> Dict[str, Any]:
        """
        When symbolic reasoning is uncertain, ask LLM for clarification.

        Args:
            symbolic_result: Result from symbolic reasoning
            confidence: Confidence level (0-1)

        Returns:
            Enhanced result with LLM input (or original if LLM disabled/not needed)
        """
        # Don't use LLM if confidence is already high enough
        if confidence >= self.config.reasoning_confidence_threshold:
            return symbolic_result

        if not self.enabled or "ambiguous" not in self.use_for:
            return symbolic_result

        try:
            prompt = self._build_disambiguation_prompt(symbolic_result)
            system = (
                "You are analyzing an uncertain reasoning result. "
                "Provide additional insights to clarify the ambiguity. "
                "Return your analysis as JSON with 'clarification' and 'confidence_boost' keys."
            )
            response = await self._call_llm(prompt, system)

            # Try to parse JSON response
            import json
            try:
                enhancement = json.loads(response)
                if "clarification" in enhancement:
                    symbolic_result["llm_clarification"] = enhancement["clarification"]
                if "confidence_boost" in enhancement:
                    symbolic_result["confidence"] = min(
                        1.0,
                        confidence + float(enhancement.get("confidence_boost", 0))
                    )
            except json.JSONDecodeError:
                symbolic_result["llm_clarification"] = response

            return symbolic_result
        except Exception as e:
            if self.fallback_to_symbolic:
                logger.warning(f"LLM disambiguation failed: {e}")
                return symbolic_result
            raise

    def _format_without_llm(
        self,
        result: Dict[str, Any],
        style: str = "concise"
    ) -> str:
        """Clean formatting without LLM."""
        conclusion = result.get("conclusion", "No conclusion")
        confidence = result.get("confidence", 0)
        chain = result.get("reasoning_chain", [])
        evidence = result.get("evidence", [])
        uncertainties = result.get("uncertainties", [])
        next_steps = result.get("next_steps", [])

        parts = []

        # Conclusion
        parts.append(f"**Conclusion:** {conclusion}")
        parts.append(f"**Confidence:** {confidence:.0%}")

        # Reasoning chain
        if chain:
            parts.append("\n**Reasoning:**")
            for i, step in enumerate(chain, 1):
                parts.append(f"  {i}. {step}")

        # Evidence
        if evidence and style != "concise":
            parts.append("\n**Evidence:**")
            for item in evidence:
                parts.append(f"  • {item}")

        # Uncertainties
        if uncertainties and style == "detailed":
            parts.append("\n**Uncertainties:**")
            for item in uncertainties:
                parts.append(f"  • {item}")

        # Next steps
        if next_steps:
            parts.append("\n**Next Steps:**")
            for item in next_steps:
                parts.append(f"  • {item}")

        return "\n".join(parts)

    def _build_synthesis_prompt(
        self,
        result: Dict[str, Any],
        style: str
    ) -> str:
        """Build prompt for LLM synthesis."""
        return f"""Transform this structured reasoning into clear natural language.

Style: {style}

Conclusion: {result.get('conclusion', 'N/A')}
Confidence: {result.get('confidence', 0):.0%}

Reasoning Chain:
{chr(10).join(f'- {step}' for step in result.get('reasoning_chain', []))}

Evidence:
{chr(10).join(f'- {e}' for e in result.get('evidence', []))}

Uncertainties:
{chr(10).join(f'- {u}' for u in result.get('uncertainties', []))}

Write a clear, natural response that captures this reasoning."""

    def _build_creativity_prompt(
        self,
        base_ideas: List[str],
        challenge: str,
        constraints: Dict[str, Any]
    ) -> str:
        """Build prompt for creativity enhancement."""
        constraint_str = "\n".join(f"- {k}: {v}" for k, v in constraints.items())
        ideas_str = "\n".join(f"- {idea}" for idea in base_ideas)

        return f"""Generate creative solutions for this challenge.

Challenge: {challenge}

Constraints:
{constraint_str or "- None specified"}

Existing ideas (do not repeat these):
{ideas_str}

Generate 3-5 novel ideas that are distinct from the existing ones.
One idea per line, no numbering or bullets."""

    def _build_disambiguation_prompt(self, result: Dict[str, Any]) -> str:
        """Build prompt for ambiguity resolution."""
        return f"""Analyze this uncertain reasoning result and provide clarification.

Current conclusion: {result.get('conclusion', 'N/A')}
Current confidence: {result.get('confidence', 0):.0%}
Reasoning: {result.get('reasoning_chain', [])}

What clarifications or additional insights can resolve the uncertainty?

Return as JSON: {{"clarification": "your insight", "confidence_boost": 0.0-0.3}}"""
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/test_llm_bridge.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add modules/llm_bridge.py tests/test_llm_bridge.py
git commit -m "feat(llm): add optional LLM bridge

- Supports OpenAI, Anthropic, Ollama, custom endpoints
- Lazy-loads client on first use
- Fallback to symbolic formatting on LLM error
- Three LLM use cases: synthesis, creative, ambiguous
- Template formatting when LLM disabled"
```

---

## Task 3: Create Cognitive Genome

**Files:**
- Create: `modules/genome.py`
- Create: `tests/test_genome.py`

**Step 1: Write the failing test**

```python
# tests/test_genome.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.genome import CognitiveGenome, Gene, GeneCategory


class TestGeneBasics:
    def test_gene_creation(self):
        """Gene should have name, value, bounds, and metadata."""
        gene = Gene(
            name="curiosity_baseline",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.DRIVES
        )
        assert gene.name == "curiosity_baseline"
        assert gene.value == 0.5
        assert gene.min_value == 0.0
        assert gene.max_value == 1.0

    def test_gene_clamps_value(self):
        """Gene value should be clamped to bounds."""
        gene = Gene(
            name="test",
            value=1.5,  # Over max
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.DRIVES
        )
        assert gene.value == 1.0  # Clamped to max


class TestCognitiveGenome:
    def test_genome_has_default_genes(self):
        """Genome should initialize with default genes."""
        genome = CognitiveGenome()
        assert len(genome.genes) > 50  # Should have 60+ genes

    def test_get_gene_value(self):
        """Should retrieve gene value by name."""
        genome = CognitiveGenome()
        value = genome.get("curiosity_baseline")
        assert 0.0 <= value <= 1.0

    def test_set_gene_value(self):
        """Should update gene value."""
        genome = CognitiveGenome()
        genome.set("curiosity_baseline", 0.8)
        assert genome.get("curiosity_baseline") == 0.8

    def test_mutate_gene(self):
        """Mutate should change gene value within bounds."""
        genome = CognitiveGenome()
        original = genome.get("curiosity_baseline")
        genome.mutate("curiosity_baseline", magnitude=0.1)
        mutated = genome.get("curiosity_baseline")
        # Value changed but within bounds
        assert 0.0 <= mutated <= 1.0

    def test_evolve_on_stagnation(self):
        """Evolve should mutate multiple genes on stagnation."""
        genome = CognitiveGenome()
        original_values = {name: genome.get(name) for name in list(genome.genes.keys())[:10]}

        genome.evolve(trigger="stagnation", mutation_rate=0.5)

        new_values = {name: genome.get(name) for name in list(genome.genes.keys())[:10]}
        # At least some values should have changed
        changed = sum(1 for k in original_values if original_values[k] != new_values[k])
        assert changed > 0

    def test_get_category_genes(self):
        """Should retrieve all genes in a category."""
        genome = CognitiveGenome()
        drive_genes = genome.get_category(GeneCategory.DRIVES)
        assert len(drive_genes) > 0
        assert all(g.category == GeneCategory.DRIVES for g in drive_genes)

    def test_genome_to_dict(self):
        """Should export genome as dictionary."""
        genome = CognitiveGenome()
        data = genome.to_dict()
        assert "genes" in data
        assert "fitness" in data
        assert len(data["genes"]) > 50
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/test_genome.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'modules.genome'"

**Step 3: Write the implementation**

```python
# modules/genome.py
"""
Cognitive Genome - Evolvable parameters controlling all cognition.

The genome contains 60+ genes organized into categories:
- ATTENTION: What draws focus
- DRIVES: Intrinsic motivation levels
- REASONING: How to think
- ACTION: When to act
- LEARNING: How to learn
- SIMULATION: World model parameters
- CREATIVITY: Novel generation
- SOCIAL: Interpersonal parameters

Evolution triggers:
- Stagnation: 50+ cycles without progress → mutate 10% of genes
- Breakthrough: >0.8 success rate → preserve good genes

This replaces hardcoded magic numbers with learnable parameters.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import random
import json
import logging


logger = logging.getLogger(__name__)


class GeneCategory(Enum):
    """Categories of cognitive genes."""
    ATTENTION = "attention"
    DRIVES = "drives"
    REASONING = "reasoning"
    ACTION = "action"
    LEARNING = "learning"
    SIMULATION = "simulation"
    CREATIVITY = "creativity"
    SOCIAL = "social"


@dataclass
class Gene:
    """
    A single evolvable parameter.

    Attributes:
        name: Unique identifier
        value: Current value (clamped to bounds)
        min_value: Lower bound
        max_value: Upper bound
        category: Which aspect of cognition this controls
        description: Human-readable description
        fitness: How well this gene has performed (0-1)
    """
    name: str
    value: float
    min_value: float
    max_value: float
    category: GeneCategory
    description: str = ""
    fitness: float = 0.5  # Neutral starting fitness

    def __post_init__(self):
        """Clamp value to bounds."""
        self.value = max(self.min_value, min(self.max_value, self.value))

    def mutate(self, magnitude: float = 0.1) -> float:
        """
        Mutate gene value by random amount.

        Args:
            magnitude: Max change as fraction of range

        Returns:
            New value after mutation
        """
        range_size = self.max_value - self.min_value
        delta = random.uniform(-magnitude, magnitude) * range_size
        self.value = max(self.min_value, min(self.max_value, self.value + delta))
        return self.value

    def to_dict(self) -> Dict[str, Any]:
        """Export gene as dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "category": self.category.value,
            "description": self.description,
            "fitness": self.fitness
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Gene":
        """Create gene from dictionary."""
        return cls(
            name=data["name"],
            value=data["value"],
            min_value=data["min_value"],
            max_value=data["max_value"],
            category=GeneCategory(data["category"]),
            description=data.get("description", ""),
            fitness=data.get("fitness", 0.5)
        )


# Default genes - the 60+ evolvable parameters
DEFAULT_GENES = [
    # === ATTENTION GENES ===
    Gene("incomplete_pattern_weight", 0.7, 0.0, 1.0, GeneCategory.ATTENTION,
         "Weight for incomplete patterns in attention"),
    Gene("knowledge_gap_weight", 0.8, 0.0, 1.0, GeneCategory.ATTENTION,
         "Weight for knowledge gaps in attention"),
    Gene("exploration_rate", 0.3, 0.0, 1.0, GeneCategory.ATTENTION,
         "How much to explore vs exploit"),
    Gene("focus_duration", 3.0, 1.0, 10.0, GeneCategory.ATTENTION,
         "How long to maintain focus (cycles)"),
    Gene("novelty_attention_boost", 0.6, 0.0, 1.0, GeneCategory.ATTENTION,
         "How much novelty boosts attention"),
    Gene("urgency_attention_weight", 0.7, 0.0, 1.0, GeneCategory.ATTENTION,
         "Weight for urgent items in attention"),

    # === DRIVE GENES ===
    Gene("curiosity_baseline", 0.5, 0.0, 1.0, GeneCategory.DRIVES,
         "Baseline curiosity level"),
    Gene("curiosity_sensitivity", 0.6, 0.0, 1.0, GeneCategory.DRIVES,
         "How much curiosity responds to novelty"),
    Gene("competence_baseline", 0.3, 0.0, 1.0, GeneCategory.DRIVES,
         "Baseline competence drive"),
    Gene("competence_sensitivity", 0.5, 0.0, 1.0, GeneCategory.DRIVES,
         "How much competence responds to success"),
    Gene("novelty_baseline", 0.4, 0.0, 1.0, GeneCategory.DRIVES,
         "Baseline novelty seeking"),
    Gene("novelty_sensitivity", 0.7, 0.0, 1.0, GeneCategory.DRIVES,
         "How much novelty drive responds to repetition"),
    Gene("connection_baseline", 0.4, 0.0, 1.0, GeneCategory.DRIVES,
         "Baseline social connection need"),
    Gene("stability_baseline", 0.5, 0.0, 1.0, GeneCategory.DRIVES,
         "Baseline stability/consistency need"),
    Gene("drive_decay_rate", 0.05, 0.01, 0.2, GeneCategory.DRIVES,
         "How fast drives decay over time"),
    Gene("drive_satisfaction_boost", 0.1, 0.01, 0.3, GeneCategory.DRIVES,
         "How much success satisfies drives"),
    Gene("drive_frustration_penalty", 0.15, 0.01, 0.3, GeneCategory.DRIVES,
         "How much failure frustrates drives"),

    # === REASONING GENES ===
    Gene("analytical_weight", 0.25, 0.0, 1.0, GeneCategory.REASONING,
         "Weight for analytical reasoning"),
    Gene("creative_weight", 0.15, 0.0, 1.0, GeneCategory.REASONING,
         "Weight for creative reasoning"),
    Gene("critical_weight", 0.20, 0.0, 1.0, GeneCategory.REASONING,
         "Weight for critical reasoning"),
    Gene("systems_weight", 0.15, 0.0, 1.0, GeneCategory.REASONING,
         "Weight for systems thinking"),
    Gene("intuitive_weight", 0.15, 0.0, 1.0, GeneCategory.REASONING,
         "Weight for intuitive reasoning"),
    Gene("ethical_weight", 0.10, 0.0, 1.0, GeneCategory.REASONING,
         "Weight for ethical reasoning"),
    Gene("max_reasoning_steps", 10.0, 3.0, 20.0, GeneCategory.REASONING,
         "Maximum inference steps"),
    Gene("min_confidence_threshold", 0.3, 0.1, 0.8, GeneCategory.REASONING,
         "Minimum confidence to accept conclusion"),
    Gene("case_similarity_threshold", 0.6, 0.3, 0.9, GeneCategory.REASONING,
         "Minimum similarity for case retrieval"),
    Gene("hypothesis_generation_breadth", 3.0, 1.0, 10.0, GeneCategory.REASONING,
         "How many hypotheses to generate"),
    Gene("analogy_abstraction_depth", 2.0, 1.0, 5.0, GeneCategory.REASONING,
         "How abstract to go in analogical reasoning"),

    # === ACTION GENES ===
    Gene("investigate_threshold", 0.6, 0.3, 0.9, GeneCategory.ACTION,
         "Confidence needed to investigate vs act"),
    Gene("explore_threshold", 0.7, 0.4, 0.95, GeneCategory.ACTION,
         "Confidence needed to explore new areas"),
    Gene("urgency_threshold", 0.4, 0.1, 0.8, GeneCategory.ACTION,
         "When to prioritize urgent over important"),
    Gene("prefer_investigation", 0.4, 0.0, 1.0, GeneCategory.ACTION,
         "Preference for investigation over action"),
    Gene("action_confidence_required", 0.5, 0.2, 0.9, GeneCategory.ACTION,
         "Confidence needed to take action"),
    Gene("risk_tolerance", 0.3, 0.0, 1.0, GeneCategory.ACTION,
         "Willingness to take risky actions"),
    Gene("persistence_threshold", 0.7, 0.3, 1.0, GeneCategory.ACTION,
         "How long to persist before giving up"),

    # === LEARNING GENES ===
    Gene("memory_strength_initial", 0.5, 0.1, 1.0, GeneCategory.LEARNING,
         "Initial strength of new memories"),
    Gene("memory_decay_rate", 0.01, 0.001, 0.1, GeneCategory.LEARNING,
         "How fast memories decay"),
    Gene("association_strength_increment", 0.1, 0.01, 0.3, GeneCategory.LEARNING,
         "How much associations strengthen per use"),
    Gene("trust_new_rules", 0.3, 0.1, 0.8, GeneCategory.LEARNING,
         "Initial trust in newly learned rules"),
    Gene("confirmation_threshold", 3.0, 1.0, 10.0, GeneCategory.LEARNING,
         "Confirmations needed to trust a pattern"),
    Gene("initial_pattern_confidence", 0.3, 0.1, 0.6, GeneCategory.LEARNING,
         "Starting confidence for new patterns"),
    Gene("curriculum_pattern_confidence", 0.8, 0.5, 1.0, GeneCategory.LEARNING,
         "Confidence for curriculum-based patterns"),
    Gene("min_pattern_success_rate", 0.3, 0.1, 0.6, GeneCategory.LEARNING,
         "Minimum success rate to keep pattern"),
    Gene("prune_after_uses", 10.0, 5.0, 50.0, GeneCategory.LEARNING,
         "Uses before evaluating pattern for pruning"),
    Gene("promotion_threshold", 0.8, 0.6, 0.95, GeneCategory.LEARNING,
         "Success rate needed for pattern promotion"),
    Gene("min_observations_for_causation", 3.0, 1.0, 10.0, GeneCategory.LEARNING,
         "Observations needed to infer causation"),
    Gene("base_learned_confidence", 0.5, 0.2, 0.8, GeneCategory.LEARNING,
         "Initial confidence for learned causations"),
    Gene("reinforcement_rate", 0.1, 0.01, 0.3, GeneCategory.LEARNING,
         "How much confirmation strengthens beliefs"),
    Gene("min_causation_strength", 0.2, 0.05, 0.5, GeneCategory.LEARNING,
         "Minimum strength to keep causation"),

    # === SIMULATION GENES ===
    Gene("default_increase_magnitude", 0.1, 0.01, 0.5, GeneCategory.SIMULATION,
         "Default magnitude for causal increases"),
    Gene("default_decrease_magnitude", 0.1, 0.01, 0.5, GeneCategory.SIMULATION,
         "Default magnitude for causal decreases"),
    Gene("equilibrium_threshold", 0.001, 0.0001, 0.01, GeneCategory.SIMULATION,
         "Threshold for simulation equilibrium"),
    Gene("unknown_link_penalty", 0.5, 0.1, 0.9, GeneCategory.SIMULATION,
         "Penalty for unknown causal links"),
    Gene("simulation_max_steps", 100.0, 10.0, 500.0, GeneCategory.SIMULATION,
         "Maximum simulation steps"),
    Gene("counterfactual_depth", 3.0, 1.0, 10.0, GeneCategory.SIMULATION,
         "Depth of counterfactual reasoning"),

    # === CREATIVITY GENES ===
    Gene("novelty_generation_rate", 0.3, 0.1, 0.8, GeneCategory.CREATIVITY,
         "Rate of novel idea generation"),
    Gene("combination_breadth", 3.0, 1.0, 10.0, GeneCategory.CREATIVITY,
         "How many concepts to combine"),
    Gene("abstraction_tendency", 0.5, 0.0, 1.0, GeneCategory.CREATIVITY,
         "Tendency to abstract vs stay concrete"),
    Gene("constraint_relaxation_rate", 0.2, 0.0, 0.5, GeneCategory.CREATIVITY,
         "Willingness to relax constraints"),
    Gene("divergent_exploration_depth", 3.0, 1.0, 7.0, GeneCategory.CREATIVITY,
         "Depth of divergent exploration"),
    Gene("blending_threshold", 0.4, 0.2, 0.8, GeneCategory.CREATIVITY,
         "Similarity threshold for concept blending"),

    # === SOCIAL GENES ===
    Gene("empathy_weight", 0.5, 0.0, 1.0, GeneCategory.SOCIAL,
         "Weight for empathetic considerations"),
    Gene("cooperation_tendency", 0.6, 0.0, 1.0, GeneCategory.SOCIAL,
         "Tendency to cooperate vs compete"),
    Gene("trust_initial", 0.5, 0.0, 1.0, GeneCategory.SOCIAL,
         "Initial trust in new entities"),
    Gene("trust_update_rate", 0.1, 0.01, 0.3, GeneCategory.SOCIAL,
         "How fast trust updates based on interactions"),
]


class CognitiveGenome:
    """
    The complete cognitive genome - 60+ evolvable parameters.

    Usage:
        genome = CognitiveGenome()

        # Get gene value
        curiosity = genome.get("curiosity_baseline")

        # Set gene value
        genome.set("curiosity_baseline", 0.8)

        # Mutate single gene
        genome.mutate("curiosity_baseline", magnitude=0.1)

        # Evolve on stagnation/breakthrough
        genome.evolve(trigger="stagnation", mutation_rate=0.1)

        # Get category
        drive_genes = genome.get_category(GeneCategory.DRIVES)
    """

    def __init__(self, genes: Optional[List[Gene]] = None):
        """Initialize genome with default or provided genes."""
        if genes is None:
            # Deep copy default genes
            self.genes: Dict[str, Gene] = {
                g.name: Gene(
                    name=g.name,
                    value=g.value,
                    min_value=g.min_value,
                    max_value=g.max_value,
                    category=g.category,
                    description=g.description,
                    fitness=g.fitness
                )
                for g in DEFAULT_GENES
            }
        else:
            self.genes = {g.name: g for g in genes}

        # Overall genome fitness
        self.fitness: float = 0.5
        self.generation: int = 0
        self.evolution_history: List[Dict[str, Any]] = []

    def get(self, name: str, default: Optional[float] = None) -> float:
        """Get gene value by name."""
        if name in self.genes:
            return self.genes[name].value
        if default is not None:
            return default
        raise KeyError(f"Unknown gene: {name}")

    def set(self, name: str, value: float) -> None:
        """Set gene value (clamped to bounds)."""
        if name not in self.genes:
            raise KeyError(f"Unknown gene: {name}")
        gene = self.genes[name]
        gene.value = max(gene.min_value, min(gene.max_value, value))

    def mutate(self, name: str, magnitude: float = 0.1) -> float:
        """Mutate a single gene."""
        if name not in self.genes:
            raise KeyError(f"Unknown gene: {name}")
        return self.genes[name].mutate(magnitude)

    def get_category(self, category: GeneCategory) -> List[Gene]:
        """Get all genes in a category."""
        return [g for g in self.genes.values() if g.category == category]

    def evolve(
        self,
        trigger: str = "stagnation",
        mutation_rate: float = 0.1,
        preserve_fit: bool = True
    ) -> Dict[str, Any]:
        """
        Evolve the genome based on trigger.

        Args:
            trigger: "stagnation" (stuck) or "breakthrough" (success)
            mutation_rate: Fraction of genes to mutate
            preserve_fit: Whether to preserve high-fitness genes

        Returns:
            Evolution report
        """
        self.generation += 1

        genes_to_mutate = list(self.genes.keys())

        # If preserving fit genes, exclude high-fitness ones
        if preserve_fit:
            genes_to_mutate = [
                name for name, gene in self.genes.items()
                if gene.fitness < 0.7  # Don't mutate high-fitness genes
            ]

        # Select genes to mutate
        num_to_mutate = max(1, int(len(genes_to_mutate) * mutation_rate))
        selected = random.sample(genes_to_mutate, min(num_to_mutate, len(genes_to_mutate)))

        # Mutation magnitude depends on trigger
        if trigger == "stagnation":
            magnitude = 0.15  # Bigger changes when stuck
        elif trigger == "breakthrough":
            magnitude = 0.05  # Small refinements on success
        else:
            magnitude = 0.1

        mutations = []
        for name in selected:
            old_value = self.genes[name].value
            new_value = self.genes[name].mutate(magnitude)
            mutations.append({
                "gene": name,
                "old": old_value,
                "new": new_value
            })

        report = {
            "generation": self.generation,
            "trigger": trigger,
            "mutation_rate": mutation_rate,
            "genes_mutated": len(mutations),
            "mutations": mutations
        }

        self.evolution_history.append(report)
        logger.info(f"Evolution triggered ({trigger}): mutated {len(mutations)} genes")

        return report

    def update_fitness(self, gene_name: str, outcome: float) -> None:
        """
        Update gene fitness based on outcome.

        Args:
            gene_name: Name of gene to update
            outcome: Success (1.0) or failure (0.0) or partial
        """
        if gene_name not in self.genes:
            return

        gene = self.genes[gene_name]
        # Exponential moving average
        alpha = 0.1
        gene.fitness = (1 - alpha) * gene.fitness + alpha * outcome

    def to_dict(self) -> Dict[str, Any]:
        """Export genome as dictionary."""
        return {
            "genes": {name: gene.to_dict() for name, gene in self.genes.items()},
            "fitness": self.fitness,
            "generation": self.generation,
            "evolution_history": self.evolution_history[-10:]  # Last 10 evolutions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveGenome":
        """Create genome from dictionary."""
        genes = [Gene.from_dict(g) for g in data["genes"].values()]
        genome = cls(genes)
        genome.fitness = data.get("fitness", 0.5)
        genome.generation = data.get("generation", 0)
        genome.evolution_history = data.get("evolution_history", [])
        return genome

    def save(self, path: str) -> None:
        """Save genome to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "CognitiveGenome":
        """Load genome from JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return f"CognitiveGenome(genes={len(self.genes)}, generation={self.generation}, fitness={self.fitness:.2f})"
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/test_genome.py -v`
Expected: All 8 tests PASS

**Step 5: Commit**

```bash
git add modules/genome.py tests/test_genome.py
git commit -m "feat(genome): add cognitive genome with 60+ evolvable genes

- 8 gene categories: attention, drives, reasoning, action, learning, simulation, creativity, social
- Evolution triggers: stagnation (bigger mutations), breakthrough (refinements)
- Fitness tracking per gene
- Save/load to JSON
- Replaces hardcoded magic numbers with learnable parameters"
```

---

## Task 4: Update Module Exports

**Files:**
- Modify: `modules/__init__.py`

**Step 1: Add new module exports**

Add to `modules/__init__.py`:

```python
# Configuration
from .config import (
    Config,
    get_config,
    set_config,
    validate_python_version,
    VALID_PROVIDERS,
)

# LLM Bridge
from .llm_bridge import (
    LLMBridge,
    LLMResponse,
)

# Cognitive Genome
from .genome import (
    CognitiveGenome,
    Gene,
    GeneCategory,
    DEFAULT_GENES,
)
```

And add to `__all__`:

```python
    # Configuration
    "Config",
    "get_config",
    "set_config",
    "validate_python_version",
    "VALID_PROVIDERS",
    # LLM Bridge
    "LLMBridge",
    "LLMResponse",
    # Cognitive Genome
    "CognitiveGenome",
    "Gene",
    "GeneCategory",
    "DEFAULT_GENES",
```

**Step 2: Run all tests**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/ -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add modules/__init__.py
git commit -m "feat(modules): export config, llm_bridge, genome from package"
```

---

## Task 5: Create Tests Directory Structure

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Create test infrastructure**

```python
# tests/__init__.py
"""Bolor-Brain-MCP test suite."""
```

```python
# tests/conftest.py
"""Pytest configuration and fixtures."""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config
from modules.genome import CognitiveGenome


@pytest.fixture
def config():
    """Provide default config for tests."""
    return Config()


@pytest.fixture
def config_with_llm():
    """Provide config with LLM enabled (but mocked)."""
    return Config(
        llm_enabled=True,
        llm_provider="openai",
        llm_api_key="test-key-not-real"
    )


@pytest.fixture
def genome():
    """Provide fresh cognitive genome for tests."""
    return CognitiveGenome()
```

**Step 2: Commit**

```bash
git add tests/__init__.py tests/conftest.py
git commit -m "test: add pytest configuration and fixtures"
```

---

## Task 6: Verify Phase 1 Complete

**Step 1: Run full test suite**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -m pytest tests/ -v --tb=short`
Expected: All tests PASS

**Step 2: Verify imports work**

Run: `cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP && python -c "from modules import Config, LLMBridge, CognitiveGenome; print('Phase 1 imports OK')"`
Expected: "Phase 1 imports OK"

**Step 3: Create phase completion tag**

```bash
git tag -a v2.0.0-phase1 -m "Phase 1: Foundation complete - Config, LLM Bridge, Genome"
```

---

## Summary

Phase 1 creates the foundation:

| Component | Purpose | Lines |
|-----------|---------|-------|
| `config.py` | Configuration with LLM toggle | ~180 |
| `llm_bridge.py` | Optional LLM integration | ~350 |
| `genome.py` | 60+ evolvable parameters | ~450 |
| Tests | Full test coverage | ~200 |
| **Total** | | **~1,180** |

Next: Phase 2 (Reasoning Core) - SymbolicReasoner, KnowledgeGraph, CaseBasedReasoner
