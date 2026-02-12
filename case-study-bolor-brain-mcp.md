# Bolor Brain MCP: Cognitive Architecture for AI Reasoning

**Personal Project** | **Role:** Architect & Developer | **Duration:** 2024-2025

`Python` `AI` `Reasoning Systems` `Knowledge Graphs` `MCP` `Cognitive Architecture`

---

## The Problem

Large Language Models excel at pattern matching and generation, but struggle with **structured reasoning**. When asked to diagnose a problem, plan a sequence of actions, or draw conclusions from interconnected facts, LLMs often:

- Hallucinate logical connections that don't exist
- Miss relevant context from previous interactions
- Fail to apply domain rules consistently
- Cannot explain their reasoning process

I needed a system that could **think systematically**—not just retrieve information, but actually reason through problems using multiple cognitive approaches.

---

## Solution & Approach

I designed and built **Bolor Brain MCP**, a modular cognitive architecture that orchestrates five distinct reasoning engines through a unified interface. The system combines:

- **Symbolic reasoning** for logical inference
- **Knowledge graphs** for relationship traversal
- **Case-based reasoning** for learning from experience
- **Hypothesis testing** for exploring possibilities
- **Analogical reasoning** for cross-domain transfer

The result: a single `brain.reason()` call that automatically detects problem type, selects appropriate reasoning approaches, and synthesizes results with confidence scores.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      HybridReasoner                          │
│              brain.reason() - Single Entry Point             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐    │
│  │  Symbolic   │  │  Knowledge  │  │    Case-Based     │    │
│  │  Reasoner   │  │    Graph    │  │     Reasoner      │    │
│  │             │  │             │  │                   │    │
│  │ • Facts     │  │ • Nodes     │  │ • Cases           │    │
│  │ • Rules     │  │ • Edges     │  │ • 4R Cycle        │    │
│  │ • Chaining  │  │ • BFS/DFS   │  │ • Similarity      │    │
│  │ • Inference │  │ • PageRank  │  │ • Adaptation      │    │
│  └─────────────┘  └─────────────┘  └───────────────────┘    │
│                                                              │
│  ┌─────────────┐  ┌───────────────────────────────────┐     │
│  │ Hypothesis  │  │       Analogical Reasoner         │     │
│  │   Engine    │  │                                   │     │
│  │             │  │ • Concepts & Domains              │     │
│  │ • Generate  │  │ • Structure Mapping               │     │
│  │ • Test      │  │ • Pattern Transfer                │     │
│  │ • Rank      │  │ • Cross-Domain Inference          │     │
│  └─────────────┘  └───────────────────────────────────┘     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│              Memory System (5 Subsystems)                    │
│  Working | Episodic | Semantic | Procedural | Self          │
├─────────────────────────────────────────────────────────────┤
│              Drive System (Homeostatic Regulation)           │
│  Curiosity | Novelty | Competence | Connection              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Challenges

### 1. Problem Type Detection
How does the system know whether to use symbolic logic versus case-based retrieval? I implemented keyword analysis and context inspection to automatically detect:
- **Deduction** ("conclude", "deduce") → Symbolic, Graph
- **Abduction** ("why", "cause") → Hypothesis, Symbolic
- **Diagnosis** ("problem", "symptom") → Hypothesis, Case-Based
- **Planning** ("how to", "steps") → Graph, Case-Based
- **Analogy** ("similar", "like") → Analogical, Case-Based

### 2. Confidence Synthesis
Each reasoning approach returns different confidence metrics. I developed weighted averaging that accounts for approach reliability and result quality.

### 3. Thread Safety
All five engines share state and can be invoked concurrently. Implemented thread-safe locks across all mutable operations.

### 4. Explainability
Every reasoning result includes a complete trace showing which approaches were used, what conclusions were drawn, and why.

---

## Reasoning Flow

The brain follows a systematic workflow for every problem:

