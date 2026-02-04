# CaseBasedReasoner

Experience-based reasoning using the 4R cycle.

## Overview

The `CaseBasedReasoner` learns from past experiences:

1. **Retrieve**: Find similar past cases
2. **Reuse**: Adapt past solutions to new problems
3. **Revise**: Incorporate feedback
4. **Retain**: Store successful new cases

## Quick Start

```python
from modules import CaseBasedReasoner, Case

cbr = CaseBasedReasoner()

# Store a past case
cbr.store_case(Case(
    id="bug_fix_1",
    problem={"type": "bug", "language": "python", "error": "TypeError"},
    solution={"action": "add_type_check", "location": "input_validation"},
    success=True
))

# Find similar cases for a new problem
matches = cbr.retrieve(
    {"type": "bug", "language": "python", "error": "AttributeError"},
    k=5
)

for match in matches:
    print(f"Case: {match.case.id}")
    print(f"Similarity: {match.similarity:.2f}")
    print(f"Solution: {match.case.solution}")
```

## The 4R Cycle

### 1. Retrieve

Find cases similar to the current problem.

```python
matches = cbr.retrieve(
    problem={"type": "bug", "language": "python"},
    k=5,               # Return top 5 matches
    min_similarity=0.3 # Minimum similarity threshold
)
```

**Returns:** List of `CaseMatch` objects sorted by similarity.

### 2. Reuse

Adapt a matched case's solution to the new problem.

```python
new_problem = {"type": "bug", "language": "javascript", "error": "TypeError"}
adapted_solution = cbr.reuse(new_problem, matches[0])
```

The reuse step performs substitution adaptation - replacing values that differ between the source case and new problem.

### 3. Revise

Incorporate feedback to improve a proposed solution.

```python
revised = cbr.revise(
    proposed_solution=adapted_solution,
    feedback={
        "modifications": {"location": "api_handler"},
        "remove": ["deprecated_field"],
        "add": {"new_check": "null_safety"}
    }
)
```

### 4. Retain

Store a new successful case for future use.

```python
new_case = cbr.retain(
    problem={"type": "bug", "language": "javascript"},
    solution=revised,
    outcome={"status": "resolved", "tests_passed": True},
    success=True,
    tags=["bug", "javascript", "type_error"]
)
```

## Full Reasoning

The `reason()` method runs Retrieve + Reuse automatically:

```python
result = cbr.reason(
    problem={"type": "performance", "component": "database"},
    min_similarity=0.3
)

if result.success:
    print(f"Proposed solution: {result.proposed_solution}")
    print(f"Confidence: {result.confidence}")
    print(f"Based on case: {result.source_case.id}")
    print(f"Adaptations: {result.adaptations}")
```

## API Reference

### Case

```python
@dataclass
class Case:
    id: str                      # Unique identifier
    problem: dict[str, Any]      # Problem features
    solution: dict[str, Any]     # Applied solution
    outcome: dict[str, Any]      # Result (optional)
    success: bool                # Did it work? (optional)
    timestamp: float             # When created
    tags: list[str]              # Categories
    use_count: int               # Times retrieved
```

### CaseMatch

```python
@dataclass
class CaseMatch:
    case: Case                    # The matched case
    similarity: float             # 0-1 similarity score
    matching_features: list[str]  # Features that matched
    differing_features: list[str] # Features that differed
    adaptation_needed: bool       # Needs modification?
```

### CaseReasoningResult

```python
@dataclass
class CaseReasoningResult:
    success: bool                   # Found a suitable case
    proposed_solution: dict         # Adapted solution
    confidence: float               # Confidence level
    source_case: Case               # Case used as basis
    adaptations: list[str]          # Changes made
    reasoning_chain: list[str]      # Step-by-step trace
```

### Case Management

```python
# Store
cbr.store_case(case)

# Get by ID
case = cbr.get_case("bug_fix_1")

# Query
cases = cbr.query_cases(
    tags=["python", "bug"],
    success_only=True
)

# Remove
cbr.remove_case("bug_fix_1")

# Update outcome
cbr.update_case_outcome(
    "bug_fix_1",
    outcome={"resolved": True},
    success=True
)
```

### Feature Weights

The reasoner learns which features matter most.

```python
# Bulk update from outcomes
cbr.update_feature_weights(
    successful_cases=[case1, case2],
    failed_cases=[case3]
)

# Weights adjust automatically when storing cases with success flag
```

### Similarity Computation

Similarity is computed per feature type:

| Type | Method |
|------|--------|
| Exact match | 1.0 |
| String | Containment (0.7) or Jaccard on words |
| Numeric | Normalized difference |
| List | Jaccard similarity |
| Dict | Recursive feature similarity |
| Type mismatch | 0.0 |

### Serialization

```python
# To dict
data = cbr.to_dict()

# From dict
cbr = CaseBasedReasoner.from_dict(data)

# Clear
cbr.clear()
```

### Statistics

```python
stats = cbr.get_stats()
# {
#   "total_cases": 50,
#   "successful_cases": 35,
#   "failed_cases": 10,
#   "pending_cases": 5,
#   "feature_weights": {"type": 1.5, "language": 1.2},
#   "most_used_cases": [("case1", 15), ("case2", 12)]
# }
```

## Example: Bug Tracking

```python
cbr = CaseBasedReasoner()

# Historical bugs
cbr.store_case(Case(
    id="mem_leak_1",
    problem={
        "type": "memory_leak",
        "language": "python",
        "component": "api",
        "symptom": "growing_memory"
    },
    solution={
        "action": "close_connection",
        "pattern": "context_manager",
        "file": "api/client.py"
    },
    success=True,
    tags=["memory", "python", "api"]
))

# New similar bug
result = cbr.reason({
    "type": "memory_leak",
    "language": "python",
    "component": "websocket",
    "symptom": "growing_memory"
})

print(result.proposed_solution)
# {
#   "action": "close_connection",
#   "pattern": "context_manager",
#   "file": "api/client.py"  # May need adaptation
# }

# After fixing, retain the new case
if bug_fixed:
    cbr.retain(
        problem=result.source_case.problem,
        solution=actual_fix,
        success=True
    )
```

## Thread Safety

All operations are thread-safe via internal locking.
