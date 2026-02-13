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
