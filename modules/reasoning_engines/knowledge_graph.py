"""Knowledge graph with traversal and inference capabilities.

This module provides a graph-based knowledge representation:
- Node and edge management
- BFS/DFS traversal algorithms
- PageRank for node importance
- Path finding algorithms
- Pattern matching and inference
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Iterator
from collections import deque
import threading
import time
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """A node in the knowledge graph.

    Attributes:
        id: Unique identifier for the node
        label: Human-readable label
        node_type: Category/type of the node
        properties: Additional key-value properties
        importance: Importance score (0-1), used by PageRank
        created_at: Timestamp when node was created
    """
    id: str
    label: str
    node_type: str = "entity"
    properties: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    created_at: float = field(default_factory=lambda: time.time())

    def __post_init__(self):
        """Validate node fields."""
        if not self.id:
            raise ValueError("Node id cannot be empty")
        if not self.label:
            raise ValueError("Node label cannot be empty")
        if not 0 <= self.importance <= 1:
            raise ValueError(f"importance must be 0-1, got {self.importance}")

    def matches(self, node_type: str = None, **properties) -> bool:
        """Check if node matches the given criteria."""
        if node_type is not None and self.node_type != node_type:
            return False
        for key, value in properties.items():
            if self.properties.get(key) != value:
                return False
        return True

    def to_dict(self) -> dict:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type,
            "properties": self.properties,
            "importance": self.importance,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            label=data["label"],
            node_type=data.get("node_type", "entity"),
            properties=data.get("properties", {}),
            importance=data.get("importance", 0.5),
            created_at=data.get("created_at", time.time()),
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            return self.id == other.id
        return False


@dataclass
class Edge:
    """An edge connecting two nodes.

    Attributes:
        source: ID of the source node
        target: ID of the target node
        relation: Type of relationship
        weight: Edge weight (for weighted algorithms)
        properties: Additional key-value properties
        directed: Whether the edge is directed (default True)
        created_at: Timestamp when edge was created
    """
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    directed: bool = True
    created_at: float = field(default_factory=lambda: time.time())

    def __post_init__(self):
        """Validate edge fields."""
        if not self.source:
            raise ValueError("Edge source cannot be empty")
        if not self.target:
            raise ValueError("Edge target cannot be empty")
        if not self.relation:
            raise ValueError("Edge relation cannot be empty")
        if self.weight < 0:
            raise ValueError(f"Edge weight cannot be negative, got {self.weight}")

    def matches(self, source: str = None, target: str = None,
                relation: str = None) -> bool:
        """Check if edge matches the given criteria."""
        if source is not None and self.source != source:
            return False
        if target is not None and self.target != target:
            return False
        if relation is not None and self.relation != relation:
            return False
        return True

    def to_dict(self) -> dict:
        """Convert edge to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "weight": self.weight,
            "properties": self.properties,
            "directed": self.directed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Edge":
        """Create edge from dictionary."""
        return cls(
            source=data["source"],
            target=data["target"],
            relation=data["relation"],
            weight=data.get("weight", 1.0),
            properties=data.get("properties", {}),
            directed=data.get("directed", True),
            created_at=data.get("created_at", time.time()),
        )

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.relation))

    def __eq__(self, other) -> bool:
        if isinstance(other, Edge):
            return (self.source == other.source and
                    self.target == other.target and
                    self.relation == other.relation)
        return False


@dataclass
class PathResult:
    """Result from a path finding operation."""
    found: bool
    path: list[str] = field(default_factory=list)
    length: int = 0
    total_weight: float = 0.0
    edges: list[Edge] = field(default_factory=list)


