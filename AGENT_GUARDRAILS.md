

# Agent Development Guardrails: NSAF + Bolor Brain

Production-ready guardrails for building safe, reliable AI agents with NSAF and Bolor Brain MCP servers.

## Critical Safety Layers

### Layer 1: Input Validation (Pre-Execution)

**Purpose**: Block malicious or malformed inputs BEFORE they reach reasoning/evolution systems.

**For Bolor Brain:**
```python
# Deterministic guardrails
BLOCKED_PATTERNS = [
    r'DROP TABLE',           # SQL injection
    r'rm -rf /',            # Destructive commands
    r'exec\(',              # Code execution
    r'__import__',          # Dynamic imports
    r'<script>',            # XSS attempts
]

def validate_reasoning_input(query: str, context: dict) -> bool:
    """Validate before passing to Bolor Brain."""
    # Check for blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            raise SecurityError(f"Blocked pattern detected: {pattern}")

    # Validate context structure
    if not isinstance(context, dict):
        raise ValueError("Context must be dict")

    # Check token limits (prevent context overflow)
    if len(query) > 10000:  # ~2.5k tokens
        raise ValueError("Query exceeds token limit")

    return True
```

**For NSAF:**
```python
# Evolution parameter bounds
EVOLUTION_LIMITS = {
    "population_size": (5, 100),      # Min 5, max 100
    "generations": (1, 100),           # Min 1, max 100
    "mutation_rate": (0.0, 0.5),       # Max 50% mutation
    "crossover_rate": (0.0, 1.0),      # 0-100%
}

def validate_evolution_params(params: dict) -> bool:
    """Validate NSAF evolution parameters."""
    for param, (min_val, max_val) in EVOLUTION_LIMITS.items():
        if param in params:
            value = params[param]
            if not (min_val <= value <= max_val):
                raise ValueError(
                    f"{param} must be between {min_val} and {max_val}, got {value}"
                )

    # Prevent resource exhaustion
    total_evaluations = params.get("population_size", 20) * params.get("generations", 10)
    if total_evaluations > 5000:
        raise ResourceError(
            f"Evolution would require {total_evaluations} evaluations (max: 5000)"
        )

    return True
```

### Layer 2: Permission Boundaries (Tool Access Control)

**Four-Tier Permission Model:**

**Tier 0: Always Safe** (No approval needed)
- Read-only operations
- Statistical queries
- Status checks
- Example: `get_nsaf_status`, `bolor-brain.get_stats`

**Tier 1: Low Risk** (Logged, no approval)
- Reasoning operations
- Knowledge graph queries
- Case retrieval
- Example: `reason_hybrid`, `analyze_nsaf_memory`

**Tier 2: Medium Risk** (Approval for production)
- Agent evolution (resource-intensive)
- Case storage (modifies knowledge base)
- Knowledge graph writes
- Example: `run_nsaf_evolution`, `store_case`, `add_knowledge`

**Tier 3: High Risk** (Always require approval)
- Deployment actions
- External API calls
- Data deletion
- System configuration changes

**Implementation:**
```python
class PermissionGate:
    def __init__(self, tier: int, production: bool):
        self.tier = tier
        self.production = production

    def check(self, tool_name: str, params: dict) -> bool:
        """Check if tool execution is permitted."""
        tool_tier = TOOL_TIERS.get(tool_name, 3)  # Default: high risk

        # Tier 0: Always allow
        if tool_tier == 0:
            return True

        # Tier 1: Log but allow
        if tool_tier == 1:
            log_tool_usage(tool_name, params)
            return True

        # Tier 2: Require approval in production
        if tool_tier == 2 and self.production:
            return request_approval(tool_name, params)

        # Tier 3: Always require approval
        if tool_tier == 3:
            return request_approval(tool_name, params, required=True)

        return True

TOOL_TIERS = {
    # Tier 0: Always safe
    "get_nsaf_status": 0,
    "get_stats": 0,

    # Tier 1: Low risk
    "reason_hybrid": 1,
    "reason_symbolic": 1,
    "reason_case_based": 1,
    "analyze_nsaf_memory": 1,
    "compare_agents": 1,

    # Tier 2: Medium risk
    "run_nsaf_evolution": 2,
    "store_case": 2,
    "add_knowledge": 2,
    "cluster_nsaf_tasks": 2,

    # Tier 3: High risk
    "deploy_agent": 3,
    "delete_knowledge": 3,
}
```

### Layer 3: Output Validation (Post-Execution)

**Purpose**: Verify outputs are safe and sensible before acting on them.

