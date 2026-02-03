"""Pytest configuration and fixtures for Bolor-Brain-MCP tests."""

import pytest
import sys
import os
import tempfile
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config
from modules.genome import CognitiveGenome, Gene, GeneCategory
from modules.llm_bridge import LLMBridge


# === CONFIG FIXTURES ===

@pytest.fixture
def config():
    """Provide default config for tests (standalone mode)."""
    return Config()


@pytest.fixture
def config_with_llm():
    """Provide config with LLM enabled (but mocked key)."""
    return Config(
        llm_enabled=True,
        llm_provider="openai",
        llm_api_key="test-key-not-real"
    )


@pytest.fixture
def config_ollama():
    """Provide config for Ollama (local, no API key needed)."""
    return Config(
        llm_enabled=True,
        llm_provider="ollama",
        llm_model="llama2"
    )


# === GENOME FIXTURES ===

@pytest.fixture
def genome():
    """Provide fresh cognitive genome for tests."""
    return CognitiveGenome()


@pytest.fixture
def sample_gene():
    """Provide a sample gene for testing."""
    return Gene(
        name="test_gene",
        value=0.5,
        min_value=0.0,
        max_value=1.0,
        category=GeneCategory.REASONING,
        description="A test gene"
    )


# === LLM BRIDGE FIXTURES ===

@pytest.fixture
def llm_bridge_disabled(config):
    """Provide LLM bridge in disabled (standalone) mode."""
    return LLMBridge(config)


@pytest.fixture
def llm_bridge_enabled(config_with_llm):
    """Provide LLM bridge in enabled mode (mocked)."""
    return LLMBridge(config_with_llm)


# === TEMP FILE FIXTURES ===

@pytest.fixture
def temp_dir():
    """Provide a temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_genome_path(temp_dir):
    """Provide a temporary path for genome save/load tests."""
    return temp_dir / "test_genome.json"


# === ASYNC FIXTURES ===

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# === SAMPLE DATA FIXTURES ===

@pytest.fixture
def sample_reasoning_result():
    """Provide a sample structured reasoning result for LLM bridge tests."""
    return {
        "conclusion": "Based on the analysis, option A is recommended.",
        "confidence": 0.85,
        "reasoning_chain": [
            "First, we evaluated all available options.",
            "Option A has the highest score on key criteria.",
            "Risks for option A are manageable."
        ],
        "evidence": [
            "Historical data shows 90% success rate.",
            "Expert consensus favors this approach."
        ],
        "uncertainties": [
            "Market conditions may change.",
            "Implementation timeline is uncertain."
        ],
        "next_steps": [
            "Begin implementation planning.",
            "Set up monitoring metrics."
        ]
    }


@pytest.fixture
def sample_ideas():
    """Provide sample base ideas for creativity enhancement tests."""
    return [
        "Implement a caching layer to improve performance",
        "Add automated testing to catch regressions",
        "Refactor the database schema for better normalization"
    ]
