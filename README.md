# Bolor Brain MCP

**The Universal Reasoning Toolkit for Claude Code** - Give Claude structured thinking capabilities through multiple reasoning engines.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

## What is Bolor Brain?

Bolor Brain is an **MCP server** that extends Claude Code with powerful reasoning capabilities. Instead of just pattern matching, Claude can now:
- 🧠 Use symbolic logic for deduction
- 🕸️ Traverse knowledge graphs
- 📚 Learn from past cases
- 🔬 Generate and test hypotheses
- 🔄 Transfer patterns between domains

All through simple tool calls in your Claude Code conversations.

## Quick Start

### 1. Install

```bash
git clone https://github.com/photoxpedia/bolor-brain-mcp.git
cd bolor-brain-mcp
pip install -e .
```

### 2. Configure Claude Code

Add to `~/.claude/mcp-config.json`:

```json
{
  "mcpServers": {
    "bolor-brain": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/bolor-brain-mcp"
    }
  }
}
```

### 3. Use in Claude Code

```
You: Use reason_hybrid to explain why my API is slow under load

Claude: [calls bolor-brain reasoning tools]
→ Problem type: diagnosis
→ Approaches used: hypothesis + case-based
→ Likely cause: connection pool exhausted (confidence: 85%)
→ Evidence: Similar to incident INC-2024-001
→ Recommended fix: Increase max_connections from 100 to 200
```

**That's it!** Claude now has structured reasoning.

## Reasoning Engines

Bolor Brain provides 6 reasoning approaches accessible via MCP tools:

| Engine | Description |
|--------|-------------|
| **Symbolic Reasoner** | Forward/backward chaining with rules and facts |
| **Knowledge Graph** | Graph-based knowledge with traversal, PageRank, inference |
| **Case-Based Reasoner** | Experience-based reasoning with 4R cycle |
| **Hypothesis Engine** | Hypothesis generation, testing, and ranking |
| **Analogical Reasoner** | Cross-domain pattern transfer using Structure-Mapping |
| **Hybrid Reasoner** | Orchestrates all approaches with ONE call |

## MCP Tools

Claude Code can call these tools directly:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `reason_hybrid` ⭐ | Auto-select best approach | "Why is my system crashing?" |
| `reason_symbolic` | Logical deduction | "If X causes Y, and Y causes Z..." |
| `reason_knowledge_graph` | Explore relationships | "How are Python and ML connected?" |
| `reason_case_based` | Learn from experience | "We had this bug before..." |
| `reason_hypothesis` | Test theories | "What could cause this symptom?" |
| `reason_analogical` | Cross-domain transfer | "Atom is like solar system..." |
| `store_case` | Save for learning | Store successful solutions |
| `add_knowledge` | Teach the brain | Add domain facts/rules |

## Real-World Usage

### Debugging with Claude Code

```
You: My API returns 500 errors under high load. Diagnose the issue.

Claude: Let me use Bolor Brain to analyze this systematically.
[calls reason_hybrid tool]

Result:
┌─ Diagnosis ────────────────────────────────────────┐
│ Problem Type: diagnosis                             │
│ Approaches: hypothesis + case-based                 │
│                                                      │
│ Root Cause: Connection pool exhausted (85% conf)    │
│ Evidence: Found similar case INC-2024-001 (95%)     │
│ Past Solution: Increased pool from 100 → 200        │
│ Recommendation: Apply same fix                      │
└─────────────────────────────────────────────────────┘

Claude: Based on the reasoning, your issue matches a past incident
where the database connection pool was exhausted. The fix was to
increase max_connections in your config from 100 to 200.
```

### Technical Decisions

```
You: Should I use PyTorch or JAX for our new ML project?
Context: We have TPUs, team size is 5, focus on research

Claude: [calls reason_hybrid with full context]

Result:
┌─ Decision Analysis ─────────────────────────────────┐
│ Problem Type: decision                               │
│ Approaches: symbolic + knowledge graph + case-based  │
│                                                       │
│ Recommendation: JAX (confidence: 87%)                │
│                                                       │
│ Reasoning:                                           │
│ • TPU optimization: JAX is designed for TPUs         │
│ • Past success: Similar research teams used JAX      │
│ • Knowledge graph: JAX→TPU edge weight: 0.95         │
│ • Rule fired: "tpu_suggests_jax" (priority: high)    │
└──────────────────────────────────────────────────────┘
```

## How It Works

When you call `reason_hybrid`, the brain:
1. **Detects problem type** from your query (deduction, diagnosis, planning, etc.)
2. **Selects best approaches** automatically
3. **Combines results** from multiple reasoning engines
4. **Returns conclusions** with confidence scores and reasoning trace

| Problem Type | Detects From | Uses |
|--------------|--------------|------|
| **Deduction** | "conclude", "deduce", "infer" | Symbolic + Graph |
| **Diagnosis** | "why", "cause", "diagnose" | Hypothesis + Case-Based |
| **Planning** | "how to", "steps", "plan" | Graph + Case-Based |
| **Decision** | "should I", "choose", "recommend" | All approaches |
| **Analogy** | "similar", "like", "analogous" | Analogical + Case-Based |
| **Classification** | "what type", "classify" | Case-Based + Symbolic |

## Documentation

### For Claude Code Users

- **[MCP Setup Guide](MCP_SETUP.md)** - Complete installation and usage guide
- **[Tool Reference](MCP_SETUP.md#available-tools)** - All available MCP tools
- **[Usage Patterns](MCP_SETUP.md#usage-patterns)** - Common workflows
- **[Troubleshooting](MCP_SETUP.md#troubleshooting)** - Fix common issues

### For Python Developers

The reasoning engines can also be used directly in Python:

```python
from modules import HybridReasoner, Fact, Node, Edge, Case

# Create the brain
brain = HybridReasoner()

# Add knowledge
brain.add_fact(Fact("python", "is", "language"))
brain.add_node(Node("python", "Python"))
brain.add_edge(Edge("python", "web", "used_for"))

# Reason
result = brain.reason({"query": "What is Python used for?"})
print(f"Confidence: {result.confidence:.2%}")
print(f"Result: {result.combined_result}")
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
