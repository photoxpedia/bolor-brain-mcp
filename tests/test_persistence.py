"""Tests for Bolor Brain JSON persistence."""

import pytest
import json
from pathlib import Path

from persistence import BrainPersistence


@pytest.fixture
def brain_dir(tmp_path):
    """Use temp dir instead of ~/.bolor-brain/ for tests."""
    return tmp_path / "bolor-brain"


@pytest.fixture
def persistence(brain_dir):
    return BrainPersistence(str(brain_dir))


class TestBrainPersistence:
    def test_creates_directory_on_init(self, persistence, brain_dir):
        assert brain_dir.exists()
        assert brain_dir.is_dir()

    def test_save_and_load_cases(self, persistence):
        case = {
            "id": "case_1",
            "problem": {"type": "bug", "error": "404"},
            "solution": {"fix": "add route"},
            "outcome": {"success": True},
        }
        persistence.save_case(case)
        cases = persistence.load_cases()
        assert len(cases) == 1
        assert cases[0]["id"] == "case_1"

    def test_save_multiple_cases(self, persistence):
        for i in range(3):
            persistence.save_case({"id": f"case_{i}", "problem": {}, "solution": {}})
        cases = persistence.load_cases()
        assert len(cases) == 3

    def test_save_and_load_facts(self, persistence):
        fact = {"id": "fact_1", "subject": "python", "predicate": "is", "object": "language"}
        persistence.save_fact(fact)
        facts = persistence.load_facts()
        assert len(facts) == 1
        assert facts[0]["subject"] == "python"

    def test_save_and_load_knowledge(self, persistence):
        nodes = [{"id": "n1", "label": "Python", "type": "language"}]
        edges = [{"source": "n1", "target": "n2", "relation": "uses"}]
        persistence.save_knowledge(nodes, edges)
        loaded_nodes, loaded_edges = persistence.load_knowledge()
        assert len(loaded_nodes) == 1
        assert len(loaded_edges) == 1

    def test_delete_case(self, persistence):
        persistence.save_case({"id": "case_1", "problem": {}, "solution": {}})
        persistence.save_case({"id": "case_2", "problem": {}, "solution": {}})
        result = persistence.delete_case("case_1")
        assert result is True
        cases = persistence.load_cases()
        assert len(cases) == 1
        assert cases[0]["id"] == "case_2"

    def test_delete_nonexistent_case(self, persistence):
        result = persistence.delete_case("nope")
        assert result is False

    def test_delete_fact(self, persistence):
        persistence.save_fact({"id": "f1", "subject": "a", "predicate": "b", "object": "c"})
        result = persistence.delete_fact("f1")
        assert result is True
        assert len(persistence.load_facts()) == 0

    def test_delete_nonexistent_fact(self, persistence):
        result = persistence.delete_fact("nope")
        assert result is False

    def test_load_empty(self, persistence):
        assert persistence.load_cases() == []
        assert persistence.load_facts() == []
        nodes, edges = persistence.load_knowledge()
        assert nodes == []
        assert edges == []

    def test_get_stats(self, persistence):
        persistence.save_case({"id": "c1", "problem": {}, "solution": {}})
        persistence.save_fact({"id": "f1", "subject": "a", "predicate": "b", "object": "c"})
        persistence.save_knowledge(
            [{"id": "n1", "label": "X", "type": "t"}],
            [{"source": "n1", "target": "n2", "relation": "r"}],
        )
        stats = persistence.get_stats()
        assert stats["cases"] == 1
        assert stats["facts"] == 1
        assert stats["nodes"] == 1
        assert stats["edges"] == 1

    def test_persistence_survives_reload(self, brain_dir):
        p1 = BrainPersistence(str(brain_dir))
        p1.save_case({"id": "c1", "problem": {"x": 1}, "solution": {"y": 2}})

        p2 = BrainPersistence(str(brain_dir))
        cases = p2.load_cases()
        assert len(cases) == 1
        assert cases[0]["id"] == "c1"
