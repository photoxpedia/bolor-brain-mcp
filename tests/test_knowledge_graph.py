"""Tests for KnowledgeGraph."""

import pytest
import threading
from modules.reasoning_engines.knowledge_graph import (
    KnowledgeGraph,
    Node,
    Edge,
    PathResult,
)


# === Node Tests ===

class TestNodeCreation:
    """Tests for Node creation and validation."""

    def test_node_creation_basic(self):
        """Test basic node creation."""
        node = Node(id="n1", label="Node 1")
        assert node.id == "n1"
        assert node.label == "Node 1"
        assert node.node_type == "entity"

    def test_node_creation_with_all_fields(self):
        """Test node creation with all fields."""
        node = Node(
            id="n1",
            label="Person",
            node_type="person",
            properties={"age": 30},
            importance=0.8,
        )
        assert node.node_type == "person"
        assert node.properties["age"] == 30
        assert node.importance == 0.8

    def test_node_empty_id_raises(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            Node(id="", label="Test")

    def test_node_empty_label_raises(self):
        """Test that empty label raises ValueError."""
        with pytest.raises(ValueError, match="label cannot be empty"):
            Node(id="n1", label="")

    def test_node_invalid_importance_raises(self):
        """Test that invalid importance raises ValueError."""
        with pytest.raises(ValueError, match="importance must be 0-1"):
            Node(id="n1", label="Test", importance=1.5)

    def test_node_negative_importance_raises(self):
        """Test that negative importance raises ValueError."""
        with pytest.raises(ValueError, match="importance must be 0-1"):
            Node(id="n1", label="Test", importance=-0.1)


class TestNodeMethods:
    """Tests for Node methods."""

    def test_node_matches_type(self):
        """Test node matching by type."""
        node = Node(id="n1", label="Test", node_type="person")
        assert node.matches(node_type="person")
        assert not node.matches(node_type="entity")

    def test_node_matches_properties(self):
        """Test node matching by properties."""
        node = Node(id="n1", label="Test", properties={"age": 30, "name": "John"})
        assert node.matches(age=30)
        assert node.matches(name="John")
        assert node.matches(age=30, name="John")
        assert not node.matches(age=25)

    def test_node_to_dict(self):
        """Test node serialization to dict."""
        node = Node(id="n1", label="Test", node_type="person", properties={"x": 1})
        d = node.to_dict()
        assert d["id"] == "n1"
        assert d["label"] == "Test"
        assert d["node_type"] == "person"
        assert d["properties"]["x"] == 1

    def test_node_from_dict(self):
        """Test node creation from dict."""
        data = {
            "id": "n1",
            "label": "Test",
            "node_type": "person",
            "properties": {"x": 1},
            "importance": 0.7,
        }
        node = Node.from_dict(data)
        assert node.id == "n1"
        assert node.label == "Test"
        assert node.node_type == "person"
        assert node.importance == 0.7

    def test_node_hash_and_equality(self):
        """Test node hashing and equality."""
        n1 = Node(id="n1", label="Test")
        n2 = Node(id="n1", label="Different")
        n3 = Node(id="n2", label="Test")
        assert n1 == n2  # Same ID
        assert n1 != n3  # Different ID
        assert hash(n1) == hash(n2)


# === Edge Tests ===

class TestEdgeCreation:
    """Tests for Edge creation and validation."""

    def test_edge_creation_basic(self):
        """Test basic edge creation."""
        edge = Edge(source="n1", target="n2", relation="connects")
        assert edge.source == "n1"
        assert edge.target == "n2"
        assert edge.relation == "connects"
        assert edge.weight == 1.0
        assert edge.directed is True

    def test_edge_creation_with_all_fields(self):
        """Test edge creation with all fields."""
        edge = Edge(
            source="n1",
            target="n2",
            relation="is_a",
            weight=2.5,
            properties={"type": "inheritance"},
            directed=False,
        )
        assert edge.weight == 2.5
        assert edge.properties["type"] == "inheritance"
        assert edge.directed is False

    def test_edge_empty_source_raises(self):
        """Test that empty source raises ValueError."""
        with pytest.raises(ValueError, match="source cannot be empty"):
            Edge(source="", target="n2", relation="rel")

    def test_edge_empty_target_raises(self):
        """Test that empty target raises ValueError."""
        with pytest.raises(ValueError, match="target cannot be empty"):
            Edge(source="n1", target="", relation="rel")

    def test_edge_empty_relation_raises(self):
        """Test that empty relation raises ValueError."""
        with pytest.raises(ValueError, match="relation cannot be empty"):
            Edge(source="n1", target="n2", relation="")

    def test_edge_negative_weight_raises(self):
        """Test that negative weight raises ValueError."""
        with pytest.raises(ValueError, match="weight cannot be negative"):
            Edge(source="n1", target="n2", relation="rel", weight=-1.0)


class TestEdgeMethods:
    """Tests for Edge methods."""

    def test_edge_matches_source(self):
        """Test edge matching by source."""
        edge = Edge(source="n1", target="n2", relation="rel")
        assert edge.matches(source="n1")
        assert not edge.matches(source="n2")

    def test_edge_matches_target(self):
        """Test edge matching by target."""
        edge = Edge(source="n1", target="n2", relation="rel")
        assert edge.matches(target="n2")
        assert not edge.matches(target="n1")

    def test_edge_matches_relation(self):
        """Test edge matching by relation."""
        edge = Edge(source="n1", target="n2", relation="is_a")
        assert edge.matches(relation="is_a")
        assert not edge.matches(relation="has_a")

    def test_edge_to_dict(self):
        """Test edge serialization to dict."""
        edge = Edge(source="n1", target="n2", relation="rel", weight=2.0)
        d = edge.to_dict()
        assert d["source"] == "n1"
        assert d["target"] == "n2"
        assert d["relation"] == "rel"
        assert d["weight"] == 2.0

    def test_edge_from_dict(self):
        """Test edge creation from dict."""
        data = {
            "source": "n1",
            "target": "n2",
            "relation": "rel",
            "weight": 2.0,
        }
        edge = Edge.from_dict(data)
        assert edge.source == "n1"
        assert edge.target == "n2"
        assert edge.weight == 2.0

    def test_edge_hash_and_equality(self):
        """Test edge hashing and equality."""
        e1 = Edge(source="n1", target="n2", relation="rel")
        e2 = Edge(source="n1", target="n2", relation="rel", weight=5.0)
        e3 = Edge(source="n1", target="n2", relation="other")
        assert e1 == e2  # Same source, target, relation
        assert e1 != e3  # Different relation
        assert hash(e1) == hash(e2)


# === KnowledgeGraph Node Operations Tests ===

class TestKnowledgeGraphNodeOperations:
    """Tests for KnowledgeGraph node operations."""

    def test_graph_creation(self):
        """Test graph creation."""
        kg = KnowledgeGraph()
        assert len(kg.nodes) == 0
        assert len(kg.edges) == 0

    def test_add_node(self):
        """Test adding a node."""
        kg = KnowledgeGraph()
        node = Node(id="n1", label="Node 1")
        assert kg.add_node(node) is True
        assert kg.has_node("n1")

    def test_add_duplicate_node_returns_false(self):
        """Test that adding duplicate node returns False."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        assert kg.add_node(Node(id="n1", label="Node 1 Again")) is False

    def test_get_node(self):
        """Test getting a node."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        node = kg.get_node("n1")
        assert node is not None
        assert node.label == "Node 1"

    def test_get_nonexistent_node(self):
        """Test getting nonexistent node."""
        kg = KnowledgeGraph()
        assert kg.get_node("nonexistent") is None

    def test_remove_node(self):
        """Test removing a node."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        assert kg.remove_node("n1") is True
        assert not kg.has_node("n1")

    def test_remove_node_removes_edges(self):
        """Test that removing a node removes its edges."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_edge(Edge(source="n1", target="n2", relation="rel"))
        kg.remove_node("n1")
        assert len(kg.edges) == 0

    def test_query_nodes_by_type(self):
        """Test querying nodes by type."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="p1", label="Alice", node_type="person"))
        kg.add_node(Node(id="p2", label="Bob", node_type="person"))
        kg.add_node(Node(id="c1", label="Acme", node_type="company"))
        people = kg.query_nodes(node_type="person")
        assert len(people) == 2

    def test_query_nodes_by_properties(self):
        """Test querying nodes by properties."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="p1", label="Alice", properties={"age": 30}))
        kg.add_node(Node(id="p2", label="Bob", properties={"age": 25}))
        results = kg.query_nodes(age=30)
        assert len(results) == 1
        assert results[0].label == "Alice"


# === KnowledgeGraph Edge Operations Tests ===

class TestKnowledgeGraphEdgeOperations:
    """Tests for KnowledgeGraph edge operations."""

    def test_add_edge(self):
        """Test adding an edge."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        assert kg.add_edge(Edge(source="n1", target="n2", relation="rel")) is True
        assert len(kg.edges) == 1

    def test_add_edge_nonexistent_source_fails(self):
        """Test that adding edge with nonexistent source fails."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n2", label="Node 2"))
        assert kg.add_edge(Edge(source="n1", target="n2", relation="rel")) is False

    def test_add_edge_nonexistent_target_fails(self):
        """Test that adding edge with nonexistent target fails."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        assert kg.add_edge(Edge(source="n1", target="n2", relation="rel")) is False

    def test_add_duplicate_edge_returns_false(self):
        """Test that adding duplicate edge returns False."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_edge(Edge(source="n1", target="n2", relation="rel"))
        assert kg.add_edge(Edge(source="n1", target="n2", relation="rel")) is False

    def test_get_edges_by_source(self):
        """Test getting edges by source."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_node(Node(id="n3", label="Node 3"))
        kg.add_edge(Edge(source="n1", target="n2", relation="r1"))
        kg.add_edge(Edge(source="n1", target="n3", relation="r2"))
        kg.add_edge(Edge(source="n2", target="n3", relation="r3"))
        edges = kg.get_edges(source="n1")
        assert len(edges) == 2

    def test_get_edges_by_relation(self):
        """Test getting edges by relation."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_edge(Edge(source="n1", target="n2", relation="is_a"))
        edges = kg.get_edges(relation="is_a")
        assert len(edges) == 1

    def test_remove_edge(self):
        """Test removing an edge."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_edge(Edge(source="n1", target="n2", relation="rel"))
        assert kg.remove_edge("n1", "n2") is True
        assert len(kg.edges) == 0

    def test_has_edge(self):
        """Test checking if edge exists."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_edge(Edge(source="n1", target="n2", relation="rel"))
        assert kg.has_edge("n1", "n2") is True
        assert kg.has_edge("n1", "n2", "rel") is True
        assert kg.has_edge("n1", "n2", "other") is False
        assert kg.has_edge("n2", "n1") is False


