# SymbolicReasoner

Rule-based logical reasoning with forward and backward chaining.

## Overview

The `SymbolicReasoner` implements classic AI symbolic reasoning:

- **Forward chaining**: Data-driven, applies rules to derive new facts
- **Backward chaining**: Goal-driven, works backward from a goal to find supporting facts
- **Conflict resolution**: Rules have priorities, higher fires first

## Quick Start

```python
from modules import SymbolicReasoner, Fact, Rule, FactType

reasoner = SymbolicReasoner()

# Add facts
reasoner.add_fact(Fact("Socrates", "is_a", "human"))
reasoner.add_fact(Fact("human", "is", "mortal", fact_type=FactType.PROPERTY))

# Add rule: All humans are mortal
reasoner.add_rule(Rule(
    name="mortality",
    conditions=[
        lambda facts: any(
            f.predicate == "is_a" and f.object == "human"
            for f in facts.values()
        )
    ],
    conclusion_template={
        "subject": lambda facts: next(
            f.subject for f in facts.values()
            if f.object == "human"
        ),
        "predicate": "is",
        "object": "mortal"
    },
    description="All humans are mortal"
))

# Forward chain to derive new facts
new_facts = reasoner.forward_chain()
# Derives: Socrates is mortal
```

## API Reference

### Fact

```python
@dataclass
class Fact:
    subject: str          # e.g., "Socrates"
    predicate: str        # e.g., "is_a"
    object: Any           # e.g., "human"
    fact_type: FactType   # ASSERTION, RELATION, PROPERTY, NEGATION
    confidence: float     # 0-1, default 1.0
    source: str           # Where it came from
    timestamp: float      # When created
    id: str               # Auto-generated UUID
```

**FactType enum:**
- `ASSERTION`: X is Y
- `RELATION`: X relates to Y
- `PROPERTY`: X has property P
- `NEGATION`: X is not Y

### Rule

```python
@dataclass
class Rule:
    name: str                    # Unique identifier
    conditions: list[Callable]   # Functions that check if rule applies
    conclusion_template: dict    # Template for new fact
    priority: int                # Higher fires first
    enabled: bool                # Can disable rules
    description: str             # Human-readable
```

### Fact Management

```python
# Add
reasoner.add_fact(Fact("X", "rel", "Y"))

# Query
facts = reasoner.query_facts(
    subject="Socrates",      # Optional filters
    predicate="is_a",
    object="human",
    min_confidence=0.8
)

# Get by ID
fact = reasoner.get_fact("abc123")

# Remove
reasoner.remove_fact("abc123")

# Clear all
count = reasoner.clear_facts()
```

### Rule Management

```python
# Add
reasoner.add_rule(rule)

# Get/remove
rule = reasoner.get_rule("mortality")
reasoner.remove_rule("mortality")

# Enable/disable
reasoner.enable_rule("mortality", enabled=False)
```

### Forward Chaining

Applies all rules repeatedly until no new facts are derived.

```python
new_facts = reasoner.forward_chain(max_iterations=100)

for fact in new_facts:
    print(f"Derived: {fact}")
```

### Backward Chaining

Proves a goal by finding supporting facts.

```python
goal = Fact("Socrates", "is", "mortal")
success, proof_path = reasoner.backward_chain(goal, max_depth=10)

if success:
    print("Goal proven!")
    for step in proof_path:
        print(f"  {step}")
```

### Full Reasoning Interface

```python
result = reasoner.reason(
    query="Is Socrates mortal?",
    mode="hybrid"  # "forward", "backward", or "hybrid"
)

print(result.success)
print(result.conclusion)
print(result.confidence)
print(result.facts_used)
print(result.rules_fired)
print(result.reasoning_chain)
```

## ReasoningResult

```python
@dataclass
class ReasoningResult:
    success: bool              # Did reasoning succeed
    conclusion: str            # Main conclusion
    confidence: float          # Confidence in conclusion
    facts_used: list[Fact]     # Contributing facts
    rules_fired: list[str]     # Applied rule names
    reasoning_chain: list[str] # Step-by-step trace
    new_facts: list[Fact]      # Newly derived facts
```

## Example: Medical Diagnosis

```python
reasoner = SymbolicReasoner()

# Symptoms
reasoner.add_fact(Fact("patient", "has_symptom", "fever"))
reasoner.add_fact(Fact("patient", "has_symptom", "cough"))
reasoner.add_fact(Fact("patient", "has_symptom", "fatigue"))

# Diagnostic rules
reasoner.add_rule(Rule(
    name="flu_diagnosis",
    conditions=[
        lambda f: any(x.object == "fever" for x in f.values()),
        lambda f: any(x.object == "cough" for x in f.values()),
        lambda f: any(x.object == "fatigue" for x in f.values()),
    ],
    conclusion_template={
        "subject": "patient",
        "predicate": "may_have",
        "object": "flu",
        "confidence": 0.8
    },
    priority=1,
    description="Fever + cough + fatigue suggests flu"
))

# Run inference
new_facts = reasoner.forward_chain()
# Derives: patient may_have flu (confidence: 0.8)
```

## Statistics

```python
stats = reasoner.get_stats()
# {
#   "fact_count": 10,
#   "rule_count": 5,
#   "enabled_rules": 4,
#   "inference_count": 15,
#   "avg_confidence": 0.85
# }
```

## Thread Safety

All operations are thread-safe via internal locking. Safe to use from multiple threads.
