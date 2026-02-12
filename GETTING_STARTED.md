# Getting Started with Bolor Brain MCP

**Transform Claude Code into a secure autonomous agent in 3 steps.**

---

## ⚡ Quick Installation

### 1. Clone and Install
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
      "cwd": "/absolute/path/to/bolor-brain-mcp"
    }
  }
}
```

### 3. Restart Claude Code
```bash
# Exit current session and restart
exit
claude
```

**That's it!** Bolor Brain is now active.

---

## 🤖 Your First Autonomous Task

Try this in Claude Code:

```
/autonomous Create a simple README.md for a Python project.
Include: project description, installation steps, and usage example.
```

**What happens:**
1. Agent decomposes goal into tasks
2. Executes autonomously
3. Creates the file
4. Stores learnings for next time

**You literally walk away and come back to results.**

---

## 🧠 Your First Reasoning Task

Try systematic debugging:

```
/debug My API returns 500 errors under high load.
Errors appear after 1000 concurrent requests.
Database and CPU usage are normal.
```

**What happens:**
1. Searches past similar incidents
2. Generates ranked hypotheses
3. Tests each systematically
4. Returns diagnosis with confidence score

**Example output:**
```
✅ Diagnosis: Connection pool exhausted (85% confidence)
📚 Similar case: INC-2024-001 (95% match)
💡 Solution: Increase max_connections from 100 to 200
📊 Past success rate: 94%
```

---

## 🎯 What to Try Next

### Reasoning Skills

**Make a decision:**
```
/decide Should I use PostgreSQL or MongoDB?
Context: Team of 5, SQL experience, relational data, complex queries
```

**Learn from experience:**
```
/learn-from We fixed the memory leak by increasing connection pool to 200
```

**Reason about anything:**
```
/reason Why is Python popular for data science?
```

### Autonomous Tasks

**Generate documentation:**
```
/autonomous Build API documentation for this project with code examples
```

**Debug systematically:**
```
/debug Memory usage increases over time in production
```

**Optimize code:**
```
/autonomous Optimize database query performance in user service
```

### Advanced

**Meta-orchestration (Bolor Brain + NSAF):**
```
/orchestrate Improve customer support ticket routing accuracy
```

---

## 📚 Available Skills

| Skill | Purpose | Example |
|-------|---------|---------|
| `/reason` | Universal reasoning | Any question or problem |
| `/debug` | Systematic debugging | Production issues |
| `/decide` | Evidence-based decisions | Technology choices |
| `/learn-from` | Store experience | Successful solutions |
| `/autonomous` | Autonomous execution | Multi-step tasks |
| `/nsaf` | Self-evolving agents | Optimization problems |
| `/orchestrate` | Combined power | Complex challenges |

---

## 🐛 Troubleshooting

### Tools not showing up

**Problem:** Claude says "I don't have access to bolor-brain tools"

**Solution:**
1. Verify config: `cat ~/.claude/mcp-config.json`
2. Check path is absolute (not relative)
3. Restart Claude Code completely
4. Test server: `python -m mcp_server`

### Import errors

**Problem:** MCP server fails to start

**Solution:**
```bash
cd bolor-brain-mcp
pip install -e .
python -c "from modules import HybridReasoner; print('OK')"
```

### Skills not loading

**Problem:** `/reason` or `/autonomous` don't work

**Solution:**
1. Ensure MCP server is running first
2. Check skills exist: `ls skills/*.md`
3. Try using tools directly before skills

### Autonomous agent stuck

**Problem:** Agent hasn't progressed in 10 minutes

**Solution:**
- Check if waiting for approval (Tier 2/3 action)
- Review execution logs
- Try with simpler goal first

---

## ✅ Verify Installation

Run these commands to verify everything works:

```bash
# 1. Test MCP server starts
python -m mcp_server
# Expected: "Starting Bolor Brain MCP Server..."
# Press Ctrl+C to stop

# 2. Test autonomous loop
python autonomous_loop.py
# Expected: Full autonomous execution with 100% success

# 3. Test in Claude Code
# Type: /reason Why is Python popular?
# Expected: Analysis with confidence score and reasoning trace
```

---

## 🎓 Learning Path

### Day 1: Basics
- ✅ Install and configure
- ✅ Try `/reason` with simple question
- ✅ Try `/debug` with a problem
- ✅ Understand how skills work

### Day 2: Autonomous Mode
- ✅ Try `/autonomous` with simple task
- ✅ Watch it decompose and execute
- ✅ See learnings stored
- ✅ Run same task again (notice it's faster)

### Day 3: Advanced
- ✅ Use `/decide` for real decision
- ✅ Store your own cases with `/learn-from`
- ✅ Try `/orchestrate` for complex problem
- ✅ Build custom workflows

### Week 2: Production
- ✅ Use for real debugging
- ✅ Build knowledge base for your team
- ✅ Autonomous documentation generation
- ✅ Let it learn your patterns

---

## 💡 Tips for Success

### 1. Be Specific
**Bad:** `/autonomous Make the app better`

**Good:** `/autonomous Optimize API response times. Target: <100ms. Focus on database queries.`

### 2. Provide Context
**Better:**
```
/decide PostgreSQL vs MongoDB

Context:
- Team: 5 developers with SQL experience
- Data: Relational (users, orders, products)
- Queries: Complex joins and aggregations
- Scale: 100K users expected
```

### 3. Learn from Every Task
After solving a problem:
```
/learn-from We fixed the performance issue by adding an index on user_id column. Query time: 2000ms → 45ms.
```

### 4. Trust the Agent
Don't micromanage autonomous tasks. Give high-level goals and let it work.

### 5. Build Knowledge Over Time
The more you use it, the smarter it gets. Every task stores patterns.

---

## 📖 Next Steps

### Read More
- **[README.md](README.md)** - Full overview
- **[STATUS.md](STATUS.md)** - Complete system status
- **[AUTONOMOUS_AGENT.md](AUTONOMOUS_AGENT.md)** - Deep dive on autonomous mode
- **[skills/](skills/)** - All skill documentation

### Try Real Tasks
- Debug an actual production issue
- Make a technology decision
- Generate documentation for your project
- Build your team's knowledge base

### Customize
- Create custom skills for your workflows
- Add domain-specific knowledge
- Build case libraries for your team

---

## 🆘 Need Help?

- **GitHub Issues:** [Report bugs or request features](https://github.com/photoxpedia/bolor-brain-mcp/issues)
- **Documentation:** Check `docs/` folder
- **Examples:** See `skills/` for patterns

---

**You're ready! Start with `/reason` or `/autonomous` and see the magic happen.** 🚀

**Remember:** The agent gets smarter with every task. The more you use it, the faster it becomes.
