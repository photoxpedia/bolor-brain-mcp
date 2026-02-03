"""Tests for CaseBasedReasoner."""

import pytest
import threading
from modules.reasoning_engines.case_based_reasoner import (
    CaseBasedReasoner,
    Case,
    CaseMatch,
    CaseReasoningResult,
)


# === Case Tests ===

class TestCaseCreation:
    """Tests for Case creation and validation."""

    def test_case_creation_basic(self):
        """Test basic case creation."""
        case = Case(
            id="c1",
            problem={"type": "bug"},
            solution={"action": "fix"},
        )
        assert case.id == "c1"
        assert case.problem["type"] == "bug"
        assert case.solution["action"] == "fix"

    def test_case_creation_with_all_fields(self):
        """Test case creation with all fields."""
        case = Case(
            id="c1",
            problem={"type": "bug"},
            solution={"action": "fix"},
            outcome={"status": "resolved"},
            success=True,
            tags=["python", "error"],
        )
        assert case.outcome["status"] == "resolved"
        assert case.success is True
        assert "python" in case.tags

    def test_case_empty_id_raises(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            Case(id="", problem={"x": 1}, solution={"y": 2})

    def test_case_empty_problem_raises(self):
        """Test that empty problem raises ValueError."""
        with pytest.raises(ValueError, match="problem cannot be empty"):
            Case(id="c1", problem={}, solution={"y": 2})

    def test_case_empty_solution_raises(self):
        """Test that empty solution raises ValueError."""
        with pytest.raises(ValueError, match="solution cannot be empty"):
            Case(id="c1", problem={"x": 1}, solution={})


class TestCaseMethods:
    """Tests for Case methods."""

    def test_case_to_dict(self):
        """Test case serialization to dict."""
        case = Case(
            id="c1",
            problem={"type": "bug"},
            solution={"action": "fix"},
            success=True,
        )
        d = case.to_dict()
        assert d["id"] == "c1"
        assert d["problem"]["type"] == "bug"
        assert d["solution"]["action"] == "fix"
        assert d["success"] is True

    def test_case_from_dict(self):
        """Test case creation from dict."""
        data = {
            "id": "c1",
            "problem": {"type": "bug"},
            "solution": {"action": "fix"},
            "success": True,
            "tags": ["python"],
        }
        case = Case.from_dict(data)
        assert case.id == "c1"
        assert case.success is True
        assert "python" in case.tags


# === CaseMatch Tests ===

class TestCaseMatch:
    """Tests for CaseMatch."""

    def test_case_match_creation(self):
        """Test CaseMatch creation."""
        case = Case(id="c1", problem={"x": 1}, solution={"y": 2})
        match = CaseMatch(
            case=case,
            similarity=0.85,
            matching_features=["x"],
            differing_features=["z"],
        )
        assert match.similarity == 0.85
        assert "x" in match.matching_features

    def test_case_match_invalid_similarity_raises(self):
        """Test that invalid similarity raises ValueError."""
        case = Case(id="c1", problem={"x": 1}, solution={"y": 2})
        with pytest.raises(ValueError, match="similarity must be 0-1"):
            CaseMatch(case=case, similarity=1.5)


# === CaseBasedReasoner Case Management Tests ===

class TestCaseManagement:
    """Tests for case management in CaseBasedReasoner."""

    def test_reasoner_creation(self):
        """Test reasoner creation."""
        cbr = CaseBasedReasoner()
        assert len(cbr.cases) == 0

    def test_store_case(self):
        """Test storing a case."""
        cbr = CaseBasedReasoner()
        case = Case(id="c1", problem={"x": 1}, solution={"y": 2})
        assert cbr.store_case(case) is True
        assert len(cbr.cases) == 1

    def test_store_duplicate_case_returns_false(self):
        """Test that storing duplicate case returns False."""
        cbr = CaseBasedReasoner()
        case1 = Case(id="c1", problem={"x": 1}, solution={"y": 2})
        case2 = Case(id="c1", problem={"a": 1}, solution={"b": 2})
        cbr.store_case(case1)
        assert cbr.store_case(case2) is False

    def test_get_case(self):
        """Test getting a case."""
        cbr = CaseBasedReasoner()
        case = Case(id="c1", problem={"x": 1}, solution={"y": 2})
        cbr.store_case(case)
        retrieved = cbr.get_case("c1")
        assert retrieved is not None
        assert retrieved.id == "c1"

    def test_get_nonexistent_case(self):
        """Test getting nonexistent case."""
        cbr = CaseBasedReasoner()
        assert cbr.get_case("nonexistent") is None

    def test_remove_case(self):
        """Test removing a case."""
        cbr = CaseBasedReasoner()
        case = Case(id="c1", problem={"x": 1}, solution={"y": 2})
        cbr.store_case(case)
        assert cbr.remove_case("c1") is True
        assert cbr.get_case("c1") is None

    def test_query_cases_by_tags(self):
        """Test querying cases by tags."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(id="c1", problem={"x": 1}, solution={"y": 2}, tags=["python"]))
        cbr.store_case(Case(id="c2", problem={"x": 1}, solution={"y": 2}, tags=["java"]))
        cbr.store_case(Case(id="c3", problem={"x": 1}, solution={"y": 2}, tags=["python", "bug"]))

        python_cases = cbr.query_cases(tags=["python"])
        assert len(python_cases) == 2

    def test_query_cases_success_only(self):
        """Test querying only successful cases."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(id="c1", problem={"x": 1}, solution={"y": 2}, success=True))
        cbr.store_case(Case(id="c2", problem={"x": 1}, solution={"y": 2}, success=False))
        cbr.store_case(Case(id="c3", problem={"x": 1}, solution={"y": 2}, success=None))

        successful = cbr.query_cases(success_only=True)
        assert len(successful) == 1
        assert successful[0].id == "c1"


# === Similarity Tests ===

class TestSimilarity:
    """Tests for similarity computation."""

    def test_identical_problems_full_similarity(self):
        """Test that identical problems have similarity 1.0."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "bug", "language": "python"},
            solution={"action": "fix"}
        ))

        matches = cbr.retrieve({"type": "bug", "language": "python"})
        assert len(matches) == 1
        assert matches[0].similarity >= 0.99

    def test_partial_match_similarity(self):
        """Test partial match has intermediate similarity."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "bug", "language": "python", "severity": "high"},
            solution={"action": "fix"}
        ))

        matches = cbr.retrieve({"type": "bug", "language": "java", "severity": "high"})
        assert len(matches) == 1
        # 2 out of 3 features match
        assert 0.3 < matches[0].similarity < 0.9

    def test_no_match_low_similarity(self):
        """Test no match has low similarity."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "bug", "language": "python"},
            solution={"action": "fix"}
        ))

        matches = cbr.retrieve({"type": "feature", "language": "java"})
        assert len(matches) == 1
        assert matches[0].similarity < 0.3

    def test_numeric_similarity(self):
        """Test numeric feature similarity."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"priority": 5},
            solution={"action": "urgent"}
        ))

        # Close numeric value
        matches = cbr.retrieve({"priority": 4})
        assert matches[0].similarity > 0.5

        # Far numeric value
        matches = cbr.retrieve({"priority": 100})
        assert matches[0].similarity < 0.3

    def test_string_containment_similarity(self):
        """Test string containment gives partial similarity."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"error": "NullPointerException"},
            solution={"action": "add_null_check"}
        ))

        matches = cbr.retrieve({"error": "NullPointer"})
        assert matches[0].similarity > 0.5

    def test_list_similarity(self):
        """Test list similarity using Jaccard."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"tags": ["a", "b", "c"]},
            solution={"action": "test"}
        ))

        # 2 out of 4 overlap
        matches = cbr.retrieve({"tags": ["a", "b", "d"]})
        assert matches[0].similarity > 0.4


