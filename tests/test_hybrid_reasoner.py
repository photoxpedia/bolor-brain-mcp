"""Tests for HybridReasoner."""

import pytest
import threading
from modules.reasoning_engines.hybrid_reasoner import (
    HybridReasoner,
    HybridReasoningResult,
    ReasoningApproach,
    ProblemType,
)
from modules.reasoning_engines.symbolic_reasoner import SymbolicReasoner, Fact, Rule
from modules.reasoning_engines.knowledge_graph import KnowledgeGraph, Node, Edge
from modules.reasoning_engines.case_based_reasoner import CaseBasedReasoner, Case
from modules.reasoning_engines.hypothesis_engine import HypothesisEngine
from modules.reasoning_engines.analogical_reasoner import AnalogicalReasoner, Concept


# === HybridReasoningResult Tests ===

class TestHybridReasoningResult:
    """Tests for HybridReasoningResult dataclass."""

    def test_result_creation(self):
        """Test result creation."""
        result = HybridReasoningResult(
            problem={"query": "test"},
            problem_type=ProblemType.DEDUCTION,
            approaches_used=[ReasoningApproach.SYMBOLIC],
        )
        assert result.problem["query"] == "test"
        assert result.problem_type == ProblemType.DEDUCTION

    def test_result_to_dict(self):
        """Test result serialization."""
        result = HybridReasoningResult(
            problem={"query": "test"},
            problem_type=ProblemType.EXPLORATION,
            approaches_used=[ReasoningApproach.GRAPH],
            confidence=0.8,
        )
        d = result.to_dict()
        assert d["problem_type"] == "exploration"
        assert d["approaches_used"] == ["graph"]
        assert d["confidence"] == 0.8


# === HybridReasoner Basic Tests ===

class TestHybridReasonerBasics:
    """Tests for basic HybridReasoner operations."""

    def test_reasoner_creation(self):
        """Test reasoner creation."""
        reasoner = HybridReasoner()
        assert reasoner.symbolic is not None
        assert reasoner.kg is not None
        assert reasoner.cbr is not None
        assert reasoner.hypothesis is not None
        assert reasoner.analogical is not None

    def test_reasoner_with_components(self):
        """Test reasoner with custom components."""
        symbolic = SymbolicReasoner()
        kg = KnowledgeGraph()
        cbr = CaseBasedReasoner()

        reasoner = HybridReasoner(
            symbolic_reasoner=symbolic,
            knowledge_graph=kg,
            case_reasoner=cbr,
        )

        assert reasoner.symbolic is symbolic
        assert reasoner.kg is kg
        assert reasoner.cbr is cbr

    def test_add_fact(self):
        """Test adding a fact."""
        reasoner = HybridReasoner()
        fact = Fact(subject="cat", predicate="is", object="animal")
        reasoner.add_fact(fact)
        assert len(reasoner.symbolic.facts) > 0

    def test_add_rule(self):
        """Test adding a rule."""
        reasoner = HybridReasoner()
        # Add a fact first
        reasoner.add_fact(Fact(subject="cat", predicate="is", object="animal"))
        rule = Rule(
            name="animal_moves",
            conditions=[lambda f: f.predicate == "is" and f.object == "animal"],
            conclusion_template={"subject": "{subject}", "predicate": "can", "object": "move"},
        )
        reasoner.add_rule(rule)
        assert len(reasoner.symbolic.rules) > 0

    def test_add_node(self):
        """Test adding a node."""
        reasoner = HybridReasoner()
        node = Node(id="n1", label="Test")
        reasoner.add_node(node)
        assert reasoner.kg.get_node("n1") is not None

    def test_add_edge(self):
        """Test adding an edge."""
        reasoner = HybridReasoner()
        reasoner.add_node(Node(id="n1", label="A"))
        reasoner.add_node(Node(id="n2", label="B"))
        reasoner.add_edge(Edge(source="n1", target="n2", relation="connects"))
        edges = reasoner.kg.get_edges(source="n1")
        assert len(edges) > 0

    def test_add_case(self):
        """Test adding a case."""
        reasoner = HybridReasoner()
        case = Case(
            id="c1",
            problem={"type": "test"},
            solution={"action": "solve"},
            outcome="success",
        )
        reasoner.add_case(case)
        assert len(reasoner.cbr.cases) > 0

    def test_add_concept(self):
        """Test adding a concept."""
        reasoner = HybridReasoner()
        concept = Concept(id="c1", name="Test", domain="test_domain")
        reasoner.add_concept(concept)
        assert "test_domain" in reasoner.analogical.domains


