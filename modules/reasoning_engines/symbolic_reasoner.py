"""Symbolic reasoning engine with forward and backward chaining.

This module provides rule-based logical reasoning capabilities:
- Fact storage with confidence tracking
- Rule-based inference
- Forward chaining (data-driven reasoning)
- Backward chaining (goal-driven reasoning)
- Conflict resolution via priority
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union
from enum import Enum
import threading
import time
import uuid
import logging

logger = logging.getLogger(__name__)


class FactType(Enum):
    """Types of facts in the knowledge base."""
    ASSERTION = "assertion"      # X is Y
    RELATION = "relation"        # X relates to Y
    PROPERTY = "property"        # X has property P
    NEGATION = "negation"        # X is not Y


@dataclass
class Fact:
    """A fact in the knowledge base.

    Attributes:
        subject: The subject of the fact
        predicate: The relationship or property
        object: The value or related entity
        fact_type: Type of fact (assertion, relation, property, negation)
        confidence: Confidence level 0-1
        source: Where this fact came from
        timestamp: When this fact was created
        id: Unique identifier (auto-generated if not provided)
    """
    subject: str
    predicate: str
    object: Any
    fact_type: FactType = FactType.ASSERTION
    confidence: float = 1.0
    source: str = "system"
    timestamp: float = field(default_factory=lambda: time.time())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __post_init__(self):
        """Validate fact fields."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be 0-1, got {self.confidence}")
        if not self.subject:
            raise ValueError("subject cannot be empty")
        if not self.predicate:
            raise ValueError("predicate cannot be empty")

    def matches(self, subject: str = None, predicate: str = None,
                object: Any = None) -> bool:
        """Check if this fact matches the given criteria."""
        if subject is not None and self.subject != subject:
            return False
        if predicate is not None and self.predicate != predicate:
            return False
        if object is not None and self.object != object:
            return False
        return True

    def to_dict(self) -> dict:
        """Convert fact to dictionary."""
        return {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "fact_type": self.fact_type.value,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Fact":
        """Create fact from dictionary."""
        return cls(
            subject=data["subject"],
            predicate=data["predicate"],
            object=data["object"],
            fact_type=FactType(data.get("fact_type", "assertion")),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "system"),
            timestamp=data.get("timestamp", time.time()),
            id=data.get("id", str(uuid.uuid4())[:8]),
        )

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.subject} {self.predicate} {self.object}"


@dataclass
class Rule:
    """An inference rule: if conditions then conclusion.

    Attributes:
        name: Unique name for the rule
        conditions: Functions that check if rule applies
        conclusion_template: Template for creating new facts
        priority: Higher priority rules fire first
        enabled: Whether the rule is active
        description: Human-readable description
    """
    name: str
    conditions: list[Callable[[dict[str, Fact]], bool]]
    conclusion_template: dict[str, Any]
    priority: int = 0
    enabled: bool = True
    description: str = ""

    def __post_init__(self):
        """Validate rule fields."""
        if not self.name:
            raise ValueError("Rule name cannot be empty")
        if not self.conditions:
            raise ValueError("Rule must have at least one condition")
        if not self.conclusion_template:
            raise ValueError("Rule must have a conclusion template")

    def evaluate(self, facts: dict[str, Fact]) -> bool:
        """Check if all conditions are satisfied."""
        try:
            return all(cond(facts) for cond in self.conditions)
        except Exception as e:
            logger.warning(f"Rule {self.name} condition evaluation failed: {e}")
            return False

    def apply(self, facts: dict[str, Fact]) -> Optional[Fact]:
        """Apply the rule to produce a new fact."""
        if not self.evaluate(facts):
            return None

        try:
            # Build conclusion from template
            conclusion = {}
            for key, value in self.conclusion_template.items():
                if callable(value):
                    conclusion[key] = value(facts)
                else:
                    conclusion[key] = value

            return Fact(
                subject=conclusion.get("subject", "unknown"),
                predicate=conclusion.get("predicate", "unknown"),
                object=conclusion.get("object", None),
                fact_type=conclusion.get("fact_type", FactType.ASSERTION),
                confidence=conclusion.get("confidence", 0.9),
                source=f"rule:{self.name}",
            )
        except Exception as e:
            logger.warning(f"Rule {self.name} application failed: {e}")
            return None


