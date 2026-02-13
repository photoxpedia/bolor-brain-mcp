"""
Tests for the configuration system.

The config system supports:
- Reasoning and persistence settings
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

    def test_default_reasoning_max_depth(self):
        """Default reasoning_max_depth should be 10."""
        from modules.config import Config

        config = Config()
        assert config.reasoning_max_depth == 10

    def test_default_learning_rate(self):
        """Default learning_rate should be 0.1."""
        from modules.config import Config

        config = Config()
        assert config.learning_rate == 0.1

    def test_default_persistence_dir(self):
        """Default persistence_dir should be ~/.bolor-brain."""
        from modules.config import Config

        config = Config()
        assert config.persistence_dir == "~/.bolor-brain"

    def test_default_debug(self):
        """Default debug should be False."""
        from modules.config import Config

        config = Config()
        assert config.debug is False


class TestConfigFromEnvironment:
    """Test loading configuration from environment variables."""

    def test_config_from_env_reasoning_max_depth(self, monkeypatch):
        """Config should load reasoning_max_depth from BOLOR_REASONING_MAX_DEPTH."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_REASONING_MAX_DEPTH", "50")

        config = Config.from_env()
        assert config.reasoning_max_depth == 50

    def test_config_from_env_learning_rate(self, monkeypatch):
        """Config should load learning_rate from BOLOR_LEARNING_RATE."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_LEARNING_RATE", "0.5")

        config = Config.from_env()
        assert config.learning_rate == 0.5

    def test_config_from_env_persistence_dir(self, monkeypatch):
        """Config should load persistence_dir from BOLOR_PERSISTENCE_DIR."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_PERSISTENCE_DIR", "/tmp/test-brain")

        config = Config.from_env()
        assert config.persistence_dir == "/tmp/test-brain"

    def test_config_from_env_debug(self, monkeypatch):
        """Config should load debug from BOLOR_DEBUG."""
        from modules.config import Config

        monkeypatch.setenv("BOLOR_DEBUG", "true")

        config = Config.from_env()
        assert config.debug is True

    def test_config_from_env_defaults(self, monkeypatch):
        """Unset environment variables should use defaults."""
        from modules.config import Config

        # Clear any existing BOLOR_* variables
        for key in list(os.environ.keys()):
            if key.startswith("BOLOR_"):
                monkeypatch.delenv(key, raising=False)

        config = Config.from_env()

        assert config.reasoning_max_depth == 10
        assert config.learning_rate == 0.1
        assert config.persistence_dir == "~/.bolor-brain"
        assert config.debug is False


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

        config = Config(reasoning_max_depth=20, learning_rate=0.5)
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["reasoning_max_depth"] == 20
        assert config_dict["learning_rate"] == 0.5
        assert config_dict["persistence_dir"] == "~/.bolor-brain"
        assert config_dict["debug"] is False

    def test_get_and_set_config(self):
        """Global config getter and setter should work."""
        from modules.config import get_config, set_config, Config

        # Get default config
        default_config = get_config()
        assert isinstance(default_config, Config)

        # Set custom config
        custom_config = Config(reasoning_max_depth=50)
        set_config(custom_config)

        # Get should return custom config
        retrieved = get_config()
        assert retrieved.reasoning_max_depth == 50

        # Reset to default for other tests
        set_config(Config())


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

    def test_persistence_dir_custom(self):
        """Custom persistence_dir should be accepted."""
        from modules.config import Config

        config = Config(persistence_dir="/tmp/my-brain")
        assert config.persistence_dir == "/tmp/my-brain"


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