# === 4R Cycle Tests ===

class TestRetrieve:
    """Tests for Retrieve (R1)."""

    def test_retrieve_returns_k_best(self):
        """Test that retrieve returns at most k cases."""
        cbr = CaseBasedReasoner()
        for i in range(10):
            cbr.store_case(Case(
                id=f"c{i}",
                problem={"type": "bug", "num": i},
                solution={"action": f"fix{i}"}
            ))

        matches = cbr.retrieve({"type": "bug", "num": 5}, k=3)
        assert len(matches) == 3

    def test_retrieve_respects_min_similarity(self):
        """Test that retrieve respects minimum similarity."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "bug"},
            solution={"action": "fix"}
        ))
        cbr.store_case(Case(
            id="c2",
            problem={"type": "feature"},
            solution={"action": "add"}
        ))

        # With high threshold
        matches = cbr.retrieve({"type": "bug"}, min_similarity=0.9)
        assert len(matches) == 1
        assert matches[0].case.id == "c1"

    def test_retrieve_increments_use_count(self):
        """Test that retrieve increments use count."""
        cbr = CaseBasedReasoner()
        case = Case(id="c1", problem={"type": "bug"}, solution={"action": "fix"})
        cbr.store_case(case)

        assert case.use_count == 0
        cbr.retrieve({"type": "bug"})
        assert cbr.get_case("c1").use_count == 1

    def test_retrieve_applies_success_bonus(self):
        """Test that successful cases get similarity bonus."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "bug"},
            solution={"action": "fix1"},
            success=True
        ))
        cbr.store_case(Case(
            id="c2",
            problem={"type": "bug"},
            solution={"action": "fix2"},
            success=False
        ))

        matches = cbr.retrieve({"type": "bug"})
        # Successful case should rank higher
        assert matches[0].case.success is True


