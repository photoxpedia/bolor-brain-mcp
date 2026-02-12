# Bolor Brain - Claude Code Usage Examples

Real-world examples of using Bolor Brain reasoning tools with Claude Code.

## Example 1: Debugging a Production Issue

### Scenario
Your API is returning 500 errors during peak hours.

### Claude Code Conversation

```
You: My order API is returning 500 errors during peak hours. Use Bolor Brain to diagnose the issue.

Claude: Let me analyze this systematically using Bolor Brain's hybrid reasoning.

[calls bolor-brain.reason_hybrid tool]
{
  "query": "API returning 500 errors during peak hours",
  "context": {
    "domain": "web_api",
    "symptoms": ["500_errors", "peak_hours"]
  }
}

[receives response]
{
  "problem_type": "diagnosis",
  "approaches_used": ["hypothesis", "case_based"],
  "confidence": 0.87,
  "result": {
    "hypotheses": [
      {
        "statement": "Database connection pool exhausted",
        "confidence": 0.92,
        "evidence": ["peak_hours", "stateful_connections"]
      },
      {
        "statement": "Memory leak accumulation",
        "confidence": 0.65
      }
    ],
    "similar_cases": [
      {
        "case_id": "INC-2024-001",
        "similarity": 0.95,
        "problem": {"symptom": "500_errors", "timing": "high_load"},
        "solution": {"action": "increase_pool_size", "from": 100, "to": 200},
        "success": true
      }
    ]
  }
}

Claude: Based on hybrid reasoning analysis:

**Diagnosis: Database Connection Pool Exhausted** (87% confidence)

**Evidence:**
- Hypothesis testing ranked "connection pool exhausted" as most likely (92%)
- Found highly similar past incident INC-2024-001 (95% match)
- Previous incident had identical symptoms: 500s during peak hours
- Past solution was successful: increased pool from 100 → 200 connections

**Recommended Fix:**
Increase your database connection pool size in your config:
```python
DATABASE_CONFIG = {
    'max_connections': 200,  # was 100
    'min_connections': 10,
    'connection_timeout': 30
}
```

**Why this works:**
Peak traffic causes connection exhaustion, leading to timeouts and 500 errors.
Increasing the pool prevents connection starvation during high load.

Would you like me to store this case for future learning?
```

## Example 2: Technical Decision Making

### Scenario
Choosing between ML frameworks for a new project.

### Claude Code Conversation

```
You: We're starting a new ML project. Should we use PyTorch or JAX?

Context:
- Team size: 5 engineers
- Hardware: Google Cloud TPUs
- Goal: Research project, need fast experimentation
- Timeline: 6 months

Claude: Let me use Bolor Brain to make a systematic recommendation.

[calls bolor-brain.reason_hybrid tool]
{
  "query": "Choose between PyTorch and JAX for ML project",
  "context": {
    "team_size": 5,
    "hardware": "tpu",
    "goal": "research",
    "timeline_months": 6
  }
}

[receives response]
{
  "problem_type": "decision",
  "approaches_used": ["symbolic", "knowledge_graph", "case_based"],
  "confidence": 0.89,
  "result": {
    "recommendation": "JAX",
    "reasoning": {
      "symbolic_rules_fired": [
        "tpu_suggests_jax (priority: high, confidence: 0.95)"
      ],
      "graph_paths": [
        {
          "path": ["JAX", "optimized_for", "TPU"],
          "weight": 0.95
        },
        {
          "path": ["JAX", "suited_for", "research"],
          "weight": 0.85
        }
      ],
      "similar_cases": [
        {
          "case_id": "deepmind_alphafold",
          "similarity": 0.82,
          "team_size": "large",
          "hardware": "tpu",
          "framework": "jax",
          "outcome": "breakthrough"
        }
      ]
    },
    "tradeoffs": {
      "jax_pros": ["tpu_optimization", "functional_paradigm", "performance"],
      "jax_cons": ["smaller_ecosystem", "learning_curve"],
      "pytorch_pros": ["large_ecosystem", "debugging_ease"],
      "pytorch_cons": ["tpu_support_limited"]
    }
  }
}

Claude: **Recommendation: JAX** (89% confidence)

**Why JAX:**

1. **Hardware Match (Critical)**
   - Symbolic rule fired: "TPU suggests JAX" (confidence: 95%)
   - Knowledge graph: JAX → TPU optimization weight: 0.95
   - PyTorch TPU support is limited

2. **Research Context**
   - Graph path: JAX → suited_for → research (weight: 0.85)
   - Functional paradigm good for experimentation
   - Fast iteration cycles

3. **Proven Success**
   - Case: DeepMind's AlphaFold project (82% similar)
   - Same hardware (TPUs), same goal (research)
   - Breakthrough results achieved with JAX

**Trade-offs to Consider:**

Advantages:
✓ Excellent TPU optimization (your hardware)
✓ Functional programming = reproducible experiments
✓ Performance optimized for large-scale training

Challenges:
⚠ Smaller ecosystem than PyTorch
⚠ Learning curve for functional paradigm
⚠ Fewer third-party libraries

**Next Steps:**
1. Run a 2-week JAX prototype
2. Evaluate team comfort with functional paradigm
3. Assess TPU performance gains

Would you like me to store this decision for future reference?
```

