# Phase 2: Reasoning Core Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the complete reasoning core with 6 reasoning engines that work together.

**Architecture:** Layered reasoning with SymbolicReasoner and KnowledgeGraph as foundation, CaseBasedReasoner for experience-based reasoning, HypothesisEngine and AnalogicalReasoner for advanced inference, and HybridReasoner to orchestrate all approaches.

**Tech Stack:** Python 3.11+, dataclasses, typing, threading (for thread safety)

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HybridReasoner                                │
│              (Orchestrates all reasoning approaches)                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ HypothesisEngine │  │AnalogicalReasoner│  │ CaseBasedReasoner│  │
│  │   (Hypotheses)   │  │ (Cross-domain)   │  │   (Experience)   │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │            │
│           └─────────────────────┼─────────────────────┘            │
│                                 │                                   │
│  ┌──────────────────────────────┴──────────────────────────────┐   │
│  │                    KnowledgeGraph                            │   │
│  │         (Nodes, edges, BFS, PageRank, inference)            │   │
│  └──────────────────────────────┬──────────────────────────────┘   │
│                                 │                                   │
│  ┌──────────────────────────────┴──────────────────────────────┐   │
│  │                   SymbolicReasoner                           │   │
│  │          (Forward/backward chaining, rules, facts)          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Task 1: Create SymbolicReasoner

**Files:**
- Create: `modules/reasoning/symbolic_reasoner.py`
- Create: `modules/reasoning/__init__.py`
- Test: `tests/test_symbolic_reasoner.py`

### Step 1: Create reasoning module structure

```python
# modules/reasoning/__init__.py
"""Reasoning engines for the Universal Thinking MCP."""
```

### Step 2: Define data structures

```python
# modules/reasoning/symbolic_reasoner.py
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum

class FactType(Enum):
    """Types of facts in the knowledge base."""
    ASSERTION = "assertion"      # X is Y
    RELATION = "relation"        # X relates to Y
    PROPERTY = "property"        # X has property P
    NEGATION = "negation"        # X is not Y

@dataclass
class Fact:
    """A fact in the knowledge base."""
    subject: str
    predicate: str
    object: Any
    fact_type: FactType = FactType.ASSERTION
    confidence: float = 1.0
    source: str = "system"
    timestamp: float = field(default_factory=lambda: time.time())

@dataclass
class Rule:
    """An inference rule: if conditions then conclusion."""
    name: str
    conditions: list[Callable[[dict[str, Fact]], bool]]
    conclusion: Callable[[dict[str, Fact]], Fact]
    priority: int = 0
    enabled: bool = True
```

### Step 3: Implement SymbolicReasoner class

```python
class SymbolicReasoner:
    """
    Symbolic reasoning engine using forward and backward chaining.

    Features:
    - Fact storage with confidence tracking
    - Rule-based inference
    - Forward chaining (data-driven)
    - Backward chaining (goal-driven)
    - Conflict resolution via priority
    """

    def __init__(self, genome: Optional[CognitiveGenome] = None):
        self.facts: dict[str, Fact] = {}
        self.rules: list[Rule] = []
        self.genome = genome
        self._lock = threading.RLock()

    def add_fact(self, fact: Fact) -> bool: ...
    def remove_fact(self, fact_id: str) -> bool: ...
    def get_fact(self, fact_id: str) -> Optional[Fact]: ...
    def query_facts(self, predicate: str = None, subject: str = None) -> list[Fact]: ...

    def add_rule(self, rule: Rule) -> None: ...
    def remove_rule(self, name: str) -> bool: ...

    def forward_chain(self, max_iterations: int = 100) -> list[Fact]: ...
    def backward_chain(self, goal: Fact, max_depth: int = 10) -> tuple[bool, list[Fact]]: ...

    def reason(self, query: str, mode: str = "forward") -> ReasoningResult: ...
```

### Step 4: Write tests

