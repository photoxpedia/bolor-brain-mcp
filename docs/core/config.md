# Configuration

Central configuration for Bolor Brain MCP.

## Two Modes

| Mode | Description | LLM Required |
|------|-------------|--------------|
| **Standalone** | Pure symbolic reasoning | No |
| **LLM-enhanced** | Symbolic + LLM synthesis | Yes |

Default is standalone mode (no external dependencies).

## Quick Start

```python
from modules import Config, get_config, set_config

# Use defaults (standalone mode)
config = get_config()

# Or create custom config
config = Config(
    llm_enabled=True,
    llm_provider="openai",
    llm_api_key="sk-...",
    database_path="my_brain.db"
)
set_config(config)

# Or load from environment
config = Config.from_env()
set_config(config)
```

## Config Options

### LLM Settings

```python
Config(
    llm_enabled=False,           # Enable LLM integration
    llm_provider="ollama",       # openai, anthropic, ollama, custom
    llm_api_key=None,            # API key (not needed for ollama)
    llm_model="llama3",          # Model name
    llm_base_url=None,           # Custom endpoint URL
    llm_use_for=["synthesis", "creative", "ambiguous"],
    llm_fallback_to_symbolic=True  # Fall back if LLM fails
)
```

**Valid providers:** `openai`, `anthropic`, `ollama`, `custom`

**Valid use cases:**
- `synthesis`: Combine reasoning results into natural language
- `creative`: Generate creative content
- `ambiguous`: Handle ambiguous queries

### Database Settings

```python
Config(
    database_path="brain_mcp_storage/brain.db"
)
```

### Embedding Settings

```python
Config(
    embedding_enabled=False,           # Enable semantic embeddings
    embedding_model="all-MiniLM-L6-v2" # Sentence transformer model
)
```

### Reasoning Settings

```python
Config(
    reasoning_max_depth=10  # Max inference chain depth (1-100)
)
```

### Framework Settings

```python
Config(
    framework_enabled_tiers=[0, 1, 2, 3, 4, 5, 6, 7]  # Which tiers to enable
)
```

**Cognitive Tiers:**
- 0: Memory
- 1: Advanced Reasoning
- 2: Predictive Intelligence
- 3: Meta-Cognitive Intelligence
- 4: Evolutionary Cognitive Intelligence
- 5: Collective Consciousness Network
- 6: Universal Field Orchestration
- 7: Pure Universal Being Integration

### Learning Settings

```python
Config(
    learning_rate=0.1  # Adaptation rate (0.0-1.0)
)
```

### Debug Settings

```python
Config(
    debug=False  # Enable debug logging
)
```

## Environment Variables

All settings can be configured via environment variables with `BOLOR_` prefix:

| Variable | Type | Default |
|----------|------|---------|
| `BOLOR_LLM_ENABLED` | bool | false |
| `BOLOR_LLM_PROVIDER` | str | ollama |
| `BOLOR_LLM_API_KEY` | str | None |
| `BOLOR_LLM_MODEL` | str | llama3 |
| `BOLOR_LLM_BASE_URL` | str | None |
| `BOLOR_LLM_USE_FOR` | list | synthesis,creative,ambiguous |
| `BOLOR_LLM_FALLBACK_TO_SYMBOLIC` | bool | true |
| `BOLOR_DATABASE_PATH` | str | brain_mcp_storage/brain.db |
| `BOLOR_EMBEDDING_ENABLED` | bool | false |
| `BOLOR_EMBEDDING_MODEL` | str | all-MiniLM-L6-v2 |
| `BOLOR_REASONING_MAX_DEPTH` | int | 10 |
| `BOLOR_LEARNING_RATE` | float | 0.1 |
| `BOLOR_DEBUG` | bool | false |

### Example .env

```bash
BOLOR_LLM_ENABLED=true
BOLOR_LLM_PROVIDER=openai
BOLOR_LLM_API_KEY=sk-...
BOLOR_LLM_MODEL=gpt-4
BOLOR_DATABASE_PATH=/data/brain.db
BOLOR_DEBUG=true
```

### Loading from Environment

```python
from modules import Config, set_config

config = Config.from_env()
set_config(config)
```

## Global Config Access

```python
from modules import get_config, set_config

# Get current config (creates default if none set)
config = get_config()

# Set new config
set_config(Config(debug=True))

# Access values
if config.llm_enabled:
    print(f"Using {config.llm_provider} / {config.llm_model}")
```

## Serialization

```python
# To dict (redacts API key by default)
data = config.to_dict()
# {"llm_enabled": True, "llm_api_key": "***REDACTED***", ...}

# Include secrets
data = config.to_dict(redact_secrets=False)
```

## Validation

Config validates on creation:

```python
# Invalid provider
Config(llm_provider="invalid")  # ValueError

# Invalid depth
Config(reasoning_max_depth=200)  # ValueError (max 100)

# Invalid learning rate
Config(learning_rate=1.5)  # ValueError (max 1.0)

# Invalid tiers
Config(framework_enabled_tiers=[0, 1, 8])  # ValueError (max 7)

# Invalid use cases
Config(llm_use_for=["invalid"])  # ValueError
```

## Python Version

Requires Python 3.11 - 3.13.

```python
from modules import validate_python_version

validate_python_version()  # Raises RuntimeError if unsupported
```

## Example: LLM-Enhanced Mode

```python
from modules import Config, set_config, HybridReasoner

# Configure for OpenAI
config = Config(
    llm_enabled=True,
    llm_provider="openai",
    llm_api_key="sk-...",
    llm_model="gpt-4",
    llm_use_for=["synthesis"],  # Only use for final synthesis
    llm_fallback_to_symbolic=True
)
set_config(config)

# Reasoning now uses symbolic + LLM
brain = HybridReasoner()
result = brain.reason({"query": "Explain quantum computing"})
# Symbolic reasoning + LLM synthesis of results
```

## Example: Standalone Mode

```python
from modules import Config, set_config, HybridReasoner

# Explicit standalone (default)
config = Config(
    llm_enabled=False,
    database_path="brain.db"
)
set_config(config)

# Pure symbolic reasoning
brain = HybridReasoner()
result = brain.reason({"query": "What is X?"})
# No external API calls
```