# === Problem Type Detection Tests ===

class TestProblemTypeDetection:
    """Tests for problem type detection."""

    def test_detect_explicit_type(self):
        """Test detection from explicit type."""
        reasoner = HybridReasoner()
        problem = {"query": "test", "type": "diagnosis"}
        result = reasoner.reason(problem)
        assert result.problem_type == ProblemType.DIAGNOSIS

    def test_detect_deduction(self):
        """Test detection of deduction."""
        reasoner = HybridReasoner()
        # Use a query with "conclude" and "deduce" but not "what"
        problem = {"query": "We can therefore conclude and deduce that..."}
        result = reasoner.reason(problem)
        assert result.problem_type == ProblemType.DEDUCTION

    def test_detect_abduction(self):
        """Test detection of abduction."""
        reasoner = HybridReasoner()
        problem = {"query": "Why did this happen?"}
        result = reasoner.reason(problem)
        assert result.problem_type == ProblemType.ABDUCTION

    def test_detect_analogy(self):
        """Test detection of analogy."""
        reasoner = HybridReasoner()
        problem = {"query": "What is similar to this?"}
        result = reasoner.reason(problem)
        assert result.problem_type == ProblemType.ANALOGY

    def test_detect_planning(self):
        """Test detection of planning."""
        reasoner = HybridReasoner()
        problem = {"query": "How to solve this problem?"}
        result = reasoner.reason(problem)
        assert result.problem_type == ProblemType.PLANNING

    def test_detect_classification(self):
        """Test detection of classification."""
        reasoner = HybridReasoner()
        problem = {"query": "What type of thing is this?"}
        result = reasoner.reason(problem)
        assert result.problem_type == ProblemType.CLASSIFICATION

    def test_default_to_exploration(self):
        """Test default to exploration."""
        reasoner = HybridReasoner()
        problem = {"query": "random query here"}
        result = reasoner.reason(problem)
        assert result.problem_type == ProblemType.EXPLORATION


# === Reasoning Tests ===

class TestReasoning:
    """Tests for the reasoning process."""

    def test_reason_basic(self):
        """Test basic reasoning."""
        reasoner = HybridReasoner()
        result = reasoner.reason({"query": "What is happening?"})
        assert result is not None
        assert len(result.approaches_used) > 0

    def test_reason_with_specific_approaches(self):
        """Test reasoning with specific approaches."""
        reasoner = HybridReasoner()
        result = reasoner.reason(
            {"query": "test"},
            approaches=[ReasoningApproach.SYMBOLIC],
        )
        assert ReasoningApproach.SYMBOLIC in result.approaches_used
        assert len(result.approaches_used) == 1

    def test_reason_max_approaches(self):
        """Test max approaches limit."""
        reasoner = HybridReasoner()
        result = reasoner.reason({"query": "test"}, max_approaches=1)
        assert len(result.approaches_used) <= 1

    def test_reason_has_results(self):
        """Test that reasoning produces results."""
        reasoner = HybridReasoner()
        result = reasoner.reason({"query": "test"})
        assert isinstance(result.results, dict)
        assert len(result.results) > 0

    def test_reason_has_trace(self):
        """Test that reasoning produces trace."""
        reasoner = HybridReasoner()
        result = reasoner.reason({"query": "test"})
        assert len(result.reasoning_trace) > 0

    def test_reason_has_processing_time(self):
        """Test that processing time is recorded."""
        reasoner = HybridReasoner()
        result = reasoner.reason({"query": "test"})
        assert result.processing_time > 0


# === Quick Reason Tests ===