```
User Query -> {Problem Type?}
  |deduction -> Symbolic Reasoning -> Forward Chain -> {Rules Match?}
                 |yes -> Derive Conclusions -> Graph Traversal -> Find Evidence
                 |no -> Try Backward Chain -> [Return Partial]

  |diagnosis -> Hypothesis Engine -> Generate Hypotheses -> {Evidence?}
                 |found -> Test Hypotheses -> Rank by Support
                 |none -> Case-Based Search -> Find Similar -> Adapt Solution

  |planning -> Knowledge Graph -> Find Path -> {Path Exists?}
                |yes -> Extract Steps -> Case-Based Verify -> [Return Plan]
                |no -> Explore Neighbors -> Generate Alternatives

  |analogy -> Analogical Reasoner -> Find Source Domain -> {Mapping Found?}
               |yes -> Structure Mapping -> Transfer Inferences -> Validate
               |no -> Case-Based Fallback -> [Return Partial]

All Paths -> Combine Results -> Calculate Confidence -> Build Trace -> [Final Result]
```

---

## Design Solutions

### Symbolic Reasoner: Rule-Based Inference

Forward and backward chaining with configurable rule sets:

```python
# Add domain knowledge
brain.add_fact(Fact("memory_leak", "causes", "crash"))
brain.add_rule(Rule(
    name="tpu_suggests_jax",
    conditions=[lambda f: any(
        fact.subject == "user" and
        fact.predicate == "has_hardware" and
        fact.object == "tpu"
        for fact in f.values()
    )],
    conclusion_template={
        "subject": "jax",
        "predicate": "recommended_because",
        "object": "tpu_optimization",
        "confidence": 0.85
    }
))
```

### Knowledge Graph: Relationship Discovery

Graph-based traversal with weighted edges and pattern matching:

```python
# Build relationship network
brain.add_node(Node("pytorch", "PyTorch", "framework"))
brain.add_node(Node("research", "Research", "use_case"))
brain.add_edge(Edge("pytorch", "research", "suited_for", weight=0.9))

# Find paths and patterns
path = brain.kg.find_path("pytorch", "scaling")
patterns = brain.kg.infer({
    "subject": "?framework",
    "predicate": "suited_for",
    "object": "research"
})
```

### Case-Based Reasoner: Learning from Experience

The 4R cycle: Retrieve, Reuse, Revise, Retain

```python
# Store past decisions
brain.add_case(Case(
    id="deepmind_alphafold",
    problem={"team_size": "large", "hardware": "tpu", "focus": "research"},
    solution={"framework": "jax", "approach": "custom_layers"},
    outcome={"success": True, "impact": "breakthrough"}
))

# Future queries benefit from this experience
matches = brain.cbr.retrieve({"hardware": "tpu", "focus": "research"}, k=3)
# Returns: [deepmind_alphafold (similarity: 0.95), ...]
```

### Hypothesis Engine: Testing Possibilities

Generate, test, and rank hypotheses against available evidence:

```
User: "System crashes under load"

-> Generate Hypotheses:
   1. Memory leak (confidence: 0.7)
   2. Connection pool exhausted (confidence: 0.6)
   3. CPU bottleneck (confidence: 0.5)

-> Test Against Evidence:
   - Memory metrics: normal
   - DB connections: at limit
   - CPU usage: moderate

-> Result: "Connection pool exhausted" (confidence: 0.85)
```

### Analogical Reasoner: Cross-Domain Transfer

Structure-Mapping Theory implementation for transferring knowledge:

```
Source Domain: Atom
  - nucleus (central)
  - electrons (orbit around)
  - electromagnetic force (holds together)

Target Domain: Solar System
  - sun (central) <- MAPPED from nucleus
  - planets (orbit around) <- MAPPED from electrons
  - gravity (holds together) <- MAPPED from electromagnetic

Inference: If atoms have energy levels, solar systems might have orbital resonances
```

---

## Real-World Applications

Built comprehensive examples demonstrating practical use cases:

