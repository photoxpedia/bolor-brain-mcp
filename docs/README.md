# Bolor Brain MCP Documentation

A cognitive architecture with multiple reasoning approaches and memory systems.

## Quick Start

```python
from modules import HybridReasoner

brain = HybridReasoner()
result = brain.reason({"query": "What causes X?"})
print(result.combined_result)
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 HybridReasoner                   │
│  (orchestrates all reasoning approaches)         │
├─────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │Symbolic │ │Knowledge│ │Case-    │ │Hypothesis│ │
│ │Reasoner │ │Graph    │ │Based    │ │Engine   │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
│                    ┌─────────┐                   │
│                    │Analogical                   │
│                    │Reasoner │                   │
│                    └─────────┘                   │
├─────────────────────────────────────────────────┤
│              Memory System                       │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│ │Working │ │Episodic│ │Semantic│ │Procedur│    │
│ └────────┘ └────────┘ └────────┘ └────────┘    │
├─────────────────────────────────────────────────┤
│              Drive System                        │
│  Curiosity | Novelty | Competence | Connection   │
└─────────────────────────────────────────────────┘
```

## Documentation

### Reasoning Engines

| Document | Description |
|----------|-------------|
| [Hybrid Reasoner](reasoning/hybrid-reasoner.md) | Main entry point - orchestrates all approaches |
| [Symbolic Reasoner](reasoning/symbolic-reasoner.md) | Forward/backward chaining with rules and facts |
| [Knowledge Graph](reasoning/knowledge-graph.md) | Graph traversal, PageRank, inference |
| [Case-Based Reasoner](reasoning/case-based-reasoner.md) | 4R cycle: Retrieve, Reuse, Revise, Retain |
| [Hypothesis Engine](reasoning/hypothesis-engine.md) | Generate, test, and rank hypotheses |
| [Analogical Reasoner](reasoning/analogical-reasoner.md) | Cross-domain pattern transfer |

### Core Systems

| Document | Description |
|----------|-------------|
| [Memory System](core/memory.md) | 5 memory subsystems with persistence |
| [Drive System](core/drives.md) | Intrinsic motivation with homeostatic regulation |
| [Configuration](core/config.md) | Environment and runtime configuration |

## Installation

```bash
pip install -e .
```

Requires Python 3.11 - 3.13.

## Modes

### Standalone (Default)

Pure symbolic reasoning, no external dependencies:

```python
from modules import Config, set_config

config = Config(llm_enabled=False)
set_config(config)
```

### LLM-Enhanced

Symbolic reasoning + LLM synthesis:

```python
config = Config(
    llm_enabled=True,
    llm_provider="openai",
    llm_api_key="sk-..."
)
set_config(config)
```

## Common Imports

```python
# Reasoning
from modules import (
    HybridReasoner,
    SymbolicReasoner, Fact, Rule,
    KnowledgeGraph, Node, Edge,
    CaseBasedReasoner, Case,
    HypothesisEngine, Hypothesis,
    AnalogicalReasoner, Concept,
)

# Memory
from modules import (
    UnifiedMemorySystem,
    WorkingMemory,
    EpisodicMemoryStore,
    SemanticKnowledgeGraph,
)

# Drives
from modules import (
    DriveManager,
    DriveState,
    DriveType,
)

# Config
from modules import (
    Config,
    get_config,
    set_config,
)
```

## Examples

### Diagnosis Problem

```python
brain = HybridReasoner()

# Add domain knowledge
brain.add_fact(Fact("memory_leak", "causes", "crash"))
brain.add_case(Case(
    id="past_crash",
    problem={"symptom": "crash"},
    solution={"fix": "increase_memory"},
    success=True
))

result = brain.reason({
    "query": "System crashes under load",
    "type": "diagnosis"
})
```

### Learning from Experience

```python
cbr = CaseBasedReasoner()

# Store past experiences
cbr.store_case(Case(
    id="bug1",
    problem={"type": "bug", "error": "TypeError"},
    solution={"action": "add_type_check"},
    success=True
))

# Solve similar problem
result = cbr.reason({"type": "bug", "error": "AttributeError"})
```

### Knowledge Graph Queries

```python
kg = KnowledgeGraph()
kg.add_node(Node("python", "Python", "language"))
kg.add_node(Node("web", "Web Dev", "domain"))
kg.add_edge(Edge("python", "web", "used_for"))

# Find path
path = kg.find_path("python", "web")

# Pattern matching
results = kg.infer({"subject": "?x", "predicate": "used_for", "object": "?y"})
```

## Thread Safety

All modules are thread-safe and can be used concurrently.
