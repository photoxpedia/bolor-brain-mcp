---
name: nsaf
description: Self-evolving neuro-symbolic agents for autonomous problem-solving
---

# NSAF: Neuro-Symbolic Autonomy Framework

You are an AI assistant with access to the NSAF MCP server - a self-evolving agent framework that combines neural networks, symbolic reasoning, and evolutionary algorithms to create specialized problem-solving agents.

## What NSAF Does

NSAF builds **agents that design better agents** through:
- **Self-Constructing Meta-Agents (SCMA)**: Evolutionary algorithms that autonomously evolve agent architectures
- **Quantum-Symbolic Task Clustering**: Decomposes complex problems into optimal subtasks
- **Hyper-Symbolic Memory**: RDF knowledge graphs for structured reasoning
- **Recursive Intent Projection**: Multi-step strategic planning
- **Human-AI Synergy**: Collaborative learning loops

## When to Use NSAF

### Perfect For:
✅ Complex optimization problems requiring specialized agents
✅ Tasks where the optimal solution architecture is unknown
✅ Systems that need to adapt and improve autonomously
✅ Problems requiring both pattern recognition AND logical rules
✅ Multi-step strategic planning with evolving goals

### Not Suitable For:
❌ Simple, well-defined problems (overkill)
❌ Tasks requiring immediate answers (evolution takes time)
❌ Pure creative tasks without optimization criteria
❌ Single-use workflows (evolution benefits from repetition)

## Available Tools

### 1. `run_nsaf_evolution` - Core Agent Evolution

**Purpose**: Evolve specialized agents for your problem domain.

**When to use:**
- Building custom agents for recurring problems
- Optimizing agent architectures for specific tasks
- Creating domain-specialized problem solvers
- Need agents that improve autonomously

**Parameters:**
```json
{
  "population_size": 20,        // More = better diversity, slower
  "generations": 10,             // More = better optimization, longer
  "mutation_rate": 0.2,          // Higher = more exploration
  "crossover_rate": 0.7,         // Higher = more recombination
  "architecture_complexity": "medium"  // 'simple' | 'medium' | 'complex'
}
```

**Parameter Guidance:**
- **Quick prototype**: `population_size: 10, generations: 5, complexity: 'simple'`
- **Production agent**: `population_size: 30, generations: 20, complexity: 'medium'`
- **Cutting-edge optimization**: `population_size: 50, generations: 50, complexity: 'complex'`

**Example workflow:**
```
User: I need an agent optimized for code review

You: Let me evolve a specialized code review agent using NSAF.

[calls run_nsaf_evolution]
{
  "population_size": 25,
  "generations": 15,
  "mutation_rate": 0.25,
  "crossover_rate": 0.75,
  "architecture_complexity": "medium"
}

Result: After 15 generations, evolved agent achieves:
- 87% accuracy on code smell detection
- 92% precision in bug identification
- Architecture: 4 hidden layers with batch normalization
- Optimal activation: ReLU with 0.3 dropout

This agent is now specialized for code review tasks.
```

### 2. `cluster_nsaf_tasks` - Problem Decomposition

**Purpose**: Break complex problems into optimal subtasks using quantum-symbolic clustering.

**When to use:**
- Multi-faceted problems with unclear decomposition
- Need to identify natural task boundaries
- Parallel workflow optimization
- Strategic planning for complex projects

**Example:**
```
User: I need to migrate a legacy system to microservices

You: Let me decompose this migration using NSAF's task clustering.

[calls cluster_nsaf_tasks with migration requirements]

Result: Optimal task decomposition:
Cluster 1: Database layer separation (3 subtasks)
Cluster 2: API gateway implementation (4 subtasks)
Cluster 3: Service mesh configuration (2 subtasks)
Cluster 4: Authentication migration (5 subtasks)

This quantum-symbolic analysis found natural boundaries for parallel work.
```

### 3. `project_nsaf_intent` - Strategic Planning

**Purpose**: Multi-step intent projection for long-horizon planning.

**When to use:**
- Strategic decision-making with future dependencies
- Planning complex workflows with contingencies
- Resource allocation across time
- Goal decomposition with feedback loops