## Example 3: Learning from Experience

### Scenario
You successfully fixed a bug and want to help the brain learn from it.

### Claude Code Conversation

```
You: We just fixed a race condition bug. Store this case so the brain can help with similar issues.

Problem:
- Concurrent requests corrupting shared state
- Happened in checkout flow
- Only under high concurrency

Solution:
- Added mutex locks around state modifications
- Switched to thread-safe data structures

Outcome:
- Bug fixed completely
- No performance impact
- 0 incidents in 2 months

Claude: Let me store this case for future learning.

[calls bolor-brain.store_case tool]
{
  "problem": {
    "symptom": "data_corruption",
    "context": "concurrent_requests",
    "component": "checkout_flow",
    "trigger": "high_concurrency"
  },
  "solution": {
    "approach": "mutex_locks",
    "data_structures": "thread_safe",
    "changes": ["add_locks", "replace_structures"]
  },
  "outcome": {
    "resolution": "complete",
    "performance_impact": "none",
    "stability_months": 2,
    "incidents_after": 0
  },
  "success": true,
  "tags": ["concurrency", "race_condition", "state_management"]
}

[receives response]
{
  "success": true,
  "case_id": "CASE-2025-147",
  "message": "Case stored successfully for future learning"
}

Claude: ✓ Case stored successfully!

**Case ID:** CASE-2025-147

This experience is now part of the brain's knowledge base. When similar
concurrency issues arise, the brain will:

1. **Retrieve this case** during similarity matching
2. **Suggest mutex locks** as a proven solution
3. **Reference your success** (0 incidents over 2 months)
4. **Adapt the solution** to the new context

Tagged with: `concurrency`, `race_condition`, `state_management`

The brain now knows that for concurrent state corruption issues,
mutex locks + thread-safe structures are an effective solution.
```

## Example 4: Knowledge Graph Exploration

### Scenario
Understanding relationships between technologies.

### Claude Code Conversation

```
You: How are Python, FastAPI, and microservices related? Build a knowledge graph.

Claude: Let me build and query a knowledge graph for these concepts.

[calls bolor-brain.add_knowledge multiple times]

Adding nodes...
{
  "knowledge_type": "node",
  "data": {"id": "python", "label": "Python", "type": "language"}
}

{
  "knowledge_type": "node",
  "data": {"id": "fastapi", "label": "FastAPI", "type": "framework"}
}

{
  "knowledge_type": "node",
  "data": {"id": "microservices", "label": "Microservices", "type": "architecture"}
}

Adding edges...
{
  "knowledge_type": "edge",
  "data": {
    "source": "python",
    "target": "fastapi",
    "relation": "language_for",
    "weight": 1.0
  }
}

{
  "knowledge_type": "edge",
  "data": {
    "source": "fastapi",
    "target": "microservices",
    "relation": "suited_for",
    "weight": 0.9
  }
}

[calls bolor-brain.reason_knowledge_graph]
{
  "query": "How are Python and microservices connected?",
  "source": "python",
  "target": "microservices"
}

Claude: Here's the knowledge graph showing these relationships:

```
Python (language)
    │
    │ language_for (1.0)
    ↓
FastAPI (framework)
    │
    │ suited_for (0.9)
    ↓
