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

from .knowledge_graph import (
    KnowledgeGraph,
    Node,
    Edge,
    PathResult,
)

from .case_based_reasoner import (
    CaseBasedReasoner,
    Case,
    CaseMatch,
    CaseReasoningResult,
)

from .hypothesis_engine import (
    HypothesisEngine,
    Hypothesis,
    HypothesisTest,
)

__all__ = [
    # Symbolic Reasoner
    "SymbolicReasoner",
    "Fact",
    "FactType",
    "Rule",
    "ReasoningResult",
    # Knowledge Graph
    "KnowledgeGraph",
    "Node",
    "Edge",
    "PathResult",
    # Case-Based Reasoner
    "CaseBasedReasoner",
    "Case",
    "CaseMatch",
    "CaseReasoningResult",
    # Hypothesis Engine
    "HypothesisEngine",
    "Hypothesis",
    "HypothesisTest",
]
