# Pure Intelligence Refactor - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Strip Bolor Brain MCP down to a pure intelligence server (reasoning + memory + learning + persistence). Delete everything Claude Code already handles.

**Architecture:** Bolor Brain MCP becomes 11 tools: 6 reasoning, 4 memory, 1 utility. Persistence via JSON files in `~/.bolor-brain/`. No autonomous loop, no execution engine, no scheduler, no approval system.

**Tech Stack:** Python 3.11+, `mcp>=1.0.0`, stdlib `json`/`pathlib`/`os` for persistence. No new dependencies.

---

## Task 1: Create feature branch

**Step 1: Create and switch to feature branch**

Run: `git checkout -b refactor/pure-intelligence`
Expected: `Switched to a new branch 'refactor/pure-intelligence'`

---

## Task 2: Build persistence layer (TDD)

**Files:**
- Create: `persistence.py`
- Create: `tests/test_persistence.py`

**Step 1: Write the failing tests**

```python
# tests/test_persistence.py
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
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_persistence.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'persistence')

**Step 3: Write the implementation**

```python
# persistence.py
"""
Bolor Brain Persistence - JSON file storage for brain state.

Stores cases, facts, and knowledge graph to ~/.bolor-brain/ as JSON files.
Loaded on server start, saved after every write operation.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEFAULT_DIR = os.path.expanduser("~/.bolor-brain")


class BrainPersistence:
    """JSON file persistence for Bolor Brain."""

    def __init__(self, directory: str = None):
        self.directory = Path(directory or DEFAULT_DIR)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._cases_file = self.directory / "cases.json"
        self._facts_file = self.directory / "facts.json"
        self._knowledge_file = self.directory / "knowledge.json"

    # --- Cases ---

    def save_case(self, case: Dict[str, Any]) -> None:
        cases = self.load_cases()
        cases.append(case)
        self._write(self._cases_file, cases)

    def load_cases(self) -> List[Dict[str, Any]]:
        return self._read(self._cases_file, [])

    def delete_case(self, case_id: str) -> bool:
        cases = self.load_cases()
        filtered = [c for c in cases if c.get("id") != case_id]
        if len(filtered) == len(cases):
            return False
        self._write(self._cases_file, filtered)
        return True

    # --- Facts ---

    def save_fact(self, fact: Dict[str, Any]) -> None:
        facts = self.load_facts()
        facts.append(fact)
        self._write(self._facts_file, facts)

    def load_facts(self) -> List[Dict[str, Any]]:
        return self._read(self._facts_file, [])

    def delete_fact(self, fact_id: str) -> bool:
        facts = self.load_facts()
        filtered = [f for f in facts if f.get("id") != fact_id]
        if len(filtered) == len(facts):
            return False
        self._write(self._facts_file, filtered)
        return True

    # --- Knowledge Graph ---

    def save_knowledge(self, nodes: List[Dict], edges: List[Dict]) -> None:
        self._write(self._knowledge_file, {"nodes": nodes, "edges": edges})

    def load_knowledge(self) -> Tuple[List[Dict], List[Dict]]:
        data = self._read(self._knowledge_file, {"nodes": [], "edges": []})
        return data.get("nodes", []), data.get("edges", [])

    # --- Stats ---

    def get_stats(self) -> Dict[str, int]:
        nodes, edges = self.load_knowledge()
        return {
            "cases": len(self.load_cases()),
            "facts": len(self.load_facts()),
            "nodes": len(nodes),
            "edges": len(edges),
        }

    # --- Internal ---

    def _write(self, path: Path, data: Any) -> None:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _read(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        with open(path, "r") as f:
            return json.load(f)
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_persistence.py -v`
Expected: ALL PASS (12 tests)

**Step 5: Commit**

```bash
git add persistence.py tests/test_persistence.py
git commit -m "feat: Add JSON persistence layer for brain state"
```

---

## Task 3: Rewrite modules/__init__.py

**Files:**
- Modify: `modules/__init__.py` (replace entirely)

**Step 1: Replace modules/__init__.py with minimal exports**

```python
# modules/__init__.py
"""
Bolor Brain - Pure Intelligence Modules
========================================

Reasoning Engines:
- SymbolicReasoner: Forward/backward chaining with rules and facts
- KnowledgeGraph: Graph-based knowledge with traversal and inference
- CaseBasedReasoner: Experience-based reasoning with 4R cycle
- HypothesisEngine: Hypothesis generation and testing
- AnalogicalReasoner: Cross-domain pattern transfer
- HybridReasoner: Orchestrates all reasoning approaches

