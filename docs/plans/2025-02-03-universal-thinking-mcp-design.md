# Universal Thinking MCP - Complete Design

**Date:** 2025-02-03
**Status:** Approved
**Goal:** Make Bolor-Brain-MCP the single, universal MCP for all thinking, reasoning, creativity, and decision-making capabilities.

---

## Vision

One MCP that provides ALL cognitive capabilities. Any application (Claude Code, custom apps, AI assistants, automation) can plug in sophisticated thinking through a clean interface.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ANY APPLICATION                                  │
│       (Claude Code, Custom Apps, AI Assistants, Automation)             │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ MCP Protocol
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BOLOR-BRAIN-MCP v2.0                                  │
│                  The Universal Thinking Engine                           │
├─────────────────────────────────────────────────────────────────────────┤
│  • 20 Thinking Frameworks (First Principles, OODA, Cynefin, etc.)       │
│  • 6 Reasoning Strategies (Analytical, Creative, Critical, etc.)        │
│  • Symbolic + Case-Based + Neural Hybrid Reasoning                      │
│  • 12 Domain Curricula (Physics to Programming)                         │
│  • Goal Planning with Outcome Validation                                │
│  • Causal Understanding (What-if scenarios)                             │
│  • Self-Evolving Skills (Learn from failures)                           │
│  • Creative Invention (Novelty Engine)                                  │
│  • Calibrated Confidence (Not arbitrary 0.7)                            │
│  • Configurable: Works standalone OR with LLM enhancement               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Module Structure (Clean, 10 modules)

```
bolor-brain-mcp/
├── modules/
│   ├── __init__.py
│   ├── brain.py              # Orchestrator (wires everything)
│   ├── memory.py             # 5 memory systems (existing)
│   ├── drives.py             # 5 intrinsic drives (existing)
│   ├── reasoning.py          # Symbolic + Case-Based + Hybrid
│   ├── frameworks.py         # 20 thinking frameworks
│   ├── learning.py           # Patterns + Outcomes + 12 Curricula
│   ├── goals.py              # Planning + Tracking + Validation
│   ├── world_model.py        # Causal + Counterfactual
│   ├── creativity.py         # Novelty + Curiosity
│   ├── genome.py             # 60+ evolvable parameters
│   └── llm_bridge.py         # Optional LLM (configurable)
│
├── server.py                 # MCP interface (16 tools)
├── config.py                 # Settings + LLM toggle
├── pyproject.toml            # Python 3.11+
└── tests/
```

### Wiring (Everything Connected)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MCP TOOLS (Simple Interface)                     │
│   think() | decide() | plan() | reason() | create() | learn()           │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            BRAIN (Orchestrator)                          │
│                                                                          │
│   ┌─────────────┐    Routes based on:                                   │
│   │   Drives    │◄── • Problem type                                     │
│   │  (5 needs)  │    • Drive state                                      │
│   └──────┬──────┘    • Confidence requirements                          │
│          │           • LLM availability                                  │
│          ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    COGNITIVE PIPELINE                            │   │
│   │                                                                  │   │
│   │  Input ──► Framework ──► Reasoning ──► World Model ──► Output   │   │
│   │                Selector      Engine        (validate)            │   │
│   │                    │            │              │                 │   │
│   │                    ▼            ▼              ▼                 │   │
│   │              ┌─────────┐  ┌─────────┐   ┌─────────┐             │   │
│   │              │20 Frames│  │Symbolic │   │ Causal  │             │   │
│   │              │  works  │  │+ Case   │   │ Graphs  │             │   │
│   │              │         │  │+ Neural │   │         │             │   │
│   │              └─────────┘  └─────────┘   └─────────┘             │   │
│   │                                                                  │   │
│   │              Memory ◄──────────────────────────────────────────►│   │
│   │                 │                                                │   │
│   │                 ▼                                                │   │
│   │           Learning System                                        │   │
│   │         (patterns, outcomes)                                     │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## MCP Tools Interface (16 Tools)

### Core Thinking (5 tools)

