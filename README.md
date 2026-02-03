# Bolor Brain MCP

**The Universal Thinking MCP** - A comprehensive reasoning and cognitive architecture for AI systems.

## Overview

Bolor Brain MCP provides a unified interface to multiple reasoning approaches:

| Engine | Description |
|--------|-------------|
| **Symbolic Reasoner** | Forward/backward chaining with rules and facts |
| **Knowledge Graph** | Graph-based knowledge with traversal, PageRank, inference |
| **Case-Based Reasoner** | Experience-based reasoning with 4R cycle |
| **Hypothesis Engine** | Hypothesis generation, testing, and ranking |
| **Analogical Reasoner** | Cross-domain pattern transfer using Structure-Mapping |
| **Hybrid Reasoner** | Orchestrates all approaches with ONE call |

## Installation

```bash
git clone https://github.com/photoxpedia/bolor-brain-mcp.git
cd bolor-brain-mcp
pip install -r requirements.txt
```

## Quick Start

```python
from modules import HybridReasoner, Fact, Node, Edge, Case

# Create the brain
brain = HybridReasoner()

# Add knowledge
brain.add_fact(Fact(subject="python", predicate="is_a", object="language"))
brain.add_node(Node(id="python", label="Python"))
brain.add_node(Node(id="web", label="Web Development"))
brain.add_edge(Edge(source="python", target="web", relation="used_for"))

# ONE CALL - brain handles everything
result = brain.reason({"query": "What is Python used for?"})

print(f"Problem Type: {result.problem_type.value}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Approaches: {[a.value for a in result.approaches_used]}")
```

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
└─────────────────────────────────────────────────────────────┘
```

## Problem Types

The brain auto-detects problem type and selects appropriate approaches:

| Type | Keywords | Approaches |
|------|----------|------------|
| Deduction | "conclude", "deduce" | Symbolic, Graph |
| Abduction | "why", "cause", "explain" | Hypothesis, Symbolic |
| Analogy | "similar", "like" | Analogical, Case-Based |
| Planning | "how to", "steps" | Graph, Case-Based |
| Diagnosis | "diagnose", "problem" | Hypothesis, Case-Based |
| Classification | "classify", "type of" | Case-Based, Symbolic |
| Exploration | "what", "find" | Graph, Analogical |

## API

### Main Interface

```python
# Full reasoning with options
result = brain.reason({
    "query": "your question",
    "context": {"domain": "...", "goal": "..."}
})

# Quick reasoning - just pass a string
result = brain.quick_reason("your question")
```

### Adding Knowledge

```python
# Symbolic facts and rules
brain.add_fact(Fact(subject="X", predicate="causes", object="Y"))
brain.add_rule(Rule(name="r1", conditions=[...], conclusion_template={...}))

# Knowledge graph
brain.add_node(Node(id="n1", label="Concept"))
brain.add_edge(Edge(source="n1", target="n2", relation="relates_to"))

# Past cases
brain.add_case(Case(id="c1", problem={...}, solution={...}, outcome="success"))

# Analogical concepts
brain.add_concept(Concept(id="c1", name="Thing", domain="domain1"))
```

### Result Object

```python
result.problem_type      # Detected: deduction, abduction, analogy, etc.
result.approaches_used   # [ReasoningApproach.SYMBOLIC, ...]
result.confidence        # 0.0 to 1.0
result.combined_result   # {"conclusions": [...], "evidence": [...]}
result.reasoning_trace   # ["Step 1...", "Step 2..."]
result.processing_time   # Seconds
```

## Testing

```bash
# Run all tests (400 tests)
pytest tests/ -v

# Quick check
pytest tests/ -q
```

## Project Structure

```
bolor-brain-mcp/
├── modules/
│   ├── __init__.py                  # Main exports
│   ├── reasoning_engines/           # Core reasoning (Phase 2)
│   │   ├── symbolic_reasoner.py     # ~500 lines
│   │   ├── knowledge_graph.py       # ~700 lines
│   │   ├── case_based_reasoner.py   # ~500 lines
│   │   ├── hypothesis_engine.py     # ~400 lines
│   │   ├── analogical_reasoner.py   # ~600 lines
│   │   └── hybrid_reasoner.py       # ~600 lines
│   ├── config.py                    # Configuration
│   ├── genome.py                    # Cognitive genome (60+ genes)
│   └── llm_bridge.py                # Optional LLM integration
├── tests/                           # 400 pytest tests
├── docs/                            # Documentation
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- pytest (for testing)

## License

MIT License - see [LICENSE](LICENSE)

## Author

**Bolorerdene Bundgaa** - [bolor.me](https://bolor.me)
