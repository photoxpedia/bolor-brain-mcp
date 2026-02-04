# Drive System

Cross-tier motivation layer with homeostatic regulation.

## Overview

Five intrinsic drives influence decision-making:

| Drive | Purpose | Default Baseline |
|-------|---------|------------------|
| Curiosity | Need to explore/learn | 0.4 |
| Novelty | Need for new experiences | 0.3 |
| Competence | Need to master skills | 0.35 |
| Connection | Need for social interaction | 0.25 |
| Stability | Need for predictability | 0.5 |

Drives are advisory - they influence but don't mandate decisions.

## Quick Start

```python
from modules import DriveManager, DriveType

manager = DriveManager()

# Record an action (auto-satisfies relevant drives)
results = manager.record_action("learn")
# {'curiosity': 0.15, 'competence': 0.25}

# Get motivation context
context = manager.get_motivation_context()
print(f"Dominant drive: {context['dominant_drive']}")
print(f"Suggested actions: {context['suggested_actions']}")
```

## How Drives Work

### Homeostatic Regulation

Drives behave like physiological needs:

1. **Baseline**: Target level (like hunger setpoint)
2. **Decay**: Level increases over time when unsatisfied
3. **Satisfaction**: Actions reduce the level

```
Level
  1.0 |           /--------  (urgent)
      |          /
  0.5 |    -----/             (baseline)
      |   /
  0.0 |--/                    (satisfied)
      +------------------------> Time
        ^        ^
        satisfy  decay
```

### Urgency

Urgency increases exponentially as level exceeds baseline:

```python
urgency = ((level - baseline) / (1 - baseline)) ** 1.5
```

## API Reference

### DriveType Enum

```python
class DriveType(Enum):
    CURIOSITY = "curiosity"
    NOVELTY = "novelty"
    COMPETENCE = "competence"
    CONNECTION = "connection"
    STABILITY = "stability"
```

### IntrinsicDrive

```python
@dataclass
class IntrinsicDrive:
    name: str
    current_level: float       # 0-1, current need level
    baseline: float            # Homeostatic setpoint
    decay_rate: float          # Increase per minute when unsatisfied
    satisfaction_rate: float   # Reduction per satisfying action
    last_satisfied: float      # Timestamp
    satisfaction_count: int    # Total satisfactions
```

**Methods:**
```python
drive.update(elapsed_minutes)  # Time-based increase
drive.satisfy(amount)          # Reduce level
drive.get_urgency()            # Get urgency (0-1)
```

### DriveState

Manages all five drives together.

```python
from modules import DriveState

state = DriveState()

# Update all drives based on elapsed time
levels = state.update_all()
# {'curiosity': 0.42, 'novelty': 0.35, ...}

# Satisfy a specific drive
state.satisfy_drive(DriveType.CURIOSITY, amount=0.2)

# Satisfy from action (auto-maps to drives)
results = state.satisfy_from_action("explore")
# {'curiosity': 0.25, 'novelty': 0.2}

# Get dominant drive
drive_type, urgency = state.get_dominant_drive()

# Get all drive states
drives = state.get_all_drives()
```

### DriveManager

High-level manager with persistence.

```python
from modules import DriveManager

manager = DriveManager(self_model_store)  # Optional persistence

# Record action
results = manager.record_action("solve_problem")

# Record outcome with reward
results = manager.record_outcome("success", reward=0.8)

# Get full context
context = manager.get_motivation_context()
# {
#   'dominant_drive': 'curiosity',
#   'dominant_urgency': 0.65,
#   'all_drives': {...},
#   'suggested_actions': ['explore', 'research', 'discover'],
#   'should_explore': True,
#   'should_consolidate': False
# }

# Prioritize options by drive satisfaction
options = [
    {"name": "A", "satisfies_drives": {"curiosity": 0.3}},
    {"name": "B", "satisfies_drives": {"stability": 0.2}},
]
ranked = manager.prioritize_options(options)

# Manual boosts
manager.boost_curiosity(0.2)
manager.boost_novelty(0.2)
manager.trigger_stability_need(0.3)
```

## Action-Drive Mappings

Built-in mappings from actions to drive satisfaction:

### Learning Actions
| Action | Curiosity | Competence |
|--------|-----------|------------|
| learn | 0.30 | 0.10 |
| explore | 0.25 | - |
| research | 0.35 | 0.15 |
| question | 0.20 | - |

### Novel Experiences
| Action | Novelty | Curiosity |
|--------|---------|-----------|
| new_experience | 0.35 | - |
| discover | 0.30 | 0.20 |
| experiment | 0.25 | 0.15 |
| create | 0.20 | - |

### Competence Building
| Action | Competence | Curiosity |
|--------|------------|-----------|
| practice | 0.30 | - |
| master | 0.40 | - |
| improve | 0.25 | - |
| solve_problem | 0.35 | 0.10 |
| succeed | 0.30 | - |

### Social Connection
| Action | Connection | Competence |
|--------|------------|------------|
| interact | 0.25 | - |
| collaborate | 0.35 | 0.10 |
| help | 0.30 | - |
| receive_feedback | 0.20 | 0.15 |

### Stability
| Action | Stability |
|--------|-----------|
| routine | 0.20 |
| familiar_task | 0.15 |
| confirm_understanding | 0.25 |
| validate | 0.20 |
| organize | 0.20 |

## Decision Support

### Should Explore?

```python
if state.should_explore(novelty_threshold=0.6, curiosity_threshold=0.6):
    # Novelty or curiosity is high - explore something new
    pass
```

### Should Consolidate?

```python
if state.should_consolidate(stability_threshold=0.7):
    # Stability need is high - organize/consolidate
    pass
```

### Get Suggested Actions

```python
actions = state.get_suggested_actions(top_n=3)
# ['explore', 'research', 'discover']
```

## Drive-Aware Utilities

### Tag Memory with Drive

```python
from modules import tag_memory_with_drive

drive = tag_memory_with_drive(
    state,
    memory_content="Learned new algorithm",
    memory_type="episodic"
)
# Returns: "curiosity" (detected from keywords)
```

### Boost Memory by Drive

```python
from modules import boost_memory_by_drive

# Boost retrieval scores for memories matching dominant drive
boosted = boost_memory_by_drive(
    episodes,
    state,
    boost_factor=0.2
)
```

## Example: Drive-Guided Learning

```python
manager = DriveManager()

# Simulate passage of time (drives increase)
# ... some time passes ...

context = manager.get_motivation_context()

if context['should_explore']:
    # High curiosity/novelty - explore new topic
    manager.record_action("explore")
    manager.record_action("discover")

elif context['dominant_drive'] == 'competence':
    # Need to build skills - practice
    manager.record_action("practice")
    manager.record_outcome("improve", reward=0.7)

elif context['should_consolidate']:
    # Need stability - organize knowledge
    manager.record_action("organize")
    manager.record_action("validate")

# After successful learning
manager.record_outcome("success", reward=0.9)
```

## Thread Safety

All operations on DriveState and DriveManager are thread-safe.
