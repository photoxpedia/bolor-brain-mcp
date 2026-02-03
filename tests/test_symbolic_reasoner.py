"""Tests for SymbolicReasoner."""

import pytest
import threading
import time
from modules.reasoning_engines.symbolic_reasoner import (
    SymbolicReasoner,
    Fact,
    FactType,
    Rule,
    ReasoningResult,
)


# === Fact Tests ===

class TestFactCreation:
    """Tests for Fact creation and validation."""

    def test_fact_creation_basic(self):
        """Test basic fact creation."""
        fact = Fact(subject="Socrates", predicate="is_a", object="human")
        assert fact.subject == "Socrates"
        assert fact.predicate == "is_a"
        assert fact.object == "human"

    def test_fact_creation_with_all_fields(self):
        """Test fact creation with all fields."""
        fact = Fact(
            subject="Python",
            predicate="version",
            object="3.11",
            fact_type=FactType.PROPERTY,
            confidence=0.95,
            source="test",
        )
        assert fact.fact_type == FactType.PROPERTY
        assert fact.confidence == 0.95
        assert fact.source == "test"

    def test_fact_auto_generates_id(self):
        """Test that facts auto-generate unique IDs."""
        fact1 = Fact(subject="A", predicate="rel", object="B")
        fact2 = Fact(subject="A", predicate="rel", object="B")
        assert fact1.id != fact2.id

    def test_fact_invalid_confidence_raises(self):
        """Test that invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be 0-1"):
            Fact(subject="A", predicate="rel", object="B", confidence=1.5)

    def test_fact_negative_confidence_raises(self):
        """Test that negative confidence raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be 0-1"):
            Fact(subject="A", predicate="rel", object="B", confidence=-0.1)

    def test_fact_empty_subject_raises(self):
        """Test that empty subject raises ValueError."""
        with pytest.raises(ValueError, match="subject cannot be empty"):
            Fact(subject="", predicate="rel", object="B")

    def test_fact_empty_predicate_raises(self):
        """Test that empty predicate raises ValueError."""
        with pytest.raises(ValueError, match="predicate cannot be empty"):
            Fact(subject="A", predicate="", object="B")


class TestFactTypes:
    """Tests for different fact types."""

    def test_assertion_fact(self):
        """Test assertion fact type."""
        fact = Fact(subject="X", predicate="is", object="Y", fact_type=FactType.ASSERTION)
        assert fact.fact_type == FactType.ASSERTION

    def test_relation_fact(self):
        """Test relation fact type."""
        fact = Fact(subject="X", predicate="connects_to", object="Y", fact_type=FactType.RELATION)
        assert fact.fact_type == FactType.RELATION

    def test_property_fact(self):
        """Test property fact type."""
        fact = Fact(subject="X", predicate="color", object="red", fact_type=FactType.PROPERTY)
        assert fact.fact_type == FactType.PROPERTY

    def test_negation_fact(self):
        """Test negation fact type."""
        fact = Fact(subject="X", predicate="is_not", object="Y", fact_type=FactType.NEGATION)
        assert fact.fact_type == FactType.NEGATION


class TestFactMethods:
    """Tests for Fact methods."""

    def test_fact_matches_all_criteria(self):
        """Test fact matching with all criteria."""
        fact = Fact(subject="A", predicate="rel", object="B")
        assert fact.matches(subject="A", predicate="rel", object="B")

    def test_fact_matches_partial_criteria(self):
        """Test fact matching with partial criteria."""
        fact = Fact(subject="A", predicate="rel", object="B")
        assert fact.matches(subject="A")
        assert fact.matches(predicate="rel")
        assert fact.matches(object="B")

    def test_fact_matches_no_criteria(self):
        """Test fact matching with no criteria (matches all)."""
        fact = Fact(subject="A", predicate="rel", object="B")
        assert fact.matches()

    def test_fact_no_match(self):
        """Test fact not matching."""
        fact = Fact(subject="A", predicate="rel", object="B")
        assert not fact.matches(subject="X")
        assert not fact.matches(predicate="other")
        assert not fact.matches(object="C")

    def test_fact_to_dict(self):
        """Test fact serialization to dict."""
        fact = Fact(subject="A", predicate="rel", object="B")
        d = fact.to_dict()
        assert d["subject"] == "A"
        assert d["predicate"] == "rel"
        assert d["object"] == "B"
        assert "id" in d
        assert "timestamp" in d

    def test_fact_from_dict(self):
        """Test fact creation from dict."""
        data = {
            "subject": "A",
            "predicate": "rel",
            "object": "B",
            "fact_type": "relation",
            "confidence": 0.8,
        }
        fact = Fact.from_dict(data)
        assert fact.subject == "A"
        assert fact.predicate == "rel"
        assert fact.object == "B"
        assert fact.fact_type == FactType.RELATION
        assert fact.confidence == 0.8

    def test_fact_str(self):
        """Test fact string representation."""
        fact = Fact(subject="Socrates", predicate="is", object="mortal")
        assert str(fact) == "Socrates is mortal"