**For Bolor Brain:**
```python
def validate_reasoning_output(result: HybridReasoningResult) -> bool:
    """Validate Bolor Brain outputs."""
    # Confidence bounds check
    if not (0.0 <= result.confidence <= 1.0):
        raise ValueError(f"Invalid confidence: {result.confidence}")

    # Reasoning trace exists
    if not result.reasoning_trace:
        log_warning("No reasoning trace provided")

    # Check for hallucination markers
    HALLUCINATION_MARKERS = [
        "I don't have information",
        "I cannot verify",
        "This is speculative",
    ]

    for marker in HALLUCINATION_MARKERS:
        if any(marker.lower() in trace.lower() for trace in result.reasoning_trace):
            result.confidence *= 0.7  # Reduce confidence
            log_warning(f"Potential hallucination detected: {marker}")

    # Low confidence warning
    if result.confidence < 0.5:
        log_warning(f"Low confidence result: {result.confidence}")
        return ask_user_to_verify()

    return True
```

**For NSAF:**
```python
def validate_evolution_output(generation: int, best_fitness: float, agent: Agent) -> bool:
    """Validate NSAF evolution outputs."""
    # Fitness improvement check
    if generation > 5 and best_fitness < 0.1:
        raise EvolutionError("No meaningful improvement after 5 generations")

    # Architecture sanity check
    if agent.num_layers > 20:
        log_warning(f"Very deep architecture: {agent.num_layers} layers")

    if agent.num_parameters > 10_000_000:
        raise ResourceError(f"Agent too large: {agent.num_parameters} parameters")

    # Generalization check (if test set provided)
    if hasattr(agent, 'test_accuracy'):
        if agent.test_accuracy < agent.train_accuracy * 0.7:
            log_warning("Possible overfitting: test accuracy << train accuracy")

    return True
```

### Layer 4: Human-in-the-Loop (Critical Decisions)

**Always require human approval for:**

1. **High-Stakes Decisions**
   - Financial transactions > $X threshold
   - Data deletion or modification
   - External communications (emails, messages)
   - Production deployments

2. **Low-Confidence Results**
   - Bolor Brain confidence < 0.6
   - NSAF fitness improvement < 10% over baseline
   - Conflicting recommendations from tools

3. **Novel Situations**
   - No similar cases in Bolor Brain knowledge base
   - NSAF evolving for entirely new problem domain
   - Integration patterns not previously validated

**Implementation:**
```python
class HumanInTheLoop:
    def __init__(self, threshold: float = 0.6):
        self.confidence_threshold = threshold

    def should_ask_human(self,
                         tool: str,
                         result: Any,
                         context: dict) -> bool:
        """Determine if human approval needed."""

        # High-stakes operations always require approval
        if context.get("stakes") == "high":
            return True

        # Low confidence requires approval
        if hasattr(result, 'confidence'):
            if result.confidence < self.confidence_threshold:
                return True

        # Novel situations require approval
        if tool == "reason_case_based":
            if not result.similar_cases or result.similar_cases[0].similarity < 0.7:
                return True  # No good match found

        # Evolution with poor improvement
        if tool == "run_nsaf_evolution":
            if result.improvement < 0.1:  # Less than 10% improvement
                return True

        return False

    def request_approval(self,
                         action: str,
                         rationale: str,
                         alternatives: list) -> bool:
        """Request human approval with context."""
        print(f"\n🔔 Human Approval Required")
        print(f"Action: {action}")
        print(f"Rationale: {rationale}")
        print(f"\nAlternatives:")
        for i, alt in enumerate(alternatives, 1):
            print(f"  {i}. {alt}")

        response = input("\nApprove? (yes/no/alternative number): ")
        return response.lower() in ['yes', 'y']
```

## Error Handling Patterns

### Progressive Degradation

**Principle**: Fail gracefully with increasingly simple fallbacks.

```python
class GracefulFailure:
    def reason_with_fallback(self, query: str, context: dict):
        """Try reasoning with progressive fallback."""
        try:
            # Level 1: Full hybrid reasoning
            return bolor_brain.reason_hybrid(query, context)
        except ResourceError:
            try:
                # Level 2: Simpler symbolic reasoning
                return bolor_brain.reason_symbolic(query)
            except Exception:
                try:
                    # Level 3: Case retrieval only
                    return bolor_brain.reason_case_based({"query": query})
                except Exception:
                    # Level 4: Acknowledge limitation
                    return {
                        "error": "Unable to reason about query",
                        "suggestion": "Try rephrasing or providing more context",
                        "query": query
                    }
```

### Timeout Management

**For NSAF Evolution** (long-running):
```python
import asyncio

async def evolve_with_timeout(params: dict, timeout_seconds: int = 3600):
    """Run evolution with timeout."""
    try:
        result = await asyncio.wait_for(
            nsaf.run_nsaf_evolution(params),
            timeout=timeout_seconds
        )
        return result
    except asyncio.TimeoutError:
        log_error(f"Evolution exceeded {timeout_seconds}s timeout")
        # Return partial results if available
        return nsaf.get_best_so_far()
```

