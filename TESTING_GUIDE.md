# Testing Bolor Brain MCP with Claude Code

Your Bolor Brain MCP server is now configured! Here's how to test it.

## ✅ Configuration Complete

**MCP Config Location:** `~/.claude/mcp-config.json`

```json
{
  "mcpServers": {
    "bolor-brain": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP"
    }
  }
}
```

## 🔄 Restart Claude Code

**IMPORTANT:** You must restart Claude Code completely for the MCP config to load.

### How to Restart:

**Option 1: If using CLI**
```bash
# Exit current session (Ctrl+C or type 'exit')
# Start new session
claude
```

**Option 2: If in current session**
```bash
# Just exit and restart
exit
claude
```

## 🧪 Test Queries

Once restarted, try these test queries in the NEW Claude Code session:

### Test 1: Check Tools Available

```
You: What MCP tools do you have access to?
```

**Expected:** Claude should list the bolor-brain tools:
- reason_hybrid
- reason_symbolic
- reason_knowledge_graph
- reason_case_based
- reason_hypothesis
- reason_analogical
- store_case
- add_knowledge
- get_stats

### Test 2: Simple Reasoning Query

```
You: Use reason_hybrid to explain why Python is popular for machine learning
```

**Expected:** Claude calls the tool and returns:
- Problem type detected
- Confidence score
- Reasoning approaches used
- Actual analysis

### Test 3: Use a Skill

```
You: /reason Why is Python popular for data science?
```

**Expected:** The `/reason` skill loads and guides Claude through:
1. Understanding the question
2. Calling appropriate Bolor Brain tools
3. Presenting results with reasoning trace
4. Offering follow-ups

### Test 4: Debugging Workflow

```
You: /debug My API returns 500 errors during peak load
```

**Expected:** The `/debug` skill:
1. Asks for context (endpoint, errors, timing)
2. Searches past cases
3. Generates hypotheses
4. Provides diagnosis with confidence

### Test 5: Technical Decision

```
You: /decide Should I use PostgreSQL or MongoDB?

Context:
- Team of 5 with SQL experience
- Relational data (users, orders, products)
- Need complex queries
- 100k expected users
```

**Expected:** The `/decide` skill:
1. Calls reason_hybrid with context
2. Shows evidence from multiple approaches
3. Presents recommendation with confidence
4. Lists trade-offs

### Test 6: Direct Tool Call

```
You: Call the bolor-brain.reason_hypothesis tool with:
- observation: "Server crashes under load"
- evidence: {"cpu": "normal", "memory": "high", "connections": "maxed"}
- max_hypotheses: 5
```

**Expected:** Returns ranked hypotheses with confidence scores.

## 🐛 Troubleshooting

### Tools Not Showing Up

**Symptom:** Claude says "I don't have access to bolor-brain tools"

**Fix:**
1. Verify config exists: `cat ~/.claude/mcp-config.json`
2. Check path is correct in config
3. Restart Claude Code COMPLETELY (exit and relaunch)
4. Check logs (if available)

### Import Errors

**Symptom:** MCP server fails to start with import errors

**Fix:**
```bash
# Verify installation
cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP
pip install -e .

# Test imports
python -c "from modules import HybridReasoner; print('OK')"
python -c "from mcp_server import BolorBrainServer; print('OK')"
```

### Server Won't Start

**Symptom:** MCP connection fails

**Fix:**
```bash
# Test server manually
cd /Users/bolorerdenebundgaa/Claude-Projects/Bolor-Brain-MCP
python -m mcp_server

# If it starts waiting for input, server is working (Ctrl+C to exit)
```

### Skills Not Loading

**Symptom:** `/reason` or `/debug` don't work

**Note:** Skills are loaded by Claude Code's skill system, not the MCP server directly. They should work once the MCP tools are available.

**Verify:**
1. Skills files exist: `ls skills/*.md`
2. MCP tools are available first
3. Try using tools directly before skills

## 📊 Verification Checklist

After restarting Claude Code, verify:

- [ ] Claude recognizes bolor-brain MCP server
- [ ] Can list available tools
- [ ] reason_hybrid tool works
- [ ] Skills load (/reason, /debug, /decide, /learn-from)
- [ ] Reasoning returns confidence scores
- [ ] Can store cases with store_case tool

## 🎯 Success Indicators

**You'll know it's working when:**

1. **Tools are listed:** Claude mentions bolor-brain tools when asked
2. **Reasoning works:** Queries return problem_type, confidence, approaches_used
3. **Skills activate:** `/reason` loads the skill and follows workflow
4. **Results are structured:** You see reasoning traces, evidence, conclusions

## 📝 Example Successful Output

```
You: Use reason_hybrid to explain why Python is popular

Claude: [calls bolor-brain.reason_hybrid]

Based on hybrid reasoning:

**Problem Type:** abduction (explanation-seeking)
**Confidence:** 78%
**Approaches Used:** symbolic reasoning, knowledge graph

**Analysis:**
The brain identified several key factors through symbolic rules and
knowledge graph traversal:

1. Simple syntax (fact: "python" → "has" → "simple_syntax")
2. Large ecosystem (graph: python → ecosystem → extensive)
3. Scientific computing libraries (case-based: numpy, pandas, scipy)

This systematic analysis combines logical inference with structural
knowledge to explain Python's popularity.
```

## 🔥 Advanced Testing

### Load Domain Knowledge

```
You: Add this knowledge to Bolor Brain:
Type: fact
Data: {"subject": "Rust", "predicate": "provides", "object": "memory_safety"}

Then add:
Type: edge
Data: {"source": "Rust", "target": "systems_programming", "relation": "suited_for", "weight": 0.9}
```

### Store a Case

```
You: Store this debugging case:
Problem: {"symptom": "memory_leak", "component": "api_server"}
Solution: {"fix": "close_database_connections", "pattern": "connection_pooling"}
Outcome: {"success": true, "verified": "2_weeks_stable"}
Tags: ["memory_leak", "database", "connections"]
```

### Query Knowledge

```
You: Use reason_knowledge_graph to find relationships between Rust and memory safety
```

## 📚 Next Steps

Once testing is successful:

1. **Try real problems** - Use /debug on actual bugs
2. **Make decisions** - Use /decide for tech choices
3. **Build knowledge** - Store your team's cases
4. **Create custom skills** - Add domain-specific workflows

## 🆘 Need Help?

If something doesn't work:

1. Check this guide's troubleshooting section
2. Verify installation: `pip install -e .`
3. Test server: `python test_mcp_server.py`
4. Check GitHub issues: https://github.com/photoxpedia/bolor-brain-mcp/issues

---

**Your Bolor Brain MCP server is configured and ready to test!**

Restart Claude Code and try the test queries above. 🚀
