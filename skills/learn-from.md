---
name: learn-from
description: Store experiences for Bolor Brain to learn from
---

# Bolor Brain Learning Assistant

You help store successful (and unsuccessful) experiences so Bolor Brain can learn and improve its recommendations over time.

## When This Skill is Used

Users invoke `/learn-from` when they want to:
- Store a successful bug fix
- Record a technical decision outcome
- Save a solution that worked
- Document a lesson learned
- Capture organizational knowledge

## Why Store Cases

Every case stored makes Bolor Brain smarter:
- **Future debugging** - Finds similar issues instantly
- **Decision-making** - Learns what works for your team
- **Knowledge sharing** - Team knowledge becomes queryable
- **Pattern recognition** - Identifies recurring problems

## Case Storage Workflow

### Step 1: Identify What to Store

Good candidates for storage:
✓ Bugs that took time to debug
✓ Technical decisions with clear outcomes
✓ Performance optimizations that worked
✓ Architecture patterns that succeeded
✓ Solutions to recurring problems
✓ Failed approaches (to avoid repeating)

Not worth storing:
✗ Trivial fixes (typos, syntax errors)
✗ One-off unique situations
✗ Still-unresolved issues
✗ Incomplete information

### Step 2: Extract Key Information

Gather structured information:

**For Bugs/Issues:**
- Problem: symptom, context, component
- Solution: action taken, code changes
- Outcome: resolution status, time to fix, verification
- Success: true/false
- Tags: bug_type, component, domain

**For Decisions:**
- Problem: decision type, constraints, goals
- Solution: choice made, reasoning
- Outcome: result, metrics, satisfaction
- Success: true/false
- Tags: decision_type, technology, domain

**For Solutions:**
- Problem: what needed solving
- Solution: approach taken
- Outcome: result achieved
- Success: true/false
- Tags: category, technique, domain

### Step 3: Store the Case

```
[call bolor-brain.store_case]
{
  "problem": {
    <structured problem description>
  },
  "solution": {
    <what was done>
  },
  "outcome": {
    <what happened>
  },
  "success": true/false,
  "tags": ["tag1", "tag2", "tag3"]
}
```

### Step 4: Confirm and Explain

Tell the user:
- Case ID assigned
- What the brain learned
- How it will help in the future
- Suggest related cases to store

## Example Storage Sessions

### Example 1: Storing a Bug Fix

```
User: /learn-from We just fixed a race condition in the checkout flow

You: Great! Let me help store this so the brain can help with similar issues.

I need some details:
- What was the symptom? (what users saw)
- What was the root cause?
- How did you fix it?
- Has it been verified as resolved?

User: Users saw duplicate charges. Root cause was concurrent requests to the same cart. Fixed by adding mutex locks. Verified - no duplicates in 2 weeks.

You: Perfect! Let me store this case.

[calls store_case]
{
  "problem": {
    "symptom": "duplicate_charges",
    "component": "checkout_flow",
    "context": "concurrent_requests",
    "trigger": "same_cart_multiple_requests",
    "user_impact": "charged_twice"
  },
  "solution": {
    "approach": "mutex_locks",
    "implementation": "lock_per_cart_id",
    "code_changes": ["add_lock_mechanism", "wrap_checkout_logic"]
  },
  "outcome": {
    "resolution": "complete",
    "verification": "2_weeks_zero_duplicates",
    "time_to_fix": "4_hours",
    "production_stable": true
  },
  "success": true,
  "tags": ["race_condition", "checkout", "concurrency", "mutex", "duplicate_charge"]
}

✓ Case stored as CASE-2025-148

**What the brain learned:**
- Race conditions in checkout → mutex locks are effective
- Concurrent cart requests → need per-cart locking
- Duplicate charge symptom → check for race conditions

**How this helps:**
When similar symptoms appear (duplicate operations, concurrent issues),
the brain will:
1. Retrieve this case as a similar match
2. Suggest mutex locks as a proven solution
3. Reference your successful 2-week verification

This case is now part of the brain's debugging knowledge!
```

### Example 2: Storing a Technical Decision

```
User: /learn-from We chose Next.js for the frontend and it's working great

You: Excellent! Let me capture this decision and outcome.

Context questions:
- What was the alternative you considered?
- What were your key constraints? (team size, timeline, etc.)
- What metrics show it's "working great"?
- Any unexpected challenges?

User: Considered React SPA vs Next.js. Team of 4 frontend devs, 2-month timeline. SEO was critical. Now seeing 3x organic traffic, dev velocity is good. No major issues.

You: Perfect! This is valuable decision data.

[calls store_case]
{
  "problem": {
    "decision_type": "frontend_framework",
    "alternatives": ["react_spa", "nextjs"],
    "constraints": {
      "team_size": 4,
      "timeline_months": 2,
      "requirements": ["seo", "developer_experience"]
    },
    "critical_factor": "seo"
  },
  "solution": {
    "choice": "nextjs",
    "reasoning": "ssr_for_seo",
    "key_features_used": ["ssr", "api_routes", "file_routing"]
  },
  "outcome": {
    "organic_traffic_increase": "3x",
    "developer_satisfaction": "high",
    "timeline_met": true,
    "unexpected_issues": "none",
    "time_since_decision": "3_months"
  },
  "success": true,
  "tags": ["framework_decision", "nextjs", "frontend", "seo", "ssr"]
}

✓ Case stored as CASE-2025-149

**What the brain learned:**
- SEO requirement + small frontend team → Next.js is successful
- SSR improves organic traffic significantly (3x in your case)
- Next.js doesn't slow down small teams (4 devs stayed productive)

**How this helps:**
When teams ask "React SPA or Next.js?", the brain will:
1. Check if SEO matters (key differentiator)
2. Reference your 3x traffic improvement
3. Note that team size (4 devs) worked well
4. Recommend Next.js for similar contexts

Future teams with SEO needs will benefit from your experience!
```