@dataclass
class ReasoningResult:
    """Result from a reasoning operation.

    Attributes:
        success: Whether reasoning succeeded
        conclusion: The main conclusion
        confidence: Confidence in the conclusion
        facts_used: Facts that contributed to conclusion
        rules_fired: Rules that were applied
        reasoning_chain: Step-by-step reasoning path
        new_facts: New facts derived during reasoning
    """
    success: bool
    conclusion: Optional[str] = None
    confidence: float = 0.0
    facts_used: list[Fact] = field(default_factory=list)
    rules_fired: list[str] = field(default_factory=list)
    reasoning_chain: list[str] = field(default_factory=list)
    new_facts: list[Fact] = field(default_factory=list)


class SymbolicReasoner:
    """Symbolic reasoning engine using forward and backward chaining.

    Features:
    - Fact storage with confidence tracking
    - Rule-based inference
    - Forward chaining (data-driven)
    - Backward chaining (goal-driven)
    - Conflict resolution via priority
    - Thread-safe operations

    Example:
        >>> reasoner = SymbolicReasoner()
        >>> reasoner.add_fact(Fact("Socrates", "is_a", "human"))
        >>> reasoner.add_rule(Rule(
        ...     name="mortality",
        ...     conditions=[lambda f: any(f[k].predicate == "is_a" and f[k].object == "human" for k in f)],
        ...     conclusion_template={
        ...         "subject": lambda f: next(f[k].subject for k in f if f[k].object == "human"),
        ...         "predicate": "is",
        ...         "object": "mortal"
        ...     }
        ... ))
        >>> result = reasoner.forward_chain()
        >>> # Now we have: Socrates is mortal
    """

    def __init__(self, genome=None):
        """Initialize the symbolic reasoner.

        Args:
            genome: Optional CognitiveGenome for configurable parameters
        """
        self.facts: dict[str, Fact] = {}
        self.rules: list[Rule] = []
        self.genome = genome
        self._lock = threading.RLock()
        self._inference_count = 0

    # === Fact Management ===

    def add_fact(self, fact: Fact) -> bool:
        """Add a fact to the knowledge base.

        Args:
            fact: The fact to add

        Returns:
            True if added, False if duplicate exists
        """
        with self._lock:
            # Check for duplicates (same subject, predicate, object)
            for existing in self.facts.values():
                if (existing.subject == fact.subject and
                    existing.predicate == fact.predicate and
                    existing.object == fact.object):
                    # Update confidence if new fact has higher confidence
                    if fact.confidence > existing.confidence:
                        existing.confidence = fact.confidence
                        existing.source = fact.source
                        existing.timestamp = fact.timestamp
                    return False

            self.facts[fact.id] = fact
            logger.debug(f"Added fact: {fact}")
            return True

    def remove_fact(self, fact_id: str) -> bool:
        """Remove a fact by ID.

        Args:
            fact_id: ID of the fact to remove

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if fact_id in self.facts:
                del self.facts[fact_id]
                return True
            return False

    def get_fact(self, fact_id: str) -> Optional[Fact]:
        """Get a fact by ID.

        Args:
            fact_id: ID of the fact

        Returns:
            The fact or None if not found
        """
        return self.facts.get(fact_id)

    def query_facts(self, subject: str = None, predicate: str = None,
                    object: Any = None, min_confidence: float = 0.0) -> list[Fact]:
        """Query facts matching criteria.

        Args:
            subject: Filter by subject
            predicate: Filter by predicate
            object: Filter by object
            min_confidence: Minimum confidence threshold

        Returns:
            List of matching facts
        """
        results = []
        for fact in self.facts.values():
            if fact.confidence < min_confidence:
                continue
            if fact.matches(subject, predicate, object):
                results.append(fact)
        return results

    def clear_facts(self) -> int:
        """Clear all facts.

        Returns:
            Number of facts cleared
        """
        with self._lock:
            count = len(self.facts)
            self.facts.clear()
            return count

    # === Rule Management ===

    def add_rule(self, rule: Rule) -> None:
        """Add an inference rule.

        Args:
            rule: The rule to add
        """
        with self._lock:
            # Check for duplicate names
            for existing in self.rules:
                if existing.name == rule.name:
                    raise ValueError(f"Rule with name '{rule.name}' already exists")
            self.rules.append(rule)
            # Keep rules sorted by priority (highest first)
            self.rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name.

        Args:
            name: Name of the rule to remove

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            for i, rule in enumerate(self.rules):
                if rule.name == name:
                    del self.rules[i]
                    return True
            return False

    def get_rule(self, name: str) -> Optional[Rule]:
        """Get a rule by name.

        Args:
            name: Name of the rule

        Returns:
            The rule or None if not found
        """
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None

    def enable_rule(self, name: str, enabled: bool = True) -> bool:
        """Enable or disable a rule.

        Args:
            name: Name of the rule
            enabled: Whether to enable (True) or disable (False)

        Returns:
            True if rule was found and updated
        """
        rule = self.get_rule(name)
        if rule:
            rule.enabled = enabled
            return True
        return False

    # === Forward Chaining ===

    def forward_chain(self, max_iterations: int = 100) -> list[Fact]:
        """Apply forward chaining to derive new facts.

        Forward chaining is data-driven: it starts with known facts
        and applies rules to derive new facts until no more can be derived.

        Args:
            max_iterations: Maximum number of inference iterations

        Returns:
            List of newly derived facts
        """
        if self.genome:
            max_depth = self.genome.get("reasoning_max_depth", max_iterations)
            max_iterations = min(max_iterations, max_depth)

        new_facts = []

        with self._lock:
            for iteration in range(max_iterations):
                facts_added = False

                for rule in self.rules:
                    if not rule.enabled:
                        continue

                    # Try to apply rule
                    new_fact = rule.apply(self.facts)
                    if new_fact:
                        if self.add_fact(new_fact):
                            new_facts.append(new_fact)
                            facts_added = True
                            self._inference_count += 1
                            logger.debug(f"Forward chain derived: {new_fact}")

                # Stop if no new facts were derived
                if not facts_added:
                    break

        return new_facts

    # === Backward Chaining ===

    def backward_chain(self, goal: Fact, max_depth: int = 10) -> tuple[bool, list[Fact]]:
        """Apply backward chaining to prove a goal.

        Backward chaining is goal-driven: it starts with a goal
        and works backward to find supporting facts.

        Args:
            goal: The fact we want to prove
            max_depth: Maximum recursion depth

        Returns:
            Tuple of (success, proof_path) where proof_path is the facts used
        """
        if self.genome:
            configured_depth = self.genome.get("reasoning_max_depth", max_depth)
            max_depth = min(max_depth, configured_depth)

        visited = set()
        proof_path = []

        success = self._backward_chain_recursive(goal, max_depth, visited, proof_path)
        return success, proof_path

    def _backward_chain_recursive(self, goal: Fact, depth: int,
                                   visited: set, proof_path: list[Fact]) -> bool:
        """Recursive helper for backward chaining."""
        if depth <= 0:
            return False

        # Create a hashable key for the goal
        goal_key = (goal.subject, goal.predicate, str(goal.object))
        if goal_key in visited:
            return False
        visited.add(goal_key)

        # Check if goal is already in facts
        for fact in self.facts.values():
            if fact.matches(goal.subject, goal.predicate, goal.object):
                proof_path.append(fact)
                return True

        # Try to find rules that can derive the goal
        for rule in self.rules:
            if not rule.enabled:
                continue

            # Check if rule's conclusion matches goal
            template = rule.conclusion_template

            # Simple template matching (can be extended)
            if callable(template.get("predicate")):
                continue  # Skip dynamic predicates for now

            if template.get("predicate") == goal.predicate:
                # Try to prove all conditions
                # This is simplified - full implementation would recursively prove conditions
                if rule.evaluate(self.facts):
                    new_fact = rule.apply(self.facts)
                    if new_fact and new_fact.matches(goal.subject, goal.predicate, goal.object):
                        self.add_fact(new_fact)
                        proof_path.append(new_fact)
                        self._inference_count += 1
                        return True

        return False

    # === Main Reasoning Interface ===

    def reason(self, query: str, mode: str = "forward",
               context: dict = None) -> ReasoningResult:
        """Perform reasoning to answer a query.

        Args:
            query: The question or goal to reason about
            mode: Reasoning mode - "forward", "backward", or "hybrid"
            context: Additional context for reasoning

        Returns:
            ReasoningResult with conclusion and supporting evidence
        """
        result = ReasoningResult(success=False)
        result.reasoning_chain.append(f"Starting {mode} reasoning for: {query}")

        try:
            if mode == "forward":
                new_facts = self.forward_chain()
                result.new_facts = new_facts
                result.rules_fired = [f.source for f in new_facts if f.source.startswith("rule:")]

                # Look for facts that might answer the query
                relevant = self._find_relevant_facts(query)
                if relevant:
                    result.success = True
                    result.conclusion = str(relevant[0])
                    result.confidence = relevant[0].confidence
                    result.facts_used = relevant
                    result.reasoning_chain.append(f"Found relevant fact: {relevant[0]}")

            elif mode == "backward":
                # Parse query into a goal fact
                goal = self._parse_query_to_goal(query)
                if goal:
                    success, proof_path = self.backward_chain(goal)
                    result.success = success
                    result.facts_used = proof_path
                    if success:
                        result.conclusion = str(proof_path[-1]) if proof_path else query
                        result.confidence = min(f.confidence for f in proof_path) if proof_path else 0.5
                        result.reasoning_chain.append(f"Proved goal through backward chaining")
                    else:
                        result.reasoning_chain.append(f"Could not prove goal")

            elif mode == "hybrid":
                # Try forward first, then backward
                forward_facts = self.forward_chain()
                result.new_facts = forward_facts

                goal = self._parse_query_to_goal(query)
                if goal:
                    success, proof_path = self.backward_chain(goal)
                    result.success = success
                    result.facts_used = proof_path + forward_facts
                    if success:
                        result.conclusion = str(proof_path[-1]) if proof_path else query
                        result.confidence = 0.8
                        result.reasoning_chain.append(f"Hybrid reasoning succeeded")

        except Exception as e:
            result.reasoning_chain.append(f"Error during reasoning: {e}")
            logger.error(f"Reasoning error: {e}")

        return result

    def _find_relevant_facts(self, query: str) -> list[Fact]:
        """Find facts relevant to a query."""
        # Simple keyword matching (can be enhanced with NLP)
        query_lower = query.lower()
        relevant = []

        for fact in self.facts.values():
            if (fact.subject.lower() in query_lower or
                fact.predicate.lower() in query_lower or
                str(fact.object).lower() in query_lower):
                relevant.append(fact)

        # Sort by confidence
        relevant.sort(key=lambda f: f.confidence, reverse=True)
        return relevant

    def _parse_query_to_goal(self, query: str) -> Optional[Fact]:
        """Parse a query string into a goal fact."""
        # Simple parsing (can be enhanced with NLP)
        parts = query.split()
        if len(parts) >= 3:
            return Fact(
                subject=parts[0],
                predicate=" ".join(parts[1:-1]),
                object=parts[-1],
                confidence=0.5
            )
        return None

    # === Statistics ===

    def get_stats(self) -> dict:
        """Get reasoning statistics.

        Returns:
            Dictionary with stats about facts, rules, inferences
        """
        return {
            "fact_count": len(self.facts),
            "rule_count": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules if r.enabled),
            "inference_count": self._inference_count,
            "avg_confidence": (
                sum(f.confidence for f in self.facts.values()) / len(self.facts)
                if self.facts else 0.0
            ),
        }

    def to_dict(self) -> dict:
        """Serialize reasoner state to dictionary."""
        return {
            "facts": [f.to_dict() for f in self.facts.values()],
            "rules": [
                {
                    "name": r.name,
                    "priority": r.priority,
                    "enabled": r.enabled,
                    "description": r.description,
                }
                for r in self.rules
            ],
            "stats": self.get_stats(),
        }