```python
@server.tool()
async def think(
    problem: str,
    frameworks: list[str] = None,  # Auto-selects if not specified
    depth: str = "standard"        # "quick" | "standard" | "deep"
) -> ThinkResult:
    """Apply structured thinking to any problem."""

@server.tool()
async def decide(
    question: str,
    options: list[str],
    criteria: dict = None,
    frameworks: list[str] = None
) -> Decision:
    """Make structured decision with reasoning chain."""

@server.tool()
async def reason(
    premises: list[str],
    question: str,
    mode: str = "hybrid"           # "symbolic" | "case_based" | "hybrid"
) -> Conclusion:
    """Pure logical reasoning from premises."""

@server.tool()
async def plan(
    goal: str,
    constraints: dict = None,
    validate_outcomes: bool = True
) -> Plan:
    """Create multi-step plan with expected outcomes."""

@server.tool()
async def create(
    challenge: str,
    constraints: dict = None,
    novelty_level: str = "moderate"
) -> Creative:
    """Generate novel solutions through structured creativity."""
```

### Analysis Tools (4 tools)

```python
@server.tool()
async def analyze_root_cause(problem: str, method: str = "auto") -> RootCause
@server.tool()
async def analyze_system(system: str, elements: list[str] = None) -> SystemAnalysis
@server.tool()
async def predict(scenario: str, variables: dict = None) -> Prediction
@server.tool()
async def counterfactual(event: str, what_if: str) -> Counterfactual
```

### Learning Tools (3 tools)

```python
@server.tool()
async def learn(topic: str, depth: str = "understand") -> Knowledge
@server.tool()
async def assess_knowledge(topic: str) -> Assessment
@server.tool()
async def find_knowledge_gaps(goal: str) -> Gaps
```

### Memory & State (4 tools)

```python
@server.tool()
async def remember(content: str, memory_type: str = "auto", importance: float = 0.5) -> Stored
@server.tool()
async def recall(query: str, limit: int = 10) -> Memories
@server.tool()
async def get_state() -> BrainState
@server.tool()
async def get_capabilities() -> Capabilities
```

---

## Configurable LLM Mode

### Configuration

```python
@dataclass
class Config:
    llm_enabled: bool = False          # Default: standalone
    llm_provider: str = "openai"       # "openai" | "anthropic" | "ollama"
    llm_model: str = "gpt-4o"
    llm_api_key: str = None
    llm_base_url: str = None           # For ollama/custom
    llm_fallback_to_symbolic: bool = True
    llm_timeout: float = 30.0
    llm_use_for: list[str] = ["synthesis", "creative", "ambiguous"]
```

### Two Modes

**Standalone (No LLM):**
- Fast, deterministic, free, offline
- Symbolic + Case-Based reasoning only
- Template-based output formatting

**LLM-Enhanced:**
- Symbolic reasoning first (verified logic)
- LLM synthesizes natural language output
- LLM enhances creativity when needed
- Fallback to symbolic if LLM fails

**Key principle:** LLM enhances, never replaces. All logic is symbolic-verified first.

---

## Components to Convert (JS → Python)

### Reasoning Engines (~6,000 lines)

| Component | Purpose |
|-----------|---------|
| SymbolicReasoner | Forward/backward chaining, rules, facts |
| KnowledgeGraph | Nodes, edges, BFS, PageRank, inference |
| CaseBasedReasoner | Retrieve/Reuse/Revise/Retain |
| HypothesisEngine | Generate/test hypotheses via KG paths |
| AnalogicalReasoner | Cross-domain pattern transfer |
| HybridReasoner | Combines all approaches |

### Thinking Frameworks (~9,500 lines)

**Problem Solving (6):**
- First Principles (Five Whys, Socratic questioning)
- Inversion (Pre-mortem, failure analysis)
- Issue Trees (MECE decomposition)
- Abstraction Laddering (Why/How reframing)
- Productive Thinking (DRIVE framework)
- Ishikawa Diagram (6Ms root cause)

**Decision Making (9):**
- Cynefin (Simple/Complicated/Complex/Chaotic)
- Eisenhower Matrix (Urgent vs Important)
- Decision Matrix (Weighted criteria)
- Second-Order Thinking (Consequence chains)
- Six Thinking Hats (6 perspectives)
- Hard Choice Model (On-par decisions)
- Ladder of Inference (Data → Action)
- OODA Loop (Observe→Orient→Decide→Act)
- Impact-Effort Matrix (Quick wins vs projects)

**Systems Thinking (4):**
- Iceberg Model (Events→Patterns→Structures→Mental Models)
- Connection Circles (Element relationships)
- Feedback Loops (Reinforcing/balancing)
- Concept Map (Knowledge organization)

