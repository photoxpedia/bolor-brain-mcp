# Bolor Brain: Pure Intelligence MCP Refactor

**Date:** 2026-02-12
**Status:** Approved
**Branch:** `refactor/pure-intelligence`

## Vision

```
Bolor Brain MCP + NSAF MCP + Claude Code = Better than OpenClaw
```

Claude Code IS the gateway. It already has persistent sessions, tool execution, scheduling, permissions, and routing. Bolor Brain should NOT reinvent any of that. Bolor Brain should ONLY be the brain: reasoning, memory, learning.

## Architecture (After Refactor)

```
User --> Claude Code (Gateway + Executor)
              |
         +----+----+
    Bolor Brain   NSAF
      (MCP)       (MCP)
      THINK       EVOLVE
```

- **Claude Code** = Gateway + Tool execution + Session + Routing + Scheduling + Permissions
- **Bolor Brain MCP** = Reasoning engines + Memory + Learning + Knowledge persistence
- **NSAF MCP** = Strategy evolution + Self-improvement (future, separate project)
- **Skills** = Glue that tells Claude Code WHEN to call Bolor Brain

## What Changes

### DELETE (Claude Code already does this)

| File | Why |
|------|-----|
| `autonomous_loop.py` | Claude Code IS the loop |
| `claude_code_engine.py` | Claude Code has Read/Write/Bash/Glob/Grep |
| `task_scheduler.py` | Claude Code has TaskCreate/TaskUpdate |
| `goal_decomposer.py` | Hardcoded heuristics, not using reasoning engines |
| `approval_system.py` | Claude Code has built-in permissions |
| `state_manager.py` | Claude Code has session persistence |
| `progress_monitor.py` | Claude Code tracks progress |
| `nsaf_client.py` | Stub that always returns None (NSAF is separate project) |
| `modules/genome.py` | Not used by MCP tools |
| `modules/drives.py` | Not used by MCP tools |
| `modules/evolutionary.py` | Not used by MCP tools |
| `modules/collective.py` | Not used by MCP tools |
| `modules/orchestration.py` | Not used by MCP tools |
| `modules/universal.py` | Not used by MCP tools |
| `modules/predictive.py` | Not used by MCP tools |
| `modules/metacognitive.py` | Not used by MCP tools |
| `modules/reasoning.py` | Not used by MCP tools |
| `modules/llm_bridge.py` | Not used by MCP tools |
| `modules/embeddings.py` | Not used by MCP tools |
| `modules/integration.py` | Not used by MCP tools |

### KEEP (the actual brain)

| File | What It Does |
|------|-------------|
| `modules/reasoning_engines/symbolic_reasoner.py` | Forward/backward chaining with rules and facts |
| `modules/reasoning_engines/knowledge_graph.py` | Graph-based knowledge with traversal |
| `modules/reasoning_engines/case_based_reasoner.py` | Learn from experience (4R cycle) |
| `modules/reasoning_engines/hypothesis_engine.py` | Generate and test hypotheses |
| `modules/reasoning_engines/analogical_reasoner.py` | Cross-domain pattern transfer |
| `modules/reasoning_engines/hybrid_reasoner.py` | Orchestrates all 5 engines, auto-detects problem type |
| `modules/memory.py` | Multi-level memory (working, episodic, semantic, procedural) |
| `modules/config.py` | Configuration (simplified) |

### NEW

| File | What It Does |
|------|-------------|
| `persistence.py` | JSON file persistence to `~/.bolor-brain/` |

### MODIFY

| File | Changes |
|------|---------|
| `mcp_server.py` | Remove autonomous tools, add memory/persistence tools |
| `modules/__init__.py` | Minimal exports (reasoning engines + memory + config only) |
| `__main__.py` | Simplified entry point |
| `pyproject.toml` | Remove unused dependencies |
| `skills/*` | Rewrite all skills for Claude Code as gateway |

## MCP Tools (Final List)

### Reasoning Tools