```python
# tests/test_symbolic_reasoner.py
class TestFactCreation:
    def test_fact_creation(self): ...
    def test_fact_types(self): ...

class TestSymbolicReasonerBasics:
    def test_add_and_get_fact(self): ...
    def test_query_facts_by_predicate(self): ...
    def test_add_rule(self): ...

class TestForwardChaining:
    def test_simple_forward_chain(self): ...
    def test_forward_chain_with_multiple_rules(self): ...
    def test_forward_chain_respects_max_iterations(self): ...

class TestBackwardChaining:
    def test_simple_backward_chain(self): ...
    def test_backward_chain_with_depth_limit(self): ...
    def test_backward_chain_returns_proof_path(self): ...

class TestThreadSafety:
    def test_concurrent_fact_addition(self): ...
```

### Expected Outcome
- SymbolicReasoner with ~400 lines of code
- Forward and backward chaining working
- Thread-safe operations
- 20+ tests passing

---

## Task 2: Create KnowledgeGraph

**Files:**
- Create: `modules/reasoning/knowledge_graph.py`
- Test: `tests/test_knowledge_graph.py`

### Step 1: Define graph data structures

```python
@dataclass
class Node:
    """A node in the knowledge graph."""
    id: str
    label: str
    node_type: str
    properties: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # For PageRank

@dataclass
class Edge:
    """An edge connecting two nodes."""
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
```

### Step 2: Implement KnowledgeGraph class

```python
class KnowledgeGraph:
    """
    Knowledge graph with inference capabilities.

    Features:
    - Node and edge management
    - BFS/DFS traversal
    - PageRank for node importance
    - Path finding
    - Pattern matching
    - Inference rules
    """

    def __init__(self, genome: Optional[CognitiveGenome] = None):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.adjacency: dict[str, list[str]] = {}  # For fast traversal
        self.genome = genome
        self._lock = threading.RLock()

    # Node operations
    def add_node(self, node: Node) -> bool: ...
    def get_node(self, node_id: str) -> Optional[Node]: ...
    def remove_node(self, node_id: str) -> bool: ...
    def query_nodes(self, node_type: str = None, **properties) -> list[Node]: ...

    # Edge operations
    def add_edge(self, edge: Edge) -> bool: ...
    def get_edges(self, source: str = None, target: str = None) -> list[Edge]: ...
    def remove_edge(self, source: str, target: str, relation: str = None) -> bool: ...

    # Traversal
    def bfs(self, start: str, max_depth: int = 10) -> list[str]: ...
    def dfs(self, start: str, max_depth: int = 10) -> list[str]: ...
    def find_path(self, start: str, end: str) -> Optional[list[str]]: ...
    def find_all_paths(self, start: str, end: str, max_paths: int = 10) -> list[list[str]]: ...

    # Analysis
    def pagerank(self, iterations: int = 20, damping: float = 0.85) -> dict[str, float]: ...
    def get_neighbors(self, node_id: str, relation: str = None) -> list[str]: ...
    def get_subgraph(self, center: str, radius: int = 2) -> 'KnowledgeGraph': ...

    # Inference
    def infer(self, pattern: dict) -> list[dict]: ...
```

### Step 3: Write tests

```python
class TestNodeOperations:
    def test_add_node(self): ...
    def test_query_nodes_by_type(self): ...

class TestEdgeOperations:
    def test_add_edge(self): ...
    def test_get_edges_by_source(self): ...

class TestTraversal:
    def test_bfs_finds_all_reachable(self): ...
    def test_dfs_respects_depth(self): ...
    def test_find_path_returns_shortest(self): ...

class TestPageRank:
    def test_pagerank_converges(self): ...
    def test_pagerank_identifies_important_nodes(self): ...

class TestInference:
    def test_simple_pattern_match(self): ...
    def test_transitive_inference(self): ...
```

### Expected Outcome
- KnowledgeGraph with ~500 lines of code
- BFS, DFS, PageRank working
- Pattern matching and inference
- 25+ tests passing

---

## Task 3: Create CaseBasedReasoner