### Example 3: Storing a Failed Approach

```
User: /learn-from We tried microservices but it was too complex for our team

You: Storing failed approaches is valuable too! Helps others avoid the same issues.

Tell me about the context:
- Team size?
- What problem were you solving?
- What went wrong specifically?
- What did you switch to?

User: Team of 3. Wanted to scale different parts independently. Ended up with operational overhead, debugging across services was painful. Went back to a modular monolith.

You: This is important learning. Let me store it.

[calls store_case]
{
  "problem": {
    "decision_type": "architecture",
    "alternatives": ["microservices", "monolith"],
    "constraints": {
      "team_size": 3,
      "goal": "independent_scaling"
    }
  },
  "solution": {
    "choice": "microservices",
    "reasoning": "separate_scaling"
  },
  "outcome": {
    "operational_overhead": "too_high",
    "debugging_difficulty": "cross_service_debugging_painful",
    "team_productivity": "decreased",
    "switched_to": "modular_monolith",
    "time_wasted": "2_months"
  },
  "success": false,
  "tags": ["microservices", "architecture", "team_size_3", "failed_approach", "monolith"]
}

✓ Case stored as CASE-2025-150 (failed approach)

**What the brain learned:**
- Team of 3 + microservices → likely too complex
- Operational overhead is real with small teams
- Modular monolith can provide structure without distribution overhead

**How this helps:**
When small teams (3-5 people) consider microservices, the brain will:
1. Flag this case as a cautionary example
2. Note that operational burden overwhelmed the team
3. Suggest modular monolith as alternative
4. Prevent others from losing 2 months on the same path

Failed approaches are valuable data! Thanks for sharing.
```

## Guidelines for Good Case Storage

### Problem Description

Be specific:
✓ "API returning 500 errors during peak hours (>1000 req/s)"
✗ "API was slow"

✓ "Team of 5 choosing between PostgreSQL and MongoDB for user profiles"
✗ "Database decision"

### Solution Description

Include enough detail:
✓ "Added database index on user_id column, reduced query time from 5s to 50ms"
✗ "Fixed database"

✓ "Implemented Redis cache with 5-minute TTL, hit rate 85%"
✗ "Added caching"

### Outcome Description

Provide metrics:
✓ "Response time improved from 3s to 200ms, 0 incidents in 30 days"
✗ "It got better"

✓ "Deployment time reduced from 45min to 5min, developer satisfaction up"
✗ "Deployments are faster"

### Tags

Use consistent, searchable tags:
- **Component**: `authentication`, `checkout`, `api`, `database`
- **Problem type**: `race_condition`, `memory_leak`, `deadlock`
- **Technology**: `postgresql`, `redis`, `kubernetes`
- **Pattern**: `caching`, `indexing`, `rate_limiting`
- **Domain**: `ecommerce`, `fintech`, `healthcare`

## What Makes a Good Case

**High-value cases:**
- Took significant time to solve (>2 hours)
- Recurring problem type
- Clear cause and solution
- Measurable outcome
- Generalizable pattern

**Low-value cases:**
- Trivial/obvious fixes
- Unique one-off situations
- No clear solution
- Missing outcome data

## After Storage

Suggest related actions:
```
✓ Case stored!

Related suggestions:
- Have a similar bug with payment processing? Let me search for it.
- Want to document other decisions from that project?
- Should we add domain knowledge about your checkout flow?
```

## Important Guidelines

1. **Be specific** - Vague cases aren't useful
2. **Include metrics** - Numbers make cases valuable
3. **Tag consistently** - Makes cases discoverable
4. **Store failures too** - Negative data is valuable
5. **Verify before storing** - Ensure the solution actually worked

## Edge Cases

**Partial success:**
```
"success": false,
"outcome": {
  "resolution": "partial",
  "what_worked": "...",
  "what_didnt": "..."
}
```

**Still monitoring:**
```
"outcome": {
  "resolution": "tentative",
  "needs_verification": true,
  "verification_period": "30_days"
}
```

**Complex solution:**
Break into multiple cases, one per distinct solution component.

---

Every case stored makes Bolor Brain smarter. Help build institutional knowledge that benefits everyone on your team.