class TestQuickReason:
    """Tests for quick reasoning."""

    def test_quick_reason_basic(self):
        """Test basic quick reasoning."""
        reasoner = HybridReasoner()
        result = reasoner.quick_reason("What is this?")
        assert result is not None

    def test_quick_reason_returns_combined(self):
        """Test that quick_reason returns combined result."""
        reasoner = HybridReasoner()
        result = reasoner.quick_reason("test query")
        # Should be the combined result dict
        assert isinstance(result, dict) or result is None


# === Integration Tests ===

class TestIntegration:
    """Tests for component integration."""

    def setup_method(self):
        """Set up test data."""
        self.reasoner = HybridReasoner()

        # Add symbolic knowledge
        self.reasoner.add_fact(Fact(
            subject="smoke",
            predicate="indicates",
            object="fire"
        ))
        self.reasoner.add_rule(Rule(
            name="fire_rule",
            conditions=[lambda f: f.predicate == "indicates" and f.object == "fire"],
            conclusion_template={"subject": "fire", "predicate": "caused_by", "object": "{subject}"},
        ))

        # Add graph knowledge
        self.reasoner.add_node(Node(id="smoke", label="smoke"))
        self.reasoner.add_node(Node(id="fire", label="fire"))
        self.reasoner.add_edge(Edge(source="smoke", target="fire", relation="indicates"))

        # Add case
        self.reasoner.add_case(Case(
            id="case1",
            problem={"symptom": "smoke"},
            solution={"diagnosis": "fire"},
            outcome="success",
        ))

    def test_integrated_reasoning(self):
        """Test reasoning with multiple data sources."""
        result = self.reasoner.reason({"query": "Why is there smoke?"})
        assert result is not None
        assert result.confidence >= 0

    def test_symbolic_contributes(self):
        """Test that symbolic reasoning contributes."""
        result = self.reasoner.reason(
            {"query": "What does smoke indicate?"},
            approaches=[ReasoningApproach.SYMBOLIC],
        )
        assert "symbolic" in result.results

    def test_graph_contributes(self):
        """Test that graph reasoning contributes."""
        result = self.reasoner.reason(
            {"query": "What is fire related to?"},
            approaches=[ReasoningApproach.GRAPH],
        )
        assert "graph" in result.results


# === Confidence Calculation Tests ===

class TestConfidence:
    """Tests for confidence calculation."""

    def test_confidence_bounded(self):
        """Test that confidence is bounded 0-1."""
        reasoner = HybridReasoner()
        result = reasoner.reason({"query": "test"})
        assert 0 <= result.confidence <= 1

    def test_confidence_from_case_based(self):
        """Test confidence from case-based reasoning."""
        reasoner = HybridReasoner()
        # Add a matching case
        reasoner.add_case(Case(
            id="c1",
            problem={"query": "specific test"},
            solution={"answer": "solution"},
            outcome="success",
        ))
        result = reasoner.reason(
            {"query": "specific test"},
            approaches=[ReasoningApproach.CASE_BASED],
        )
        # Should have some confidence from the match
        assert result.confidence >= 0


# === Configuration Tests ===

class TestConfiguration:
    """Tests for configuration."""

    def test_set_approach_weight(self):
        """Test setting approach weight."""
        reasoner = HybridReasoner()
        reasoner.set_approach_weight(ReasoningApproach.SYMBOLIC, 0.9)
        weights = reasoner.get_approach_weights()
        assert weights[ReasoningApproach.SYMBOLIC] == 0.9

    def test_set_invalid_weight_raises(self):
        """Test that invalid weight raises."""
        reasoner = HybridReasoner()
        with pytest.raises(ValueError):
            reasoner.set_approach_weight(ReasoningApproach.SYMBOLIC, 1.5)

    def test_get_approach_weights(self):
        """Test getting approach weights."""
        reasoner = HybridReasoner()
        weights = reasoner.get_approach_weights()
        assert ReasoningApproach.SYMBOLIC in weights
        assert ReasoningApproach.GRAPH in weights


# === Statistics Tests ===

