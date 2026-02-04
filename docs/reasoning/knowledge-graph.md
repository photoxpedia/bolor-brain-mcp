# KnowledgeGraph

Graph-based knowledge representation with traversal and inference.

## Overview

The `KnowledgeGraph` provides:

- Node and edge management
- BFS/DFS traversal
- Path finding (shortest, all paths)
- PageRank for node importance
- Pattern matching and inference
- Transitive closure

## Quick Start

```python
from modules import KnowledgeGraph, Node, Edge

kg = KnowledgeGraph()

# Add nodes
kg.add_node(Node("python", "Python", "language"))
kg.add_node(Node("web", "Web Development", "domain"))
kg.add_node(Node("django", "Django", "framework"))

# Add edges
kg.add_edge(Edge("python", "web", "used_for"))
kg.add_edge(Edge("django", "python", "built_with"))
kg.add_edge(Edge("django", "web", "enables"))

# Find path
result = kg.find_path("django", "web")
print(result.path)  # ['django', 'web']

# Traverse
nodes = kg.bfs("python", max_depth=2)
print(nodes)  # ['python', 'web', 'django']
```

## API Reference

### Node

```python
@dataclass
class Node:
    id: str                      # Unique identifier
    label: str                   # Human-readable name
    node_type: str               # Category (default: "entity")
    properties: dict[str, Any]   # Additional key-value data
    importance: float            # 0-1, used by PageRank
    created_at: float            # Timestamp
```

### Edge

```python
@dataclass
class Edge:
    source: str           # Source node ID
    target: str           # Target node ID
    relation: str         # Relationship type
    weight: float         # Edge weight (default: 1.0)
    properties: dict      # Additional data
    directed: bool        # True by default
    created_at: float     # Timestamp
```

### Node Operations

```python
# Add
kg.add_node(Node("id", "Label", "type"))

# Get
node = kg.get_node("id")

# Check existence
exists = kg.has_node("id")

# Query by type/properties
nodes = kg.query_nodes(node_type="language", version="3.11")

# Remove (also removes connected edges)
kg.remove_node("id")
```

### Edge Operations

```python
# Add (fails if source/target don't exist)
kg.add_edge(Edge("a", "b", "connects"))

# Query
edges = kg.get_edges(source="a", target="b", relation="connects")

# Check existence
exists = kg.has_edge("a", "b", relation="connects")

# Remove
kg.remove_edge("a", "b", relation="connects")  # Specific
kg.remove_edge("a", "b")  # All edges between a and b
```

### Traversal

#### Get Neighbors

```python
# Outgoing neighbors
neighbors = kg.get_neighbors("node_id", direction="outgoing")

# Incoming neighbors
neighbors = kg.get_neighbors("node_id", direction="incoming")

# Both directions
neighbors = kg.get_neighbors("node_id", direction="both")

# Filter by relation
neighbors = kg.get_neighbors("node_id", relation="causes")
```

#### BFS (Breadth-First Search)

```python
# Visit all reachable nodes in BFS order
nodes = kg.bfs("start_node", max_depth=5)

# Filter by relation type
nodes = kg.bfs("start_node", relation="is_a")
```

#### DFS (Depth-First Search)

```python
nodes = kg.dfs("start_node", max_depth=5)
```

### Path Finding

#### Shortest Path

```python
result = kg.find_path("start", "end")

if result.found:
    print(result.path)          # ['start', 'mid', 'end']
    print(result.length)        # 2
    print(result.total_weight)  # 2.5
    print(result.edges)         # Edge objects along path
```

#### All Paths

```python
paths = kg.find_all_paths(
    "start", "end",
    max_paths=10,
    max_length=5
)

for path in paths:
    print(path.path, path.total_weight)
```

### PathResult

```python
@dataclass
class PathResult:
    found: bool           # Path exists
    path: list[str]       # Node IDs in order
    length: int           # Number of edges
    total_weight: float   # Sum of edge weights
    edges: list[Edge]     # Edge objects
```

### PageRank

Calculate node importance scores.

```python
# Get scores (0-1, normalized)
ranks = kg.pagerank(iterations=20, damping=0.85)
# {"node1": 0.35, "node2": 0.25, ...}

# Update node importance attributes
kg.update_importance_from_pagerank()
```

### Subgraph Extraction

Get nodes within a radius of a center node.

```python
subgraph = kg.get_subgraph("center_node", radius=2)

print(len(subgraph.nodes))  # Nodes within 2 hops
print(len(subgraph.edges))  # Edges between them
```

### Pattern Matching / Inference

Query the graph with patterns. Variables start with `?`.

```python
# Find all "is_a" relationships
results = kg.infer({
    "subject": "?x",
    "predicate": "is_a",
    "object": "?y"
})
# [{"?x": "python", "?y": "language"}, ...]

# Find what Python is used for
results = kg.infer({
    "subject": "python",
    "predicate": "used_for",
    "object": "?domain"
})
# [{"?domain": "web"}, {"?domain": "data_science"}]
```

### Transitive Closure

Get all nodes reachable via a specific relation.

```python
# All things Python "is_a" (transitively)
ancestors = kg.transitive_closure("python", "is_a")
```

### Serialization

```python
# To dict
data = kg.to_dict()
# {"nodes": [...], "edges": [...], "stats": {...}}

# From dict
kg = KnowledgeGraph.from_dict(data)

# Clear
kg.clear()
```

### Statistics

```python
stats = kg.get_stats()
# {
#   "node_count": 100,
#   "edge_count": 250,
#   "avg_out_degree": 2.5,
#   "relation_counts": {"is_a": 50, "causes": 30},
#   "type_counts": {"entity": 60, "concept": 40}
# }
```

## Example: Concept Hierarchy

```python
kg = KnowledgeGraph()

# Build hierarchy
kg.add_node(Node("animal", "Animal", "category"))
kg.add_node(Node("mammal", "Mammal", "category"))
kg.add_node(Node("dog", "Dog", "species"))
kg.add_node(Node("cat", "Cat", "species"))

kg.add_edge(Edge("mammal", "animal", "is_a"))
kg.add_edge(Edge("dog", "mammal", "is_a"))
kg.add_edge(Edge("cat", "mammal", "is_a"))

# Find all ancestors of dog
ancestors = kg.transitive_closure("dog", "is_a")
print(ancestors)  # ['mammal', 'animal']

# Find all mammals
mammals = kg.infer({
    "subject": "?species",
    "predicate": "is_a",
    "object": "mammal"
})
# [{"?species": "dog"}, {"?species": "cat"}]
```

## Thread Safety

All operations are thread-safe. The graph uses internal locking for concurrent access.
