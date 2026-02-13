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
"""

from .config import Config, get_config, set_config, validate_python_version

from .reasoning_engines import (
    SymbolicReasoner, Fact, FactType, Rule, ReasoningResult,
    KnowledgeGraph, Node, Edge, PathResult,
    CaseBasedReasoner, Case, CaseMatch, CaseReasoningResult,
    HypothesisEngine, Hypothesis, HypothesisTest,
    AnalogicalReasoner, Concept, Analogy, AnalogicalMapping, MappingType,
    HybridReasoner, HybridReasoningResult, ReasoningApproach, ProblemType,
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