class TestStatistics:
    """Tests for statistics."""

    def test_get_stats(self):
        """Test getting statistics."""
        reasoner = HybridReasoner()
        reasoner.reason({"query": "test1"})
        reasoner.reason({"query": "test2"})

        stats = reasoner.get_stats()
        assert stats["total_problems"] == 2
        assert "by_type" in stats
        assert "by_approach" in stats
        assert "component_stats" in stats

    def test_stats_track_problem_types(self):
        """Test that stats track problem types."""
        reasoner = HybridReasoner()
        reasoner.reason({"query": "Why did this happen?"})  # abduction
        reasoner.reason({"query": "How to do this?"})  # planning

        stats = reasoner.get_stats()
        assert len(stats["by_type"]) >= 1

    def test_to_dict(self):
        """Test serialization."""
        reasoner = HybridReasoner()
        reasoner.reason({"query": "test"})

        d = reasoner.to_dict()
        assert "approach_weights" in d
        assert "stats" in d

    def test_clear(self):
        """Test clearing data."""
        reasoner = HybridReasoner()
        reasoner.add_fact(Fact(subject="a", predicate="b", object="c"))
        reasoner.reason({"query": "test"})

        reasoner.clear()

        stats = reasoner.get_stats()
        assert stats["total_problems"] == 0
        assert stats["component_stats"]["symbolic_facts"] == 0


# === Thread Safety Tests ===

class TestThreadSafety:
    """Tests for thread safety."""

    def test_reasoner_has_lock(self):
        """Test that reasoner has a lock."""
        reasoner = HybridReasoner()
        assert hasattr(reasoner, "_lock")
        assert isinstance(reasoner._lock, type(threading.RLock()))

    def test_concurrent_reasoning(self):
        """Test concurrent reasoning."""
        reasoner = HybridReasoner()
        errors = []
        results = []

        def reason_query(query_id):
            try:
                result = reasoner.reason({"query": f"Query {query_id}"})
                results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=reason_query, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

    def test_concurrent_modification(self):
        """Test concurrent data modification."""
        reasoner = HybridReasoner()
        errors = []

        def add_facts(prefix):
            try:
                for i in range(5):
                    reasoner.add_fact(Fact(
                        subject=f"{prefix}_{i}",
                        predicate="is",
                        object="thing"
                    ))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_facts, args=(f"t{i}",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(reasoner.symbolic.facts) == 25


# === All Approaches Tests ===

class TestAllApproaches:
    """Tests that each approach can be used."""

    def test_symbolic_approach(self):
        """Test symbolic approach works."""
        reasoner = HybridReasoner()
        result = reasoner.reason(
            {"query": "test"},
            approaches=[ReasoningApproach.SYMBOLIC],
        )
        assert "symbolic" in result.results
        assert result.results["symbolic"].get("method") == "symbolic"

    def test_graph_approach(self):
        """Test graph approach works."""
        reasoner = HybridReasoner()
        result = reasoner.reason(
            {"query": "test"},
            approaches=[ReasoningApproach.GRAPH],
        )
        assert "graph" in result.results
        assert result.results["graph"].get("method") == "graph"

    def test_case_based_approach(self):
        """Test case-based approach works."""
        reasoner = HybridReasoner()
        result = reasoner.reason(
            {"query": "test"},
            approaches=[ReasoningApproach.CASE_BASED],
        )
        assert "case_based" in result.results
        assert result.results["case_based"].get("method") == "case_based"

    def test_hypothesis_approach(self):
        """Test hypothesis approach works."""
        reasoner = HybridReasoner()
        result = reasoner.reason(
            {"query": "test"},
            approaches=[ReasoningApproach.HYPOTHESIS],
        )
        assert "hypothesis" in result.results
        assert result.results["hypothesis"].get("method") == "hypothesis"

    def test_analogical_approach(self):
        """Test analogical approach works."""
        reasoner = HybridReasoner()
        result = reasoner.reason(
            {"query": "test"},
            approaches=[ReasoningApproach.ANALOGICAL],
        )
        assert "analogical" in result.results
        assert result.results["analogical"].get("method") == "analogical"