# === Traversal Tests ===

class TestTraversal:
    """Tests for graph traversal algorithms."""

    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph for traversal tests."""
        kg = KnowledgeGraph()
        # Create a simple tree: A -> B -> D, A -> C -> E
        for node_id in ["A", "B", "C", "D", "E"]:
            kg.add_node(Node(id=node_id, label=node_id))
        kg.add_edge(Edge(source="A", target="B", relation="to"))
        kg.add_edge(Edge(source="A", target="C", relation="to"))
        kg.add_edge(Edge(source="B", target="D", relation="to"))
        kg.add_edge(Edge(source="C", target="E", relation="to"))
        return kg

    def test_get_neighbors_outgoing(self, sample_graph):
        """Test getting outgoing neighbors."""
        neighbors = sample_graph.get_neighbors("A")
        assert set(neighbors) == {"B", "C"}

    def test_get_neighbors_incoming(self, sample_graph):
        """Test getting incoming neighbors."""
        neighbors = sample_graph.get_neighbors("D", direction="incoming")
        assert neighbors == ["B"]

    def test_get_neighbors_both(self, sample_graph):
        """Test getting both incoming and outgoing neighbors."""
        neighbors = sample_graph.get_neighbors("B", direction="both")
        assert set(neighbors) == {"A", "D"}

    def test_bfs_visits_all_reachable(self, sample_graph):
        """Test that BFS visits all reachable nodes."""
        visited = sample_graph.bfs("A")
        assert set(visited) == {"A", "B", "C", "D", "E"}

    def test_bfs_order_is_breadth_first(self, sample_graph):
        """Test that BFS visits in breadth-first order."""
        visited = sample_graph.bfs("A")
        # A should be first, then B and C (depth 1), then D and E (depth 2)
        assert visited[0] == "A"
        assert set(visited[1:3]) == {"B", "C"}
        assert set(visited[3:5]) == {"D", "E"}

    def test_bfs_respects_max_depth(self, sample_graph):
        """Test that BFS respects max depth."""
        visited = sample_graph.bfs("A", max_depth=1)
        assert set(visited) == {"A", "B", "C"}

    def test_bfs_nonexistent_start(self, sample_graph):
        """Test BFS with nonexistent start node."""
        visited = sample_graph.bfs("nonexistent")
        assert visited == []

    def test_dfs_visits_all_reachable(self, sample_graph):
        """Test that DFS visits all reachable nodes."""
        visited = sample_graph.dfs("A")
        assert set(visited) == {"A", "B", "C", "D", "E"}

    def test_dfs_respects_max_depth(self, sample_graph):
        """Test that DFS respects max depth."""
        visited = sample_graph.dfs("A", max_depth=1)
        assert set(visited) == {"A", "B", "C"}


# === Path Finding Tests ===

class TestPathFinding:
    """Tests for path finding algorithms."""

    @pytest.fixture
    def path_graph(self):
        """Create a graph for path finding tests."""
        kg = KnowledgeGraph()
        # A -> B -> C, A -> D -> C (two paths to C)
        for node_id in ["A", "B", "C", "D"]:
            kg.add_node(Node(id=node_id, label=node_id))
        kg.add_edge(Edge(source="A", target="B", relation="to", weight=1.0))
        kg.add_edge(Edge(source="B", target="C", relation="to", weight=1.0))
        kg.add_edge(Edge(source="A", target="D", relation="to", weight=1.0))
        kg.add_edge(Edge(source="D", target="C", relation="to", weight=1.0))
        return kg

    def test_find_path_exists(self, path_graph):
        """Test finding an existing path."""
        result = path_graph.find_path("A", "C")
        assert result.found is True
        assert result.path[0] == "A"
        assert result.path[-1] == "C"
        assert result.length == 2

    def test_find_path_same_node(self, path_graph):
        """Test path to same node."""
        result = path_graph.find_path("A", "A")
        assert result.found is True
        assert result.path == ["A"]
        assert result.length == 0

    def test_find_path_not_exists(self, path_graph):
        """Test finding nonexistent path."""
        # Add isolated node
        path_graph.add_node(Node(id="X", label="X"))
        result = path_graph.find_path("A", "X")
        assert result.found is False

    def test_find_path_nonexistent_nodes(self, path_graph):
        """Test path finding with nonexistent nodes."""
        result = path_graph.find_path("nonexistent", "C")
        assert result.found is False

    def test_find_all_paths(self, path_graph):
        """Test finding all paths."""
        results = path_graph.find_all_paths("A", "C")
        assert len(results) == 2
        paths = [tuple(r.path) for r in results]
        assert ("A", "B", "C") in paths
        assert ("A", "D", "C") in paths

    def test_find_all_paths_max_paths(self, path_graph):
        """Test limiting number of paths."""
        results = path_graph.find_all_paths("A", "C", max_paths=1)
        assert len(results) == 1


# === PageRank Tests ===

class TestPageRank:
    """Tests for PageRank algorithm."""

    def test_pagerank_simple(self):
        """Test PageRank on simple graph."""
        kg = KnowledgeGraph()
        # A -> B -> C, A -> C (C has highest in-degree)
        for node_id in ["A", "B", "C"]:
            kg.add_node(Node(id=node_id, label=node_id))
        kg.add_edge(Edge(source="A", target="B", relation="to"))
        kg.add_edge(Edge(source="B", target="C", relation="to"))
        kg.add_edge(Edge(source="A", target="C", relation="to"))

        ranks = kg.pagerank()
        # C should have highest rank (most incoming)
        assert ranks["C"] > ranks["B"]
        assert ranks["C"] > ranks["A"]

    def test_pagerank_converges(self):
        """Test that PageRank converges to sum of 1."""
        kg = KnowledgeGraph()
        for i in range(5):
            kg.add_node(Node(id=f"n{i}", label=f"Node {i}"))
        for i in range(4):
            kg.add_edge(Edge(source=f"n{i}", target=f"n{i+1}", relation="to"))

        ranks = kg.pagerank()
        total = sum(ranks.values())
        assert abs(total - 1.0) < 0.01

    def test_pagerank_empty_graph(self):
        """Test PageRank on empty graph."""
        kg = KnowledgeGraph()
        ranks = kg.pagerank()
        assert ranks == {}

    def test_update_importance_from_pagerank(self):
        """Test updating node importance from PageRank."""
        kg = KnowledgeGraph()
        for node_id in ["A", "B", "C"]:
            kg.add_node(Node(id=node_id, label=node_id))
        kg.add_edge(Edge(source="A", target="B", relation="to"))
        kg.add_edge(Edge(source="B", target="C", relation="to"))

        kg.update_importance_from_pagerank()
        # Check that importance was updated
        assert kg.get_node("C").importance > 0


# === Subgraph Tests ===

class TestSubgraph:
    """Tests for subgraph extraction."""

    def test_get_subgraph(self):
        """Test extracting a subgraph."""
        kg = KnowledgeGraph()
        # A -> B -> C -> D
        for node_id in ["A", "B", "C", "D"]:
            kg.add_node(Node(id=node_id, label=node_id))
        kg.add_edge(Edge(source="A", target="B", relation="to"))
        kg.add_edge(Edge(source="B", target="C", relation="to"))
        kg.add_edge(Edge(source="C", target="D", relation="to"))

        # Subgraph with radius 1 from B
        subgraph = kg.get_subgraph("B", radius=1)
        assert len(subgraph.nodes) == 3  # A, B, C
        assert len(subgraph.edges) == 2

    def test_get_subgraph_nonexistent_center(self):
        """Test subgraph with nonexistent center."""
        kg = KnowledgeGraph()
        subgraph = kg.get_subgraph("nonexistent")
        assert len(subgraph.nodes) == 0


# === Pattern Matching Tests ===

class TestPatternMatching:
    """Tests for pattern matching and inference."""

    @pytest.fixture
    def type_graph(self):
        """Create a graph with type hierarchy."""
        kg = KnowledgeGraph()
        # Socrates -> human -> mortal
        kg.add_node(Node(id="socrates", label="Socrates", node_type="person"))
        kg.add_node(Node(id="human", label="Human", node_type="category"))
        kg.add_node(Node(id="mortal", label="Mortal", node_type="category"))
        kg.add_edge(Edge(source="socrates", target="human", relation="is_a"))
        kg.add_edge(Edge(source="human", target="mortal", relation="is_a"))
        return kg

    def test_infer_simple_pattern(self, type_graph):
        """Test simple pattern matching."""
        results = type_graph.infer({"subject": "socrates", "predicate": "is_a", "object": "?y"})
        assert len(results) == 1
        assert results[0]["?y"] == "human"

    def test_infer_variable_subject(self, type_graph):
        """Test pattern with variable subject."""
        results = type_graph.infer({"subject": "?x", "predicate": "is_a", "object": "human"})
        assert len(results) == 1
        assert results[0]["?x"] == "socrates"

    def test_infer_all_variables(self, type_graph):
        """Test pattern with all variables."""
        results = type_graph.infer({"subject": "?x", "predicate": "is_a", "object": "?y"})
        assert len(results) == 2  # socrates->human and human->mortal

    def test_transitive_closure(self, type_graph):
        """Test transitive closure."""
        reachable = type_graph.transitive_closure("socrates", "is_a")
        assert "human" in reachable
        assert "mortal" in reachable


# === Thread Safety Tests ===

class TestThreadSafety:
    """Tests for thread safety."""

    def test_graph_has_lock(self):
        """Test that graph has a lock."""
        kg = KnowledgeGraph()
        assert hasattr(kg, "_lock")
        assert isinstance(kg._lock, type(threading.RLock()))

    def test_concurrent_node_addition(self):
        """Test concurrent node addition."""
        kg = KnowledgeGraph()
        errors = []

        def add_nodes(start):
            try:
                for i in range(100):
                    kg.add_node(Node(id=f"n{start}_{i}", label=f"Node {start}_{i}"))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_nodes, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(kg.nodes) == 500


# === Serialization Tests ===

class TestSerialization:
    """Tests for graph serialization."""

    def test_to_dict(self):
        """Test graph serialization to dict."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_edge(Edge(source="n1", target="n2", relation="rel"))

        d = kg.to_dict()
        assert len(d["nodes"]) == 2
        assert len(d["edges"]) == 1
        assert "stats" in d

    def test_from_dict(self):
        """Test graph creation from dict."""
        data = {
            "nodes": [
                {"id": "n1", "label": "Node 1"},
                {"id": "n2", "label": "Node 2"},
            ],
            "edges": [
                {"source": "n1", "target": "n2", "relation": "rel"},
            ],
        }
        kg = KnowledgeGraph.from_dict(data)
        assert len(kg.nodes) == 2
        assert len(kg.edges) == 1

    def test_round_trip(self):
        """Test serialization round trip."""
        kg1 = KnowledgeGraph()
        kg1.add_node(Node(id="n1", label="Node 1", properties={"x": 1}))
        kg1.add_node(Node(id="n2", label="Node 2"))
        kg1.add_edge(Edge(source="n1", target="n2", relation="rel", weight=2.0))

        data = kg1.to_dict()
        kg2 = KnowledgeGraph.from_dict(data)

        assert len(kg2.nodes) == 2
        assert len(kg2.edges) == 1
        assert kg2.get_node("n1").properties["x"] == 1
        assert kg2.edges[0].weight == 2.0


# === Statistics Tests ===

class TestStatistics:
    """Tests for graph statistics."""

    def test_get_stats(self):
        """Test getting graph statistics."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1", node_type="person"))
        kg.add_node(Node(id="n2", label="Node 2", node_type="person"))
        kg.add_node(Node(id="n3", label="Node 3", node_type="company"))
        kg.add_edge(Edge(source="n1", target="n2", relation="knows"))
        kg.add_edge(Edge(source="n1", target="n3", relation="works_at"))

        stats = kg.get_stats()
        assert stats["node_count"] == 3
        assert stats["edge_count"] == 2
        assert stats["type_counts"]["person"] == 2
        assert stats["type_counts"]["company"] == 1
        assert stats["relation_counts"]["knows"] == 1
        assert stats["relation_counts"]["works_at"] == 1

    def test_clear_graph(self):
        """Test clearing the graph."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="n1", label="Node 1"))
        kg.add_node(Node(id="n2", label="Node 2"))
        kg.add_edge(Edge(source="n1", target="n2", relation="rel"))

        kg.clear()
        assert len(kg.nodes) == 0
        assert len(kg.edges) == 0
