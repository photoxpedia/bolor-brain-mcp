"""Reasoning engines for the Universal Thinking MCP.

This module provides multiple reasoning approaches:
- SymbolicReasoner: Forward/backward chaining with rules and facts
- KnowledgeGraph: Graph-based knowledge with traversal and inference
- CaseBasedReasoner: Experience-based reasoning with 4R cycle
- HypothesisEngine: Hypothesis generation and testing
- AnalogicalReasoner: Cross-domain pattern transfer
- HybridReasoner: Orchestrates all approaches
"""

from .symbolic_reasoner import (
    SymbolicReasoner,
    Fact,
    FactType,
    Rule,
    ReasoningResult,
)

__all__ = [
    # Symbolic Reasoner
    "SymbolicReasoner",
    "Fact",
    "FactType",
    "Rule",
    "ReasoningResult",
]