Configuration:
- Config: Central configuration dataclass
"""

# Configuration
from .config import Config, get_config, set_config, validate_python_version

# Reasoning Engines
from .reasoning_engines import (
    SymbolicReasoner,
    Fact,
    FactType,
    Rule,
    ReasoningResult,
    KnowledgeGraph,
    Node,
    Edge,
    PathResult,
    CaseBasedReasoner,
    Case,
    CaseMatch,
    CaseReasoningResult,
    HypothesisEngine,
    Hypothesis,
    HypothesisTest,
    AnalogicalReasoner,
    Concept,
    Analogy,
    AnalogicalMapping,
    MappingType,
    HybridReasoner,
    HybridReasoningResult,
    ReasoningApproach,
    ProblemType,
)

__all__ = [
    "Config", "get_config", "set_config", "validate_python_version",
    "SymbolicReasoner", "Fact", "FactType", "Rule", "ReasoningResult",
    "KnowledgeGraph", "Node", "Edge", "PathResult",
    "CaseBasedReasoner", "Case", "CaseMatch", "CaseReasoningResult",
    "HypothesisEngine", "Hypothesis", "HypothesisTest",
    "AnalogicalReasoner", "Concept", "Analogy", "AnalogicalMapping", "MappingType",
    "HybridReasoner", "HybridReasoningResult", "ReasoningApproach", "ProblemType",
]
```

**Step 2: Run existing reasoning engine tests to verify nothing broke**

Run: `python -m pytest tests/test_symbolic_reasoner.py tests/test_knowledge_graph.py tests/test_case_based_reasoner.py tests/test_hypothesis_engine.py tests/test_analogical_reasoner.py tests/test_hybrid_reasoner.py -v`
Expected: ALL PASS (reasoning engines are untouched)

**Step 3: Commit**

```bash
git add modules/__init__.py
git commit -m "refactor: Strip modules/__init__.py to reasoning engines + config only"
```

---

## Task 4: Simplify modules/config.py

**Files:**
- Modify: `modules/config.py` (remove GUARDRAILS_CONFIG and unused LLM/embedding settings)

**Step 1: Remove GUARDRAILS_CONFIG from config.py**

Remove lines 301-314 (the `GUARDRAILS_CONFIG` dict). This was only used by autonomous_loop.py which we're deleting.

Also remove LLM-related fields, embedding fields, framework_enabled_tiers, and their validators since the new architecture doesn't use them. Keep `reasoning_max_depth`, `learning_rate`, `debug`, and `from_env`.

The simplified Config should only have:
- `reasoning_max_depth: int = 10`
- `learning_rate: float = 0.1`
- `persistence_dir: str = "~/.bolor-brain"`
- `debug: bool = False`

**Step 2: Run config test**

Run: `python -m pytest tests/test_config.py -v`
Expected: Some tests will fail (they test LLM config). This is expected — update the test in next step.

**Step 3: Update tests/test_config.py to match simplified config**

Remove tests for LLM provider validation, embedding settings, genome, and llm_bridge. Keep tests for reasoning_max_depth, learning_rate, and from_env.

**Step 4: Run config test again**

Run: `python -m pytest tests/test_config.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add modules/config.py tests/test_config.py
git commit -m "refactor: Simplify config to reasoning + persistence settings only"
```

---

## Task 5: Rewrite mcp_server.py

**Files:**
- Modify: `mcp_server.py` (replace entirely)

**Step 1: Write the new MCP server**

The new server has 11 tools:
- `reason` (hybrid), `reason_symbolic`, `reason_graph`, `reason_cases`, `reason_hypothesis`, `reason_analogy`
- `remember`, `recall`, `learn`, `forget`
- `brain_stats`

Key changes from current:
- Remove ALL autonomous tool definitions and handlers (run_autonomous, get_autonomous_status, pause, resume, stop)
- Remove imports of autonomous_loop, task_scheduler, goal_decomposer
- Add persistence import and load on startup
- Add memory tools (remember, recall, learn, forget)
- Add persistence hooks (save after every write)

The tool implementations for reasoning stay almost identical to current code (lines 472-669 of current mcp_server.py). The new additions are the memory tools that use persistence.py.

**Step 2: Write integration test**

```python
# tests/test_mcp_server_tools.py
"""Test that MCP server tools work end-to-end."""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import BolorBrainServer


@pytest.fixture
def server(tmp_path):
    """Create server with temp persistence dir."""
    os.environ["BOLOR_PERSISTENCE_DIR"] = str(tmp_path / "brain")
    s = BolorBrainServer()
    yield s
    if "BOLOR_PERSISTENCE_DIR" in os.environ:
        del os.environ["BOLOR_PERSISTENCE_DIR"]


class TestReasoningTools:
    @pytest.mark.asyncio
    async def test_reason_hybrid(self, server):
        result = await server._reason_hybrid({"query": "Is Python good for AI?"})
        assert "problem_type" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_reason_symbolic(self, server):
        result = await server._reason_symbolic({
            "query": "test",
            "facts": [["python", "is", "language"]],
            "mode": "forward",
        })
        assert "mode" in result

    @pytest.mark.asyncio
    async def test_reason_hypothesis(self, server):
        result = await server._reason_hypothesis({
            "observation": "Server is slow",
        })
        assert "hypotheses" in result


class TestMemoryTools:
    @pytest.mark.asyncio
    async def test_learn_and_recall(self, server):
        learn_result = await server._learn({
            "problem": {"type": "bug", "error": "timeout"},
            "solution": {"fix": "increase timeout"},
            "outcome": {"success": True},
            "success": True,
        })
        assert learn_result["success"] is True

        recall_result = await server._recall({
            "query": {"type": "bug"},
            "k": 3,
        })
        assert "cases" in recall_result

    @pytest.mark.asyncio
    async def test_remember_fact(self, server):
        result = await server._remember({
            "type": "fact",
            "data": {"subject": "python", "predicate": "is", "object": "language"},
        })
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_brain_stats(self, server):
        stats = await server._brain_stats({})
        assert "cases" in stats
        assert "facts" in stats
```

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v --ignore=tests/test_genome.py --ignore=tests/test_llm_bridge.py`
Expected: ALL PASS

**Step 4: Commit**

```bash
git add mcp_server.py tests/test_mcp_server_tools.py
git commit -m "refactor: Rewrite MCP server with brain-only tools (11 tools, no autonomous)"
```

---

## Task 6: Delete redundant files

**Files to delete:**

Root level (8 files):
- `autonomous_loop.py`
- `claude_code_engine.py`
- `task_scheduler.py`
- `goal_decomposer.py`
- `approval_system.py`
- `state_manager.py`
- `progress_monitor.py`
- `nsaf_client.py`

Modules (10 files):
- `modules/genome.py`
- `modules/drives.py`
- `modules/evolutionary.py`
- `modules/collective.py`
- `modules/orchestration.py`
- `modules/universal.py`
- `modules/predictive.py`
- `modules/metacognitive.py`
- `modules/reasoning.py`
- `modules/llm_bridge.py`
- `modules/embeddings.py`
- `modules/integration.py`

Tests that test deleted modules (3 files):
- `tests/test_genome.py`
- `tests/test_llm_bridge.py`
- `tests/conftest.py` (references genome + llm_bridge, needs rewrite)

Root-level test files (6 files):
- `test_real_autonomous.py`
- `test_approval.py`
- `test_persistent.py` (if exists)
- `test_nsaf_integration.py`
- `test_autonomous_debugging.py` (if exists)
- `test_autonomous_optimization.py` (if exists)
- `test_web_scraping.py`

**Step 1: Delete root-level execution files**

```bash
git rm autonomous_loop.py claude_code_engine.py task_scheduler.py goal_decomposer.py approval_system.py state_manager.py progress_monitor.py nsaf_client.py
```

**Step 2: Delete unused module files**

```bash
git rm modules/genome.py modules/drives.py modules/evolutionary.py modules/collective.py modules/orchestration.py modules/universal.py modules/predictive.py modules/metacognitive.py modules/reasoning.py modules/llm_bridge.py modules/embeddings.py modules/integration.py
```

**Step 3: Delete obsolete tests**

```bash
git rm tests/test_genome.py tests/test_llm_bridge.py
git rm -f test_real_autonomous.py test_approval.py test_persistent.py test_nsaf_integration.py test_autonomous_debugging.py test_autonomous_optimization.py test_web_scraping.py
```

**Step 4: Rewrite tests/conftest.py**

```python
# tests/conftest.py
"""Pytest configuration and fixtures for Bolor Brain MCP tests."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config


