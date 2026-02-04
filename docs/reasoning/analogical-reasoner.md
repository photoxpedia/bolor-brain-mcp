# AnalogicalReasoner

Cross-domain pattern transfer using Structure-Mapping Theory.

## Overview

The `AnalogicalReasoner` finds structural similarities between domains and transfers knowledge:

- Map concepts between source and target domains
- Transfer solutions from familiar to unfamiliar domains
- Generate inferences based on analogical mappings

Based on Structure-Mapping Theory (SMT) principles:
- **Systematicity**: Prefer mappings that preserve relational structure
- **One-to-one**: Each element maps to at most one element
- **Parallel connectivity**: Arguments of relations should map consistently

## Quick Start

```python
from modules import AnalogicalReasoner, Concept

reasoner = AnalogicalReasoner()

# Add concepts to source domain (solar system)
reasoner.add_concept(Concept(
    id="sun", name="Sun", domain="solar_system",
    attributes={"type": "center", "mass": "large"},
    relations=[{"type": "attracts", "target": "earth"}]
))
reasoner.add_concept(Concept(
    id="earth", name="Earth", domain="solar_system",
    attributes={"type": "orbiter", "mass": "small"},
    relations=[{"type": "orbits", "target": "sun"}]
))

# Add concepts to target domain (atom)
reasoner.add_concept(Concept(
    id="nucleus", name="Nucleus", domain="atom",
    attributes={"type": "center", "mass": "large"},
    relations=[{"type": "attracts", "target": "electron"}]
))
reasoner.add_concept(Concept(
    id="electron", name="Electron", domain="atom",
    attributes={"type": "orbiter", "mass": "small"},
    relations=[{"type": "orbits", "target": "nucleus"}]
))

# Find analogy
analogy = reasoner.find_analogy("solar_system", "atom")

print(f"Similarity: {analogy.overall_similarity:.2f}")
for mapping in analogy.mappings:
    print(f"  {mapping.source_concept} -> {mapping.target_concept}")
# sun -> nucleus
# earth -> electron
```

## API Reference

### Concept

```python
@dataclass
class Concept:
    id: str                    # Unique identifier
    name: str                  # Human-readable name
    domain: str                # Domain this belongs to
    attributes: dict[str, Any] # Properties (color, size, type)
    relations: list[dict]      # Relations to other concepts
                               # [{"type": "causes", "target": "id"}]
```

### AnalogicalMapping

```python
@dataclass
class AnalogicalMapping:
    id: str                          # Unique identifier
    source_concept: str              # Source concept ID
    target_concept: str              # Target concept ID
    mapping_type: MappingType        # ATTRIBUTE, RELATIONAL, STRUCTURAL
    similarity: float                # Mapping strength (0-1)
    mapped_attributes: dict[str,str] # Attribute correspondences
    mapped_relations: list[dict]     # Relation correspondences
```

### MappingType

```python
class MappingType(Enum):
    ATTRIBUTE = "attribute"    # Object properties match
    RELATIONAL = "relational"  # Relationships match
    STRUCTURAL = "structural"  # Higher-order structure matches
    CAUSAL = "causal"          # Causal relationships match
```

### Analogy

```python
@dataclass
class Analogy:
    id: str                           # Unique identifier
    source_domain: str                # Well-understood domain
    target_domain: str                # Domain to understand
    mappings: list[AnalogicalMapping] # Concept mappings
    overall_similarity: float         # Quality score (0-1)
    inferences: list[str]             # Derived inferences
    created_at: float                 # Timestamp
```

### Concept Management

```python
# Add concept
reasoner.add_concept(concept)

# Get concept
concept = reasoner.get_concept("sun", "solar_system")

# Get all concepts in domain
concepts = reasoner.get_domain_concepts("solar_system")
```

### Finding Analogies

```python
analogy = reasoner.find_analogy(
    source_domain="solar_system",  # Known domain
    target_domain="atom",          # Target domain
    source_focus="sun"             # Optional: focus on specific concept
)

if analogy:
    print(f"Similarity: {analogy.overall_similarity}")
    print(f"Inferences: {analogy.inferences}")
```

