---
name: autonomous
description: Run Claude Code in autonomous mode - like OpenClaw, but secure
---

# Autonomous Agent Mode

Transform Claude Code into an autonomous agent that runs independently, learns from experience, and improves over time.

**Like OpenClaw, but with:**
- ✅ Bolor Brain memory (structured knowledge, not just embeddings)
- ✅ NSAF evolution (self-improving strategies)
- ✅ Security guardrails (4-tier permission model)
- ✅ Systematic learning (reasoning engines)

## How It Works

```
User gives goal → Agent runs autonomously → Produces results

You: "Build documentation for Bolor Brain"
[walk away]

Agent (autonomously):
├─ Day 1: Analyze codebase, generate architecture docs
├─ Day 2: Create API reference, write examples
├─ Day 3: Integration guides, cross-reference
└─ Complete: Notify you with results

You come back: Documentation exists. Agent learned.
```

## When to Use Autonomous Mode

### ✅ Perfect For:
- **Multi-step projects** - Tasks that take hours/days
- **Well-defined goals** - Clear outcome, flexible approach
- **Learning opportunities** - Agent can improve strategies
- **Recurring tasks** - Will get faster each time

### ❌ Not For:
- **Single quick tasks** - Just do it normally
- **Ambiguous goals** - Need human clarification
- **High-risk operations** - Use manual mode with approvals
- **First-time workflows** - Let agent learn first

## Usage Pattern

### 1. Start Autonomous Mode

```
You: /autonomous Build comprehensive documentation for Bolor Brain MCP.
     Include architecture diagrams, API reference, usage examples,
     and integration guides.
```

### 2. Agent Plans (Bolor Brain Orchestrates)

```
📋 Planning autonomous execution...

Decomposing goal...
✓ Identified 5 task clusters

Task execution order:
1. Read and analyze codebase (priority: 9)
2. Generate architecture documentation (priority: 8)
3. Create API reference (priority: 7)
4. Write usage examples (priority: 6)
5. Create integration guides (priority: 5)

📅 Creating execution schedule...
✓ Schedule created (estimated: ~3-5 hours)

🚀 Starting autonomous execution...
```

### 3. Agent Executes (Claude Code Engine)

```
🔨 Executing: Read and analyze codebase
  └─ Using: Glob tool (find files)
  └─ Using: Read tool (read source)
  └─ Using: Bolor Brain (analyze structure)
✓ Complete (45.2s)
💾 Stored learning: Read and analyze codebase...

🔨 Executing: Generate architecture documentation
  └─ Using: Bolor Brain (recall architecture)
  └─ Using: Write tool (create docs/ARCHITECTURE.md)
✓ Complete (127.8s)
💾 Stored learning: Generate architecture documentation...

🔨 Executing: Create API reference
  └─ Using: Grep tool (find functions)
  └─ Using: Bolor Brain (organize by module)
  └─ Using: Write tool (create docs/API_REFERENCE.md)
✓ Complete (156.4s)
💾 Stored learning: Create API reference...
```

### 4. Agent Learns (Bolor Brain Stores)

```
🧠 Learning from execution...

Patterns identified:
✓ Documentation structure (3 successful cases)
✓ API reference format (1 successful case)
✓ Example code patterns (2 successful cases)

All stored in Bolor Brain for future use.
```

### 5. Agent Completes

```
✅ Goal complete!

Results:
✓ docs/ARCHITECTURE.md (2,847 words)
✓ docs/API_REFERENCE.md (4,123 words)
✓ docs/EXAMPLES.md (18 code examples)
✓ docs/INTEGRATION.md (5 integration patterns)

⏱️  Duration: 2h 14m
📚 Learnings stored: 12 cases
🔄 Evolutions: 1 (improved doc structure)

Next time: Will be 47% faster (learned patterns)
```

## Guardrails (Safety)

Autonomous mode uses 4-tier permission model:

### Tier 0 (Always Safe - Auto-approved)
- Read files
- Analyze code
- Search patterns
- Query knowledge

### Tier 1 (Low Risk - Auto-approved)
- Create new files
- Run tests
- Generate documentation
- Update comments