class TestReuse:
    """Tests for Reuse (R2)."""

    def test_reuse_returns_solution(self):
        """Test that reuse returns a solution."""
        cbr = CaseBasedReasoner()
        case = Case(
            id="c1",
            problem={"type": "bug", "language": "python"},
            solution={"action": "add_try_except", "target": "python"}
        )
        cbr.store_case(case)

        matches = cbr.retrieve({"type": "bug", "language": "python"})
        solution = cbr.reuse({"type": "bug", "language": "python"}, matches[0])
        assert "action" in solution

    def test_reuse_adapts_solution(self):
        """Test that reuse adapts solution for differing features."""
        cbr = CaseBasedReasoner()
        case = Case(
            id="c1",
            problem={"type": "bug", "language": "python"},
            solution={"action": "add_try_except", "lang": "python"}
        )
        cbr.store_case(case)

        matches = cbr.retrieve({"type": "bug", "language": "java"})
        solution = cbr.reuse({"type": "bug", "language": "java"}, matches[0])
        # Should have adapted "python" to "java" in solution
        assert solution["lang"] == "java"


class TestRevise:
    """Tests for Revise (R3)."""

    def test_revise_applies_modifications(self):
        """Test that revise applies modifications."""
        cbr = CaseBasedReasoner()
        solution = {"action": "fix", "priority": "low"}
        feedback = {"modifications": {"priority": "high"}}

        revised = cbr.revise(solution, feedback)
        assert revised["priority"] == "high"
        assert revised["action"] == "fix"

    def test_revise_removes_keys(self):
        """Test that revise removes specified keys."""
        cbr = CaseBasedReasoner()
        solution = {"action": "fix", "temp": "value"}
        feedback = {"remove": ["temp"]}

        revised = cbr.revise(solution, feedback)
        assert "temp" not in revised
        assert revised["action"] == "fix"

    def test_revise_adds_keys(self):
        """Test that revise adds new keys."""
        cbr = CaseBasedReasoner()
        solution = {"action": "fix"}
        feedback = {"add": {"extra": "value"}}

        revised = cbr.revise(solution, feedback)
        assert revised["extra"] == "value"


class TestRetain:
    """Tests for Retain (R4)."""

    def test_retain_stores_new_case(self):
        """Test that retain creates and stores a new case."""
        cbr = CaseBasedReasoner()
        case = cbr.retain(
            problem={"type": "bug"},
            solution={"action": "fix"},
            outcome={"status": "resolved"},
            success=True
        )

        assert case.id is not None
        assert cbr.get_case(case.id) is not None

    def test_retain_with_tags(self):
        """Test that retain stores tags."""
        cbr = CaseBasedReasoner()
        case = cbr.retain(
            problem={"type": "bug"},
            solution={"action": "fix"},
            tags=["python", "critical"]
        )

        assert "python" in case.tags
        assert "critical" in case.tags

    def test_retain_updates_weights(self):
        """Test that retain updates feature weights."""
        cbr = CaseBasedReasoner()

        # Successful case
        cbr.retain(
            problem={"important_feature": "value"},
            solution={"action": "fix"},
            success=True
        )

        # Weight should increase for features in successful case
        assert cbr.feature_weights.get("important_feature", 1.0) > 1.0


# === Learning Tests ===

class TestLearning:
    """Tests for learning from outcomes."""

    def test_update_case_outcome(self):
        """Test updating a case with its outcome."""
        cbr = CaseBasedReasoner()
        case = Case(id="c1", problem={"x": 1}, solution={"y": 2})
        cbr.store_case(case)

        result = cbr.update_case_outcome(
            "c1",
            outcome={"status": "success"},
            success=True
        )

        assert result is True
        updated = cbr.get_case("c1")
        assert updated.outcome["status"] == "success"
        assert updated.success is True

    def test_update_feature_weights_bulk(self):
        """Test bulk update of feature weights."""
        cbr = CaseBasedReasoner()

        successful = [
            Case(id="s1", problem={"feature_a": 1}, solution={"y": 2}, success=True),
            Case(id="s2", problem={"feature_a": 2}, solution={"y": 2}, success=True),
        ]
        failed = [
            Case(id="f1", problem={"feature_b": 1}, solution={"y": 2}, success=False),
        ]

        cbr.update_feature_weights(successful, failed)

        # feature_a should have higher weight (successful)
        assert cbr.feature_weights.get("feature_a", 1.0) > 1.0
        # feature_b should have lower weight (failed)
        assert cbr.feature_weights.get("feature_b", 1.0) < 1.0


