"""
Tests for the configuration system.

TDD: These tests are written BEFORE the implementation.
The config system must support:
- Standalone mode (LLM disabled by default)
- LLM-enhanced mode (optional)
- Environment variable configuration
- Python version validation
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_config_has_llm_disabled(self):
        """Default config should have LLM disabled for standalone mode."""
        from modules.config import Config

        config = Config()
        assert config.llm_enabled is False, "Default config should have LLM disabled"

    def test_default_provider_is_ollama(self):
        """Default provider should be ollama (local, free)."""
        from modules.config import Config

        config = Config()
        assert config.llm_provider == "ollama"


class TestConfigLLMSettings:
    """Test LLM configuration options."""

    def test_config_accepts_llm_settings(self):
        """Config should accept LLM settings when provided."""
        from modules.config import Config

        config = Config(
            llm_enabled=True,
            llm_provider="openai",
            llm_api_key="test-key",
            llm_model="gpt-4"
        )

        assert config.llm_enabled is True
        assert config.llm_provider == "openai"
        assert config.llm_api_key == "test-key"
        assert config.llm_model == "gpt-4"

    def test_invalid_provider_raises(self):
        """Invalid LLM provider should raise ValueError."""
        from modules.config import Config

        with pytest.raises(ValueError, match="Invalid LLM provider"):
            Config(llm_provider="invalid_provider")

    def test_enabled_without_provider_uses_default(self):
        """Enabling LLM without specifying provider should use default."""
        from modules.config import Config

        config = Config(llm_enabled=True)
        assert config.llm_enabled is True
        assert config.llm_provider == "ollama"  # Default provider

    def test_valid_providers(self):
        """All valid providers should be accepted."""
        from modules.config import Config, VALID_PROVIDERS

        for provider in VALID_PROVIDERS:
            config = Config(llm_provider=provider)
            assert config.llm_provider == provider


class TestConfigFromEnvironment:
    """Test loading configuration from environment variables."""

    def test_config_from_env(self, monkeypatch):
        """Config should load settings from BOLOR_* environment variables."""
        from modules.config import Config

        # Set environment variables
        monkeypatch.setenv("BOLOR_LLM_ENABLED", "true")
        monkeypatch.setenv("BOLOR_LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("BOLOR_LLM_API_KEY", "env-test-key")
        monkeypatch.setenv("BOLOR_LLM_MODEL", "claude-3-opus")

        config = Config.from_env()

        assert config.llm_enabled is True
        assert config.llm_provider == "anthropic"
        assert config.llm_api_key == "env-test-key"
        assert config.llm_model == "claude-3-opus"

    def test_config_from_env_with_false(self, monkeypatch):
        """Environment variable 'false' should disable LLM."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_LLM_ENABLED", "false")

        config = Config.from_env()
        assert config.llm_enabled is False

    def test_config_from_env_defaults(self, monkeypatch):
        """Unset environment variables should use defaults."""
        from modules.config import Config

        # Clear any existing BOLOR_* variables
        for key in list(os.environ.keys()):
            if key.startswith("BOLOR_"):
                monkeypatch.delenv(key, raising=False)

        config = Config.from_env()

        assert config.llm_enabled is False
        assert config.llm_provider == "ollama"


class TestPythonVersionValidation:
    """Test Python version checking."""

    def test_python_version_check(self):
        """Should validate Python version is compatible."""
        from modules.config import validate_python_version, MIN_PYTHON, MAX_PYTHON

        # Current Python version should be valid (we're running on it!)
        current_version = sys.version_info[:2]

        # If current version is in range, should not raise
        if MIN_PYTHON <= current_version <= MAX_PYTHON:
            validate_python_version()  # Should not raise
        else:
            with pytest.raises(RuntimeError):
                validate_python_version()

    def test_python_version_bounds(self):
        """Check that version bounds are sensible."""
        from modules.config import MIN_PYTHON, MAX_PYTHON

        assert MIN_PYTHON == (3, 11), "Minimum Python should be 3.11"
        assert MAX_PYTHON == (3, 13), "Maximum Python should be 3.13"


class TestConfigMethods:
    """Test Config utility methods."""

    def test_config_to_dict(self):
        """Config should be convertible to dict."""
        from modules.config import Config

        config = Config(llm_enabled=True, llm_provider="openai")
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["llm_enabled"] is True
        assert config_dict["llm_provider"] == "openai"

    def test_get_and_set_config(self):
        """Global config getter and setter should work."""
        from modules.config import get_config, set_config, Config

        # Get default config
        default_config = get_config()
        assert isinstance(default_config, Config)

        # Set custom config
        custom_config = Config(llm_enabled=True)
        set_config(custom_config)

        # Get should return custom config
        retrieved = get_config()
        assert retrieved.llm_enabled is True

        # Reset to default for other tests
        set_config(Config())


