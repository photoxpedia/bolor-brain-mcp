# HybridReasoner

Orchestrates multiple reasoning approaches to solve problems.

## Overview

The `HybridReasoner` automatically selects and combines reasoning strategies based on problem type. It coordinates:

- Symbolic reasoning (forward/backward chaining)
- Knowledge graph traversal
- Case-based reasoning (4R cycle)
- Hypothesis testing
- Analogical reasoning

## Quick Start

```python
from modules import HybridReasoner

brain = HybridReasoner()
result = brain.reason({"query": "What causes X?", "type": "diagnosis"})

print(result.combined_result)
print(f"Confidence: {result.confidence}")
print(f"Approaches used: {result.approaches_used}")
```

## Problem Types

The reasoner auto-detects problem types from keywords:

| Type | Keywords | Primary Approaches |
|------|----------|-------------------|
| `DEDUCTION` | therefore, conclude, deduce | Symbolic, Graph |
| `INDUCTION` | patterns, examples | Case-based, Graph |
| `ABDUCTION` | why, cause, explain | Hypothesis, Symbolic |
| `ANALOGY` | like, similar | Analogical, Case-based |
| `CLASSIFICATION` | classify, categorize, type of | Case-based, Symbolic |
| `PLANNING` | how to, steps, plan | Graph, Case-based |
| `DIAGNOSIS` | diagnose, symptom, problem with | Hypothesis, Case-based |
| `EXPLORATION` | what, find, discover | Graph, Analogical |

## API Reference

### Constructor

```python
HybridReasoner(
    symbolic_reasoner=None,    # Custom SymbolicReasoner
    knowledge_graph=None,       # Custom KnowledgeGraph
    case_reasoner=None,         # Custom CaseBasedReasoner
    hypothesis_engine=None,     # Custom HypothesisEngine
    analogical_reasoner=None,   # Custom AnalogicalReasoner
    genome=None                 # CognitiveGenome for tuning
)
```

### Main Methods

#### `reason(problem, approaches=None, max_approaches=3)`

Full reasoning with multiple approaches.

**Args:**
- `problem`: Dict with `query`, optional `type`, `context`, `goal`
- `approaches`: Specific `ReasoningApproach` list, or auto-select
- `max_approaches`: Max approaches to combine (default: 3)

**Returns:** `HybridReasoningResult`

```python
result = brain.reason({
    "query": "Why does the system crash?",
    "context": {"symptoms": ["memory leak", "high CPU"]},
    "goal": "find root cause"
})
```

#### `quick_reason(query)`

Minimal config, returns best result directly.

```python
answer = brain.quick_reason("What causes memory leaks?")
```

### Adding Knowledge

```python
# Add to symbolic reasoner
brain.add_fact(Fact("python", "is_a", "programming_language"))
brain.add_rule(rule)

# Add to knowledge graph
brain.add_node(Node("n1", "Python", "language"))
brain.add_edge(Edge("n1", "n2", "used_for"))

# Add to case base
brain.add_case(Case(id="c1", problem={...}, solution={...}))

# Add to analogical reasoner
brain.add_concept(Concept(id="sun", name="Sun", domain="solar_system"))
```

### Configuration

```python
# Adjust approach weights (0-1)
brain.set_approach_weight(ReasoningApproach.SYMBOLIC, 0.9)
brain.set_approach_weight(ReasoningApproach.CASE_BASED, 0.8)

# Get current weights
weights = brain.get_approach_weights()
```

### Statistics

```python
stats = brain.get_stats()
# {
#   "total_problems": 42,
#   "by_type": {"diagnosis": 15, "exploration": 27},
#   "by_approach": {"symbolic": 30, "case_based": 25},
#   "avg_confidence": 0.73,
#   "component_stats": {
#     "symbolic_facts": 100,
#     "kg_nodes": 50,
#     "cbr_cases": 25,
#     ...
#   }
# }
```

## HybridReasoningResult

```python
@dataclass
class HybridReasoningResult:
    problem: dict              # Original problem
    problem_type: ProblemType  # Detected type
    approaches_used: list      # ReasoningApproach list
    results: dict              # Results per approach
    combined_result: Any       # Final combined answer
    confidence: float          # Overall confidence (0-1)
    reasoning_trace: list      # Step-by-step trace
    processing_time: float     # Seconds elapsed
```

## Example: Diagnosis Problem

```python
from modules import HybridReasoner, Fact, Case, Node, Edge

brain = HybridReasoner()

# Add domain knowledge
brain.add_fact(Fact("memory_leak", "causes", "high_memory"))
brain.add_fact(Fact("high_memory", "leads_to", "crash"))

brain.add_node(Node("ml", "Memory Leak", "issue"))
brain.add_node(Node("crash", "System Crash", "symptom"))
brain.add_edge(Edge("ml", "crash", "causes"))

brain.add_case(Case(
    id="past_crash",
    problem={"symptom": "crash", "context": "high load"},
    solution={"action": "restart_service", "fix": "memory_limit"},
    success=True
))

# Diagnose
result = brain.reason({
    "query": "System crashes under high load",
    "type": "diagnosis"
})

print(result.combined_result)
# {'conclusions': ['Memory leak may cause crash'],
#  'evidence': ['memory_leak causes high_memory'],
#  'suggestions': ['restart_service']}
```