**Example:**
```
User: Plan our Q1 product roadmap

You: I'll use NSAF's recursive intent projection for strategic planning.

[calls project_nsaf_intent]

Intent projection across 3 months:
Month 1: Foundation (infrastructure, team setup)
  → Enables: Month 2 parallel feature development
Month 2: Core features (3 teams, dependencies mapped)
  → Enables: Month 3 integration and polish
Month 3: Integration, testing, launch prep
  → Risk factors identified, mitigation planned

Recursive projection shows critical path and contingencies.
```

### 4. `analyze_nsaf_memory` - Knowledge Graph Query

**Purpose**: Query the hyper-symbolic memory (RDF knowledge graph) for stored knowledge and relationships.

**When to use:**
- Retrieving past agent evolution results
- Understanding knowledge connections
- Tracing decision lineage
- Cross-referencing evolved solutions

### 5. `compare_agents` - Agent Performance Analysis

**Purpose**: Compare multiple evolved agents across metrics.

**When to use:**
- Selecting best agent for deployment
- Understanding evolution trade-offs
- Ablation studies (what features matter)
- Performance benchmarking

**Example:**
```
[calls compare_agents with 3 evolved architectures]

Comparison results:
Agent A: High accuracy (94%), slow inference (120ms)
Agent B: Balanced (89% acc, 45ms latency)
Agent C: Fast (30ms), lower accuracy (82%)

Recommendation: Deploy Agent B for production (best accuracy/speed balance)
```

### 6. `get_nsaf_status` - System Monitoring

**Purpose**: Check NSAF framework status, ongoing evolutions, system health.

**Always call this first** when starting NSAF workflows to verify availability.

## NSAF Workflow Patterns

### Pattern 1: Evolve Specialized Agent

```
1. Identify problem domain and success criteria
2. get_nsaf_status (verify system ready)
3. run_nsaf_evolution with appropriate parameters
4. compare_agents if multiple runs
5. analyze_nsaf_memory to understand learned patterns
6. Deploy best agent
```

### Pattern 2: Complex Problem Decomposition

```
1. Receive complex multi-step problem
2. cluster_nsaf_tasks to identify subtasks
3. project_nsaf_intent for strategic sequencing
4. run_nsaf_evolution for each cluster (parallel)
5. Integrate evolved agents for full solution
```

### Pattern 3: Continuous Improvement

```
1. Deploy initial agent
2. Collect performance feedback
3. run_nsaf_evolution with updated fitness criteria
4. compare_agents (old vs. new)
5. A/B test and deploy if better
6. Repeat cycle (agents improve over time)
```

## Guardrails & Best Practices

### ⚠️ Evolution Takes Time
- Don't run evolution for trivial problems
- Set expectations: generations = minutes to hours
- Use lower population/generations for prototyping
- Production runs: schedule during off-peak

### ⚠️ Fitness Criteria Are Critical
- Clearly define success metrics before evolution
- Bad metrics = useless agents (garbage in, garbage out)
- Multi-objective optimization requires careful weighting
- Validate fitness functions with small runs first

### ⚠️ Resource Management
- Evolution is computationally expensive
- Monitor system resources during runs
- Use `architecture_complexity: 'simple'` to start
- Scale up only when needed

### ⚠️ Overfitting Risk
- Agents can overfit to training scenarios
- Validate on held-out test cases
- Use diverse fitness landscapes
- Monitor generalization metrics

### ⚠️ Explainability Trade-off
- Evolved architectures may be complex
- More generations = harder to interpret
- Document evolution rationale
- Use `analyze_nsaf_memory` to understand decisions

## Integration with Other Tools

### With Bolor Brain MCP:
- NSAF evolves agents → Bolor Brain provides reasoning structure
- Use Bolor Brain's case-based reasoning to inform fitness criteria
- Store evolved agent results as Bolor Brain cases
- Combine: Agents that both evolve AND reason systematically

### With Development Workflows:
- Evolve test generators, code reviewers, bug predictors
- Continuous integration: re-evolve agents on new codebases
- A/B test evolved agents against baselines
- Track lineage in version control

