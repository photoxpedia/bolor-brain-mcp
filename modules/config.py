"""
Configuration system for Bolor Brain MCP.

Pure reasoning configuration - no LLM or embedding dependencies.
Environment variables use BOLOR_* prefix.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, asdict
from typing import Optional


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
        reasoning_max_depth: Maximum reasoning chain depth (1-100)
        learning_rate: Rate of learning/adaptation (0.0-1.0)
        persistence_dir: Directory for persisted brain state
        debug: Enable debug logging
    """

    reasoning_max_depth: int = 10
    learning_rate: float = 0.1
    persistence_dir: str = "~/.bolor-brain"
    debug: bool = False

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_reasoning_max_depth()
        self._validate_learning_rate()

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

    @classmethod
    def from_env(cls) -> Config:
        """
        Create a Config instance from environment variables.

        Environment variables use BOLOR_* prefix:
        - BOLOR_REASONING_MAX_DEPTH: Max reasoning depth (int)
        - BOLOR_LEARNING_RATE: Learning rate (float)
        - BOLOR_PERSISTENCE_DIR: Directory for brain state persistence
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

        return cls(
            reasoning_max_depth=get_int("BOLOR_REASONING_MAX_DEPTH", 10),
            learning_rate=get_float("BOLOR_LEARNING_RATE", 0.1),
            persistence_dir=os.environ.get("BOLOR_PERSISTENCE_DIR", "~/.bolor-brain"),
            debug=get_bool("BOLOR_DEBUG", False),
        )

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            dict: Configuration as dictionary.
        """
        return asdict(self)


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


# Validate Python version on module import
validate_python_version()