class TestConfigAllSettings:
    """Test all configuration settings exist and have reasonable defaults."""

    def test_all_settings_present(self):
        """Config should have all expected settings."""
        from modules.config import Config

        config = Config()

        # LLM settings
        assert hasattr(config, "llm_enabled")
        assert hasattr(config, "llm_provider")
        assert hasattr(config, "llm_api_key")
        assert hasattr(config, "llm_model")
        assert hasattr(config, "llm_base_url")

        # Database settings
        assert hasattr(config, "database_path")

        # Embedding settings
        assert hasattr(config, "embedding_enabled")
        assert hasattr(config, "embedding_model")

        # Reasoning settings
        assert hasattr(config, "reasoning_max_depth")

        # Framework settings
        assert hasattr(config, "framework_enabled_tiers")

        # Learning settings
        assert hasattr(config, "learning_rate")

        # Debug settings
        assert hasattr(config, "debug")

    def test_database_default(self):
        """Default database path should be set."""
        from modules.config import Config

        config = Config()
        assert config.database_path == "brain_mcp_storage/brain.db"


class TestConfigValidation:
    """Test configuration validation."""

    def test_reasoning_max_depth_too_low(self):
        """reasoning_max_depth below 1 should raise ValueError."""
        from modules.config import Config

        with pytest.raises(ValueError, match="reasoning_max_depth must be between 1 and 100"):
            Config(reasoning_max_depth=0)

    def test_reasoning_max_depth_too_high(self):
        """reasoning_max_depth above 100 should raise ValueError."""
        from modules.config import Config

        with pytest.raises(ValueError, match="reasoning_max_depth must be between 1 and 100"):
            Config(reasoning_max_depth=101)

    def test_reasoning_max_depth_valid(self):
        """Valid reasoning_max_depth values should be accepted."""
        from modules.config import Config

        config = Config(reasoning_max_depth=1)
        assert config.reasoning_max_depth == 1

        config = Config(reasoning_max_depth=50)
        assert config.reasoning_max_depth == 50

        config = Config(reasoning_max_depth=100)
        assert config.reasoning_max_depth == 100

    def test_learning_rate_too_low(self):
        """learning_rate below 0.0 should raise ValueError."""
        from modules.config import Config

        with pytest.raises(ValueError, match="learning_rate must be between 0.0 and 1.0"):
            Config(learning_rate=-0.1)

    def test_learning_rate_too_high(self):
        """learning_rate above 1.0 should raise ValueError."""
        from modules.config import Config

        with pytest.raises(ValueError, match="learning_rate must be between 0.0 and 1.0"):
            Config(learning_rate=1.1)

    def test_learning_rate_valid(self):
        """Valid learning_rate values should be accepted."""
        from modules.config import Config

        config = Config(learning_rate=0.0)
        assert config.learning_rate == 0.0

        config = Config(learning_rate=0.5)
        assert config.learning_rate == 0.5

        config = Config(learning_rate=1.0)
        assert config.learning_rate == 1.0

    def test_framework_enabled_tiers_invalid(self):
        """Invalid tier values should raise ValueError."""
        from modules.config import Config

        with pytest.raises(ValueError, match="framework_enabled_tiers contains invalid values"):
            Config(framework_enabled_tiers=[0, 1, 8])

        with pytest.raises(ValueError, match="framework_enabled_tiers contains invalid values"):
            Config(framework_enabled_tiers=[-1, 0, 1])

    def test_framework_enabled_tiers_valid(self):
        """Valid tier values should be accepted."""
        from modules.config import Config

        config = Config(framework_enabled_tiers=[0, 7])
        assert config.framework_enabled_tiers == [0, 7]

        config = Config(framework_enabled_tiers=[0, 1, 2, 3, 4, 5, 6, 7])
        assert config.framework_enabled_tiers == [0, 1, 2, 3, 4, 5, 6, 7]

        config = Config(framework_enabled_tiers=[])
        assert config.framework_enabled_tiers == []


class TestConfigTypeConversion:
    """Test type conversion for environment variables."""

    def test_invalid_int_env_raises(self, monkeypatch):
        """Invalid integer in environment variable should raise ValueError."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_REASONING_MAX_DEPTH", "not_an_int")

        with pytest.raises(ValueError, match="must be an integer"):
            Config.from_env()

    def test_invalid_float_env_raises(self, monkeypatch):
        """Invalid float in environment variable should raise ValueError."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_LEARNING_RATE", "not_a_float")

        with pytest.raises(ValueError, match="must be a float"):
            Config.from_env()

    def test_empty_string_env_uses_default(self, monkeypatch):
        """Empty string environment variables should use defaults."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_REASONING_MAX_DEPTH", "")
        monkeypatch.setenv("BOLOR_LEARNING_RATE", "")

        config = Config.from_env()

        assert config.reasoning_max_depth == 10  # Default
        assert config.learning_rate == 0.1  # Default


class TestConfigSecurityRedaction:
    """Test API key redaction in to_dict."""

    def test_to_dict_redacts_api_key_by_default(self):
        """API key should be redacted by default in to_dict."""
        from modules.config import Config

        config = Config(llm_api_key="super-secret-key")
        config_dict = config.to_dict()

        assert config_dict["llm_api_key"] == "***REDACTED***"

    def test_to_dict_can_show_api_key(self):
        """API key should be visible when redact_secrets=False."""
        from modules.config import Config

        config = Config(llm_api_key="super-secret-key")
        config_dict = config.to_dict(redact_secrets=False)

        assert config_dict["llm_api_key"] == "super-secret-key"

    def test_to_dict_no_redaction_when_no_key(self):
        """No redaction needed when API key is None."""
        from modules.config import Config

        config = Config(llm_api_key=None)
        config_dict = config.to_dict()

        assert config_dict["llm_api_key"] is None
