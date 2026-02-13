"""Pytest configuration and fixtures for Bolor Brain MCP tests."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config


@pytest.fixture
def config():
    """Provide default config for tests."""
    return Config()


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
