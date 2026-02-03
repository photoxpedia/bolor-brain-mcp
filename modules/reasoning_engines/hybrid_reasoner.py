"""Hybrid reasoning engine that orchestrates multiple reasoning approaches.

This module provides a unified interface for:
- Symbolic reasoning (forward/backward chaining)
- Knowledge graph traversal and inference
- Case-based reasoning (4R cycle)
- Hypothesis-driven reasoning
- Analogical reasoning (cross-domain transfer)

The HybridReasoner selects and combines approaches based on problem type.
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from enum import Enum
import threading
import time
import logging

from .symbolic_reasoner import SymbolicReasoner, Fact, Rule, ReasoningResult
from .knowledge_graph import KnowledgeGraph, Node, Edge, PathResult
from .case_based_reasoner import CaseBasedReasoner, Case, CaseReasoningResult
from .hypothesis_engine import HypothesisEngine, Hypothesis, HypothesisTest
from .analogical_reasoner import AnalogicalReasoner, Concept, Analogy

logger = logging.getLogger(__name__)


class ReasoningApproach(Enum):
    """Types of reasoning approaches."""
    SYMBOLIC = "symbolic"
    GRAPH = "graph"
    CASE_BASED = "case_based"
    HYPOTHESIS = "hypothesis"
    ANALOGICAL = "analogical"
    HYBRID = "hybrid"


class ProblemType(Enum):
    """Types of problems for reasoning."""
    DEDUCTION = "deduction"  # Given rules, derive conclusion
    INDUCTION = "induction"  # Given examples, find pattern
    ABDUCTION = "abduction"  # Given observation, find explanation
    ANALOGY = "analogy"  # Given similarity, transfer knowledge
    CLASSIFICATION = "classification"  # Categorize input
    PLANNING = "planning"  # Find sequence of actions
    DIAGNOSIS = "diagnosis"  # Identify cause of symptoms
    EXPLORATION = "exploration"  # Discover new knowledge


@dataclass
class HybridReasoningResult:
    """Result from hybrid reasoning.

    Attributes:
        problem: Original problem
        problem_type: Detected problem type
        approaches_used: Reasoning approaches applied
        results: Results from each approach
        combined_result: Final combined result
        confidence: Overall confidence (0-1)
        reasoning_trace: Step-by-step reasoning trace
        processing_time: Time taken in seconds
    """
    problem: dict
    problem_type: ProblemType
    approaches_used: list[ReasoningApproach]
    results: dict[str, Any] = field(default_factory=dict)
    combined_result: Any = None
    confidence: float = 0.0
    reasoning_trace: list[str] = field(default_factory=list)
    processing_time: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "problem": self.problem,
            "problem_type": self.problem_type.value,
            "approaches_used": [a.value for a in self.approaches_used],
            "results": self.results,
            "combined_result": self.combined_result,
            "confidence": self.confidence,
            "reasoning_trace": self.reasoning_trace,
            "processing_time": self.processing_time,
        }


class HybridReasoner:
    """Hybrid reasoning engine that orchestrates multiple approaches.

    Selects and combines reasoning approaches based on problem characteristics.
    Supports configurable weights via CognitiveGenome.

    Example:
        >>> reasoner = HybridReasoner()
        >>> result = reasoner.reason({"query": "What causes X?", "type": "diagnosis"})
        >>> print(result.combined_result)
    """

    def __init__(self,
                 symbolic_reasoner: SymbolicReasoner = None,
                 knowledge_graph: KnowledgeGraph = None,
                 case_reasoner: CaseBasedReasoner = None,
                 hypothesis_engine: HypothesisEngine = None,
                 analogical_reasoner: AnalogicalReasoner = None,
                 genome=None):
        """Initialize the hybrid reasoner.

        Args:
            symbolic_reasoner: For deductive reasoning
            knowledge_graph: For graph-based inference
            case_reasoner: For experience-based reasoning
            hypothesis_engine: For hypothesis testing
            analogical_reasoner: For cross-domain transfer
            genome: Optional CognitiveGenome for configuration
        """
        # Initialize or create component reasoners
        self.symbolic = symbolic_reasoner or SymbolicReasoner()
        self.kg = knowledge_graph or KnowledgeGraph()
        self.cbr = case_reasoner or CaseBasedReasoner()
        self.hypothesis = hypothesis_engine or HypothesisEngine(self.kg, self.symbolic)
        self.analogical = analogical_reasoner or AnalogicalReasoner(self.kg, self.cbr)

        self.genome = genome
        self._lock = threading.RLock()

        # Approach weights (can be tuned by genome)
        self._approach_weights = {
            ReasoningApproach.SYMBOLIC: 0.8,
            ReasoningApproach.GRAPH: 0.7,
            ReasoningApproach.CASE_BASED: 0.7,
            ReasoningApproach.HYPOTHESIS: 0.6,
            ReasoningApproach.ANALOGICAL: 0.5,
        }

        # Problem type to approach mapping
        self._problem_approach_map = {
            ProblemType.DEDUCTION: [ReasoningApproach.SYMBOLIC, ReasoningApproach.GRAPH],
            ProblemType.INDUCTION: [ReasoningApproach.CASE_BASED, ReasoningApproach.GRAPH],
            ProblemType.ABDUCTION: [ReasoningApproach.HYPOTHESIS, ReasoningApproach.SYMBOLIC],
            ProblemType.ANALOGY: [ReasoningApproach.ANALOGICAL, ReasoningApproach.CASE_BASED],
            ProblemType.CLASSIFICATION: [ReasoningApproach.CASE_BASED, ReasoningApproach.SYMBOLIC],
            ProblemType.PLANNING: [ReasoningApproach.GRAPH, ReasoningApproach.CASE_BASED],
            ProblemType.DIAGNOSIS: [ReasoningApproach.HYPOTHESIS, ReasoningApproach.CASE_BASED],
            ProblemType.EXPLORATION: [ReasoningApproach.GRAPH, ReasoningApproach.ANALOGICAL],
        }

        # Statistics
        self._stats = {
            "total_problems": 0,
            "by_type": {},
            "by_approach": {},
            "avg_confidence": 0.0,
        }

    # === Main Reasoning Interface ===

    def reason(self, problem: dict, approaches: list[ReasoningApproach] = None,
               max_approaches: int = 3) -> HybridReasoningResult:
        """Perform hybrid reasoning on a problem.

        Args:
            problem: Problem description with keys like 'query', 'type', 'context'
            approaches: Specific approaches to use (auto-selects if None)
            max_approaches: Maximum number of approaches to combine

        Returns:
            HybridReasoningResult with combined solution
        """
        start_time = time.time()
        trace = []

        # Detect problem type
        problem_type = self._detect_problem_type(problem)
        trace.append(f"Detected problem type: {problem_type.value}")

        # Select approaches
        if approaches is None:
            approaches = self._select_approaches(problem_type, max_approaches)
        trace.append(f"Selected approaches: {[a.value for a in approaches]}")

        # Apply each approach
        results = {}
        for approach in approaches:
            result = self._apply_approach(approach, problem, problem_type)
            results[approach.value] = result
            trace.append(f"{approach.value}: {self._summarize_result(result)}")

        # Combine results
        combined = self._combine_results(results, problem_type, approaches)
        confidence = self._calculate_confidence(results, approaches)
        trace.append(f"Combined confidence: {confidence:.2f}")

        # Update statistics
        self._update_stats(problem_type, approaches, confidence)

        processing_time = time.time() - start_time

        return HybridReasoningResult(
            problem=problem,
            problem_type=problem_type,
            approaches_used=approaches,
            results=results,
            combined_result=combined,
            confidence=confidence,
            reasoning_trace=trace,
            processing_time=processing_time,
        )

    def quick_reason(self, query: str) -> Any:
        """Quick reasoning with minimal configuration.

        Args:
            query: Simple query string

        Returns:
            Best result from automatic reasoning
        """
        problem = {"query": query}
        result = self.reason(problem, max_approaches=2)
        return result.combined_result

    # === Problem Type Detection ===

    def _detect_problem_type(self, problem: dict) -> ProblemType:
        """Detect the type of reasoning problem."""
        # Check explicit type
        if "type" in problem:
            type_str = problem["type"].lower()
            for pt in ProblemType:
                if pt.value in type_str:
                    return pt

        # Infer from query keywords
        query = problem.get("query", "").lower()

        if any(w in query for w in ["why", "cause", "explain"]):
            return ProblemType.ABDUCTION
        if any(w in query for w in ["what if", "suppose", "hypothetically"]):
            return ProblemType.HYPOTHESIS
        if any(w in query for w in ["like", "similar", "analogy"]):
            return ProblemType.ANALOGY
        if any(w in query for w in ["classify", "categorize", "type of"]):
            return ProblemType.CLASSIFICATION
        if any(w in query for w in ["how to", "steps", "plan"]):
            return ProblemType.PLANNING
        if any(w in query for w in ["diagnose", "symptom", "problem with"]):
            return ProblemType.DIAGNOSIS
        if any(w in query for w in ["what", "find", "discover"]):
            return ProblemType.EXPLORATION
        if any(w in query for w in ["therefore", "conclude", "deduce"]):
            return ProblemType.DEDUCTION

        # Default to exploration
        return ProblemType.EXPLORATION

    # === Approach Selection ===

    def _select_approaches(self, problem_type: ProblemType,
                          max_approaches: int) -> list[ReasoningApproach]:
        """Select best approaches for the problem type."""
        # Get recommended approaches
        recommended = self._problem_approach_map.get(
            problem_type,
            [ReasoningApproach.CASE_BASED, ReasoningApproach.GRAPH]
        )

        # Sort by weight
        sorted_approaches = sorted(
            recommended,
            key=lambda a: self._approach_weights.get(a, 0.5),
            reverse=True
        )

        return sorted_approaches[:max_approaches]

    # === Approach Application ===

    def _apply_approach(self, approach: ReasoningApproach, problem: dict,
                       problem_type: ProblemType) -> Any:
        """Apply a specific reasoning approach."""
        query = problem.get("query", "")
        context = problem.get("context", {})

        try:
            if approach == ReasoningApproach.SYMBOLIC:
                return self._apply_symbolic(query, context)
            elif approach == ReasoningApproach.GRAPH:
                return self._apply_graph(query, context)
            elif approach == ReasoningApproach.CASE_BASED:
                return self._apply_case_based(query, context)
            elif approach == ReasoningApproach.HYPOTHESIS:
                return self._apply_hypothesis(query, context)
            elif approach == ReasoningApproach.ANALOGICAL:
                return self._apply_analogical(query, context)
            else:
                return {"error": f"Unknown approach: {approach}"}
        except Exception as e:
            logger.warning(f"Approach {approach.value} failed: {e}")
            return {"error": str(e)}

    def _apply_symbolic(self, query: str, context: dict) -> dict:
        """Apply symbolic reasoning."""
        # Try forward chaining
        forward_result = self.symbolic.forward_chain()

        # Extract relevant facts
        relevant_facts = []
        query_terms = query.lower().split()
        for fact in self.symbolic.facts.values():
            fact_str = str(fact).lower()
            if any(term in fact_str for term in query_terms if len(term) > 2):
                relevant_facts.append(fact.to_dict())

        # Try backward chaining if goal specified
        backward_result = None
        goal = context.get("goal")
        if goal:
            backward_result = self.symbolic.backward_chain(goal)

        return {
            "method": "symbolic",
            "forward_derived": forward_result.derived if forward_result else [],
            "relevant_facts": relevant_facts,
            "backward_result": backward_result.success if backward_result else None,
        }

    def _apply_graph(self, query: str, context: dict) -> dict:
        """Apply knowledge graph reasoning."""
        # Find relevant nodes
        query_terms = query.lower().split()
        relevant_nodes = []

        for node in self.kg.query_nodes():
            if any(term in node.label.lower() for term in query_terms if len(term) > 2):
                relevant_nodes.append(node)

        # Find paths between relevant nodes
        paths = []
        if len(relevant_nodes) >= 2:
            for i, source in enumerate(relevant_nodes[:3]):
                for target in relevant_nodes[i+1:3]:
                    path = self.kg.find_path(source.id, target.id)
                    if path:
                        paths.append({
                            "from": source.label,
                            "to": target.label,
                            "path": path.nodes,
                        })

        # Get subgraph around first relevant node
        subgraph = None
        if relevant_nodes:
            subgraph = self.kg.get_subgraph(relevant_nodes[0].id, radius=2)

        return {
            "method": "graph",
            "relevant_nodes": [n.label for n in relevant_nodes[:5]],
            "paths": paths[:3],
            "subgraph_size": len(subgraph.nodes) if subgraph else 0,
        }

    def _apply_case_based(self, query: str, context: dict) -> dict:
        """Apply case-based reasoning."""
        # Create problem description
        problem_features = {"query": query, **context}

        # Find similar cases
        result = self.cbr.reason(problem_features)

        return {
            "method": "case_based",
            "source_case": result.source_case.id if result and result.source_case else None,
            "proposed_solution": result.proposed_solution if result else None,
            "confidence": result.confidence if result else 0.0,
        }

    def _apply_hypothesis(self, query: str, context: dict) -> dict:
        """Apply hypothesis-driven reasoning."""
        # Generate hypotheses from the query
        hypotheses = self.hypothesis.generate_hypotheses(query, max_hypotheses=3)

        # Test each hypothesis
        tested = []
        for hyp in hypotheses:
            test_result = self.hypothesis.test_hypothesis(hyp.id)
            tested.append({
                "statement": hyp.statement,
                "confidence": hyp.confidence,
                "status": hyp.status,
                "supports": test_result.supports if test_result else None,
            })

        # Get best hypothesis
        best = self.hypothesis.get_best_hypothesis() if hypotheses else None

        return {
            "method": "hypothesis",
            "hypotheses": tested,
            "best_hypothesis": best.statement if best else None,
            "best_confidence": best.confidence if best else 0.0,
        }

    def _apply_analogical(self, query: str, context: dict) -> dict:
        """Apply analogical reasoning."""
        source_domain = context.get("source_domain")
        target_domain = context.get("target_domain")

        analogy = None
        if source_domain and target_domain:
            analogy = self.analogical.find_analogy(source_domain, target_domain)

        # Try to solve by analogy
        solution = None
        if analogy:
            solution = self.analogical.solve_by_analogy(
                target_domain,
                {"query": query, "goal": context.get("goal", "")},
                source_domain
            )

        return {
            "method": "analogical",
            "analogy_found": analogy is not None,
            "similarity": analogy.overall_similarity if analogy else 0.0,
            "inferences": analogy.inferences[:3] if analogy else [],
            "solution": solution,
        }

    # === Result Combination ===

    def _combine_results(self, results: dict, problem_type: ProblemType,
                        approaches: list[ReasoningApproach]) -> Any:
        """Combine results from multiple approaches."""
        combined = {
            "conclusions": [],
            "evidence": [],
            "suggestions": [],
        }

        for approach, result in results.items():
            if isinstance(result, dict) and "error" not in result:
                # Extract conclusions
                if result.get("relevant_facts"):
                    combined["evidence"].extend(
                        f.get("statement", str(f)) if isinstance(f, dict) else str(f)
                        for f in result["relevant_facts"][:3]
                    )
                if result.get("best_hypothesis"):
                    combined["conclusions"].append(result["best_hypothesis"])
                if result.get("adapted_solution"):
                    combined["suggestions"].append(result["adapted_solution"])
                if result.get("inferences"):
                    combined["conclusions"].extend(result["inferences"][:2])
                if result.get("paths"):
                    for path in result["paths"]:
                        combined["evidence"].append(
                            f"{path['from']} -> {path['to']}"
                        )

        # Deduplicate and limit
        combined["conclusions"] = list(set(combined["conclusions"]))[:5]
        combined["evidence"] = list(set(combined["evidence"]))[:5]
        combined["suggestions"] = combined["suggestions"][:3]

        return combined

    def _calculate_confidence(self, results: dict,
                             approaches: list[ReasoningApproach]) -> float:
        """Calculate overall confidence from approach results."""
        confidences = []

        for approach in approaches:
            result = results.get(approach.value, {})
            weight = self._approach_weights.get(approach, 0.5)

            if isinstance(result, dict):
                # Extract confidence from result
                if "confidence" in result:
                    confidences.append(result["confidence"] * weight)
                elif "best_confidence" in result:
                    confidences.append(result["best_confidence"] * weight)
                elif "similarity" in result:
                    confidences.append(result["similarity"] * weight)
                elif "error" not in result:
                    # Some result but no explicit confidence
                    confidences.append(0.5 * weight)

        if not confidences:
            return 0.0

        # Weighted average
        return sum(confidences) / len(confidences)

    def _summarize_result(self, result: Any) -> str:
        """Create a brief summary of a result."""
        if isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"
            method = result.get("method", "unknown")
            if "confidence" in result:
                return f"{method} (conf={result['confidence']:.2f})"
            if "best_confidence" in result:
                return f"{method} (conf={result['best_confidence']:.2f})"
            return f"{method} (completed)"
        return str(result)[:50]

    # === Statistics ===

    def _update_stats(self, problem_type: ProblemType,
                     approaches: list[ReasoningApproach],
                     confidence: float) -> None:
        """Update internal statistics."""
        with self._lock:
            self._stats["total_problems"] += 1

            # By type
            type_key = problem_type.value
            self._stats["by_type"][type_key] = \
                self._stats["by_type"].get(type_key, 0) + 1

            # By approach
            for approach in approaches:
                approach_key = approach.value
                self._stats["by_approach"][approach_key] = \
                    self._stats["by_approach"].get(approach_key, 0) + 1

            # Running average confidence
            n = self._stats["total_problems"]
            old_avg = self._stats["avg_confidence"]
            self._stats["avg_confidence"] = old_avg + (confidence - old_avg) / n

    def get_stats(self) -> dict:
        """Get reasoning statistics."""
        return {
            **self._stats,
            "component_stats": {
                "symbolic_facts": len(self.symbolic.facts),
                "symbolic_rules": len(self.symbolic.rules),
                "kg_nodes": len(self.kg.nodes),
                "kg_edges": len(self.kg.edges),
                "cbr_cases": len(self.cbr.cases),
                "hypotheses": len(self.hypothesis.hypotheses),
                "analogical_domains": len(self.analogical.domains),
            }
        }

    # === Component Access ===

    def add_fact(self, fact: Fact) -> None:
        """Add a fact to symbolic reasoner."""
        self.symbolic.add_fact(fact)

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to symbolic reasoner."""
        self.symbolic.add_rule(rule)

    def add_node(self, node: Node) -> None:
        """Add a node to knowledge graph."""
        self.kg.add_node(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to knowledge graph."""
        self.kg.add_edge(edge)

    def add_case(self, case: Case) -> None:
        """Add a case to case-based reasoner."""
        self.cbr.store_case(case)

    def add_concept(self, concept: Concept) -> None:
        """Add a concept to analogical reasoner."""
        self.analogical.add_concept(concept)

    # === Configuration ===

    def set_approach_weight(self, approach: ReasoningApproach, weight: float) -> None:
        """Set weight for an approach."""
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        with self._lock:
            self._approach_weights[approach] = weight

    def get_approach_weights(self) -> dict[ReasoningApproach, float]:
        """Get current approach weights."""
        return dict(self._approach_weights)

    def to_dict(self) -> dict:
        """Serialize reasoner state."""
        return {
            "approach_weights": {k.value: v for k, v in self._approach_weights.items()},
            "stats": self.get_stats(),
        }

    def clear(self) -> None:
        """Clear all component data."""
        with self._lock:
            self.symbolic.clear_facts()
            self.symbolic.rules.clear()
            self.kg.clear()
            self.cbr.clear()
            self.hypothesis.clear()
            self.analogical.clear()
            self._stats = {
                "total_problems": 0,
                "by_type": {},
                "by_approach": {},
                "avg_confidence": 0.0,
            }
