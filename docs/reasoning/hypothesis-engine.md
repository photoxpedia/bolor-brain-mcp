# HypothesisEngine

Hypothesis generation and testing for explanatory reasoning.

## Overview

The `HypothesisEngine` supports abductive reasoning:

- Generate hypotheses from observations
- Find supporting and contradicting evidence
- Update confidence based on evidence
- Rank hypotheses by plausibility

Integrates with `KnowledgeGraph` and `SymbolicReasoner` to find evidence.

## Quick Start

```python
from modules import HypothesisEngine, KnowledgeGraph, SymbolicReasoner

kg = KnowledgeGraph()
reasoner = SymbolicReasoner()
engine = HypothesisEngine(kg, reasoner)

# Create a hypothesis
hyp = engine.create_hypothesis(
    "Memory leak causes the crash",
    initial_evidence=["High memory usage observed"]
)

# Test it
test = engine.test_hypothesis(hyp.id)

print(f"Status: {hyp.status}")  # supported, refuted, inconclusive
print(f"Confidence: {hyp.confidence}")
```

## API Reference

### Hypothesis

```python
@dataclass
class Hypothesis:
    id: str                           # Unique identifier
    statement: str                    # The hypothesis text
    supporting_evidence: list[str]    # Evidence for
    contradicting_evidence: list[str] # Evidence against
    confidence: float                 # 0-1, starts at 0.5
    status: str                       # untested, supported, refuted, inconclusive
    source: str                       # How it was generated
    created_at: float                 # Timestamp
```

**Status values:**
- `untested`: Not yet tested
- `supported`: confidence >= 0.7
- `refuted`: confidence <= 0.3
- `inconclusive`: Evidence found but unclear

### HypothesisTest

```python
@dataclass
class HypothesisTest:
    hypothesis_id: str       # Tested hypothesis
    test_type: str           # Type of test performed
    evidence_found: list[str] # All evidence discovered
    supports: bool           # Does evidence support?
    confidence_delta: float  # Change in confidence
```

### Creating Hypotheses

```python
# Manual creation
hyp = engine.create_hypothesis(
    statement="X causes Y",
    initial_evidence=["Observed correlation"],
    source="manual"
)

# Auto-generate from observation
hypotheses = engine.generate_hypotheses(
    observation="System is slow",
    max_hypotheses=5
)
```

### Generation Strategies

`generate_hypotheses()` uses three strategies:

1. **Causal paths**: Finds paths in knowledge graph with causal relations
2. **Symbolic inference**: Uses reasoner to find facts about causes
3. **Correlations**: Finds co-occurring concepts in facts

### Testing Hypotheses

```python
test = engine.test_hypothesis(hyp.id)

# Test searches:
# - Knowledge graph for related nodes/edges
# - Symbolic reasoner facts
# - Updates confidence based on evidence found
```

### Finding Evidence

```python
supporting, contradicting = engine.find_evidence(hypothesis)

# Supporting: Evidence that overlaps with hypothesis terms
# Contradicting: Evidence with negation patterns ("not", "never", etc.)
```

### Confidence Updates

Evidence affects confidence:

| Evidence | Effect |
|----------|--------|
| Supporting | +0.15 per item |
| Contradicting | -0.20 per item |

Confidence is clamped to [0.05, 0.95].

```python
# Manual update
new_conf = engine.update_confidence(hyp.id, test_result)
```

### Ranking Hypotheses

```python
# Rank all hypotheses
ranked = engine.rank_hypotheses()

# Get best hypothesis for an observation
best = engine.get_best_hypothesis("System crashes")
```

Ranking score = confidence + (0.05 * supporting) - (0.05 * contradicting)

### Management

```python
# Get
hyp = engine.get_hypothesis("hyp_id")

# Remove
engine.remove_hypothesis("hyp_id")

# Clear all
engine.clear()
```

### Statistics

```python
stats = engine.get_stats()
# {
#   "total_hypotheses": 10,
#   "status_counts": {"supported": 3, "refuted": 2, "inconclusive": 5},
#   "avg_confidence": 0.55
# }
```

## Example: Root Cause Analysis

```python
from modules import HypothesisEngine, KnowledgeGraph, SymbolicReasoner, Fact, Node, Edge

# Set up knowledge
kg = KnowledgeGraph()
kg.add_node(Node("mem_leak", "Memory Leak", "issue"))
kg.add_node(Node("crash", "System Crash", "symptom"))
kg.add_node(Node("db_lock", "Database Lock", "issue"))
kg.add_edge(Edge("mem_leak", "crash", "causes"))
kg.add_edge(Edge("db_lock", "crash", "causes"))

reasoner = SymbolicReasoner()
reasoner.add_fact(Fact("memory_leak", "causes", "high_memory"))
reasoner.add_fact(Fact("high_memory", "leads_to", "crash"))

engine = HypothesisEngine(kg, reasoner)

# Generate hypotheses for crash
hypotheses = engine.generate_hypotheses("crash", max_hypotheses=3)

for hyp in hypotheses:
    print(f"Hypothesis: {hyp.statement}")

    # Test each
    test = engine.test_hypothesis(hyp.id)
    print(f"  Confidence: {hyp.confidence:.2f}")
    print(f"  Status: {hyp.status}")
    print(f"  Supporting: {hyp.supporting_evidence}")
    print()

# Get best explanation
best = engine.get_best_hypothesis()
print(f"Most likely cause: {best.statement}")
```

## Integration with HybridReasoner

The `HypothesisEngine` is used automatically by `HybridReasoner` for:

- `ABDUCTION` problems (why, cause, explain)
- `DIAGNOSIS` problems (symptoms, problems)

```python
brain = HybridReasoner()
result = brain.reason({
    "query": "Why does the server crash at midnight?",
    "type": "abduction"
})
# Uses hypothesis engine internally
```

## Thread Safety

All operations are thread-safe via internal locking.