# === Full Reasoning Cycle Tests ===

class TestReasoningCycle:
    """Tests for the full reasoning cycle."""

    def test_reason_finds_solution(self):
        """Test that reason finds a solution."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "null_error", "language": "python"},
            solution={"action": "add_null_check", "pattern": "if x is not None"},
            success=True
        ))

        result = cbr.reason({"type": "null_error", "language": "python"})

        assert result.success is True
        assert result.proposed_solution is not None
        assert result.confidence > 0.5
        assert result.source_case is not None

    def test_reason_no_similar_cases(self):
        """Test reasoning when no similar cases exist."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "database_error"},
            solution={"action": "reconnect"}
        ))

        result = cbr.reason(
            {"type": "network_error"},
            min_similarity=0.9
        )

        assert result.success is False
        assert result.proposed_solution is None

    def test_reason_returns_reasoning_chain(self):
        """Test that reason returns a reasoning chain."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "bug"},
            solution={"action": "fix"}
        ))

        result = cbr.reason({"type": "bug"})

        assert len(result.reasoning_chain) > 0
        assert any("Retrieved" in step for step in result.reasoning_chain)


# === Thread Safety Tests ===

class TestThreadSafety:
    """Tests for thread safety."""

    def test_reasoner_has_lock(self):
        """Test that reasoner has a lock."""
        cbr = CaseBasedReasoner()
        assert hasattr(cbr, "_lock")
        assert isinstance(cbr._lock, type(threading.RLock()))

    def test_concurrent_case_storage(self):
        """Test concurrent case storage."""
        cbr = CaseBasedReasoner()
        errors = []

        def store_cases(start):
            try:
                for i in range(50):
                    cbr.store_case(Case(
                        id=f"c{start}_{i}",
                        problem={"thread": start, "num": i},
                        solution={"action": f"fix_{start}_{i}"}
                    ))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=store_cases, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(cbr.cases) == 250


# === Serialization Tests ===

class TestSerialization:
    """Tests for serialization."""

    def test_to_dict(self):
        """Test serialization to dict."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(
            id="c1",
            problem={"type": "bug"},
            solution={"action": "fix"},
            success=True
        ))
        cbr.feature_weights["type"] = 1.5

        d = cbr.to_dict()
        assert len(d["cases"]) == 1
        assert d["feature_weights"]["type"] == 1.5
        assert "stats" in d

    def test_from_dict(self):
        """Test creation from dict."""
        data = {
            "cases": [
                {"id": "c1", "problem": {"x": 1}, "solution": {"y": 2}}
            ],
            "feature_weights": {"x": 1.5}
        }
        cbr = CaseBasedReasoner.from_dict(data)

        assert len(cbr.cases) == 1
        assert cbr.feature_weights["x"] == 1.5

    def test_round_trip(self):
        """Test serialization round trip."""
        cbr1 = CaseBasedReasoner()
        cbr1.store_case(Case(
            id="c1",
            problem={"type": "bug", "severity": "high"},
            solution={"action": "fix"},
            success=True,
            tags=["python"]
        ))
        cbr1.feature_weights["type"] = 2.0

        data = cbr1.to_dict()
        cbr2 = CaseBasedReasoner.from_dict(data)

        assert len(cbr2.cases) == 1
        case = cbr2.get_case("c1")
        assert case.problem["type"] == "bug"
        assert case.success is True
        assert "python" in case.tags
        assert cbr2.feature_weights["type"] == 2.0


# === Statistics Tests ===

class TestStatistics:
    """Tests for statistics."""

    def test_get_stats(self):
        """Test getting statistics."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(id="c1", problem={"x": 1}, solution={"y": 2}, success=True))
        cbr.store_case(Case(id="c2", problem={"x": 1}, solution={"y": 2}, success=False))
        cbr.store_case(Case(id="c3", problem={"x": 1}, solution={"y": 2}))

        stats = cbr.get_stats()
        assert stats["total_cases"] == 3
        assert stats["successful_cases"] == 1
        assert stats["failed_cases"] == 1
        assert stats["pending_cases"] == 1

    def test_clear(self):
        """Test clearing the case base."""
        cbr = CaseBasedReasoner()
        cbr.store_case(Case(id="c1", problem={"x": 1}, solution={"y": 2}))
        cbr.feature_weights["x"] = 2.0

        cbr.clear()
        assert len(cbr.cases) == 0
        assert len(cbr.feature_weights) == 0