**Files:**
- Create: `modules/reasoning/case_based_reasoner.py`
- Test: `tests/test_case_based_reasoner.py`

### Step 1: Define case data structures

```python
@dataclass
class Case:
    """A case for case-based reasoning."""
    id: str
    problem: dict[str, Any]      # Problem description
    solution: dict[str, Any]     # Applied solution
    outcome: Optional[dict[str, Any]] = None  # Result
    success: Optional[bool] = None
    timestamp: float = field(default_factory=lambda: time.time())
    tags: list[str] = field(default_factory=list)

@dataclass
class CaseMatch:
    """A matched case with similarity score."""
    case: Case
    similarity: float
    matching_features: list[str]
    differing_features: list[str]
```

### Step 2: Implement CaseBasedReasoner

```python
class CaseBasedReasoner:
    """
    Case-based reasoning using the 4R cycle:
    Retrieve → Reuse → Revise → Retain

    Features:
    - Case storage with feature extraction
    - Similarity matching (multiple metrics)
    - Solution adaptation
    - Learning from outcomes
    """

    def __init__(self, genome: Optional[CognitiveGenome] = None):
        self.cases: dict[str, Case] = {}
        self.feature_weights: dict[str, float] = {}
        self.genome = genome
        self._lock = threading.RLock()

    # Case management
    def store_case(self, case: Case) -> bool: ...
    def get_case(self, case_id: str) -> Optional[Case]: ...
    def remove_case(self, case_id: str) -> bool: ...

    # 4R Cycle
    def retrieve(self, problem: dict, k: int = 5) -> list[CaseMatch]: ...
    def reuse(self, problem: dict, matched_case: Case) -> dict: ...
    def revise(self, proposed_solution: dict, feedback: dict) -> dict: ...
    def retain(self, problem: dict, solution: dict, outcome: dict) -> Case: ...

    # Similarity
    def compute_similarity(self, problem1: dict, problem2: dict) -> float: ...
    def _feature_similarity(self, val1: Any, val2: Any) -> float: ...

    # Learning
    def update_feature_weights(self, successful_cases: list[Case]) -> None: ...

    # Full reasoning cycle
    def reason(self, problem: dict) -> CaseReasoningResult: ...
```

### Step 3: Write tests

```python
class TestCaseManagement:
    def test_store_and_retrieve_case(self): ...
    def test_case_with_outcome(self): ...

class TestSimilarity:
    def test_identical_problems_full_similarity(self): ...
    def test_partial_match_similarity(self): ...
    def test_no_match_zero_similarity(self): ...

class TestFourRCycle:
    def test_retrieve_returns_k_best(self): ...
    def test_reuse_adapts_solution(self): ...
    def test_revise_incorporates_feedback(self): ...
    def test_retain_stores_new_case(self): ...

class TestLearning:
    def test_feature_weights_update(self): ...
```

### Expected Outcome
- CaseBasedReasoner with ~350 lines of code
- Full 4R cycle working
- Similarity computation with multiple metrics
- 20+ tests passing

---

## Task 4: Create HypothesisEngine

**Files:**
- Create: `modules/reasoning/hypothesis_engine.py`
- Test: `tests/test_hypothesis_engine.py`

### Step 1: Define hypothesis data structures

```python
@dataclass
class Hypothesis:
    """A hypothesis to be tested."""
    id: str
    statement: str
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    confidence: float = 0.5
    status: str = "untested"  # untested, supported, refuted, inconclusive

@dataclass
class HypothesisTest:
    """Result of testing a hypothesis."""
    hypothesis_id: str
    test_type: str
    evidence_found: list[str]
    supports: bool
    confidence_delta: float
```

### Step 2: Implement HypothesisEngine