### Similarity Computation

Three levels of similarity are computed:

| Level | Weight | What it measures |
|-------|--------|------------------|
| Attribute | 0.3 | Matching property names/values |
| Relational | 0.5 | Matching relation types |
| Structural | 0.7 | Consistent mapping of relation arguments |

Minimum similarity threshold: 0.3

### Pattern Transfer

Transfer a pattern from source to target domain.

```python
pattern = {
    "concepts": ["sun", "earth"],
    "relations": [{"source": "earth", "target": "sun", "type": "orbits"}]
}

transferred = reasoner.transfer_pattern(
    source_domain="solar_system",
    pattern=pattern,
    target_domain="atom"
)
# {
#   "concepts": ["nucleus", "electron"],
#   "relations": [{"source": "electron", "target": "nucleus", "type": "orbits"}]
# }
```

### Solving by Analogy

Solve a problem using analogical reasoning.

```python
solution = reasoner.solve_by_analogy(
    problem_domain="atom",
    problem={"goal": "predict_behavior"},
    analogy_domain="solar_system"  # Optional, auto-selects if None
)

if solution:
    print(f"Solution: {solution}")
    print(f"Confidence: {solution['confidence']}")
    print(f"Based on: {solution['source_domain']}")
```

### Learning

Adjust weights based on analogy success/failure.

```python
reasoner.learn_analogy(analogy, success=True)
# Strengthens relational/structural weights

reasoner.learn_analogy(analogy, success=False)
# Strengthens attribute weight
```

### Statistics

```python
stats = reasoner.get_stats()
# {
#   "total_domains": 3,
#   "total_concepts": 15,
#   "total_analogies": 5,
#   "domains": ["solar_system", "atom", "company"]
# }
```

## Example: Teaching by Analogy

```python
reasoner = AnalogicalReasoner()

# Source domain: familiar (water flow)
reasoner.add_concept(Concept(
    id="pump", name="Pump", domain="water",
    attributes={"role": "source", "provides": "pressure"},
    relations=[{"type": "drives", "target": "water"}]
))
reasoner.add_concept(Concept(
    id="water", name="Water", domain="water",
    attributes={"role": "medium", "type": "flow"},
    relations=[{"type": "flows_through", "target": "pipe"}]
))
reasoner.add_concept(Concept(
    id="pipe", name="Pipe", domain="water",
    attributes={"role": "conductor", "resists": "flow"},
    relations=[]
))

# Target domain: unfamiliar (electricity)
reasoner.add_concept(Concept(
    id="battery", name="Battery", domain="electricity",
    attributes={"role": "source", "provides": "voltage"},
    relations=[{"type": "drives", "target": "current"}]
))
reasoner.add_concept(Concept(
    id="current", name="Current", domain="electricity",
    attributes={"role": "medium", "type": "flow"},
    relations=[{"type": "flows_through", "target": "wire"}]
))
reasoner.add_concept(Concept(
    id="wire", name="Wire", domain="electricity",
    attributes={"role": "conductor", "resists": "flow"},
    relations=[]
))

# Find analogy
analogy = reasoner.find_analogy("water", "electricity")

print("Mappings:")
for m in analogy.mappings:
    print(f"  {m.source_concept} -> {m.target_concept}")
# pump -> battery
# water -> current
# pipe -> wire

print("Inferences:")
for inf in analogy.inferences:
    print(f"  {inf}")
# "Battery may have pressure (by analogy with Pump)"
```

## Integration with HybridReasoner

Used automatically for `ANALOGY` and `EXPLORATION` problems:

```python
brain = HybridReasoner()
result = brain.reason({
    "query": "Explain electricity like water flow",
    "context": {
        "source_domain": "water",
        "target_domain": "electricity"
    }
})
```

## Thread Safety

All operations are thread-safe via internal locking.