Microservices (architecture)
```

**Path Found:** Python → FastAPI → Microservices

**Relationship Analysis:**
1. Python is the implementation language for FastAPI
2. FastAPI is well-suited for building microservices (weight: 0.9)
3. Therefore: Python → microservices via FastAPI framework

**Why this path makes sense:**
- FastAPI provides async support (good for microservices)
- Built-in API documentation (essential for service interfaces)
- Type hints (helps with service contracts)
- High performance (comparable to Node.js/Go)

This knowledge is now stored in the brain's graph and can be used
for future reasoning about architecture decisions.
```

## Example 5: Hypothesis Testing

### Scenario
System behavior is strange, need to test theories.

### Claude Code Conversation

```
You: Our Redis cache hit rate dropped from 95% to 60%. What could cause this?

Claude: Let me generate and test hypotheses for this observation.

[calls bolor-brain.reason_hypothesis]
{
  "observation": "Redis cache hit rate dropped from 95% to 60%",
  "evidence": {
    "hit_rate_before": "95%",
    "hit_rate_after": "60%",
    "timing": "sudden",
    "redis_status": "healthy"
  },
  "max_hypotheses": 5
}

[receives response]
{
  "observation": "Redis cache hit rate dropped from 95% to 60%",
  "hypotheses": [
    {
      "statement": "Cache keys changed (schema/naming change)",
      "confidence": 0.89,
      "status": "supported",
      "evidence": ["sudden_drop", "healthy_redis"]
    },
    {
      "statement": "Traffic pattern changed (new feature/users)",
      "confidence": 0.76,
      "status": "plausible"
    },
    {
      "statement": "TTL configuration changed",
      "confidence": 0.72,
      "status": "plausible"
    },
    {
      "statement": "Cache size insufficient (eviction)",
      "confidence": 0.45,
      "status": "unlikely"
    },
    {
      "statement": "Redis instance failure",
      "confidence": 0.10,
      "status": "rejected",
      "reason": "redis_status: healthy"
    }
  ]
}

Claude: **Hypothesis Testing Results:**

**Most Likely: Cache keys changed** (89% confidence)

Ranked hypotheses:

1. ✓ **Cache keys changed** (89%) - LIKELY
   - Evidence: Sudden drop + Redis healthy
   - Reason: Schema or naming convention changed
   - Action: Check recent deploys for key format changes

2. ⚠ **Traffic pattern changed** (76%) - PLAUSIBLE
   - New feature or user segment
   - Action: Check analytics for traffic shifts

3. ⚠ **TTL configuration changed** (72%) - PLAUSIBLE
   - Cache expiring faster than expected
   - Action: Review cache config in recent changes

4. ❌ **Cache size insufficient** (45%) - UNLIKELY
   - Would see gradual degradation, not sudden drop

5. ❌ **Redis failure** (10%) - REJECTED
   - Evidence contradicts: Redis reports healthy

**Recommended Investigation Order:**
1. Check git log for cache key changes in last deploy
2. Review traffic analytics for new patterns
3. Audit TTL configurations

Most likely root cause is a code change that modified how cache
keys are generated, causing old cached data to be missed.
```

## Best Practices

### 1. Provide Context
```
❌ Bad:  "Is this good?"
✓ Good: "Is PyTorch good for our 5-person team with NVIDIA GPUs doing research?"
```

### 2. Use Hybrid Reasoning by Default
```
✓ Start with: reason_hybrid - let the brain choose approaches
→ Use specific tools only if you need a particular reasoning type
```

### 3. Store Successful Solutions
```
✓ After fixing bugs: store_case with problem/solution/outcome
→ Helps the brain learn and assist with similar issues
```

### 4. Check Confidence Scores
```
✓ High confidence (>80%): Strong recommendation
⚠ Medium (60-80%): Consider additional factors
❌ Low (<60%): Need more information
```

### 5. Build Knowledge Over Time
```
✓ Add domain facts, rules, cases as you work
→ The brain gets smarter about your specific domain
```

## Troubleshooting

**Tools not appearing:**
- Restart Claude Code completely
- Check `~/.claude/mcp-config.json` path
- Verify installation: `python -c "from mcp_server import main"`

**Poor results:**
- Add more context to your queries
- Teach the brain domain knowledge with add_knowledge
- Store past cases for learning

**Want to see reasoning process:**
- Check `reasoning_trace` field in responses
- Shows step-by-step logic

## Next Steps

1. Try the examples above in your Claude Code
2. Store your first successful case
3. Build domain-specific knowledge for your projects
4. See [MCP_SETUP.md](MCP_SETUP.md) for complete documentation