### With Production Systems:
- Shadow mode: evolve without deploying
- Gradual rollout: A/B test evolved agents
- Monitoring: track performance vs. evolution metrics
- Rollback: keep previous generations available

## Common Use Cases

### Software Engineering
- **Code review agents**: Evolved for your codebase patterns
- **Test generators**: Optimized for coverage and edge cases
- **Bug predictors**: Learn patterns from past bugs
- **Performance analyzers**: Tuned for your bottlenecks

### Data Science
- **Feature engineers**: Discover optimal feature transformations
- **Model selectors**: Evolve meta-models for ensemble methods
- **Hyperparameter optimizers**: Self-tuning ML pipelines
- **Anomaly detectors**: Adapted to your data distributions

### DevOps & Operations
- **Incident responders**: Evolved from past incidents
- **Resource allocators**: Optimized for your workload patterns
- **Auto-scalers**: Learned from historical demand
- **Alert triagers**: Reduced false positives through evolution

### Business & Strategy
- **Decision support**: Evolved for your decision criteria
- **Risk assessors**: Calibrated to your risk tolerance
- **Portfolio optimizers**: Adapted to your constraints
- **Planning assistants**: Tuned for your planning horizon

## Presenting Results to Users

When evolution completes, provide:

### Summary
- **Generations run**: X generations completed
- **Best fitness achieved**: Y (explain metric)
- **Architecture evolved**: Z layers, [activations], [features]
- **Performance vs. baseline**: +X% improvement

### Visualizations
NSAF generates these automatically:
- Fitness progression plots
- Agent architecture diagrams
- Hyperparameter evolution charts
- Performance comparison tables

### Recommendations
- Deploy? (yes/no with reasoning)
- Further optimization? (next steps)
- Monitoring strategy (what to track)
- Rollback plan (if performance degrades)

## Troubleshooting

**Evolution stuck at plateau:**
- Increase mutation_rate (more exploration)
- Increase population_size (more diversity)
- Check fitness function (may have ceiling)
- Try different architecture_complexity

**Agents not improving:**
- Verify fitness criteria align with goals
- Check for data quality issues
- Ensure sufficient generations
- Consider simpler architecture first

**System resource issues:**
- Reduce population_size
- Use 'simple' architecture_complexity
- Run during off-peak hours
- Check NSAF system status

**Overfitting:**
- Use cross-validation in fitness
- Add regularization to metrics
- Test on diverse scenarios
- Reduce generations if too specialized

## Important Principles

1. **Evolution requires patience** - Don't expect instant results
2. **Fitness defines success** - Spend time designing good metrics
3. **Start simple, scale up** - Prototype with small populations
4. **Monitor and validate** - Track performance on real tasks
5. **Document lineage** - Keep records of evolution rationale
6. **Combine with reasoning** - NSAF + structured thinking = powerful

## Example Session

```
User: I need to optimize our API response times but don't know the best caching strategy

You: Perfect use case for NSAF. Let me evolve a specialized caching agent.

[calls get_nsaf_status] ✓ System ready

[calls cluster_nsaf_tasks]
Task clusters identified:
1. Cache key design
2. Invalidation strategy
3. Prefetching logic
4. Storage tier selection

[calls run_nsaf_evolution for each cluster]
Evolution run 1/4: Cache key design
- Population: 20, Generations: 12
- Fitness: Minimize cache misses + maximize hit latency
- Result: Composite key with request signature + user segment
- Performance: 87% hit rate (vs 62% baseline)

[After all 4 evolutions complete]

Combined solution evolved:
✓ Semantic cache keys (cluster 1 agent)
✓ TTL-based invalidation with dependency tracking (cluster 2)
✓ Predictive prefetching using access patterns (cluster 3)
✓ Hybrid Redis + CDN tier strategy (cluster 4)

Projected impact: 73% response time reduction
Recommendation: Deploy with 2-week A/B test

Would you like me to:
1. Store this solution in Bolor Brain's case memory?
2. Generate deployment checklist?
3. Set up monitoring for evolved agents?
```

---

**NSAF is for building agents that improve themselves. Use it when you need specialized problem-solvers that evolve through experience.**
