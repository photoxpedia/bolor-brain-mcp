# Memory System

5 differentiated memory subsystems with appropriate data representations.

## Overview

| Subsystem | Purpose | Persistence |
|-----------|---------|-------------|
| Working Memory | Transient context | In-memory only |
| Episodic Memory | Experiences | SQLite |
| Semantic Memory | Knowledge graph | SQLite |
| Procedural Memory | Executable skills | SQLite |
| Self/Meta Memory | Identity model | SQLite |

Plus: Plasticity mechanisms for decay and consolidation.

## Quick Start

```python
from modules import UnifiedMemorySystem

memory = UnifiedMemorySystem(db_path="brain.db")

# Store an experience
memory.store_episode(
    content="Learned about Python decorators",
    context={"topic": "python", "difficulty": "medium"},
    reward=0.8
)

# Query semantic knowledge
knowledge = memory.query_semantic("python")

# Retrieve relevant memories
memories = memory.retrieve(
    query="How do Python decorators work?",
    memory_types=["episodic", "semantic"]
)
```

## Working Memory

Transient buffer with 7±2 capacity. Never persisted.

```python
from modules import WorkingMemory, WorkingMemoryItem

wm = WorkingMemory(capacity=7)

# Add item
item = WorkingMemoryItem(
    content="Current task context",
    priority=0.8,
    metadata={"source": "user"}
)
wm.add(item)

# Get all items (sorted by priority)
items = wm.get_all()

# Get by ID
item = wm.get(item_id)

# Clear
wm.clear()
```

### WorkingMemoryItem

```python
@dataclass
class WorkingMemoryItem:
    content: str           # Content text
    priority: float        # 0-1, higher = more important
    metadata: dict         # Additional data
    timestamp: float       # Creation time
    id: str               # Auto-generated
```

## Episodic Memory

Experiences with reward/emotion signals.

```python
from modules import EpisodicMemoryStore, EpisodicMemory

store = EpisodicMemoryStore(db_path="brain.db")

# Store episode
episode = EpisodicMemory(
    content="Fixed a complex bug",
    context={"type": "debugging", "language": "python"},
    reward=0.9,
    emotion="satisfaction",
    tags=["success", "learning"]
)
store.store(episode)

# Query by context
episodes = store.query(
    context_filter={"type": "debugging"},
    min_reward=0.5,
    limit=10
)

# Get recent episodes
recent = store.get_recent(hours=24)
```

### EpisodicMemory

```python
@dataclass
class EpisodicMemory:
    content: str           # What happened
    context: dict          # Situation context
    reward: float          # -1 to 1, outcome valence
    emotion: str           # Emotional tag
    timestamp: float       # When it happened
    tags: list[str]        # Categories
    strength: float        # Memory strength (decay target)
    id: str               # Auto-generated
```

## Semantic Memory

Knowledge graph with inference.

```python
from modules import SemanticKnowledgeGraph, SemanticNode, SemanticEdge

graph = SemanticKnowledgeGraph(db_path="brain.db")

# Add knowledge
graph.add_node(SemanticNode(
    id="python",
    label="Python",
    node_type="language",
    properties={"paradigm": "multi", "typing": "dynamic"}
))

graph.add_edge(SemanticEdge(
    source="python",
    target="programming",
    relation="is_a"
))

# Query
nodes = graph.query_nodes(node_type="language")

# Find path
path = graph.find_path("python", "web_development")

# Run inference
results = graph.infer({
    "subject": "?x",
    "predicate": "is_a",
    "object": "language"
})
```

### SemanticNode

```python
@dataclass
class SemanticNode:
    id: str                # Unique identifier
    label: str             # Display name
    node_type: str         # Category
    properties: dict       # Key-value attributes
    importance: float      # 0-1, from PageRank
```

### SemanticEdge