| Example | Domain | Reasoning Used |
|---------|--------|----------------|
| **Tech Decision Reasoner** | ML framework selection | All 5 approaches |
| **Debugging Assistant** | Root cause analysis | Hypothesis + Case-Based |
| **Medical Triage** | Symptom assessment | Rules + Case-Based |
| **Legal Compliance** | Regulatory checking | Symbolic + Graph |
| **Investment Advisor** | Portfolio strategy | Case-Based + Rules |
| **Learning Path Advisor** | Skill development | Graph + Case-Based |

### Example: Debugging Assistant Flow

```
Incident Input -> Extract Symptoms -> {Symptoms Match Rules?}
  |yes -> Rule-Based Triage -> Identify Likely Cause
  |no -> Search Historical Incidents -> {Similar Found?}
          |yes -> Retrieve Past Solution -> Adapt to Context
          |no -> Dependency Analysis -> Trace Component Graph

{Hypothesis?}
  |generated -> Test Against Logs -> Rank by Evidence
  |none -> [Request More Info]

All Analysis -> Combine Findings -> Generate Recommendation -> [Return Diagnosis]
```

Sample output from debugging assistant:

```
INCIDENT: Order API returning 500 during peak hours

--- SIMILAR PAST INCIDENTS ---
  Case: INC-2024-001
  Similarity: 100%
  Root cause was: connection_pool_exhausted
  Fix applied: increase_pool_size

--- HYPOTHESIS ---
  Based on INC-2024-001 (100% similar):
  Likely root cause: connection_pool_exhausted
  Suggested action: increase_pool_size
  Config change: max_connections: 100 -> 200
```

---

## Technical Implementation

### Module Structure

```
bolor-brain-mcp/
├── modules/
│   ├── reasoning_engines/
│   │   ├── symbolic_reasoner.py     # ~500 lines
│   │   ├── knowledge_graph.py       # ~700 lines
│   │   ├── case_based_reasoner.py   # ~500 lines
│   │   ├── hypothesis_engine.py     # ~400 lines
│   │   ├── analogical_reasoner.py   # ~600 lines
│   │   └── hybrid_reasoner.py       # ~600 lines
│   ├── memory.py                    # 5 memory subsystems
│   ├── drives.py                    # Homeostatic regulation
│   ├── genome.py                    # 60+ cognitive genes
│   └── config.py
├── tests/                           # 400+ pytest tests
├── examples/                        # 6 real-world demos
└── docs/                            # API documentation
```

### Key Metrics

- **5 reasoning engines** with unified interface
- **400+ unit tests** with full coverage
- **60+ configurable parameters** via cognitive genome
- **Thread-safe** for concurrent use
- **Zero external dependencies** for core reasoning

---

## Outcome & Impact

### Technical Achievements
- Single `brain.reason()` call replaces manual approach selection
- Automatic problem type detection with 90%+ accuracy
- Explainable reasoning traces for every decision
- Extensible architecture for adding new reasoning types

### Learning
This project deepened my understanding of:
- Classical AI reasoning techniques (symbolic, case-based, analogical)
- Graph algorithms and knowledge representation
- Designing systems that combine multiple paradigms
- Building thread-safe, production-quality Python modules

### What's Different from LLM-Only Approaches

| Aspect | LLM-Only | Bolor Brain |
|--------|----------|-------------|
| **Reasoning** | Implicit pattern matching | Explicit logical inference |
| **Explainability** | "I think because..." | Step-by-step trace |
| **Consistency** | Varies per query | Deterministic rules |
| **Learning** | Requires fine-tuning | Runtime case storage |
| **Domain Knowledge** | Baked into weights | Explicit graphs & rules |

---

## Links

- **Repository:** [github.com/photoxpedia/bolor-brain-mcp](https://github.com/photoxpedia/bolor-brain-mcp)
- **Documentation:** [docs/README.md](https://github.com/photoxpedia/bolor-brain-mcp/tree/main/docs)
- **Examples:** [examples/](https://github.com/photoxpedia/bolor-brain-mcp/tree/main/examples)

---

**Author:** Bolorerdene Bundgaa
**Website:** [bolor.me](https://bolor.me)