| Tool | Input | Output |
|------|-------|--------|
| `reason` | query, context | problem_type, approaches_used, confidence, result, trace |
| `reason_symbolic` | query, facts, mode | derived_facts, conclusions, trace |
| `reason_graph` | query, nodes, edges, source, target | paths, stats |
| `reason_cases` | problem, k | similar_cases with similarity scores |
| `reason_hypothesis` | observation, evidence | ranked hypotheses with confidence |
| `reason_analogy` | source_domain, target_domain, concepts | analogies with mappings |

### Memory Tools

| Tool | Input | Output |
|------|-------|--------|
| `remember` | type (case/fact/node/edge), data | stored confirmation |
| `recall` | query, type, k | matching cases/facts/knowledge |
| `learn` | problem, solution, outcome, success | case stored for future |
| `forget` | type, id | removed from knowledge base |

### Utility Tools

| Tool | Input | Output |
|------|-------|--------|
| `brain_stats` | (none) | facts count, cases count, nodes count, edges count |

**Total: 11 tools. Pure intelligence. No execution.**

## Persistence

```
~/.bolor-brain/
  cases.json         # Case library (problem -> solution -> outcome)
  facts.json         # Symbolic reasoning facts
  knowledge.json     # Knowledge graph (nodes + edges)
  stats.json         # Usage statistics
```

- Loaded on MCP server start
- Saved after every write operation (remember, learn, forget)
- JSON format for simplicity and debuggability

## Data Flow (After Refactor)

### Example: Debugging a Bug

```
1. User: "Fix the login bug"

2. Claude Code (gateway):
   - Reads error logs (Read tool)
   - Calls: reason_hypothesis("login 401 errors", evidence={stack_trace, logs})

3. Bolor Brain (MCP):
   - Checks case library for similar bugs
   - Generates hypotheses using evidence
   - Returns ranked hypotheses with confidence

4. Claude Code:
   - Tests hypothesis #1 (Bash tool)
   - Confirms root cause
   - Implements fix (Edit tool)
   - Calls: learn(problem={login_401}, solution={fix_token_refresh}, outcome={success})

5. Bolor Brain:
   - Stores case in cases.json
   - Updates knowledge graph

6. Next time similar bug:
   - Claude Code calls: recall(problem={login_error})
   - Brain returns previous solution instantly
   - 47% faster resolution
```

### Example: Architecture Decision

```
1. User: "Should we use Redis or Memcached for caching?"

2. Claude Code:
   - Calls: reason(query="Redis vs Memcached", context={use_case, requirements})

3. Bolor Brain:
   - Symbolic: Evaluates facts about both technologies
   - Knowledge Graph: Maps relationships (features, trade-offs)
   - Case-Based: Finds similar decisions from past
   - Analogical: Maps patterns from similar domains
   - Returns combined analysis with confidence

4. Claude Code:
   - Presents analysis to user
   - Calls: remember(type="case", data={decision, rationale, context})
```

## Skills (After Refactor)

### /reason
When user asks Claude Code to think deeply about something, this skill tells it to call Bolor Brain's `reason` tool and present the structured analysis.

### /debug
When debugging, tells Claude Code to use `reason_hypothesis` + `recall` for similar bugs + `learn` to store the solution.

### /decide
For decisions, tells Claude Code to use `reason` with full context + present trade-offs from knowledge graph.

### /learn-from
After completing any task, tells Claude Code to call `learn` to store the experience.

## What We DON'T Build

- No autonomous loop (Claude Code is the loop)
- No task scheduler (Claude Code has TaskCreate/TaskUpdate)
- No file operations (Claude Code has Read/Write/Bash/Glob/Grep)
- No approval system (Claude Code has permissions)
- No state manager (Claude Code has sessions)
- No progress monitor (Claude Code tracks progress)
- No NSAF integration (that's a separate MCP server)
- No cognitive tiers beyond reasoning engines (YAGNI)

## Implementation Order

1. Create feature branch `refactor/pure-intelligence`
2. Create `persistence.py` (JSON file storage)
3. Rewrite `mcp_server.py` (brain-only tools)
4. Rewrite `modules/__init__.py` (minimal exports)
5. Simplify `modules/config.py`
6. Delete all redundant files
7. Update `pyproject.toml`
8. Rewrite skills
9. Test MCP server starts and tools respond
10. Update README
