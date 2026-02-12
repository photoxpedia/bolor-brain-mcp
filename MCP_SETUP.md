# Bolor Brain MCP Setup Guide

Complete guide to installing and using Bolor Brain with Claude Code.

## Installation

### Option 1: Install from Source (Recommended for now)

```bash
# Clone the repository
git clone https://github.com/photoxpedia/bolor-brain-mcp.git
cd bolor-brain-mcp

# Install in development mode
pip install -e .
```

### Option 2: Install from PyPI (Coming Soon)

```bash
pip install bolor-brain-mcp
```

## Configure Claude Code

### For Claude Code CLI

Add to your Claude Code MCP configuration (`~/.claude/mcp-config.json`):

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

Replace `/path/to/bolor-brain-mcp` with your actual installation path.

### For Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

## Verify Installation

1. **Restart Claude Code** (or Claude Desktop)

2. **Check available tools:**
   ```
   You: What tools do you have access to?
   Claude: [should list bolor-brain tools]
   ```

3. **Test a simple query:**
   ```
   You: Use reason_hybrid to explain why Python is popular for ML
   Claude: [calls bolor-brain.reason_hybrid tool]
   ```

## Available Tools

### `reason_hybrid` ⭐ (Recommended)

Universal reasoning that automatically selects the best approach.

**Example:**
```
User: Use reason_hybrid to diagnose why my API is slow

Claude will:
1. Detect problem type (diagnosis)
2. Use hypothesis + case-based reasoning
3. Return conclusions with confidence scores
```

### `reason_symbolic`

Rule-based logical inference with forward/backward chaining.

**Example:**
```
User: Use reason_symbolic with facts:
- ["Python", "has", "simple_syntax"]
- ["simple_syntax", "enables", "fast_learning"]
Query: What does Python enable?
```

### `reason_knowledge_graph`

Graph-based relationship exploration.

**Example:**
```
User: Use reason_knowledge_graph to find how "Python" connects to "AI"
With nodes: Python, NumPy, TensorFlow, AI
And edges: Python->NumPy, NumPy->TensorFlow, TensorFlow->AI
```

### `reason_case_based`

Learn from past experiences and adapt solutions.

**Example:**
```
User: Use reason_case_based for a memory leak issue
Problem: {"symptom": "memory_growing", "context": "production"}
```

### `reason_hypothesis`

Generate and test hypotheses for diagnostic problems.

**Example:**
```
User: Use reason_hypothesis for "server crashes under load"
Evidence: {"cpu": "normal", "memory": "high", "connections": "maxed"}
```

### `reason_analogical`

Cross-domain pattern transfer.

**Example:**
```
User: Use reason_analogical: atom structure is like solar system
Source: atom, Target: solar_system
```

### `store_case`

Save experiences for future learning.

**Example:**
```
User: Store this case:
Problem: {"error": "connection_timeout"}
Solution: {"fix": "increase_pool_size"}
Success: true
```

### `add_knowledge`

Teach the brain domain-specific knowledge.

**Example:**
```
User: Add knowledge:
Type: fact
Data: {"subject": "Rust", "predicate": "provides", "object": "memory_safety"}
```

### `get_stats`

Get statistics about the brain's knowledge base.

## Usage Patterns

### Pattern 1: Debugging

```
User: I have a bug where users can't login after deployment

Claude: Let me use Bolor Brain to diagnose this.
[calls reason_hybrid with the problem description]

Result:
- Problem type: diagnosis
- Approaches: hypothesis + case-based
- Likely cause: session storage configuration changed (confidence: 0.85)
- Similar past case: deployment-2024-001 (fixed by reverting session config)
```

### Pattern 2: Technical Decisions

```
User: Should I use React or Vue for my new project?

Claude: Let me analyze this decision systematically.
[calls reason_hybrid with context about your project]

Result:
- Problem type: decision
- Approaches: knowledge graph + case-based + symbolic
- Recommendation: React (confidence: 0.78)
- Reasoning: Large ecosystem, team experience, similar past projects succeeded
```

### Pattern 3: Learning from Experience

```
User: We just fixed a performance issue. Store this for future reference.
Problem: {"symptom": "slow_queries", "scale": "10k_users"}
Solution: {"fix": "add_database_index", "index": "user_id"}
Outcome: {"latency_improvement": "80%"}

Claude: [calls store_case]
Done! This case is now stored and will help with similar issues in the future.
```

## Troubleshooting

### Tools not showing up

1. Check MCP config path is correct
2. Restart Claude Code completely
3. Check logs: `tail -f ~/.claude/logs/mcp.log`

### Import errors

```bash
# Make sure all dependencies are installed
pip install -e .

# Verify installation
python -c "from modules import HybridReasoner; print('OK')"
```

### Server not starting

```bash
# Test the server directly
python mcp_server.py

# Check Python version (requires 3.11+)
python --version
```

## Advanced Configuration

### Custom Knowledge Base

Create a startup script that pre-loads domain knowledge:

```python
# startup_knowledge.py
from modules import HybridReasoner, Fact, Node, Edge

brain = HybridReasoner()

# Add your domain facts
brain.add_fact(Fact("Django", "is", "Python_framework"))
brain.add_fact(Fact("Django", "good_for", "rapid_development"))

# Add your domain graph
brain.add_node(Node("Django", "Django Framework", "framework"))
brain.add_node(Node("REST", "REST APIs", "pattern"))
brain.add_edge(Edge("Django", "REST", "supports"))
```

### Memory Persistence

By default, the brain's memory is per-session. To persist knowledge:

```python
# TODO: Add persistence layer
# Coming in v1.1
```

## Best Practices

1. **Use `reason_hybrid` by default** - Let the brain choose the best approach
2. **Provide context** - More context = better reasoning
3. **Store successful solutions** - Help the brain learn
4. **Be specific in queries** - "API slow under load" better than "performance issue"
5. **Check confidence scores** - Low confidence = needs more information

## Examples Repository

See `examples/` directory for detailed use cases:
- `tech_decision_reasoner.py` - Framework selection
- `debugging_assistant.py` - Root cause analysis
- `learning_path_advisor.py` - Skill development planning

## Need Help?

- **Documentation:** [docs/README.md](docs/README.md)
- **Issues:** [GitHub Issues](https://github.com/photoxpedia/bolor-brain-mcp/issues)
- **Author:** [bolor.me](https://bolor.me)
