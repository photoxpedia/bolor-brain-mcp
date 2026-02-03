"""Hypothesis generation and testing engine.

This module provides hypothesis-driven reasoning:
- Generate hypotheses from observations
- Find supporting/contradicting evidence
- Update confidence based on evidence
- Rank hypotheses by plausibility
"""

from dataclasses import dataclass, field
from typing import Optional, Any
import threading
import time
import uuid
import logging

from .knowledge_graph import KnowledgeGraph, Node, Edge
from .symbolic_reasoner import SymbolicReasoner, Fact

logger = logging.getLogger(__name__)


@dataclass
class Hypothesis:
    """A hypothesis to be tested.

    Attributes:
        id: Unique identifier
        statement: The hypothesis statement
        supporting_evidence: Evidence that supports the hypothesis
        contradicting_evidence: Evidence that contradicts the hypothesis
        confidence: Confidence level (0-1)
        status: Current status (untested, supported, refuted, inconclusive)
        source: How the hypothesis was generated
        created_at: When the hypothesis was created
    """
    id: str
    statement: str
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    confidence: float = 0.5
    status: str = "untested"  # untested, supported, refuted, inconclusive
    source: str = "manual"
    created_at: float = field(default_factory=lambda: time.time())

    def __post_init__(self):
        """Validate hypothesis fields."""
        if not self.id:
            raise ValueError("Hypothesis id cannot be empty")
        if not self.statement:
            raise ValueError("Hypothesis statement cannot be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be 0-1, got {self.confidence}")
        valid_statuses = {"untested", "supported", "refuted", "inconclusive"}
        if self.status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")

    def to_dict(self) -> dict:
        """Convert hypothesis to dictionary."""
        return {
            "id": self.id,
            "statement": self.statement,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "confidence": self.confidence,
            "status": self.status,
            "source": self.source,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Hypothesis":
        """Create hypothesis from dictionary."""
        return cls(
            id=data["id"],
            statement=data["statement"],
            supporting_evidence=data.get("supporting_evidence", []),
            contradicting_evidence=data.get("contradicting_evidence", []),
            confidence=data.get("confidence", 0.5),
            status=data.get("status", "untested"),
            source=data.get("source", "manual"),
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class HypothesisTest:
    """Result of testing a hypothesis.

    Attributes:
        hypothesis_id: ID of the tested hypothesis
        test_type: Type of test performed
        evidence_found: Evidence discovered during testing
        supports: Whether the evidence supports the hypothesis
        confidence_delta: Change in confidence
    """
    hypothesis_id: str
    test_type: str
    evidence_found: list[str] = field(default_factory=list)
    supports: bool = True
    confidence_delta: float = 0.0


class HypothesisEngine:
    """Hypothesis generation and testing engine.

    Uses KnowledgeGraph paths and SymbolicReasoner to:
    - Generate hypotheses from observations
    - Find evidence for/against hypotheses
    - Update confidence based on evidence

    Example:
        >>> engine = HypothesisEngine(knowledge_graph, symbolic_reasoner)
        >>> hyp = engine.create_hypothesis("X causes Y")
        >>> test_result = engine.test_hypothesis(hyp.id)
        >>> # Confidence updated based on evidence found
    """

    def __init__(self, knowledge_graph: KnowledgeGraph = None,
                 symbolic_reasoner: SymbolicReasoner = None,
                 genome=None):
        """Initialize the hypothesis engine.

        Args:
            knowledge_graph: KnowledgeGraph for path finding
            symbolic_reasoner: SymbolicReasoner for logical inference
            genome: Optional CognitiveGenome for configurable parameters
        """
        self.kg = knowledge_graph or KnowledgeGraph()
        self.reasoner = symbolic_reasoner or SymbolicReasoner()
        self.hypotheses: dict[str, Hypothesis] = {}
        self.genome = genome
        self._lock = threading.RLock()

        # Confidence update parameters
        self._support_boost = 0.15
        self._contradict_penalty = 0.2
        self._min_confidence = 0.05
        self._max_confidence = 0.95

    # === Hypothesis Management ===

    def create_hypothesis(self, statement: str,
                         initial_evidence: list[str] = None,
                         source: str = "manual") -> Hypothesis:
        """Create a new hypothesis.

        Args:
            statement: The hypothesis statement
            initial_evidence: Initial supporting evidence
            source: How the hypothesis was created

        Returns:
            The created hypothesis
        """
        hyp_id = str(uuid.uuid4())[:8]

        hypothesis = Hypothesis(
            id=hyp_id,
            statement=statement,
            supporting_evidence=initial_evidence or [],
            source=source,
        )

        with self._lock:
            self.hypotheses[hyp_id] = hypothesis

        logger.debug(f"Created hypothesis: {hyp_id}")
        return hypothesis

    def get_hypothesis(self, hyp_id: str) -> Optional[Hypothesis]:
        """Get a hypothesis by ID."""
        return self.hypotheses.get(hyp_id)

    def remove_hypothesis(self, hyp_id: str) -> bool:
        """Remove a hypothesis."""
        with self._lock:
            if hyp_id in self.hypotheses:
                del self.hypotheses[hyp_id]
                return True
            return False

    # === Hypothesis Generation ===

    def generate_hypotheses(self, observation: str,
                           max_hypotheses: int = 5) -> list[Hypothesis]:
        """Generate hypotheses to explain an observation.

        Args:
            observation: The observation to explain
            max_hypotheses: Maximum number of hypotheses to generate

        Returns:
            List of generated hypotheses
        """
        hypotheses = []

        # Strategy 1: Find causal paths in knowledge graph
        causal_paths = self._find_causal_paths(observation)
        for path in causal_paths[:max_hypotheses // 2]:
            hyp = self._path_to_hypothesis(path, observation)
            if hyp:
                hypotheses.append(hyp)

        # Strategy 2: Use symbolic reasoning to infer causes
        inferred = self._infer_causes(observation)
        for cause in inferred[:max_hypotheses - len(hypotheses)]:
            hyp = self.create_hypothesis(
                statement=f"{cause} causes {observation}",
                source="symbolic_inference"
            )
            hypotheses.append(hyp)

        # Strategy 3: Generate from correlations in facts
        correlations = self._find_correlations(observation)
        remaining = max_hypotheses - len(hypotheses)
        for corr in correlations[:remaining]:
            hyp = self.create_hypothesis(
                statement=f"{corr} is related to {observation}",
                source="correlation"
            )
            hypotheses.append(hyp)

        return hypotheses[:max_hypotheses]

    def _find_causal_paths(self, observation: str) -> list[list[str]]:
        """Find causal paths in the knowledge graph."""
        paths = []

        # Look for nodes related to the observation
        related_nodes = self.kg.query_nodes()
        for node in related_nodes:
            if observation.lower() in node.label.lower():
                # Find incoming edges (potential causes)
                incoming = self.kg.get_edges(target=node.id)
                for edge in incoming:
                    if edge.relation in ("causes", "leads_to", "results_in"):
                        paths.append([edge.source, edge.relation, edge.target])

        return paths

    def _path_to_hypothesis(self, path: list[str],
                           observation: str) -> Optional[Hypothesis]:
        """Convert a knowledge graph path to a hypothesis."""
        if len(path) < 2:
            return None

        statement = f"{path[0]} may explain {observation}"
        return self.create_hypothesis(
            statement=statement,
            initial_evidence=[f"Path found: {' -> '.join(path)}"],
            source="knowledge_graph_path"
        )

    def _infer_causes(self, observation: str) -> list[str]:
        """Use symbolic reasoning to infer potential causes."""
        causes = []

        # Query facts related to the observation
        facts = self.reasoner.query_facts(predicate="causes")
        for fact in facts:
            if observation.lower() in str(fact.object).lower():
                causes.append(str(fact.subject))

        return causes

    def _find_correlations(self, observation: str) -> list[str]:
        """Find concepts that correlate with the observation."""
        correlations = []

        # Look at co-occurring concepts in facts
        related_facts = self.reasoner.query_facts()
        for fact in related_facts:
            if observation.lower() in str(fact).lower():
                correlations.append(fact.subject)

        return list(set(correlations))[:5]

    # === Hypothesis Testing ===

    def test_hypothesis(self, hyp_id: str) -> Optional[HypothesisTest]:
        """Test a hypothesis by finding evidence.

        Args:
            hyp_id: ID of the hypothesis to test

        Returns:
            HypothesisTest result or None if hypothesis not found
        """
        hypothesis = self.get_hypothesis(hyp_id)
        if not hypothesis:
            return None

        # Find evidence
        supporting, contradicting = self.find_evidence(hypothesis)

        # Create test result
        test = HypothesisTest(
            hypothesis_id=hyp_id,
            test_type="evidence_search",
            evidence_found=supporting + contradicting,
            supports=len(supporting) > len(contradicting),
            confidence_delta=0.0,
        )

        # Update hypothesis based on evidence
        with self._lock:
            hypothesis.supporting_evidence.extend(supporting)
            hypothesis.contradicting_evidence.extend(contradicting)

            # Calculate confidence change
            support_score = len(supporting) * self._support_boost
            contradict_score = len(contradicting) * self._contradict_penalty
            delta = support_score - contradict_score
            test.confidence_delta = delta

            # Update confidence
            new_confidence = hypothesis.confidence + delta
            hypothesis.confidence = max(
                self._min_confidence,
                min(self._max_confidence, new_confidence)
            )

            # Update status
            if hypothesis.confidence >= 0.7:
                hypothesis.status = "supported"
            elif hypothesis.confidence <= 0.3:
                hypothesis.status = "refuted"
            elif supporting or contradicting:
                hypothesis.status = "inconclusive"

        return test

    def find_evidence(self, hypothesis: Hypothesis
                     ) -> tuple[list[str], list[str]]:
        """Find evidence for and against a hypothesis.

        Args:
            hypothesis: The hypothesis to find evidence for

        Returns:
            Tuple of (supporting_evidence, contradicting_evidence)
        """
        supporting = []
        contradicting = []

        # Extract key terms from hypothesis
        terms = hypothesis.statement.lower().split()

        # Search knowledge graph for related information
        for term in terms:
            if len(term) > 3:  # Skip short words
                nodes = self.kg.query_nodes()
                for node in nodes:
                    if term in node.label.lower():
                        # Check relationships
                        edges = self.kg.get_edges(source=node.id)
                        for edge in edges:
                            evidence = f"{node.label} {edge.relation} {edge.target}"
                            if self._supports_hypothesis(evidence, hypothesis):
                                supporting.append(evidence)
                            elif self._contradicts_hypothesis(evidence, hypothesis):
                                contradicting.append(evidence)

        # Search symbolic reasoner facts
        for fact in self.reasoner.query_facts():
            fact_str = str(fact)
            if any(t in fact_str.lower() for t in terms if len(t) > 3):
                if self._supports_hypothesis(fact_str, hypothesis):
                    supporting.append(fact_str)
                elif self._contradicts_hypothesis(fact_str, hypothesis):
                    contradicting.append(fact_str)

        return list(set(supporting)), list(set(contradicting))

    def _supports_hypothesis(self, evidence: str,
                            hypothesis: Hypothesis) -> bool:
        """Check if evidence supports a hypothesis."""
        # Simple heuristic: overlapping terms suggest support
        evidence_terms = set(evidence.lower().split())
        hypothesis_terms = set(hypothesis.statement.lower().split())
        overlap = evidence_terms & hypothesis_terms
        return len(overlap) >= 2

    def _contradicts_hypothesis(self, evidence: str,
                               hypothesis: Hypothesis) -> bool:
        """Check if evidence contradicts a hypothesis."""
        # Check for negation patterns
        negation_patterns = ["not ", "never ", "no ", "cannot ", "doesn't "]
        for pattern in negation_patterns:
            if pattern in evidence.lower():
                # If negation appears with hypothesis terms
                hypothesis_terms = hypothesis.statement.lower().split()
                if any(t in evidence.lower() for t in hypothesis_terms if len(t) > 3):
                    return True
        return False

    def update_confidence(self, hyp_id: str,
                         test_result: HypothesisTest) -> float:
        """Update hypothesis confidence based on test result.

        Args:
            hyp_id: ID of the hypothesis
            test_result: The test result to apply

        Returns:
            New confidence value
        """
        hypothesis = self.get_hypothesis(hyp_id)
        if not hypothesis:
            return 0.0

        with self._lock:
            hypothesis.confidence = max(
                self._min_confidence,
                min(self._max_confidence,
                    hypothesis.confidence + test_result.confidence_delta)
            )
            return hypothesis.confidence

    # === Hypothesis Ranking ===

    def rank_hypotheses(self, hypotheses: list[Hypothesis] = None
                       ) -> list[Hypothesis]:
        """Rank hypotheses by confidence and evidence.

        Args:
            hypotheses: Hypotheses to rank (defaults to all)

        Returns:
            Sorted list of hypotheses
        """
        if hypotheses is None:
            hypotheses = list(self.hypotheses.values())

        def score(hyp: Hypothesis) -> float:
            # Base score is confidence
            score = hyp.confidence

            # Bonus for supporting evidence
            score += len(hyp.supporting_evidence) * 0.05

            # Penalty for contradicting evidence
            score -= len(hyp.contradicting_evidence) * 0.05

            return score

        return sorted(hypotheses, key=score, reverse=True)

    def get_best_hypothesis(self, observation: str = None
                           ) -> Optional[Hypothesis]:
        """Get the best hypothesis for an observation.

        Args:
            observation: Optional observation to generate hypotheses for

        Returns:
            Best hypothesis or None
        """
        if observation:
            hypotheses = self.generate_hypotheses(observation)
            for hyp in hypotheses:
                self.test_hypothesis(hyp.id)
        else:
            hypotheses = list(self.hypotheses.values())

        if not hypotheses:
            return None

        ranked = self.rank_hypotheses(hypotheses)
        return ranked[0] if ranked else None

    # === Statistics ===

    def get_stats(self) -> dict:
        """Get engine statistics."""
        status_counts = {}
        for hyp in self.hypotheses.values():
            status_counts[hyp.status] = status_counts.get(hyp.status, 0) + 1

        return {
            "total_hypotheses": len(self.hypotheses),
            "status_counts": status_counts,
            "avg_confidence": (
                sum(h.confidence for h in self.hypotheses.values()) /
                len(self.hypotheses) if self.hypotheses else 0
            ),
        }

    def to_dict(self) -> dict:
        """Serialize engine state."""
        return {
            "hypotheses": [h.to_dict() for h in self.hypotheses.values()],
            "stats": self.get_stats(),
        }

    def clear(self) -> None:
        """Clear all hypotheses."""
        with self._lock:
            self.hypotheses.clear()
