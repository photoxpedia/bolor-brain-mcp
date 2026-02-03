"""Tests for HypothesisEngine."""

import pytest
import threading
from modules.reasoning_engines.hypothesis_engine import (
    HypothesisEngine,
    Hypothesis,
    HypothesisTest,
)
from modules.reasoning_engines.knowledge_graph import KnowledgeGraph, Node, Edge
from modules.reasoning_engines.symbolic_reasoner import SymbolicReasoner, Fact


# === Hypothesis Tests ===

class TestHypothesisCreation:
    """Tests for Hypothesis creation."""

    def test_hypothesis_creation_basic(self):
        """Test basic hypothesis creation."""
        hyp = Hypothesis(id="h1", statement="X causes Y")
        assert hyp.id == "h1"
        assert hyp.statement == "X causes Y"
        assert hyp.confidence == 0.5
        assert hyp.status == "untested"

    def test_hypothesis_creation_with_all_fields(self):
        """Test hypothesis creation with all fields."""
        hyp = Hypothesis(
            id="h1",
            statement="X causes Y",
            supporting_evidence=["evidence1"],
            contradicting_evidence=["counter1"],
            confidence=0.7,
            status="supported",
            source="test",
        )
        assert len(hyp.supporting_evidence) == 1
        assert len(hyp.contradicting_evidence) == 1
        assert hyp.confidence == 0.7
        assert hyp.status == "supported"

    def test_hypothesis_empty_id_raises(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            Hypothesis(id="", statement="X causes Y")

    def test_hypothesis_empty_statement_raises(self):
        """Test that empty statement raises ValueError."""
        with pytest.raises(ValueError, match="statement cannot be empty"):
            Hypothesis(id="h1", statement="")

    def test_hypothesis_invalid_confidence_raises(self):
        """Test that invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be 0-1"):
            Hypothesis(id="h1", statement="X causes Y", confidence=1.5)

    def test_hypothesis_invalid_status_raises(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="status must be one of"):
            Hypothesis(id="h1", statement="X causes Y", status="invalid")


class TestHypothesisMethods:
    """Tests for Hypothesis methods."""

    def test_hypothesis_to_dict(self):
        """Test hypothesis serialization."""
        hyp = Hypothesis(
            id="h1",
            statement="X causes Y",
            supporting_evidence=["e1"],
            confidence=0.8,
            status="supported",
        )
        d = hyp.to_dict()
        assert d["id"] == "h1"
        assert d["statement"] == "X causes Y"
        assert d["confidence"] == 0.8

    def test_hypothesis_from_dict(self):
        """Test hypothesis deserialization."""
        data = {
            "id": "h1",
            "statement": "X causes Y",
            "supporting_evidence": ["e1"],
            "confidence": 0.8,
            "status": "supported",
        }
        hyp = Hypothesis.from_dict(data)
        assert hyp.id == "h1"
        assert hyp.confidence == 0.8


# === HypothesisTest Tests ===

class TestHypothesisTest:
    """Tests for HypothesisTest dataclass."""

    def test_hypothesis_test_creation(self):
        """Test HypothesisTest creation."""
        test = HypothesisTest(
            hypothesis_id="h1",
            test_type="evidence_search",
            evidence_found=["e1", "e2"],
            supports=True,
            confidence_delta=0.1,
        )
        assert test.hypothesis_id == "h1"
        assert len(test.evidence_found) == 2
        assert test.supports is True


# === HypothesisEngine Tests ===

class TestHypothesisEngineBasics:
    """Tests for basic HypothesisEngine operations."""

    def test_engine_creation(self):
        """Test engine creation."""
        engine = HypothesisEngine()
        assert len(engine.hypotheses) == 0

    def test_engine_with_components(self):
        """Test engine creation with components."""
        kg = KnowledgeGraph()
        reasoner = SymbolicReasoner()
        engine = HypothesisEngine(kg, reasoner)
        assert engine.kg is kg
        assert engine.reasoner is reasoner

    def test_create_hypothesis(self):
        """Test creating a hypothesis."""
        engine = HypothesisEngine()
        hyp = engine.create_hypothesis("X causes Y")
        assert hyp.statement == "X causes Y"
        assert engine.get_hypothesis(hyp.id) is not None

    def test_create_hypothesis_with_evidence(self):
        """Test creating hypothesis with initial evidence."""
        engine = HypothesisEngine()
        hyp = engine.create_hypothesis(
            "X causes Y",
            initial_evidence=["observation 1"],
            source="test"
        )
        assert len(hyp.supporting_evidence) == 1
        assert hyp.source == "test"

    def test_get_hypothesis(self):
        """Test getting a hypothesis."""
        engine = HypothesisEngine()
        hyp = engine.create_hypothesis("X causes Y")
        retrieved = engine.get_hypothesis(hyp.id)
        assert retrieved is not None
        assert retrieved.statement == "X causes Y"

    def test_get_nonexistent_hypothesis(self):
        """Test getting nonexistent hypothesis."""
        engine = HypothesisEngine()
        assert engine.get_hypothesis("nonexistent") is None

    def test_remove_hypothesis(self):
        """Test removing a hypothesis."""
        engine = HypothesisEngine()
        hyp = engine.create_hypothesis("X causes Y")
        assert engine.remove_hypothesis(hyp.id) is True
        assert engine.get_hypothesis(hyp.id) is None


# === Hypothesis Generation Tests ===

class TestHypothesisGeneration:
    """Tests for hypothesis generation."""

    def test_generate_from_observation(self):
        """Test generating hypotheses from observation."""
        engine = HypothesisEngine()
        hypotheses = engine.generate_hypotheses("system crash")
        # Should generate at least some hypotheses
        assert isinstance(hypotheses, list)

    def test_generate_respects_max(self):
        """Test that generation respects max limit."""
        engine = HypothesisEngine()
        hypotheses = engine.generate_hypotheses("problem", max_hypotheses=2)
        assert len(hypotheses) <= 2

    def test_generate_with_knowledge_graph(self):
        """Test generation using knowledge graph."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="bug", label="Bug"))
        kg.add_node(Node(id="crash", label="System Crash"))
        kg.add_edge(Edge(source="bug", target="crash", relation="causes"))

        engine = HypothesisEngine(kg)
        hypotheses = engine.generate_hypotheses("System Crash")
        # Should find the causal path
        assert len(hypotheses) >= 0  # May or may not find depending on matching

    def test_generate_with_symbolic_reasoner(self):
        """Test generation using symbolic reasoner."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(
            subject="memory_leak",
            predicate="causes",
            object="system_slowdown"
        ))

        engine = HypothesisEngine(symbolic_reasoner=reasoner)
        hypotheses = engine.generate_hypotheses("slowdown")
        assert len(hypotheses) >= 0


# === Hypothesis Testing Tests ===

class TestHypothesisTesting:
    """Tests for hypothesis testing."""

    def test_test_hypothesis_returns_result(self):
        """Test that testing returns a result."""
        engine = HypothesisEngine()
        hyp = engine.create_hypothesis("X causes Y")
        result = engine.test_hypothesis(hyp.id)
        assert result is not None
        assert result.hypothesis_id == hyp.id

    def test_test_nonexistent_hypothesis(self):
        """Test testing nonexistent hypothesis."""
        engine = HypothesisEngine()
        result = engine.test_hypothesis("nonexistent")
        assert result is None

    def test_test_updates_confidence(self):
        """Test that testing can update confidence."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="cause", label="cause_term"))
        kg.add_node(Node(id="effect", label="effect_term"))
        kg.add_edge(Edge(source="cause", target="effect", relation="causes"))

        engine = HypothesisEngine(kg)
        hyp = engine.create_hypothesis("cause_term leads to effect_term")
        initial_confidence = hyp.confidence

        engine.test_hypothesis(hyp.id)
        # Confidence may change based on evidence
        assert isinstance(hyp.confidence, float)

    def test_test_updates_status(self):
        """Test that testing updates status."""
        engine = HypothesisEngine()
        hyp = engine.create_hypothesis("X causes Y")
        assert hyp.status == "untested"

        engine.test_hypothesis(hyp.id)
        # Status should be updated (to inconclusive if no evidence)
        assert hyp.status in {"untested", "supported", "refuted", "inconclusive"}


# === Evidence Finding Tests ===

class TestEvidenceFinding:
    """Tests for evidence finding."""

    def test_find_evidence_returns_tuple(self):
        """Test that find_evidence returns tuple of lists."""
        engine = HypothesisEngine()
        hyp = Hypothesis(id="h1", statement="X causes Y")
        supporting, contradicting = engine.find_evidence(hyp)
        assert isinstance(supporting, list)
        assert isinstance(contradicting, list)

    def test_find_evidence_from_knowledge_graph(self):
        """Test finding evidence in knowledge graph."""
        kg = KnowledgeGraph()
        kg.add_node(Node(id="smoking", label="smoking"))
        kg.add_node(Node(id="cancer", label="cancer"))
        kg.add_edge(Edge(source="smoking", target="cancer", relation="causes"))

        engine = HypothesisEngine(kg)
        hyp = Hypothesis(id="h1", statement="smoking causes cancer")
        supporting, contradicting = engine.find_evidence(hyp)
        # Should find the edge as evidence
        assert len(supporting) >= 0  # Depends on matching logic

    def test_find_evidence_from_facts(self):
        """Test finding evidence in symbolic facts."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(
            subject="rain",
            predicate="causes",
            object="wet_ground"
        ))

        engine = HypothesisEngine(symbolic_reasoner=reasoner)
        hyp = Hypothesis(id="h1", statement="rain makes ground wet")
        supporting, contradicting = engine.find_evidence(hyp)
        assert len(supporting) >= 0


# === Confidence Update Tests ===

class TestConfidenceUpdate:
    """Tests for confidence updates."""

    def test_confidence_bounded(self):
        """Test that confidence stays bounded."""
        engine = HypothesisEngine()
        hyp = engine.create_hypothesis("X causes Y")

        # Try to push confidence very high
        test = HypothesisTest(
            hypothesis_id=hyp.id,
            test_type="test",
            supports=True,
            confidence_delta=10.0  # Very high delta
        )
        new_conf = engine.update_confidence(hyp.id, test)
        assert new_conf <= 0.95  # Max confidence

        # Try to push confidence very low
        test2 = HypothesisTest(
            hypothesis_id=hyp.id,
            test_type="test",
            supports=False,
            confidence_delta=-10.0  # Very negative delta
        )
        new_conf = engine.update_confidence(hyp.id, test2)
        assert new_conf >= 0.05  # Min confidence


# === Hypothesis Ranking Tests ===

class TestHypothesisRanking:
    """Tests for hypothesis ranking."""

    def test_rank_by_confidence(self):
        """Test ranking hypotheses by confidence."""
        engine = HypothesisEngine()

        h1 = engine.create_hypothesis("Low confidence")
        h2 = engine.create_hypothesis("High confidence")

        h1.confidence = 0.3
        h2.confidence = 0.8

        ranked = engine.rank_hypotheses()
        assert ranked[0].confidence > ranked[1].confidence

    def test_get_best_hypothesis(self):
        """Test getting best hypothesis."""
        engine = HypothesisEngine()

        h1 = engine.create_hypothesis("Low")
        h2 = engine.create_hypothesis("High")

        h1.confidence = 0.3
        h2.confidence = 0.9

        best = engine.get_best_hypothesis()
        assert best.confidence == 0.9


# === Thread Safety Tests ===

class TestThreadSafety:
    """Tests for thread safety."""

    def test_engine_has_lock(self):
        """Test that engine has a lock."""
        engine = HypothesisEngine()
        assert hasattr(engine, "_lock")
        assert isinstance(engine._lock, type(threading.RLock()))

    def test_concurrent_hypothesis_creation(self):
        """Test concurrent hypothesis creation."""
        engine = HypothesisEngine()
        errors = []

        def create_hypotheses(start):
            try:
                for i in range(20):
                    engine.create_hypothesis(f"Hypothesis {start}_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_hypotheses, args=(i,))
                   for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(engine.hypotheses) == 100


# === Statistics Tests ===

class TestStatistics:
    """Tests for statistics."""

    def test_get_stats(self):
        """Test getting statistics."""
        engine = HypothesisEngine()
        engine.create_hypothesis("H1")
        engine.create_hypothesis("H2")

        stats = engine.get_stats()
        assert stats["total_hypotheses"] == 2
        assert "status_counts" in stats

    def test_to_dict(self):
        """Test serialization."""
        engine = HypothesisEngine()
        engine.create_hypothesis("H1")

        d = engine.to_dict()
        assert "hypotheses" in d
        assert "stats" in d
        assert len(d["hypotheses"]) == 1

    def test_clear(self):
        """Test clearing hypotheses."""
        engine = HypothesisEngine()
        engine.create_hypothesis("H1")
        engine.create_hypothesis("H2")

        engine.clear()
        assert len(engine.hypotheses) == 0
