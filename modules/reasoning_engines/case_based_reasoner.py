"""Case-based reasoning using the 4R cycle.

This module provides experience-based reasoning:
- Retrieve: Find similar past cases
- Reuse: Adapt past solutions
- Revise: Incorporate feedback
- Retain: Store successful solutions

The approach learns from experience rather than rules.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import threading
import time
import uuid
import logging
import math

logger = logging.getLogger(__name__)


@dataclass
class Case:
    """A case for case-based reasoning.

    Attributes:
        id: Unique identifier
        problem: Problem description as key-value features
        solution: Applied solution
        outcome: Result of applying the solution
        success: Whether the solution was successful
        timestamp: When the case was created
        tags: Categorization tags
        use_count: Number of times this case was retrieved
    """
    id: str
    problem: dict[str, Any]
    solution: dict[str, Any]
    outcome: Optional[dict[str, Any]] = None
    success: Optional[bool] = None
    timestamp: float = field(default_factory=lambda: time.time())
    tags: list[str] = field(default_factory=list)
    use_count: int = 0

    def __post_init__(self):
        """Validate case fields."""
        if not self.id:
            raise ValueError("Case id cannot be empty")
        if not self.problem:
            raise ValueError("Case problem cannot be empty")
        if not self.solution:
            raise ValueError("Case solution cannot be empty")

    def to_dict(self) -> dict:
        """Convert case to dictionary."""
        return {
            "id": self.id,
            "problem": self.problem,
            "solution": self.solution,
            "outcome": self.outcome,
            "success": self.success,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "use_count": self.use_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Case":
        """Create case from dictionary."""
        return cls(
            id=data["id"],
            problem=data["problem"],
            solution=data["solution"],
            outcome=data.get("outcome"),
            success=data.get("success"),
            timestamp=data.get("timestamp", time.time()),
            tags=data.get("tags", []),
            use_count=data.get("use_count", 0),
        )


@dataclass
class CaseMatch:
    """A matched case with similarity score.

    Attributes:
        case: The matched case
        similarity: Overall similarity score (0-1)
        matching_features: Features that matched
        differing_features: Features that differed
        adaptation_needed: Whether the solution needs adaptation
    """
    case: Case
    similarity: float
    matching_features: list[str] = field(default_factory=list)
    differing_features: list[str] = field(default_factory=list)
    adaptation_needed: bool = False

    def __post_init__(self):
        """Validate match fields."""
        if not 0 <= self.similarity <= 1:
            raise ValueError(f"similarity must be 0-1, got {self.similarity}")


@dataclass
class CaseReasoningResult:
    """Result from case-based reasoning.

    Attributes:
        success: Whether a suitable case was found
        proposed_solution: The proposed solution
        confidence: Confidence in the solution
        source_case: The case used as basis
        adaptations: Changes made to adapt the solution
        reasoning_chain: Steps taken to reach the solution
    """
    success: bool
    proposed_solution: Optional[dict[str, Any]] = None
    confidence: float = 0.0
    source_case: Optional[Case] = None
    adaptations: list[str] = field(default_factory=list)
    reasoning_chain: list[str] = field(default_factory=list)


class CaseBasedReasoner:
    """Case-based reasoning using the 4R cycle.

    The 4R Cycle:
    1. Retrieve - Find similar past cases
    2. Reuse - Adapt past solutions to new problem
    3. Revise - Incorporate feedback to improve
    4. Retain - Store successful new cases

    Features:
    - Multiple similarity metrics
    - Feature weight learning
    - Solution adaptation
    - Success-based learning
    - Thread-safe operations

    Example:
        >>> cbr = CaseBasedReasoner()
        >>> case = Case(
        ...     id="c1",
        ...     problem={"type": "bug", "language": "python"},
        ...     solution={"action": "add_try_except"},
        ... )
        >>> cbr.store_case(case)
        >>> matches = cbr.retrieve({"type": "bug", "language": "python"})
        >>> # matches[0] will be the stored case
    """

    def __init__(self, genome=None):
        """Initialize the case-based reasoner.

        Args:
            genome: Optional CognitiveGenome for configurable parameters
        """
        self.cases: dict[str, Case] = {}
        self.feature_weights: dict[str, float] = {}
        self.genome = genome
        self._lock = threading.RLock()

        # Default weights for common features
        self._default_weight = 1.0
        self._success_bonus = 1.5  # Bonus weight for successful cases

    # === Case Management ===

    def store_case(self, case: Case) -> bool:
        """Store a case in the case base.

        Args:
            case: The case to store

        Returns:
            True if stored, False if case with same ID exists
        """
        with self._lock:
            if case.id in self.cases:
                return False
            self.cases[case.id] = case
            logger.debug(f"Stored case: {case.id}")
            return True

    def get_case(self, case_id: str) -> Optional[Case]:
        """Get a case by ID.

        Args:
            case_id: ID of the case

        Returns:
            The case or None if not found
        """
        return self.cases.get(case_id)

    def remove_case(self, case_id: str) -> bool:
        """Remove a case by ID.

        Args:
            case_id: ID of the case to remove

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if case_id in self.cases:
                del self.cases[case_id]
                return True
            return False

    def query_cases(self, tags: list[str] = None,
                    success_only: bool = False) -> list[Case]:
        """Query cases by criteria.

        Args:
            tags: Filter by tags (any match)
            success_only: Only return successful cases

        Returns:
            List of matching cases
        """
        results = []
        for case in self.cases.values():
            if success_only and not case.success:
                continue
            if tags:
                if not any(t in case.tags for t in tags):
                    continue
            results.append(case)
        return results

    # === 4R Cycle ===

    def retrieve(self, problem: dict[str, Any], k: int = 5,
                 min_similarity: float = 0.0) -> list[CaseMatch]:
        """Retrieve the most similar cases (R1).

        Args:
            problem: The new problem to find cases for
            k: Maximum number of cases to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of CaseMatch objects sorted by similarity
        """
        if not problem:
            return []

        matches = []

        for case in self.cases.values():
            similarity, matching, differing = self._compute_similarity(
                problem, case.problem
            )

            # Apply success bonus
            if case.success:
                similarity = min(1.0, similarity * self._success_bonus)

            if similarity >= min_similarity:
                matches.append(CaseMatch(
                    case=case,
                    similarity=similarity,
                    matching_features=matching,
                    differing_features=differing,
                    adaptation_needed=len(differing) > 0,
                ))

                # Increment use count
                with self._lock:
                    case.use_count += 1

        # Sort by similarity (highest first)
        matches.sort(key=lambda m: m.similarity, reverse=True)

        return matches[:k]

    def reuse(self, problem: dict[str, Any],
              matched_case: CaseMatch) -> dict[str, Any]:
        """Adapt a matched case's solution to the new problem (R2).

        Args:
            problem: The new problem
            matched_case: The matched case to adapt from

        Returns:
            Adapted solution
        """
        if not matched_case:
            return {}

        source_solution = matched_case.case.solution.copy()
        adaptations = []

        # For each differing feature, try to adapt the solution
        for feature in matched_case.differing_features:
            if feature in problem:
                new_value = problem[feature]
                old_value = matched_case.case.problem.get(feature)

                # Simple substitution adaptation
                for key, value in source_solution.items():
                    if value == old_value:
                        source_solution[key] = new_value
                        adaptations.append(f"Adapted {key}: {old_value} -> {new_value}")

        logger.debug(f"Reuse adaptations: {adaptations}")
        return source_solution

    def revise(self, proposed_solution: dict[str, Any],
               feedback: dict[str, Any]) -> dict[str, Any]:
        """Revise a solution based on feedback (R3).

        Args:
            proposed_solution: The initial solution
            feedback: Feedback about what to change

        Returns:
            Revised solution
        """
        revised = proposed_solution.copy()

        # Apply feedback modifications
        if "modifications" in feedback:
            for key, value in feedback["modifications"].items():
                revised[key] = value

        # Apply removals
        if "remove" in feedback:
            for key in feedback["remove"]:
                revised.pop(key, None)

        # Apply additions
        if "add" in feedback:
            revised.update(feedback["add"])

        return revised

    def retain(self, problem: dict[str, Any], solution: dict[str, Any],
               outcome: dict[str, Any] = None,
               success: bool = None, tags: list[str] = None) -> Case:
        """Store a new case learned from experience (R4).

        Args:
            problem: The problem description
            solution: The solution that was applied
            outcome: The result of applying the solution
            success: Whether the solution was successful
            tags: Categorization tags

        Returns:
            The newly created and stored case
        """
        case_id = str(uuid.uuid4())[:8]

        case = Case(
            id=case_id,
            problem=problem,
            solution=solution,
            outcome=outcome,
            success=success,
            tags=tags or [],
        )

        self.store_case(case)
        logger.debug(f"Retained new case: {case_id}")

        # Update feature weights if success information is available
        if success is not None:
            self._update_weights_from_case(case)

        return case

    # === Similarity Computation ===

    def _compute_similarity(self, problem1: dict, problem2: dict
                            ) -> tuple[float, list[str], list[str]]:
        """Compute similarity between two problems.

        Args:
            problem1: First problem
            problem2: Second problem

        Returns:
            Tuple of (similarity_score, matching_features, differing_features)
        """
        all_features = set(problem1.keys()) | set(problem2.keys())
        if not all_features:
            return 0.0, [], []

        matching = []
        differing = []
        weighted_sum = 0.0
        total_weight = 0.0

        for feature in all_features:
            weight = self.feature_weights.get(feature, self._default_weight)
            total_weight += weight

            val1 = problem1.get(feature)
            val2 = problem2.get(feature)

            if val1 is None or val2 is None:
                differing.append(feature)
                continue

            feature_sim = self._feature_similarity(val1, val2)
            weighted_sum += feature_sim * weight

            if feature_sim >= 0.8:
                matching.append(feature)
            else:
                differing.append(feature)

        similarity = weighted_sum / total_weight if total_weight > 0 else 0.0
        return similarity, matching, differing

    def _feature_similarity(self, val1: Any, val2: Any) -> float:
        """Compute similarity between two feature values.

        Args:
            val1: First value
            val2: Second value

        Returns:
            Similarity score (0-1)
        """
        # Exact match
        if val1 == val2:
            return 1.0

        # Type mismatch
        if type(val1) != type(val2):
            return 0.0

        # String similarity (simple containment)
        if isinstance(val1, str):
            val1_lower = val1.lower()
            val2_lower = val2.lower()
            if val1_lower in val2_lower or val2_lower in val1_lower:
                return 0.7
            # Jaccard similarity on words
            words1 = set(val1_lower.split())
            words2 = set(val2_lower.split())
            if words1 and words2:
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                return intersection / union
            return 0.0

        # Numeric similarity
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            # Normalized difference
            max_val = max(abs(val1), abs(val2))
            if max_val == 0:
                return 1.0
            diff = abs(val1 - val2) / max_val
            return max(0.0, 1.0 - diff)

        # List similarity (Jaccard)
        if isinstance(val1, list):
            set1 = set(str(x) for x in val1)
            set2 = set(str(x) for x in val2)
            if not set1 and not set2:
                return 1.0
            if not set1 or not set2:
                return 0.0
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union

        # Dict similarity (recursive)
        if isinstance(val1, dict):
            sim, _, _ = self._compute_similarity(val1, val2)
            return sim

        # Default: no similarity
        return 0.0

    # === Learning ===

    def _update_weights_from_case(self, case: Case) -> None:
        """Update feature weights based on a case's success.

        Args:
            case: Case to learn from
        """
        if case.success is None:
            return

        with self._lock:
            for feature in case.problem.keys():
                current_weight = self.feature_weights.get(feature, self._default_weight)

                if case.success:
                    # Increase weight for features in successful cases
                    self.feature_weights[feature] = min(
                        5.0, current_weight * 1.1
                    )
                else:
                    # Decrease weight for features in failed cases
                    self.feature_weights[feature] = max(
                        0.2, current_weight * 0.95
                    )

    def update_feature_weights(self, successful_cases: list[Case],
                                failed_cases: list[Case] = None) -> None:
        """Bulk update feature weights from case outcomes.

        Args:
            successful_cases: Cases that succeeded
            failed_cases: Cases that failed
        """
        for case in successful_cases:
            case.success = True
            self._update_weights_from_case(case)

        for case in (failed_cases or []):
            case.success = False
            self._update_weights_from_case(case)

    def update_case_outcome(self, case_id: str, outcome: dict,
                            success: bool) -> bool:
        """Update a case with its outcome.

        Args:
            case_id: ID of the case to update
            outcome: The outcome of applying the solution
            success: Whether the solution was successful

        Returns:
            True if updated, False if case not found
        """
        with self._lock:
            case = self.cases.get(case_id)
            if not case:
                return False

            case.outcome = outcome
            case.success = success
            self._update_weights_from_case(case)
            return True

    # === Main Reasoning Interface ===

    def reason(self, problem: dict[str, Any],
               min_similarity: float = 0.3) -> CaseReasoningResult:
        """Perform case-based reasoning to solve a problem.

        This implements the full 4R cycle:
        1. Retrieve similar cases
        2. Reuse the best match's solution
        3. Return the adapted solution for revision/evaluation

        Args:
            problem: The problem to solve
            min_similarity: Minimum similarity for case retrieval

        Returns:
            CaseReasoningResult with the proposed solution
        """
        result = CaseReasoningResult(success=False)
        result.reasoning_chain.append(f"Starting case-based reasoning for problem")

        # R1: Retrieve
        matches = self.retrieve(problem, k=5, min_similarity=min_similarity)
        result.reasoning_chain.append(f"Retrieved {len(matches)} similar cases")

        if not matches:
            result.reasoning_chain.append("No similar cases found")
            return result

        # Select best match
        best_match = matches[0]
        result.source_case = best_match.case
        result.reasoning_chain.append(
            f"Best match: case {best_match.case.id} "
            f"(similarity: {best_match.similarity:.2f})"
        )

        # R2: Reuse
        adapted_solution = self.reuse(problem, best_match)
        result.proposed_solution = adapted_solution
        result.reasoning_chain.append(
            f"Adapted solution with {len(best_match.differing_features)} modifications"
        )

        # Record adaptations
        if best_match.adaptation_needed:
            result.adaptations = [
                f"Adapted for feature: {f}" for f in best_match.differing_features
            ]

        # Set confidence based on similarity and success history
        base_confidence = best_match.similarity
        if best_match.case.success:
            base_confidence = min(1.0, base_confidence * 1.2)
        result.confidence = base_confidence
        result.success = True

        result.reasoning_chain.append(
            f"Proposed solution with confidence: {result.confidence:.2f}"
        )

        return result

    # === Statistics ===

    def get_stats(self) -> dict:
        """Get statistics about the case base.

        Returns:
            Dictionary with case base statistics
        """
        success_count = sum(1 for c in self.cases.values() if c.success)
        failure_count = sum(1 for c in self.cases.values() if c.success is False)
        pending_count = sum(1 for c in self.cases.values() if c.success is None)

        return {
            "total_cases": len(self.cases),
            "successful_cases": success_count,
            "failed_cases": failure_count,
            "pending_cases": pending_count,
            "feature_weights": dict(self.feature_weights),
            "most_used_cases": sorted(
                [(c.id, c.use_count) for c in self.cases.values()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
        }

    def to_dict(self) -> dict:
        """Serialize the case base to dictionary."""
        return {
            "cases": [c.to_dict() for c in self.cases.values()],
            "feature_weights": dict(self.feature_weights),
            "stats": self.get_stats(),
        }

    @classmethod
    def from_dict(cls, data: dict, genome=None) -> "CaseBasedReasoner":
        """Create case-based reasoner from dictionary."""
        cbr = cls(genome)

        for case_data in data.get("cases", []):
            cbr.store_case(Case.from_dict(case_data))

        cbr.feature_weights = dict(data.get("feature_weights", {}))
        return cbr

    def clear(self) -> None:
        """Clear all cases and reset weights."""
        with self._lock:
            self.cases.clear()
            self.feature_weights.clear()