### Tier 2 (Medium Risk - **Requires Approval**)
- Modify existing code
- Install dependencies
- Change configuration
- Update database

### Tier 3 (High Risk - **Always Requires Approval**)
- Delete files
- Deploy to production
- Commit to git
- Push to remote

**Example:**

```
🔨 Executing: Update database schema
⚠️  Action requires approval (Tier 2)

Action details:
- Type: modify
- Target: database/schema.sql
- Changes: Add user_preferences table

Approve? (y/n):
```

## Monitoring Progress

### Check Status

```
You: How's the autonomous task going?

Agent:
📊 Autonomous Execution Status

Goal: Build documentation for Bolor Brain MCP
Progress: 67% (4/6 tasks)
Time elapsed: 1h 32m
Estimated completion: 43 minutes

Current: Writing usage examples
Status: On track

Completed:
✓ Read codebase
✓ Generate architecture docs
✓ Create API reference
✓ Generate diagrams

Remaining:
- Write usage examples (in progress)
- Create integration guides

Learnings: 8 cases stored
Evolutions: 1 (optimized doc structure)
```

### Pause/Resume

```
You: /pause

Agent:
⏸️  Autonomous execution paused

Current task will complete, then pause.
Use /resume to continue.

---

You: /resume

Agent:
▶️  Autonomous execution resumed

Continuing from: Write usage examples
```

### Stop

```
You: /stop

Agent:
⏹️  Autonomous execution stopped

Progress saved:
✓ 4/6 tasks completed
✓ 8 learnings stored

Partial results available in docs/
Resume later with: /resume
```

## Advanced Features

### Learning from Experience

Every autonomous run stores learnings:

```
Run 1: Build docs (first time)
→ Duration: 3h 47m
→ Stored: 12 patterns

Run 2: Build docs (second time, different project)
→ Duration: 2h 14m (47% faster!)
→ Used: 8 learned patterns
→ Stored: 4 new patterns

Run 3: Build docs (third time)
→ Duration: 1h 38m (57% faster than first!)
→ Used: 12 learned patterns
→ Refined: 2 patterns
```

**Agent gets faster with each run.**

### Evolution (NSAF Integration)

Agent evolves strategies when performance is suboptimal:

```
🔄 Evolving strategy based on learnings...

Performance metrics:
- Success rate: 67% (below threshold)
- Avg duration: 142s (slower than expected)
- Bottleneck: API reference generation

Running NSAF evolution...
Generation 1/5: Fitness 0.45
Generation 2/5: Fitness 0.58
Generation 3/5: Fitness 0.67
Generation 4/5: Fitness 0.72
Generation 5/5: Fitness 0.78

✓ Strategy evolved

Improved approach:
- Group API calls by module (not alphabetically)
- Generate examples inline (not separate section)
- Use consistent formatting template

Applying to remaining tasks...
```

### Self-Monitoring

Agent monitors its own progress and adjusts:

```
Agent (thinking):
"I'm 2 hours in, but only 40% done.
Expected to be 60% done by now.
I'm behind schedule.

Analyzing bottleneck: API reference taking too long.

Options:
1. Continue current approach (finish in 5h total)
2. Evolve faster strategy (finish in 3.5h)
3. Request human help (finish in 2.5h)

Choosing: Option 2 (evolve strategy)
Reason: Within autonomy bounds, no human needed"

🔄 Evolving strategy to catch up...
```

## Integration with Bolor Brain + NSAF

### Architecture

```
┌───────────────────────────────────┐
│  You: Give goal                   │
└───────────────────────────────────┘
              ↓
┌───────────────────────────────────┐
│  Bolor Brain (Orchestrator)       │
│  - Decomposes goal                │
│  - Plans execution                │
│  - Stores learnings               │
│  - Provides reasoning             │
└───────────────────────────────────┘
              ↓
┌───────────────────────────────────┐
│  Task Scheduler                   │
│  - Manages dependencies           │
│  - Prioritizes tasks              │
│  - Tracks progress                │
└───────────────────────────────────┘
              ↓
┌───────────────────────────────────┐
│  Claude Code (Executor)           │
│  - Reads files (Read tool)        │
│  - Writes code (Write tool)       │
│  - Runs commands (Bash tool)      │
│  - Searches (Grep/Glob tools)     │
└───────────────────────────────────┘
              ↓
┌───────────────────────────────────┐
│  Results + Learnings              │
│  - Outcome achieved               │
│  - Patterns stored                │
│  - Strategies improved (NSAF)     │
└───────────────────────────────────┘
```