```python
class HypothesisEngine:
    """
    Hypothesis generation and testing engine.

    Uses KnowledgeGraph paths to:
    - Generate hypotheses from patterns
    - Find evidence for/against
    - Update confidence based on evidence
    """

    def __init__(self, knowledge_graph: KnowledgeGraph,
                 symbolic_reasoner: SymbolicReasoner,
                 genome: Optional[CognitiveGenome] = None):
        self.kg = knowledge_graph
        self.reasoner = symbolic_reasoner
        self.hypotheses: dict[str, Hypothesis] = {}
        self.genome = genome
        self._lock = threading.RLock()

    # Hypothesis management
    def create_hypothesis(self, statement: str, initial_evidence: list[str] = None) -> Hypothesis: ...
    def get_hypothesis(self, hyp_id: str) -> Optional[Hypothesis]: ...

    # Generation
    def generate_hypotheses(self, observation: str, max_hypotheses: int = 5) -> list[Hypothesis]: ...
    def _find_causal_paths(self, observation: str) -> list[list[str]]: ...
    def _path_to_hypothesis(self, path: list[str]) -> Hypothesis: ...

    # Testing
    def test_hypothesis(self, hyp_id: str) -> HypothesisTest: ...
    def find_evidence(self, hypothesis: Hypothesis) -> tuple[list[str], list[str]]: ...
    def update_confidence(self, hyp_id: str, test_result: HypothesisTest) -> float: ...

    # Ranking
    def rank_hypotheses(self, hypotheses: list[Hypothesis]) -> list[Hypothesis]: ...
    def get_best_hypothesis(self, observation: str) -> Optional[Hypothesis]: ...
```

### Step 3: Write tests

```python
class TestHypothesisCreation:
    def test_create_hypothesis(self): ...
    def test_hypothesis_with_initial_evidence(self): ...

class TestHypothesisGeneration:
    def test_generate_from_observation(self): ...
    def test_generate_respects_max(self): ...

class TestHypothesisTesting:
    def test_find_supporting_evidence(self): ...
    def test_find_contradicting_evidence(self): ...
    def test_confidence_increases_with_support(self): ...
    def test_confidence_decreases_with_contradiction(self): ...

class TestHypothesisRanking:
    def test_rank_by_confidence(self): ...
    def test_get_best_hypothesis(self): ...
```

### Expected Outcome
- HypothesisEngine with ~300 lines of code
- Hypothesis generation from KG paths
- Evidence-based confidence updates
- 15+ tests passing

---

## Task 5: Create AnalogicalReasoner

**Files:**
- Create: `modules/reasoning/analogical_reasoner.py`
- Test: `tests/test_analogical_reasoner.py`

### Step 1: Define analogy data structures

```python
@dataclass
class Analogy:
    """An analogy between two domains."""
    id: str
    source_domain: str
    target_domain: str
    mappings: dict[str, str]  # source_concept -> target_concept
    structural_similarity: float
    confidence: float = 0.5

@dataclass
class AnalogicalInference:
    """An inference made through analogy."""
    analogy_id: str
    source_fact: str
    inferred_fact: str
    confidence: float
```

### Step 2: Implement AnalogicalReasoner

```python
class AnalogicalReasoner:
    """
    Cross-domain analogical reasoning.

    Features:
    - Structure mapping between domains
    - Analogy-based inference
    - Transfer learning between domains
    """

    def __init__(self, knowledge_graph: KnowledgeGraph,
                 genome: Optional[CognitiveGenome] = None):
        self.kg = knowledge_graph
        self.analogies: dict[str, Analogy] = {}
        self.genome = genome
        self._lock = threading.RLock()

    # Analogy management
    def create_analogy(self, source: str, target: str, mappings: dict) -> Analogy: ...
    def find_analogies(self, domain: str) -> list[Analogy]: ...

    # Structure mapping
    def compute_structural_similarity(self, domain1: str, domain2: str) -> float: ...
    def find_mappings(self, source_domain: str, target_domain: str) -> dict[str, str]: ...
    def _extract_structure(self, domain: str) -> dict: ...

    # Inference
    def infer_by_analogy(self, analogy: Analogy, source_fact: str) -> AnalogicalInference: ...
    def transfer_knowledge(self, source: str, target: str) -> list[AnalogicalInference]: ...

    # Evaluation
    def evaluate_analogy(self, analogy: Analogy) -> float: ...
```