class KnowledgeGraph:
    """Knowledge graph with inference capabilities.

    Features:
    - Node and edge management
    - BFS/DFS traversal
    - PageRank for node importance
    - Path finding (single and all paths)
    - Pattern matching
    - Transitive inference
    - Thread-safe operations

    Example:
        >>> kg = KnowledgeGraph()
        >>> kg.add_node(Node("socrates", "Socrates", "person"))
        >>> kg.add_node(Node("human", "Human", "category"))
        >>> kg.add_edge(Edge("socrates", "human", "is_a"))
        >>> kg.bfs("socrates")
        ['socrates', 'human']
    """

    def __init__(self, genome=None):
        """Initialize the knowledge graph.

        Args:
            genome: Optional CognitiveGenome for configurable parameters
        """
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.genome = genome
        self._lock = threading.RLock()

        # Adjacency lists for fast traversal
        self._outgoing: dict[str, list[Edge]] = {}  # source -> edges
        self._incoming: dict[str, list[Edge]] = {}  # target -> edges

    # === Node Operations ===

    def add_node(self, node: Node) -> bool:
        """Add a node to the graph.

        Args:
            node: The node to add

        Returns:
            True if added, False if node with same ID exists
        """
        with self._lock:
            if node.id in self.nodes:
                return False
            self.nodes[node.id] = node
            # Initialize adjacency lists
            if node.id not in self._outgoing:
                self._outgoing[node.id] = []
            if node.id not in self._incoming:
                self._incoming[node.id] = []
            return True

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID.

        Args:
            node_id: ID of the node

        Returns:
            The node or None if not found
        """
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and all its edges.

        Args:
            node_id: ID of the node to remove

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if node_id not in self.nodes:
                return False

            # Remove all edges involving this node
            self.edges = [e for e in self.edges
                         if e.source != node_id and e.target != node_id]

            # Update adjacency lists
            if node_id in self._outgoing:
                del self._outgoing[node_id]
            if node_id in self._incoming:
                del self._incoming[node_id]

            # Remove from other adjacency lists
            for edges_list in self._outgoing.values():
                edges_list[:] = [e for e in edges_list if e.target != node_id]
            for edges_list in self._incoming.values():
                edges_list[:] = [e for e in edges_list if e.source != node_id]

            del self.nodes[node_id]
            return True

    def query_nodes(self, node_type: str = None, **properties) -> list[Node]:
        """Query nodes matching criteria.

        Args:
            node_type: Filter by node type
            **properties: Filter by properties

        Returns:
            List of matching nodes
        """
        results = []
        for node in self.nodes.values():
            if node.matches(node_type, **properties):
                results.append(node)
        return results

    def has_node(self, node_id: str) -> bool:
        """Check if a node exists."""
        return node_id in self.nodes

    # === Edge Operations ===

    def add_edge(self, edge: Edge) -> bool:
        """Add an edge to the graph.

        Args:
            edge: The edge to add

        Returns:
            True if added, False if source/target not found or duplicate
        """
        with self._lock:
            # Check that source and target exist
            if edge.source not in self.nodes:
                logger.warning(f"Edge source '{edge.source}' not found")
                return False
            if edge.target not in self.nodes:
                logger.warning(f"Edge target '{edge.target}' not found")
                return False

            # Check for duplicate
            for existing in self.edges:
                if (existing.source == edge.source and
                    existing.target == edge.target and
                    existing.relation == edge.relation):
                    return False

            self.edges.append(edge)

            # Update adjacency lists
            self._outgoing[edge.source].append(edge)
            self._incoming[edge.target].append(edge)

            # For undirected edges, add reverse
            if not edge.directed:
                reverse = Edge(
                    source=edge.target,
                    target=edge.source,
                    relation=edge.relation,
                    weight=edge.weight,
                    properties=edge.properties,
                    directed=False,
                )
                self._outgoing[edge.target].append(reverse)
                self._incoming[edge.source].append(reverse)

            return True

    def get_edges(self, source: str = None, target: str = None,
                  relation: str = None) -> list[Edge]:
        """Get edges matching criteria.

        Args:
            source: Filter by source node
            target: Filter by target node
            relation: Filter by relation type

        Returns:
            List of matching edges
        """
        results = []
        for edge in self.edges:
            if edge.matches(source, target, relation):
                results.append(edge)
        return results

    def remove_edge(self, source: str, target: str,
                    relation: str = None) -> bool:
        """Remove an edge.

        Args:
            source: Source node ID
            target: Target node ID
            relation: Relation type (if None, removes all edges between nodes)

        Returns:
            True if any edges were removed
        """
        with self._lock:
            original_count = len(self.edges)

            if relation:
                self.edges = [e for e in self.edges
                             if not (e.source == source and
                                    e.target == target and
                                    e.relation == relation)]
            else:
                self.edges = [e for e in self.edges
                             if not (e.source == source and e.target == target)]

            removed = original_count - len(self.edges)

            if removed > 0:
                # Update adjacency lists
                self._outgoing[source] = [e for e in self._outgoing.get(source, [])
                                          if e.target != target or
                                          (relation and e.relation != relation)]
                self._incoming[target] = [e for e in self._incoming.get(target, [])
                                         if e.source != source or
                                         (relation and e.relation != relation)]

            return removed > 0

    def has_edge(self, source: str, target: str, relation: str = None) -> bool:
        """Check if an edge exists."""
        for edge in self._outgoing.get(source, []):
            if edge.target == target:
                if relation is None or edge.relation == relation:
                    return True
        return False

    # === Traversal ===

    def get_neighbors(self, node_id: str, relation: str = None,
                      direction: str = "outgoing") -> list[str]:
        """Get neighboring nodes.

        Args:
            node_id: ID of the center node
            relation: Filter by relation type
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of neighbor node IDs
        """
        neighbors = set()

        if direction in ("outgoing", "both"):
            for edge in self._outgoing.get(node_id, []):
                if relation is None or edge.relation == relation:
                    neighbors.add(edge.target)

        if direction in ("incoming", "both"):
            for edge in self._incoming.get(node_id, []):
                if relation is None or edge.relation == relation:
                    neighbors.add(edge.source)

        return list(neighbors)

    def bfs(self, start: str, max_depth: int = 10,
            relation: str = None) -> list[str]:
        """Breadth-first search from a starting node.

        Args:
            start: Starting node ID
            max_depth: Maximum depth to traverse
            relation: Filter by relation type

        Returns:
            List of node IDs in BFS order
        """
        if start not in self.nodes:
            return []

        visited = []
        queue = deque([(start, 0)])
        seen = {start}

        while queue:
            node_id, depth = queue.popleft()
            visited.append(node_id)

            if depth >= max_depth:
                continue

            for neighbor in self.get_neighbors(node_id, relation):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return visited

    def dfs(self, start: str, max_depth: int = 10,
            relation: str = None) -> list[str]:
        """Depth-first search from a starting node.

        Args:
            start: Starting node ID
            max_depth: Maximum depth to traverse
            relation: Filter by relation type

        Returns:
            List of node IDs in DFS order
        """
        if start not in self.nodes:
            return []

        visited = []
        stack = [(start, 0)]
        seen = {start}

        while stack:
            node_id, depth = stack.pop()
            visited.append(node_id)

            if depth >= max_depth:
                continue

            for neighbor in reversed(self.get_neighbors(node_id, relation)):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append((neighbor, depth + 1))

        return visited

    # === Path Finding ===

    def find_path(self, start: str, end: str,
                  relation: str = None) -> PathResult:
        """Find a path between two nodes (BFS - finds shortest).

        Args:
            start: Starting node ID
            end: Ending node ID
            relation: Filter by relation type

        Returns:
            PathResult with the found path
        """
        if start not in self.nodes or end not in self.nodes:
            return PathResult(found=False)

        if start == end:
            return PathResult(found=True, path=[start], length=0)

        # BFS to find shortest path
        queue = deque([(start, [start], [], 0.0)])
        seen = {start}

        while queue:
            node_id, path, edges, weight = queue.popleft()

            for edge in self._outgoing.get(node_id, []):
                if relation is not None and edge.relation != relation:
                    continue

                neighbor = edge.target
                if neighbor == end:
                    return PathResult(
                        found=True,
                        path=path + [neighbor],
                        length=len(path),
                        total_weight=weight + edge.weight,
                        edges=edges + [edge],
                    )

                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((
                        neighbor,
                        path + [neighbor],
                        edges + [edge],
                        weight + edge.weight,
                    ))

        return PathResult(found=False)

    def find_all_paths(self, start: str, end: str, max_paths: int = 10,
                       max_length: int = 10, relation: str = None) -> list[PathResult]:
        """Find all paths between two nodes.

        Args:
            start: Starting node ID
            end: Ending node ID
            max_paths: Maximum number of paths to return
            max_length: Maximum path length
            relation: Filter by relation type

        Returns:
            List of PathResults
        """
        if start not in self.nodes or end not in self.nodes:
            return []

        paths = []

        def dfs_paths(current: str, path: list, edges: list, weight: float):
            if len(paths) >= max_paths:
                return
            if len(path) > max_length:
                return

            if current == end:
                paths.append(PathResult(
                    found=True,
                    path=path.copy(),
                    length=len(path) - 1,
                    total_weight=weight,
                    edges=edges.copy(),
                ))
                return

            for edge in self._outgoing.get(current, []):
                if relation is not None and edge.relation != relation:
                    continue

                neighbor = edge.target
                if neighbor not in path:  # Avoid cycles
                    path.append(neighbor)
                    edges.append(edge)
                    dfs_paths(neighbor, path, edges, weight + edge.weight)
                    path.pop()
                    edges.pop()

        dfs_paths(start, [start], [], 0.0)
        return paths

    # === PageRank ===

    def pagerank(self, iterations: int = 20, damping: float = 0.85) -> dict[str, float]:
        """Calculate PageRank scores for all nodes.

        Args:
            iterations: Number of iterations
            damping: Damping factor (typically 0.85)

        Returns:
            Dictionary mapping node IDs to PageRank scores
        """
        n = len(self.nodes)
        if n == 0:
            return {}

        # Initialize ranks
        ranks = {node_id: 1.0 / n for node_id in self.nodes}

        for _ in range(iterations):
            new_ranks = {}

            for node_id in self.nodes:
                # Start with minimum rank from random jumps
                rank = (1 - damping) / n

                # Add contributions from incoming edges
                for edge in self._incoming.get(node_id, []):
                    source = edge.source
                    out_degree = len(self._outgoing.get(source, []))
                    if out_degree > 0:
                        rank += damping * ranks[source] / out_degree

                new_ranks[node_id] = rank

            ranks = new_ranks

        # Normalize
        total = sum(ranks.values())
        if total > 0:
            ranks = {k: v / total for k, v in ranks.items()}

        return ranks

    def update_importance_from_pagerank(self) -> None:
        """Update node importance scores based on PageRank."""
        ranks = self.pagerank()
        with self._lock:
            for node_id, rank in ranks.items():
                if node_id in self.nodes:
                    self.nodes[node_id].importance = rank

    # === Subgraph ===

    def get_subgraph(self, center: str, radius: int = 2) -> "KnowledgeGraph":
        """Get a subgraph around a center node.

        Args:
            center: Center node ID
            radius: Maximum distance from center (considers both directions)

        Returns:
            New KnowledgeGraph containing the subgraph
        """
        if center not in self.nodes:
            return KnowledgeGraph(self.genome)

        # Find all nodes within radius (bidirectional BFS)
        node_ids = set()
        queue = deque([(center, 0)])
        node_ids.add(center)

        while queue:
            node_id, depth = queue.popleft()
            if depth >= radius:
                continue

            # Get neighbors in both directions
            for neighbor in self.get_neighbors(node_id, direction="both"):
                if neighbor not in node_ids:
                    node_ids.add(neighbor)
                    queue.append((neighbor, depth + 1))

        # Create subgraph
        subgraph = KnowledgeGraph(self.genome)

        for node_id in node_ids:
            node = self.nodes[node_id]
            subgraph.add_node(Node(
                id=node.id,
                label=node.label,
                node_type=node.node_type,
                properties=node.properties.copy(),
                importance=node.importance,
            ))

        for edge in self.edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(Edge(
                    source=edge.source,
                    target=edge.target,
                    relation=edge.relation,
                    weight=edge.weight,
                    properties=edge.properties.copy(),
                    directed=edge.directed,
                ))

        return subgraph

    # === Pattern Matching / Inference ===

    def infer(self, pattern: dict) -> list[dict]:
        """Find matches for a pattern in the graph.

        Pattern format:
        {
            "subject": "?x" or "specific_id",
            "predicate": "relation_type",
            "object": "?y" or "specific_id"
        }

        Variables start with "?".

        Args:
            pattern: Pattern to match

        Returns:
            List of variable bindings that match
        """
        results = []

        subject = pattern.get("subject")
        predicate = pattern.get("predicate")
        object_ = pattern.get("object")

        for edge in self.edges:
            # Check predicate match
            if predicate and not predicate.startswith("?"):
                if edge.relation != predicate:
                    continue

            binding = {}

            # Check subject
            if subject:
                if subject.startswith("?"):
                    binding[subject] = edge.source
                elif edge.source != subject:
                    continue

            # Check object
            if object_:
                if object_.startswith("?"):
                    binding[object_] = edge.target
                elif edge.target != object_:
                    continue

            # Add predicate binding if it's a variable
            if predicate and predicate.startswith("?"):
                binding[predicate] = edge.relation

            results.append(binding)

        return results

    def transitive_closure(self, start: str, relation: str) -> list[str]:
        """Get all nodes reachable via a specific relation (transitively).

        Args:
            start: Starting node ID
            relation: Relation to follow

        Returns:
            List of reachable node IDs
        """
        return self.bfs(start, max_depth=100, relation=relation)[1:]  # Exclude start

    # === Statistics ===

    def get_stats(self) -> dict:
        """Get graph statistics.

        Returns:
            Dictionary with stats about the graph
        """
        relation_counts = {}
        for edge in self.edges:
            relation_counts[edge.relation] = relation_counts.get(edge.relation, 0) + 1

        type_counts = {}
        for node in self.nodes.values():
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1

        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "avg_out_degree": (
                sum(len(edges) for edges in self._outgoing.values()) / len(self.nodes)
                if self.nodes else 0
            ),
            "relation_counts": relation_counts,
            "type_counts": type_counts,
        }

    def to_dict(self) -> dict:
        """Serialize graph to dictionary."""
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "stats": self.get_stats(),
        }

    @classmethod
    def from_dict(cls, data: dict, genome=None) -> "KnowledgeGraph":
        """Create graph from dictionary."""
        graph = cls(genome)

        for node_data in data.get("nodes", []):
            graph.add_node(Node.from_dict(node_data))

        for edge_data in data.get("edges", []):
            graph.add_edge(Edge.from_dict(edge_data))

        return graph

    def clear(self) -> None:
        """Clear all nodes and edges."""
        with self._lock:
            self.nodes.clear()
            self.edges.clear()
            self._outgoing.clear()
            self._incoming.clear()