# === Rule Tests ===

class TestRuleCreation:
    """Tests for Rule creation."""

    def test_rule_creation(self):
        """Test basic rule creation."""
        rule = Rule(
            name="test_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        assert rule.name == "test_rule"
        assert rule.enabled is True
        assert rule.priority == 0

    def test_rule_with_priority(self):
        """Test rule with priority."""
        rule = Rule(
            name="high_priority",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
            priority=10,
        )
        assert rule.priority == 10

    def test_rule_empty_name_raises(self):
        """Test that empty rule name raises ValueError."""
        with pytest.raises(ValueError, match="Rule name cannot be empty"):
            Rule(
                name="",
                conditions=[lambda f: True],
                conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
            )

    def test_rule_no_conditions_raises(self):
        """Test that rule with no conditions raises ValueError."""
        with pytest.raises(ValueError, match="must have at least one condition"):
            Rule(
                name="test",
                conditions=[],
                conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
            )

    def test_rule_no_conclusion_raises(self):
        """Test that rule with no conclusion raises ValueError."""
        with pytest.raises(ValueError, match="must have a conclusion template"):
            Rule(
                name="test",
                conditions=[lambda f: True],
                conclusion_template={},
            )


class TestRuleEvaluation:
    """Tests for Rule evaluation."""

    def test_rule_evaluate_true(self):
        """Test rule evaluation returning True."""
        rule = Rule(
            name="always_true",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        assert rule.evaluate({}) is True

    def test_rule_evaluate_false(self):
        """Test rule evaluation returning False."""
        rule = Rule(
            name="always_false",
            conditions=[lambda f: False],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        assert rule.evaluate({}) is False

    def test_rule_evaluate_all_conditions(self):
        """Test rule requires all conditions to be True."""
        rule = Rule(
            name="multi_condition",
            conditions=[lambda f: True, lambda f: False],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        assert rule.evaluate({}) is False

    def test_rule_evaluate_with_facts(self):
        """Test rule evaluation using facts."""
        fact = Fact(subject="A", predicate="is_a", object="human")
        rule = Rule(
            name="check_human",
            conditions=[lambda f: any(f[k].object == "human" for k in f)],
            conclusion_template={"subject": "X", "predicate": "is", "object": "mortal"},
        )
        assert rule.evaluate({"f1": fact}) is True

    def test_rule_apply_creates_fact(self):
        """Test rule application creates a new fact."""
        rule = Rule(
            name="simple_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        result = rule.apply({})
        assert result is not None
        assert result.subject == "X"
        assert result.predicate == "is"
        assert result.object == "Y"

    def test_rule_apply_returns_none_when_false(self):
        """Test rule application returns None when conditions are False."""
        rule = Rule(
            name="false_rule",
            conditions=[lambda f: False],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        result = rule.apply({})
        assert result is None


# === SymbolicReasoner Tests ===

class TestSymbolicReasonerBasics:
    """Tests for basic SymbolicReasoner operations."""

    def test_reasoner_creation(self):
        """Test reasoner creation."""
        reasoner = SymbolicReasoner()
        assert len(reasoner.facts) == 0
        assert len(reasoner.rules) == 0

    def test_add_and_get_fact(self):
        """Test adding and retrieving a fact."""
        reasoner = SymbolicReasoner()
        fact = Fact(subject="A", predicate="rel", object="B")
        reasoner.add_fact(fact)
        retrieved = reasoner.get_fact(fact.id)
        assert retrieved is not None
        assert retrieved.subject == "A"

    def test_add_duplicate_fact_returns_false(self):
        """Test that adding duplicate fact returns False."""
        reasoner = SymbolicReasoner()
        fact1 = Fact(subject="A", predicate="rel", object="B")
        fact2 = Fact(subject="A", predicate="rel", object="B")
        assert reasoner.add_fact(fact1) is True
        assert reasoner.add_fact(fact2) is False

    def test_remove_fact(self):
        """Test removing a fact."""
        reasoner = SymbolicReasoner()
        fact = Fact(subject="A", predicate="rel", object="B")
        reasoner.add_fact(fact)
        assert reasoner.remove_fact(fact.id) is True
        assert reasoner.get_fact(fact.id) is None

    def test_remove_nonexistent_fact(self):
        """Test removing nonexistent fact returns False."""
        reasoner = SymbolicReasoner()
        assert reasoner.remove_fact("nonexistent") is False

    def test_query_facts_by_subject(self):
        """Test querying facts by subject."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel1", object="B"))
        reasoner.add_fact(Fact(subject="A", predicate="rel2", object="C"))
        reasoner.add_fact(Fact(subject="X", predicate="rel3", object="Y"))
        results = reasoner.query_facts(subject="A")
        assert len(results) == 2

    def test_query_facts_by_predicate(self):
        """Test querying facts by predicate."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="is_a", object="B"))
        reasoner.add_fact(Fact(subject="C", predicate="is_a", object="D"))
        reasoner.add_fact(Fact(subject="X", predicate="has", object="Y"))
        results = reasoner.query_facts(predicate="is_a")
        assert len(results) == 2

    def test_query_facts_with_min_confidence(self):
        """Test querying facts with minimum confidence."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel", object="B", confidence=0.9))
        reasoner.add_fact(Fact(subject="C", predicate="rel", object="D", confidence=0.5))
        results = reasoner.query_facts(min_confidence=0.7)
        assert len(results) == 1
        assert results[0].subject == "A"

    def test_clear_facts(self):
        """Test clearing all facts."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel", object="B"))
        reasoner.add_fact(Fact(subject="C", predicate="rel", object="D"))
        count = reasoner.clear_facts()
        assert count == 2
        assert len(reasoner.facts) == 0


class TestRuleManagement:
    """Tests for rule management in SymbolicReasoner."""

    def test_add_rule(self):
        """Test adding a rule."""
        reasoner = SymbolicReasoner()
        rule = Rule(
            name="test_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        reasoner.add_rule(rule)
        assert len(reasoner.rules) == 1

    def test_add_duplicate_rule_raises(self):
        """Test adding duplicate rule name raises ValueError."""
        reasoner = SymbolicReasoner()
        rule1 = Rule(
            name="test_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        rule2 = Rule(
            name="test_rule",
            conditions=[lambda f: False],
            conclusion_template={"subject": "A", "predicate": "is", "object": "B"},
        )
        reasoner.add_rule(rule1)
        with pytest.raises(ValueError, match="already exists"):
            reasoner.add_rule(rule2)

    def test_remove_rule(self):
        """Test removing a rule."""
        reasoner = SymbolicReasoner()
        rule = Rule(
            name="test_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        reasoner.add_rule(rule)
        assert reasoner.remove_rule("test_rule") is True
        assert len(reasoner.rules) == 0

    def test_get_rule(self):
        """Test getting a rule by name."""
        reasoner = SymbolicReasoner()
        rule = Rule(
            name="test_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        reasoner.add_rule(rule)
        retrieved = reasoner.get_rule("test_rule")
        assert retrieved is not None
        assert retrieved.name == "test_rule"

    def test_rules_sorted_by_priority(self):
        """Test that rules are sorted by priority."""
        reasoner = SymbolicReasoner()
        rule_low = Rule(
            name="low",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
            priority=1,
        )
        rule_high = Rule(
            name="high",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
            priority=10,
        )
        reasoner.add_rule(rule_low)
        reasoner.add_rule(rule_high)
        assert reasoner.rules[0].name == "high"
        assert reasoner.rules[1].name == "low"

    def test_enable_disable_rule(self):
        """Test enabling and disabling rules."""
        reasoner = SymbolicReasoner()
        rule = Rule(
            name="test_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        )
        reasoner.add_rule(rule)
        reasoner.enable_rule("test_rule", False)
        assert reasoner.get_rule("test_rule").enabled is False
        reasoner.enable_rule("test_rule", True)
        assert reasoner.get_rule("test_rule").enabled is True


# === Forward Chaining Tests ===

class TestForwardChaining:
    """Tests for forward chaining."""

    def test_simple_forward_chain(self):
        """Test simple forward chaining."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="Socrates", predicate="is_a", object="human"))
        reasoner.add_rule(Rule(
            name="mortality",
            conditions=[lambda f: any(f[k].object == "human" for k in f)],
            conclusion_template={
                "subject": lambda f: next(f[k].subject for k in f if f[k].object == "human"),
                "predicate": "is",
                "object": "mortal",
            },
        ))
        new_facts = reasoner.forward_chain()
        assert len(new_facts) == 1
        assert new_facts[0].predicate == "is"
        assert new_facts[0].object == "mortal"

    def test_forward_chain_no_applicable_rules(self):
        """Test forward chaining with no applicable rules."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel", object="B"))
        reasoner.add_rule(Rule(
            name="never_fires",
            conditions=[lambda f: any(f[k].object == "nonexistent" for k in f)],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        ))
        new_facts = reasoner.forward_chain()
        assert len(new_facts) == 0

    def test_forward_chain_disabled_rule_skipped(self):
        """Test that disabled rules are skipped in forward chaining."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel", object="B"))
        reasoner.add_rule(Rule(
            name="disabled_rule",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
            enabled=False,
        ))
        new_facts = reasoner.forward_chain()
        assert len(new_facts) == 0

    def test_forward_chain_respects_max_iterations(self):
        """Test that forward chaining respects max iterations."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="num", object=1))
        # Rule that would fire indefinitely (always True)
        call_count = [0]

        def counting_condition(f):
            call_count[0] += 1
            return call_count[0] <= 5

        reasoner.add_rule(Rule(
            name="counter",
            conditions=[counting_condition],
            conclusion_template={
                "subject": lambda f: f"X{call_count[0]}",
                "predicate": "is",
                "object": "counted",
            },
        ))
        reasoner.forward_chain(max_iterations=3)
        # Should stop due to max iterations or no new facts
        assert call_count[0] <= 5

    def test_forward_chain_multiple_rules(self):
        """Test forward chaining with multiple rules."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="Socrates", predicate="is_a", object="human"))

        # Rule 1: humans are mortal
        reasoner.add_rule(Rule(
            name="mortality",
            conditions=[lambda f: any(f[k].object == "human" for k in f)],
            conclusion_template={
                "subject": lambda f: next(f[k].subject for k in f if f[k].object == "human"),
                "predicate": "is",
                "object": "mortal",
            },
        ))

        # Rule 2: humans have names
        reasoner.add_rule(Rule(
            name="names",
            conditions=[lambda f: any(f[k].object == "human" for k in f)],
            conclusion_template={
                "subject": lambda f: next(f[k].subject for k in f if f[k].object == "human"),
                "predicate": "has",
                "object": "name",
            },
        ))

        new_facts = reasoner.forward_chain()
        assert len(new_facts) == 2


# === Backward Chaining Tests ===

class TestBackwardChaining:
    """Tests for backward chaining."""

    def test_backward_chain_goal_in_facts(self):
        """Test backward chaining when goal is already in facts."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="Socrates", predicate="is", object="mortal"))
        goal = Fact(subject="Socrates", predicate="is", object="mortal")
        success, proof = reasoner.backward_chain(goal)
        assert success is True
        assert len(proof) == 1

    def test_backward_chain_goal_not_provable(self):
        """Test backward chaining when goal cannot be proved."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel", object="B"))
        goal = Fact(subject="X", predicate="is", object="Y")
        success, proof = reasoner.backward_chain(goal)
        assert success is False

    def test_backward_chain_respects_depth(self):
        """Test that backward chaining respects depth limit."""
        reasoner = SymbolicReasoner()
        goal = Fact(subject="X", predicate="is", object="Y")
        success, proof = reasoner.backward_chain(goal, max_depth=1)
        assert success is False


# === Reasoning Interface Tests ===

class TestReasoningInterface:
    """Tests for the main reasoning interface."""

    def test_reason_forward_mode(self):
        """Test reasoning in forward mode."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="Python", predicate="is_a", object="language"))
        result = reasoner.reason("What is Python?", mode="forward")
        assert isinstance(result, ReasoningResult)
        assert "forward reasoning" in result.reasoning_chain[0].lower()

    def test_reason_backward_mode(self):
        """Test reasoning in backward mode."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="Python", predicate="is_a", object="language"))
        result = reasoner.reason("Python is_a language", mode="backward")
        assert isinstance(result, ReasoningResult)
        assert "backward reasoning" in result.reasoning_chain[0].lower()

    def test_reason_hybrid_mode(self):
        """Test reasoning in hybrid mode."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="Python", predicate="is_a", object="language"))
        result = reasoner.reason("Python is_a language", mode="hybrid")
        assert isinstance(result, ReasoningResult)
        assert "hybrid reasoning" in result.reasoning_chain[0].lower()


# === Thread Safety Tests ===

class TestThreadSafety:
    """Tests for thread safety."""

    def test_reasoner_has_lock(self):
        """Test that reasoner has a lock."""
        reasoner = SymbolicReasoner()
        assert hasattr(reasoner, "_lock")
        assert isinstance(reasoner._lock, type(threading.RLock()))

    def test_concurrent_fact_addition(self):
        """Test concurrent fact addition."""
        reasoner = SymbolicReasoner()
        errors = []

        def add_facts(start):
            try:
                for i in range(100):
                    fact = Fact(
                        subject=f"Subject_{start}_{i}",
                        predicate="rel",
                        object=f"Object_{start}_{i}"
                    )
                    reasoner.add_fact(fact)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_facts, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # Should have 500 unique facts
        assert len(reasoner.facts) == 500


# === Statistics Tests ===

class TestStatistics:
    """Tests for statistics and serialization."""

    def test_get_stats(self):
        """Test getting statistics."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel", object="B", confidence=0.8))
        reasoner.add_fact(Fact(subject="C", predicate="rel", object="D", confidence=1.0))
        reasoner.add_rule(Rule(
            name="test",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
        ))

        stats = reasoner.get_stats()
        assert stats["fact_count"] == 2
        assert stats["rule_count"] == 1
        assert stats["enabled_rules"] == 1
        assert stats["avg_confidence"] == 0.9

    def test_to_dict(self):
        """Test serialization to dict."""
        reasoner = SymbolicReasoner()
        reasoner.add_fact(Fact(subject="A", predicate="rel", object="B"))
        reasoner.add_rule(Rule(
            name="test",
            conditions=[lambda f: True],
            conclusion_template={"subject": "X", "predicate": "is", "object": "Y"},
            description="Test rule",
        ))

        d = reasoner.to_dict()
        assert "facts" in d
        assert "rules" in d
        assert "stats" in d
        assert len(d["facts"]) == 1
        assert len(d["rules"]) == 1
        assert d["rules"][0]["name"] == "test"
        assert d["rules"][0]["description"] == "Test rule"


# === Integration Tests ===

class TestIntegration:
    """Integration tests for SymbolicReasoner."""

    def test_classic_syllogism(self):
        """Test the classic Socrates syllogism."""
        reasoner = SymbolicReasoner()

        # Premise 1: Socrates is a human
        reasoner.add_fact(Fact(subject="Socrates", predicate="is_a", object="human"))

        # Premise 2: All humans are mortal (as a rule)
        reasoner.add_rule(Rule(
            name="all_humans_mortal",
            conditions=[
                lambda f: any(
                    f[k].predicate == "is_a" and f[k].object == "human"
                    for k in f
                )
            ],
            conclusion_template={
                "subject": lambda f: next(
                    f[k].subject for k in f
                    if f[k].predicate == "is_a" and f[k].object == "human"
                ),
                "predicate": "is",
                "object": "mortal",
            },
        ))

        # Forward chain to derive: Socrates is mortal
        new_facts = reasoner.forward_chain()

        assert len(new_facts) == 1
        assert new_facts[0].subject == "Socrates"
        assert new_facts[0].predicate == "is"
        assert new_facts[0].object == "mortal"

    def test_chained_inference(self):
        """Test chained inference across multiple rules."""
        reasoner = SymbolicReasoner()

        # Base fact
        reasoner.add_fact(Fact(subject="Fido", predicate="is_a", object="dog"))

        # Rule 1: dogs are mammals
        reasoner.add_rule(Rule(
            name="dogs_are_mammals",
            conditions=[
                lambda f: any(f[k].object == "dog" for k in f)
            ],
            conclusion_template={
                "subject": lambda f: next(f[k].subject for k in f if f[k].object == "dog"),
                "predicate": "is_a",
                "object": "mammal",
            },
        ))

        # Rule 2: mammals are animals
        reasoner.add_rule(Rule(
            name="mammals_are_animals",
            conditions=[
                lambda f: any(f[k].object == "mammal" for k in f)
            ],
            conclusion_template={
                "subject": lambda f: next(f[k].subject for k in f if f[k].object == "mammal"),
                "predicate": "is_a",
                "object": "animal",
            },
        ))

        # Forward chain should derive both: Fido is_a mammal AND Fido is_a animal
        new_facts = reasoner.forward_chain()

        subjects = [f.object for f in new_facts]
        assert "mammal" in subjects
        assert "animal" in subjects
