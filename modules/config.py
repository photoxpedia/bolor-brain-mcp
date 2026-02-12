"""
Configuration system for Bolor Brain MCP.

Supports two modes:
- Standalone mode (default): Pure symbolic reasoning, no LLM dependency
- LLM-enhanced mode: Symbolic reasoning + LLM synthesis for richer outputs

Environment variables use BOLOR_* prefix.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional, Set, List, FrozenSet


# Valid LLM providers
VALID_PROVIDERS: Set[str] = {"openai", "anthropic", "ollama", "custom"}

# Valid LLM use cases for the LLM bridge
VALID_LLM_USE_CASES: FrozenSet[str] = frozenset({"synthesis", "creative", "ambiguous"})

# Python version constraints
MIN_PYTHON = (3, 11)
MAX_PYTHON = (3, 13)


def validate_python_version() -> None:
    """
    Validate that the current Python version is supported.

    Raises:
        RuntimeError: If Python version is outside supported range.
    """
    current = sys.version_info[:2]

    if current < MIN_PYTHON:
        raise RuntimeError(
            f"Python {current[0]}.{current[1]} is too old. "
            f"Bolor Brain MCP requires Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer."
        )

    if current > MAX_PYTHON:
        raise RuntimeError(
            f"Python {current[0]}.{current[1]} is not yet supported. "
            f"Maximum supported version is {MAX_PYTHON[0]}.{MAX_PYTHON[1]}."
        )


@dataclass
class Config:
    """
    Configuration for Bolor Brain MCP.

    Attributes:
        llm_enabled: Enable LLM for enhanced synthesis (default: False for standalone mode)
        llm_provider: LLM provider to use (openai, anthropic, ollama, custom)
        llm_api_key: API key for the LLM provider
        llm_model: Model name to use
        llm_base_url: Custom base URL (for custom/ollama providers)

        database_path: Path to SQLite database

        embedding_enabled: Enable embeddings for semantic search
        embedding_model: Embedding model to use

        reasoning_max_depth: Maximum reasoning chain depth

        framework_enabled_tiers: Which cognitive tiers to enable (0-7)

        learning_rate: Rate of learning/adaptation

        debug: Enable debug logging
    """

    # LLM settings
    llm_enabled: bool = False
    llm_provider: str = "ollama"
    llm_api_key: Optional[str] = None
    llm_model: str = "llama3"
    llm_base_url: Optional[str] = None
    llm_use_for: List[str] = field(default_factory=lambda: ["synthesis", "creative", "ambiguous"])
    llm_fallback_to_symbolic: bool = True

    # Database settings
    database_path: str = "brain_mcp_storage/brain.db"

    # Embedding settings
    embedding_enabled: bool = False
    embedding_model: str = "all-MiniLM-L6-v2"

    # Reasoning settings
    reasoning_max_depth: int = 10

    # Framework settings
    framework_enabled_tiers: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6, 7])

    # Learning settings
    learning_rate: float = 0.1

    # Debug settings
    debug: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_provider()
        self._validate_reasoning_max_depth()
        self._validate_learning_rate()
        self._validate_framework_enabled_tiers()
        self._validate_llm_use_for()

    def _validate_provider(self) -> None:
        """
        Validate that the LLM provider is valid.

        Raises:
            ValueError: If provider is not in VALID_PROVIDERS.
        """
        if self.llm_provider not in VALID_PROVIDERS:
            raise ValueError(
                f"Invalid LLM provider: '{self.llm_provider}'. "
                f"Valid providers are: {', '.join(sorted(VALID_PROVIDERS))}"
            )

    def _validate_reasoning_max_depth(self) -> None:
        """
        Validate that reasoning_max_depth is within bounds (1-100).

        Raises:
            ValueError: If reasoning_max_depth is outside valid range.
        """
        if not 1 <= self.reasoning_max_depth <= 100:
            raise ValueError(
                f"reasoning_max_depth must be between 1 and 100, got {self.reasoning_max_depth}"
            )

    def _validate_learning_rate(self) -> None:
        """
        Validate that learning_rate is within bounds (0.0-1.0).

        Raises:
            ValueError: If learning_rate is outside valid range.
        """
        if not 0.0 <= self.learning_rate <= 1.0:
            raise ValueError(
                f"learning_rate must be between 0.0 and 1.0, got {self.learning_rate}"
            )

    def _validate_framework_enabled_tiers(self) -> None:
        """
        Validate that framework_enabled_tiers contains only valid tier values (0-7).

        Raises:
            ValueError: If any tier value is outside the valid range.
        """
        valid_tiers = set(range(8))  # 0-7
        invalid_tiers = [t for t in self.framework_enabled_tiers if t not in valid_tiers]
        if invalid_tiers:
            raise ValueError(
                f"framework_enabled_tiers contains invalid values: {invalid_tiers}. "
                f"Valid tier values are 0-7."
            )

    def _validate_llm_use_for(self) -> None:
        """
        Validate that llm_use_for contains only valid use case values.

        Raises:
            ValueError: If any use case is not in VALID_LLM_USE_CASES.
        """
        invalid_cases = [c for c in self.llm_use_for if c not in VALID_LLM_USE_CASES]
        if invalid_cases:
            raise ValueError(
                f"llm_use_for contains invalid values: {invalid_cases}. "
                f"Valid use cases are: {', '.join(sorted(VALID_LLM_USE_CASES))}"
            )

    @classmethod
    def from_env(cls) -> Config:
        """
        Create a Config instance from environment variables.

        Environment variables use BOLOR_* prefix:
        - BOLOR_LLM_ENABLED: true/false
        - BOLOR_LLM_PROVIDER: openai/anthropic/ollama/custom
        - BOLOR_LLM_API_KEY: API key
        - BOLOR_LLM_MODEL: Model name
        - BOLOR_LLM_BASE_URL: Custom base URL
        - BOLOR_DATABASE_PATH: Database file path
        - BOLOR_EMBEDDING_ENABLED: true/false
        - BOLOR_EMBEDDING_MODEL: Embedding model name
        - BOLOR_REASONING_MAX_DEPTH: Max reasoning depth (int)
        - BOLOR_LEARNING_RATE: Learning rate (float)
        - BOLOR_LLM_USE_FOR: Comma-separated list (synthesis,creative,ambiguous)
        - BOLOR_LLM_FALLBACK_TO_SYMBOLIC: true/false
        - BOLOR_DEBUG: true/false

        Returns:
            Config: Configuration loaded from environment.
        """
        def get_bool(key: str, default: bool) -> bool:
            value = os.environ.get(key, "").lower()
            if value == "true":
                return True
            elif value == "false":
                return False
            return default

        def get_int(key: str, default: int) -> int:
            value = os.environ.get(key)
            if value is not None and value != "":
                try:
                    return int(value)
                except ValueError:
                    raise ValueError(
                        f"Environment variable {key} must be an integer, got '{value}'"
                    )
            return default

        def get_float(key: str, default: float) -> float:
            value = os.environ.get(key)
            if value is not None and value != "":
                try:
                    return float(value)
                except ValueError:
                    raise ValueError(
                        f"Environment variable {key} must be a float, got '{value}'"
                    )
            return default

        def get_list(key: str, default: List[str]) -> List[str]:
            value = os.environ.get(key)
            if value is not None and value != "":
                return [item.strip() for item in value.split(",") if item.strip()]
            return default

        return cls(
            llm_enabled=get_bool("BOLOR_LLM_ENABLED", False),
            llm_provider=os.environ.get("BOLOR_LLM_PROVIDER", "ollama"),
            llm_api_key=os.environ.get("BOLOR_LLM_API_KEY"),
            llm_model=os.environ.get("BOLOR_LLM_MODEL", "llama3"),
            llm_base_url=os.environ.get("BOLOR_LLM_BASE_URL"),
            llm_use_for=get_list("BOLOR_LLM_USE_FOR", ["synthesis", "creative", "ambiguous"]),
            llm_fallback_to_symbolic=get_bool("BOLOR_LLM_FALLBACK_TO_SYMBOLIC", True),
            database_path=os.environ.get("BOLOR_DATABASE_PATH", "brain_mcp_storage/brain.db"),
            embedding_enabled=get_bool("BOLOR_EMBEDDING_ENABLED", False),
            embedding_model=os.environ.get("BOLOR_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            reasoning_max_depth=get_int("BOLOR_REASONING_MAX_DEPTH", 10),
            learning_rate=get_float("BOLOR_LEARNING_RATE", 0.1),
            debug=get_bool("BOLOR_DEBUG", False),
        )

    def to_dict(self, redact_secrets: bool = True) -> dict:
        """
        Convert configuration to dictionary.

        Args:
            redact_secrets: If True, redact sensitive values like API keys (default: True).

        Returns:
            dict: Configuration as dictionary.
        """
        config_dict = asdict(self)
        if redact_secrets and config_dict.get('llm_api_key'):
            config_dict['llm_api_key'] = '***REDACTED***'
        return config_dict


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    If no configuration has been set, creates a default one.

    Returns:
        Config: The global configuration.
    """
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config) -> None:
    """
    Set the global configuration instance.

    Args:
        config: The configuration to set as global.
    """
    global _global_config
    _global_config = config


# Guardrails configuration for autonomous agent
# From AGENT_GUARDRAILS.md - 4-tier permission model
GUARDRAILS_CONFIG = {
    "approval_tier": 2,  # Tier 2+ requires approval
    "blocked_patterns": [
        "rm -rf /",
        "DROP DATABASE",
        "DELETE FROM",
        "format",
        "mkfs",
    ],
    "max_file_size": 10_000_000,  # 10MB
    "max_execution_time": 300,  # 5 minutes per task
}


# Validate Python version on module import
validate_python_version()
