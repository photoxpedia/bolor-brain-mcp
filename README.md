# Bolor Brain MCP

**Pure intelligence for Claude Code.** Reasoning, memory, and learning -- nothing else.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

---

## What Is This?

Bolor Brain is an MCP server that gives Claude Code a **brain**: structured reasoning, persistent memory, and learning from experience.

```
User --> Claude Code (Gateway + Executor)
              |
         +----+----+
    Bolor Brain   NSAF
      (MCP)       (MCP)
      THINK       EVOLVE
```

- **Claude Code** = Gateway + tool execution + sessions + permissions
- **Bolor Brain** = Reasoning engines + memory + learning + persistence
- **NSAF** = Strategy evolution + self-improvement (separate MCP server)

Bolor Brain does NOT execute anything. No file ops, no scheduling, no autonomous loop. Claude Code already does all of that. Bolor Brain only thinks.

---

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

### 3. Use

```
/reason Why is Python popular for data science?
/debug API returns 500 errors under load
/decide PostgreSQL or MongoDB for our app?
/learn-from We fixed the memory leak by increasing connection pool
```

---

## MCP Tools (11)

### Reasoning (6)

| Tool | What It Does |
|------|-------------|
| `reason_hybrid` | Auto-selects best reasoning approach for any query |
| `reason_symbolic` | Forward/backward chaining with facts and rules |
| `reason_knowledge_graph` | Graph traversal, path finding, relationship exploration |
| `reason_case_based` | Find similar past problems and their solutions |
| `reason_hypothesis` | Generate and test hypotheses from observations |
| `reason_analogical` | Cross-domain pattern transfer (atom ~ solar system) |

### Memory (4)

| Tool | What It Does |
|------|-------------|
| `remember` | Store a case, fact, node, or edge |
| `recall` | Retrieve matching cases or facts |
| `learn` | Store problem/solution/outcome (shortcut for remember) |
| `forget` | Delete a case or fact by ID |

### Utility (1)

| Tool | What It Does |
|------|-------------|
| `brain_stats` | Cases, facts, nodes, edges count |

---

## Skills (6)

| Skill | When To Use |
|-------|------------|
| `/reason` | Deep analysis of any complex problem |
| `/debug` | Systematic bug hunting with hypothesis testing |
| `/decide` | Evidence-based technical decisions |
| `/learn-from` | Store experiences for future use |
| `/nsaf` | NSAF evolution integration (requires NSAF MCP) |
| `/orchestrate` | Meta-orchestration combining Bolor Brain + NSAF |

---

## Persistence

Brain state persists to `~/.bolor-brain/` as JSON:

```
~/.bolor-brain/
  cases.json       # Problem -> solution -> outcome
  facts.json       # Symbolic reasoning facts
  knowledge.json   # Knowledge graph (nodes + edges)
```

Knowledge compounds over time. Solve a bug once, recall the solution instantly next time.

---

## With NSAF

Add NSAF to get evolution capabilities:

```json
{
  "mcpServers": {
    "bolor-brain": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/bolor-brain-mcp"
    },
    "nsaf": {
      "command": "python3",
      "args": ["nsaf_mcp_server.py"],
      "cwd": "/path/to/nsaf",
      "env": { "PYTHONPATH": "/path/to/nsaf" }
    }
  }
}
```

Together: Bolor Brain reasons about WHAT to do. NSAF evolves HOW to do it better. Claude Code executes.

See [skills/nsaf.md](skills/nsaf.md) and [skills/orchestrate.md](skills/orchestrate.md) for combined workflows.

---

## Testing

```bash
pytest tests/ -v
# 376 tests
```

---

## Project Structure

```
mcp_server.py                    # MCP server (11 tools)
persistence.py                   # JSON persistence to ~/.bolor-brain/
modules/
  config.py                      # Configuration
  reasoning_engines/
    symbolic_reasoner.py          # Forward/backward chaining
    knowledge_graph.py            # Graph-based knowledge
    case_based_reasoner.py        # 4R cycle (retrieve, reuse, revise, retain)
    hypothesis_engine.py          # Hypothesis generation and testing
    analogical_reasoner.py        # Cross-domain pattern transfer
    hybrid_reasoner.py            # Orchestrates all 5 engines
skills/                          # Claude Code skills
  reason.md, debug.md, decide.md, learn-from.md, nsaf.md, orchestrate.md
tests/                           # 376 tests
AGENT_GUARDRAILS.md              # Production safety guidelines
```

---

## Author

**Bolorerdene Bundgaa**
- Website: [bolor.me](https://bolor.me)
- Email: bolor@ariunbolor.org

## License

MIT -- see [LICENSE](LICENSE)