```python
@dataclass
class SemanticEdge:
    source: str            # Source node ID
    target: str            # Target node ID
    relation: str          # Relationship type
    weight: float          # Edge strength
    properties: dict       # Additional data
```

## Procedural Memory

Executable skills with conditions and actions.

```python
from modules import ProceduralMemoryStore, ProceduralSkill

store = ProceduralMemoryStore(db_path="brain.db")

# Store skill
skill = ProceduralSkill(
    name="format_code",
    description="Format Python code using black",
    conditions={"file_type": "python"},
    actions=[
        {"tool": "bash", "command": "black {file}"},
        {"tool": "notify", "message": "Formatted {file}"}
    ],
    success_rate=0.95
)
store.store(skill)

# Find applicable skills
skills = store.find_applicable({"file_type": "python"})

# Update success rate
store.record_outcome("format_code", success=True)
```

### ProceduralSkill

```python
@dataclass
class ProceduralSkill:
    name: str              # Skill identifier
    description: str       # What it does
    conditions: dict       # When to apply
    actions: list[dict]    # Steps to execute
    success_rate: float    # Historical success
    use_count: int         # Times executed
    last_used: float       # Timestamp
```

## Self/Meta Memory

Identity and developmental stage tracking.

```python
from modules import SelfModelStore, SelfModel

store = SelfModelStore(db_path="brain.db")

# Get current model
self_model = store.get_current()

print(f"Stage: {self_model.stage}")
print(f"Capabilities: {self_model.capabilities}")
print(f"Values: {self_model.values}")

# Update capability
store.update_capability("python_debugging", level=0.8)

# Update developmental stage
store.advance_stage()  # infant -> child -> adolescent -> adult
```

### SelfModel

```python
@dataclass
class SelfModel:
    stage: str             # Developmental stage
    capabilities: dict     # skill -> proficiency (0-1)
    values: dict           # value -> importance (0-1)
    goals: list[str]       # Current goals
    personality: dict      # Trait scores
    drive_state: dict      # Current drive levels
```

## Unified Memory System

Single interface to all subsystems.

```python
from modules import UnifiedMemorySystem

memory = UnifiedMemorySystem(db_path="brain.db")

# Store (auto-routes to appropriate subsystem)
memory.store(content, memory_type="episodic", **kwargs)

# Retrieve across subsystems
results = memory.retrieve(
    query="python debugging",
    memory_types=["episodic", "semantic"],
    limit=10
)

# Consolidate (move important working -> long-term)
memory.consolidate()

# Run decay
memory.decay(hours=24)
```

## Memory Plasticity

Decay and consolidation mechanisms.

```python
from modules import MemoryPlasticity

plasticity = MemoryPlasticity(memory_system)

# Apply time-based decay
plasticity.apply_decay(
    decay_rate=0.01,      # Per hour
    min_strength=0.1
)

# Consolidate based on access patterns
plasticity.consolidate(
    access_threshold=3,    # Min accesses
    time_window_hours=24
)

# Strengthen recently accessed
plasticity.strengthen_accessed(boost=0.1)
```

## Inference Rules

Built-in semantic inference rules:

| Rule | Pattern | Inference |
|------|---------|-----------|
| Transitivity | A is_a B, B is_a C | A is_a C |
| Inheritance | A is_a B, B has P | A has P |
| Symmetry | A related_to B | B related_to A |

```python
# Inference is automatic in semantic queries
nodes = graph.query_with_inference("?x", "is_a", "animal")
# Includes direct and inferred relationships
```

## Developmental Stages

Self-model tracks developmental progress:

| Stage | Description | Thresholds |
|-------|-------------|------------|
| infant | Basic responses | Initial |
| child | Learning patterns | capabilities > 0.3 |
| adolescent | Complex reasoning | capabilities > 0.5 |
| adult | Full autonomy | capabilities > 0.7 |

## Thread Safety

All stores use internal locking for thread-safe operations. Safe for concurrent access from multiple threads.