### Step 3: Write tests

```python
class TestAnalogyCreation:
    def test_create_analogy(self): ...
    def test_analogy_mappings(self): ...

class TestStructureMapping:
    def test_structural_similarity_identical(self): ...
    def test_structural_similarity_partial(self): ...
    def test_find_mappings(self): ...

class TestAnalogicalInference:
    def test_simple_inference(self): ...
    def test_transfer_knowledge(self): ...
    def test_inference_confidence(self): ...
```

### Expected Outcome
- AnalogicalReasoner with ~250 lines of code
- Structure mapping between domains
- Analogy-based inference working
- 12+ tests passing

---

## Task 6: Create HybridReasoner

**Files:**
- Create: `modules/reasoning/hybrid_reasoner.py`
- Update: `modules/reasoning/__init__.py`
- Test: `tests/test_hybrid_reasoner.py`

### Step 1: Implement HybridReasoner

```python
@dataclass
class ReasoningResult:
    """Result from hybrid reasoning."""
    conclusion: str
    confidence: float
    reasoning_chain: list[str]
    methods_used: list[str]
    evidence: list[str]
    alternatives: list[str] = field(default_factory=list)

class HybridReasoner:
    """
    Hybrid reasoning engine that combines all approaches.

    Orchestrates:
    - SymbolicReasoner for logical inference
    - KnowledgeGraph for relationship queries
    - CaseBasedReasoner for experience-based solutions
    - HypothesisEngine for hypothesis generation
    - AnalogicalReasoner for cross-domain transfer
    """

    def __init__(self, genome: Optional[CognitiveGenome] = None):
        self.genome = genome or CognitiveGenome()

        # Initialize components
        self.symbolic = SymbolicReasoner(genome)
        self.kg = KnowledgeGraph(genome)
        self.case_based = CaseBasedReasoner(genome)
        self.hypothesis = HypothesisEngine(self.kg, self.symbolic, genome)
        self.analogical = AnalogicalReasoner(self.kg, genome)

        self._lock = threading.RLock()

    # Main reasoning interface
    def reason(self, query: str, context: dict = None,
               mode: str = "auto") -> ReasoningResult: ...

    # Mode selection
    def _select_mode(self, query: str, context: dict) -> str: ...
    def _classify_query(self, query: str) -> str: ...

    # Individual reasoning modes
    def _symbolic_reasoning(self, query: str, context: dict) -> ReasoningResult: ...
    def _case_based_reasoning(self, query: str, context: dict) -> ReasoningResult: ...
    def _hypothesis_reasoning(self, query: str, context: dict) -> ReasoningResult: ...
    def _analogical_reasoning(self, query: str, context: dict) -> ReasoningResult: ...

    # Hybrid combination
    def _combine_results(self, results: list[ReasoningResult]) -> ReasoningResult: ...
    def _resolve_conflicts(self, results: list[ReasoningResult]) -> ReasoningResult: ...

    # Learning
    def learn_from_outcome(self, query: str, result: ReasoningResult,
                          actual_outcome: dict) -> None: ...
```

### Step 2: Update module exports

```python
# modules/reasoning/__init__.py
"""Reasoning engines for the Universal Thinking MCP."""

from .symbolic_reasoner import (
    SymbolicReasoner,
    Fact,
    FactType,
    Rule,
)
from .knowledge_graph import (
    KnowledgeGraph,
    Node,
    Edge,
)
from .case_based_reasoner import (
    CaseBasedReasoner,
    Case,
    CaseMatch,
)
from .hypothesis_engine import (
    HypothesisEngine,
    Hypothesis,
    HypothesisTest,
)
from .analogical_reasoner import (
    AnalogicalReasoner,
    Analogy,
    AnalogicalInference,
)
from .hybrid_reasoner import (
    HybridReasoner,
    ReasoningResult,
)

__all__ = [
    # Symbolic
    "SymbolicReasoner", "Fact", "FactType", "Rule",
    # Knowledge Graph
    "KnowledgeGraph", "Node", "Edge",
    # Case-Based
    "CaseBasedReasoner", "Case", "CaseMatch",
    # Hypothesis
    "HypothesisEngine", "Hypothesis", "HypothesisTest",
    # Analogical
    "AnalogicalReasoner", "Analogy", "AnalogicalInference",
    # Hybrid
    "HybridReasoner", "ReasoningResult",
]
```