### Learning System (~9,200 lines)

| Component | Purpose |
|-----------|---------|
| PatternStore | Dynamic patterns with outcome tracking |
| OutcomeTracker | Calibrated confidence from actual results |
| DomainDiscoverer | Learn any domain dynamically |
| **12 Curricula:** | Physics, Chemistry, Math, Programming, Logic, Decision Theory, Epistemology, Information Theory, Language Semantics, Cognitive Science, Systems Thinking, Automation Tools |

### World Model (~1,300 lines)

| Component | Purpose |
|-----------|---------|
| CausalGraph | Cause → effect relationships |
| Counterfactual | What-if reasoning |
| Simulation | Forward prediction |

### Goal Engine (~4,800 lines)

| Component | Purpose |
|-----------|---------|
| GoalPlanner | Multi-step plans with expected outcomes |
| ExecutionTracker | Track progress vs expectations |
| OutcomeValidator | Validate REAL outcomes (not process) |
| KnowledgeGapAnalyzer | What to learn first |

### Creativity (~2,800 lines)

| Component | Purpose |
|-----------|---------|
| NoveltyEngine | Creative invention, conceptual blending |
| CuriosityEngine | Question generation, opportunity detection |

### Self-Awareness (~2,100 lines)

| Component | Purpose |
|-----------|---------|
| CognitiveGenome | 60+ evolvable parameters |
| SelfDiscovery | Know own capabilities |
| ExperienceLearner | Learn from outcomes |

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Config + version checking
- LLM Bridge (configurable)
- Cognitive Genome (60+ genes)

### Phase 2: Reasoning Core (Week 2)
- SymbolicReasoner
- KnowledgeGraph
- CaseBasedReasoner
- HypothesisEngine
- AnalogicalReasoner
- HybridReasoner

### Phase 3: Thinking Frameworks (Week 3)
- Base Framework class
- 6 Problem Solving frameworks
- 9 Decision Making frameworks
- 4 Systems Thinking frameworks
- Framework Selector

### Phase 4: Learning System (Week 4)
- PatternStore
- OutcomeTracker
- DomainDiscoverer
- 12 Domain Curricula

### Phase 5: World Model + Goals (Week 5)
- Causal Graph
- Counterfactual reasoning
- Simulation
- Goal Planner
- Execution Tracker
- Outcome Validator
- Knowledge Gap Analyzer

### Phase 6: Creativity + Self-Awareness (Week 6)
- Novelty Engine
- Curiosity Engine
- Self Discovery
- Experience Learner

### Phase 7: Integration + MCP (Week 7)
- Brain Orchestrator (wire everything)
- 16 MCP Tools
- Comprehensive tests

---

## Python Version Strategy

```toml
# pyproject.toml
[project]
requires-python = ">=3.11,<3.13"
```

```python
# server.py - Startup check
import sys
MIN_PYTHON = (3, 11)
if sys.version_info < MIN_PYTHON:
    sys.exit(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required")
```

---

## Output Data Structures

```python
@dataclass
class ThinkResult:
    conclusion: str
    confidence: float              # Calibrated 0-1
    reasoning_chain: list[str]
    frameworks_used: list[str]
    evidence: list[str]
    uncertainties: list[str]
    next_steps: list[str]

@dataclass
class Decision:
    choice: str
    confidence: float
    scores: dict[str, float]
    reasoning_chain: list[str]
    risks: dict[str, list[str]]
    what_if: dict[str, str]

@dataclass
class Plan:
    steps: list[PlanStep]
    expected_outcomes: list[str]
    knowledge_gaps: list[str]
    risks: list[str]
    validation_criteria: list[str]
```

---

## Summary

| Metric | Value |
|--------|-------|
| **Total JS to convert** | ~41,400 lines |
| **Estimated Python** | ~36,700 lines |
| **Modules** | 10 clean modules |
| **MCP Tools** | 16 tools |
| **Thinking Frameworks** | 20 frameworks |
| **Reasoning Strategies** | 6 strategies |
| **Curriculum Domains** | 12 domains |
| **Python Version** | 3.11+ |
| **LLM Mode** | Configurable (standalone or enhanced) |

**Outcome:** The only MCP anyone needs for thinking, reasoning, creativity, and decision-making.