@pytest.fixture
def config():
    """Provide default config for tests."""
    return Config()


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
```

**Step 5: Run all remaining tests**

Run: `python -m pytest tests/ -v`
Expected: ALL PASS (only reasoning engine tests + persistence + config + server tests remain)

**Step 6: Commit**

```bash
git add -A
git commit -m "refactor: Delete 20 redundant files - Claude Code handles execution"
```

---

## Task 7: Update pyproject.toml and __main__.py

**Files:**
- Modify: `pyproject.toml`
- Modify: `__main__.py`

**Step 1: Update pyproject.toml**

Remove `requests` from implied dependencies (was used by claude_code_engine). Add `pytest-asyncio` for async tests. Keep `mcp>=1.0.0` as only runtime dependency.

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.23.0",
]
```

**Step 2: Simplify __main__.py**

```python
"""
Bolor Brain MCP Server - Pure Intelligence
"""

from mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 3: Verify MCP server starts**

Run: `timeout 5 python -m mcp_server 2>&1 || true`
Expected: Should start without import errors (will hang waiting for stdio, that's fine)

**Step 4: Commit**

```bash
git add pyproject.toml __main__.py
git commit -m "chore: Update pyproject.toml and entry point for pure intelligence"
```

---

## Task 8: Rewrite skills

**Files:**
- Modify: `skills/reason.md`
- Modify: `skills/debug.md`
- Modify: `skills/decide.md`
- Modify: `skills/learn-from.md`
- Delete: `skills/autonomous.md`
- Delete: `skills/nsaf.md`
- Delete: `skills/orchestrate.md`

**Step 1: Delete obsolete skills**

```bash
git rm skills/autonomous.md skills/nsaf.md skills/orchestrate.md
```

**Step 2: Rewrite skills/reason.md**

Core message: When user needs deep analysis, call Bolor Brain's `reason` tool. Present the structured result. Let Claude Code handle everything else.

**Step 3: Rewrite skills/debug.md**

Core message: For debugging, call `reason_hypothesis` with observation + evidence, then `recall` for similar bugs. After fix, call `learn` to store the solution.

**Step 4: Rewrite skills/decide.md**

Core message: For decisions, call `reason` with full context. Present trade-offs from multiple reasoning approaches. After decision, call `remember` to store it.

**Step 5: Rewrite skills/learn-from.md**

Core message: After completing any task, call `learn` with problem/solution/outcome. Brain persists it for future retrieval.

**Step 6: Commit**

```bash
git add skills/
git commit -m "refactor: Rewrite skills for Claude Code as gateway"
```

---

## Task 9: Final verification

**Step 1: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: ALL PASS

**Step 2: Verify MCP server imports cleanly**

Run: `python -c "from mcp_server import BolorBrainServer; print('OK')"`
Expected: `OK`

**Step 3: Verify no import of deleted modules**

Run: `grep -r "autonomous_loop\|claude_code_engine\|task_scheduler\|goal_decomposer\|approval_system\|state_manager\|progress_monitor\|nsaf_client" --include="*.py" . | grep -v __pycache__ | grep -v .git`
Expected: No matches (or only in test files/docs)

**Step 4: Count remaining Python files**

Run: `find . -name "*.py" -not -path "./__pycache__/*" -not -path "./.git/*" -not -path "./dist/*" | wc -l`
Expected: ~16-18 files (down from 58)

**Step 5: Commit any fixes**

```bash
git add -A
git commit -m "chore: Final cleanup for pure intelligence refactor"
```

---

## Task 10: Update README and docs

**Files:**
- Modify: `README.md`
- Modify: `skills/README.md`
- Delete obsolete docs: `AUTONOMOUS_AGENT.md`, `AGENT_GUARDRAILS.md`, `STATUS.md` (if they reference deleted features)

**Step 1: Update README.md header and description**

Change from "autonomous agent framework" to "pure intelligence MCP server". Update architecture diagram. Update tool list. Remove references to autonomous loop, OpenClaw comparison, etc.

**Step 2: Clean up obsolete docs**

```bash
git rm -f AUTONOMOUS_AGENT.md AGENT_GUARDRAILS.md STATUS.md TESTING_GUIDE.md GENERATED_OUTPUT.md GETTING_STARTED.md
```

**Step 3: Commit**

```bash
git add -A
git commit -m "docs: Update README and remove obsolete docs for pure intelligence"
```

---

## Summary: What We End Up With

```
bolor-brain-mcp/
├── mcp_server.py              # MCP server (11 brain tools)
├── persistence.py             # JSON persistence to ~/.bolor-brain/
├── __main__.py                # Entry point
├── pyproject.toml             # Package config
├── modules/
│   ├── __init__.py            # Minimal exports
│   ├── config.py              # Simplified config
│   └── reasoning_engines/
│       ├── __init__.py
│       ├── symbolic_reasoner.py
│       ├── knowledge_graph.py
│       ├── case_based_reasoner.py
│       ├── hypothesis_engine.py
│       ├── analogical_reasoner.py
│       └── hybrid_reasoner.py
├── tests/
│   ├── conftest.py
│   ├── test_persistence.py
│   ├── test_mcp_server_tools.py
│   ├── test_config.py
│   ├── test_symbolic_reasoner.py
│   ├── test_knowledge_graph.py
│   ├── test_case_based_reasoner.py
│   ├── test_hypothesis_engine.py
│   ├── test_analogical_reasoner.py
│   └── test_hybrid_reasoner.py
├── skills/
│   ├── README.md
│   ├── reason.md
│   ├── debug.md
│   ├── decide.md
│   └── learn-from.md
├── docs/
│   └── plans/
│       ├── 2026-02-12-pure-intelligence-refactor-design.md
│       └── 2026-02-12-pure-intelligence-implementation.md
└── README.md
```

**~20 files total. Down from 58. Pure brain. No body.**