## Example Workflows

### 1. Documentation Generation

```
/autonomous Build complete docs for Bolor Brain with examples

→ Agent reads codebase
→ Generates architecture overview
→ Creates API reference
→ Writes usage examples
→ Cross-references everything
→ Stores patterns for next time
```

### 2. Bug Fix

```
/autonomous Fix memory leak in production API (logs in logs/error.log)

→ Agent analyzes error logs
→ Generates hypotheses (Bolor Brain)
→ Tests hypotheses
→ Identifies root cause
→ Implements fix
→ Runs tests to verify
→ Stores solution as case
```

### 3. Optimization

```
/autonomous Optimize database query performance in users service

→ Agent profiles current performance
→ Identifies bottlenecks
→ Generates optimization strategies (NSAF)
→ Implements top 3 strategies
→ Benchmarks results
→ Selects best approach
→ Stores patterns
```

### 4. Feature Development

```
/autonomous Implement user authentication with JWT tokens

→ Agent analyzes requirements
→ Searches for similar implementations (Bolor cases)
→ Designs architecture
→ Implements auth system
→ Writes tests
→ Generates documentation
→ Stores as reusable pattern
```

## Tips for Effective Autonomous Mode

### 1. Be Specific About Goals

**Bad:**
```
/autonomous Make the app better
```

**Good:**
```
/autonomous Improve API response time by optimizing database queries.
Current avg response: 340ms. Target: <100ms.
Focus on users and orders endpoints.
```

### 2. Provide Context

**Better:**
```
/autonomous Build documentation for Bolor Brain MCP.

Context:
- Target audience: Claude Code developers
- Include code examples in Python
- Cover MCP setup, reasoning engines, and skills
- Reference existing docs in docs/ for style
```

### 3. Set Boundaries

```
/autonomous Refactor authentication system.

Boundaries:
- Do NOT modify database schema
- Keep existing API contracts
- Maintain backward compatibility
- Require approval for any breaking changes
```

### 4. Trust the Agent

```
❌ Don't micromanage:
   "First read file.py, then check line 47,
    then modify the function, then..."

✅ Give goals:
   "Fix the authentication bug causing 401 errors"
```

## Troubleshooting

### Agent Stuck

```
Problem: Agent hasn't progressed in 30 minutes

Check:
/status

Agent might be:
- Waiting for approval (Tier 2/3 action)
- Encountering errors (check logs)
- Evolving strategy (NSAF running)

Solution:
- Approve pending actions
- Check error logs
- Wait for evolution to complete
```

### Unexpected Results

```
Problem: Agent did something unexpected

Review:
- Check guardrails configuration
- Review execution log
- Examine learnings stored

Adjust:
- Tighten approval tier (require approval for more actions)
- Provide more specific goals
- Add explicit boundaries
```

### Want to Intervene

```
You can:
/pause - Finish current task, then pause
/stop - Stop immediately
/adjust "Use different approach: XYZ" - Give feedback

Agent will:
- Incorporate your feedback
- Adjust strategy
- Continue with new approach
```

## Key Principles

1. **Give clear goals** - Agent needs to know the destination
2. **Trust the process** - Agent learns and improves
3. **Set guardrails** - Define what's off-limits
4. **Review learnings** - Agent stores patterns for future use
5. **Iterate** - Each run makes the agent smarter

---

**Autonomous mode turns Claude Code into a self-improving agent that learns from experience and gets better over time.**

**Like OpenClaw's magic, but with Bolor Brain's memory and NSAF's evolution - secure and systematic.**