### Step 3: Write tests

```python
class TestHybridReasonerInit:
    def test_creates_all_components(self): ...
    def test_components_share_knowledge_graph(self): ...

class TestModeSelection:
    def test_auto_selects_symbolic_for_logical(self): ...
    def test_auto_selects_case_for_similar_problems(self): ...
    def test_auto_selects_hypothesis_for_uncertain(self): ...

class TestHybridReasoning:
    def test_combines_multiple_approaches(self): ...
    def test_resolves_conflicts_by_confidence(self): ...
    def test_returns_reasoning_chain(self): ...

class TestLearning:
    def test_learns_from_outcome(self): ...
    def test_updates_case_base(self): ...
```

### Expected Outcome
- HybridReasoner with ~400 lines of code
- All reasoning components integrated
- Mode auto-selection working
- 15+ tests passing

---

## Task 7: Update Main Module Exports

**Files:**
- Update: `modules/__init__.py`

### Step 1: Add reasoning exports

Add to `modules/__init__.py`:

```python
# Reasoning engines
from .reasoning import (
    # Symbolic
    SymbolicReasoner,
    Fact,
    FactType,
    Rule,
    # Knowledge Graph
    KnowledgeGraph,
    Node,
    Edge,
    # Case-Based
    CaseBasedReasoner,
    Case,
    CaseMatch,
    # Hypothesis
    HypothesisEngine,
    Hypothesis,
    HypothesisTest,
    # Analogical
    AnalogicalReasoner,
    Analogy,
    AnalogicalInference,
    # Hybrid
    HybridReasoner,
    ReasoningResult,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    # Reasoning
    "SymbolicReasoner", "Fact", "FactType", "Rule",
    "KnowledgeGraph", "Node", "Edge",
    "CaseBasedReasoner", "Case", "CaseMatch",
    "HypothesisEngine", "Hypothesis", "HypothesisTest",
    "AnalogicalReasoner", "Analogy", "AnalogicalInference",
    "HybridReasoner", "ReasoningResult",
]
```

---

## Task 8: Verify Phase 2 Complete

### Step 1: Run full test suite

```bash
python -m pytest tests/ -v --tb=short
```

Expected: All tests pass (101 Phase 1 + ~107 Phase 2 = ~208 total)

### Step 2: Verify imports

```python
python -c "
from modules import (
    SymbolicReasoner, KnowledgeGraph, CaseBasedReasoner,
    HypothesisEngine, AnalogicalReasoner, HybridReasoner
)
print('Phase 2 imports OK')
"
```

### Step 3: Create git tag

```bash
git tag -a v2.0.0-phase2 -m "Phase 2: Reasoning Core complete"
```

---

## Summary

| Task | Component | Est. Lines | Est. Tests |
|------|-----------|------------|------------|
| 1 | SymbolicReasoner | ~400 | 20+ |
| 2 | KnowledgeGraph | ~500 | 25+ |
| 3 | CaseBasedReasoner | ~350 | 20+ |
| 4 | HypothesisEngine | ~300 | 15+ |
| 5 | AnalogicalReasoner | ~250 | 12+ |
| 6 | HybridReasoner | ~400 | 15+ |
| 7 | Module Exports | ~50 | - |
| 8 | Verification | - | - |
| **Total** | | **~2,250** | **~107** |

**Key Principles:**
- All components use genome for configurable parameters
- Thread-safe with RLock
- Each component can work independently
- HybridReasoner orchestrates all approaches
- Full TDD approach