### Retry Logic with Backoff

```python
import time

def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed

            delay = base_delay * (2 ** attempt)  # Exponential backoff
            log_warning(f"Attempt {attempt + 1} failed, retrying in {delay}s")
            time.sleep(delay)
```

## Resource Management

### Context Window Tracking

```python
class ContextManager:
    def __init__(self, max_tokens: int = 100000):
        self.max_tokens = max_tokens
        self.current_usage = 0

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        return len(text) // 4

    def check_capacity(self, additional: str) -> bool:
        """Check if adding text would exceed limit."""
        additional_tokens = self.estimate_tokens(additional)
        return (self.current_usage + additional_tokens) < (self.max_tokens * 0.9)

    def add(self, text: str, source: str):
        """Add to context with tracking."""
        tokens = self.estimate_tokens(text)

        if not self.check_capacity(text):
            log_warning(f"Context approaching limit: {self.current_usage}/{self.max_tokens}")
            return False

        self.current_usage += tokens
        log_info(f"Added {tokens} tokens from {source} (total: {self.current_usage})")
        return True

    def should_compress(self) -> bool:
        """Determine if compression needed."""
        usage_percent = (self.current_usage / self.max_tokens) * 100
        return usage_percent > 70  # Compress at 70% full
```

### Evolution Resource Limits

```python
class ResourceLimiter:
    def __init__(self):
        self.max_concurrent_evolutions = 3
        self.current_evolutions = 0
        self.lock = threading.Lock()

    def can_start_evolution(self, params: dict) -> bool:
        """Check if evolution can start."""
        with self.lock:
            # Check concurrency
            if self.current_evolutions >= self.max_concurrent_evolutions:
                return False

            # Check estimated cost
            estimated_cost = (
                params.get("population_size", 20) *
                params.get("generations", 10) *
                0.01  # $0.01 per evaluation
            )

            if estimated_cost > 50:  # $50 limit
                log_warning(f"Evolution would cost ${estimated_cost:.2f}")
                return False

            self.current_evolutions += 1
            return True

    def evolution_complete(self):
        """Mark evolution as complete."""
        with self.lock:
            self.current_evolutions = max(0, self.current_evolutions - 1)
```

## Monitoring & Observability

### Tool Usage Tracking

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class ToolInvocation:
    tool: str
    timestamp: datetime
    params: dict
    result: Any
    duration_ms: float
    success: bool
    confidence: Optional[float] = None
    error: Optional[str] = None

class ToolMonitor:
    def __init__(self):
        self.invocations: List[ToolInvocation] = []

    def record(self, invocation: ToolInvocation):
        """Record tool usage."""
        self.invocations.append(invocation)

        # Alert on failures
        if not invocation.success:
            log_error(f"Tool {invocation.tool} failed: {invocation.error}")

        # Alert on low confidence
        if invocation.confidence and invocation.confidence < 0.5:
            log_warning(f"Low confidence result from {invocation.tool}: {invocation.confidence}")

    def get_stats(self, time_window_hours: int = 24) -> dict:
        """Get usage statistics."""
        cutoff = datetime.now() - timedelta(hours=time_window_hours)
        recent = [inv for inv in self.invocations if inv.timestamp > cutoff]

        return {
            "total_calls": len(recent),
            "by_tool": Counter(inv.tool for inv in recent),
            "success_rate": sum(inv.success for inv in recent) / len(recent) if recent else 0,
            "avg_confidence": np.mean([inv.confidence for inv in recent if inv.confidence]),
            "avg_duration_ms": np.mean([inv.duration_ms for inv in recent]),
        }
```

### Fitness Progression Monitoring (NSAF)

```python
class FitnessMonitor:
    def on_generation(self, generation: int, best_fitness: float, population: List[Agent]):
        """Monitor evolution progress."""
        # Check for plateau
        if generation > 5:
            recent_improvement = best_fitness - self.history[-5]
            if recent_improvement < 0.01:
                log_warning(f"Evolution plateaued at generation {generation}")
                return "consider_stopping"

        # Check for divergence
        population_variance = np.var([agent.fitness for agent in population])
        if population_variance < 0.001:
            log_warning("Population converged too early (low diversity)")

        self.history.append(best_fitness)
        return "continue"
