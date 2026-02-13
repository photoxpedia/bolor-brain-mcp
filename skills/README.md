# Bolor Brain Skills for Claude Code

Skills that tell Claude Code WHEN and HOW to use Bolor Brain's reasoning tools.

## Available Skills

| Skill | File | When To Use |
|-------|------|------------|
| `/reason` | [reason.md](reason.md) | Deep analysis of complex problems |
| `/debug` | [debug.md](debug.md) | Systematic bug hunting with hypothesis testing |
| `/decide` | [decide.md](decide.md) | Evidence-based technical decisions |
| `/learn-from` | [learn-from.md](learn-from.md) | Store experiences for future use |
| `/nsaf` | [nsaf.md](nsaf.md) | NSAF evolution integration (requires NSAF MCP) |
| `/orchestrate` | [orchestrate.md](orchestrate.md) | Meta-orchestration combining Bolor Brain + NSAF |

## How Skills Work

Skills are instructions that guide Claude Code to call the right Bolor Brain MCP tools in the right order.

Example flow for `/debug`:

```
User: /debug checkout endpoint returns 500 errors

Claude Code:
1. Gathers context (reads logs, code)
2. Calls reason_case_based (search past incidents)
3. Calls reason_hypothesis (generate theories)
4. Calls reason_hybrid (combine findings)
5. Presents diagnosis with confidence
6. After fix: calls learn (store for next time)
```

## MCP Tools Used by Skills

| Skill | Primary Tools |
|-------|---------------|
| `/reason` | `reason_hybrid` |
| `/debug` | `reason_case_based`, `reason_hypothesis`, `learn` |
| `/decide` | `reason_hybrid`, `reason_symbolic`, `reason_knowledge_graph` |
| `/learn-from` | `learn`, `remember` |
| `/nsaf` | NSAF MCP tools + `reason_hybrid` |
| `/orchestrate` | Both Bolor Brain + NSAF MCP tools |

## Prerequisites

- Bolor Brain MCP server configured in `~/.claude/mcp-config.json`
- For `/nsaf` and `/orchestrate`: NSAF MCP server also configured