```

## Testing & Validation

### Reasoning Test Suite

```python
class ReasoningTests:
    def test_hallucination_detection(self):
        """Ensure low confidence for unverifiable claims."""
        result = bolor_brain.reason_hybrid("What is the capital of Atlantis?")
        assert result.confidence < 0.3, "Should have low confidence for fictional data"

    def test_case_retrieval(self):
        """Verify similar cases are found."""
        # Store known case
        bolor_brain.store_case(
            problem={"type": "bug", "symptom": "crash"},
            solution={"fix": "memory_leak"},
            success=True
        )

        # Query similar
        result = bolor_brain.reason_case_based({"type": "bug", "symptom": "crash"})
        assert result.similar_cases[0].similarity > 0.9

    def test_confidence_calibration(self):
        """Check confidence scores match accuracy."""
        results = []
        for test_case in self.test_set:
            result = bolor_brain.reason_hybrid(test_case.query)
            results.append((result.confidence, result.is_correct(test_case.answer)))

        # High confidence should correlate with correctness
        high_conf = [r for r in results if r[0] > 0.8]
        accuracy = sum(r[1] for r in high_conf) / len(high_conf)
        assert accuracy > 0.85, "High confidence should be accurate"
```

### Evolution Test Suite

```python
class EvolutionTests:
    def test_fitness_improvement(self):
        """Ensure evolution improves fitness."""
        initial_fitness = 0.5
        result = nsaf.run_nsaf_evolution({
            "population_size": 10,
            "generations": 5,
            "initial_fitness": initial_fitness
        })

        assert result.best_fitness > initial_fitness, "Evolution should improve fitness"

    def test_parameter_validation(self):
        """Ensure invalid parameters are rejected."""
        with pytest.raises(ValueError):
            nsaf.run_nsaf_evolution({
                "population_size": 1000,  # Too large
                "generations": 1000,      # Too many
            })

    def test_reproducibility(self):
        """Ensure same seed produces same results."""
        params = {"population_size": 10, "generations": 3, "seed": 42}
        result1 = nsaf.run_nsaf_evolution(params)
        result2 = nsaf.run_nsaf_evolution(params)

        assert result1.best_fitness == result2.best_fitness
```

## Production Deployment Checklist

### Pre-Deployment

- [ ] All guardrails enabled and tested
- [ ] Permission tiers configured correctly
- [ ] Timeout limits set appropriately
- [ ] Resource limits enforced
- [ ] Monitoring dashboards configured
- [ ] Alert thresholds defined
- [ ] Rollback plan documented
- [ ] Incident response procedures ready

### Deployment Gates

- [ ] Test suite passes 100%
- [ ] Confidence calibration validated
- [ ] Evolution improvements verified
- [ ] Human approval received for high-stakes tools
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Documentation updated

### Post-Deployment

- [ ] Monitor tool usage metrics
- [ ] Track confidence score distributions
- [ ] Review human approval patterns
- [ ] Analyze failure modes
- [ ] Collect user feedback
- [ ] Iterate on guardrails based on learnings

## Emergency Procedures

### Rollback Protocol

```python
class EmergencyRollback:
    def execute(self, reason: str):
        """Emergency rollback procedure."""
        log_critical(f"EMERGENCY ROLLBACK: {reason}")

        # 1. Disable all high-risk tools
        for tool in TIER_3_TOOLS:
            disable_tool(tool)

        # 2. Restore previous knowledge state
        bolor_brain.restore_checkpoint(checkpoint="last_known_good")

        # 3. Halt all running evolutions
        nsaf.stop_all_evolutions()

        # 4. Alert operators
        send_alert("ROLLBACK_EXECUTED", reason)

        # 5. Switch to read-only mode
        set_mode("read_only")
```

### Incident Response

```python
class IncidentResponse:
    SEVERITY_LEVELS = {
        "CRITICAL": "Human intervention required immediately",
        "HIGH": "Automated mitigation, human notification",
        "MEDIUM": "Logged and monitored",
        "LOW": "Logged only"
    }

    def handle(self, incident: str, severity: str):
        """Handle incident based on severity."""
        if severity == "CRITICAL":
            self.emergency_rollback(incident)
            self.notify_humans(incident, urgent=True)
            self.disable_system()

        elif severity == "HIGH":
            self.apply_mitigation(incident)
            self.notify_humans(incident, urgent=False)

        elif severity in ["MEDIUM", "LOW"]:
            self.log_incident(incident, severity)

        self.create_postmortem(incident)
```

---

## Key Principles

1. **Defense in Depth**: Multiple layers catch different failure modes
2. **Fail Gracefully**: Degrade capabilities rather than crash
3. **Human Oversight**: Critical decisions require approval
4. **Monitor Everything**: Track usage, performance, failures
5. **Test Continuously**: Validate guardrails work as expected
6. **Document Thoroughly**: Clear procedures for incidents
7. **Iterate Based on Data**: Improve guardrails from real usage

**Guardrails enable innovation by making experimentation safe.**
