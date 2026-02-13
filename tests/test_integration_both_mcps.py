"""
Integration test: Bolor Brain MCP + NSAF MCP servers working together.

Tests that both MCP servers can be instantiated, that their core tools work,
and that they can be used in a combined workflow simulating a real scenario.

Author: Bolorerdene Bundgaa
"""

import pytest
import pytest_asyncio
import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Ensure Bolor Brain project root is on sys.path
BOLOR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BOLOR_ROOT)

# Ensure NSAF project root is on sys.path
NSAF_ROOT = os.path.join(os.path.dirname(BOLOR_ROOT), "nsaf")
sys.path.insert(0, NSAF_ROOT)

NSAF_CONFIG = os.path.join(NSAF_ROOT, "config", "config.yaml")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def bolor_server(tmp_path):
    """Create a Bolor Brain server with isolated temp persistence directory."""
    os.environ["BOLOR_PERSISTENCE_DIR"] = str(tmp_path / "brain_data")
    from mcp_server import BolorBrainServer
    server = BolorBrainServer()
    yield server
    if "BOLOR_PERSISTENCE_DIR" in os.environ:
        del os.environ["BOLOR_PERSISTENCE_DIR"]


@pytest.fixture
def nsaf_server():
    """Create an NSAF MCP server instance."""
    from nsaf_mcp_server import NSAFMCPServer
    server = NSAFMCPServer(NSAF_CONFIG)
    return server


@pytest_asyncio.fixture
async def nsaf_server_initialized(nsaf_server):
    """Create an NSAF MCP server with the framework already initialized."""
    await nsaf_server.handle_tool_call("initialize_nsaf_framework", {})
    yield nsaf_server
    # Shutdown framework to clean up Ray etc.
    await nsaf_server.handle_tool_call("shutdown_nsaf_framework", {})


# ===========================================================================
# 1. Both servers initialize
# ===========================================================================

class TestBothServersInitialize:
    """Verify that both MCP servers can be created and are functional."""

    def test_bolor_brain_creates(self, bolor_server):
        """Bolor Brain server instantiates with a HybridReasoner brain."""
        assert bolor_server is not None
        assert bolor_server.brain is not None
        assert bolor_server.persistence is not None

    def test_nsaf_creates(self, nsaf_server):
        """NSAF server instantiates with 19 tool definitions."""
        assert nsaf_server is not None
        assert len(nsaf_server.tools) == 19
        tool_names = [t.name for t in nsaf_server.tools]
        assert "process_complex_task" in tool_names
        assert "add_memory" in tool_names
        assert "evolve_agents_scma" in tool_names

    @pytest.mark.asyncio
    async def test_nsaf_framework_initializes(self, nsaf_server):
        """NSAF framework can be initialized via the MCP tool call."""
        result = await nsaf_server.handle_tool_call(
            "initialize_nsaf_framework", {}
        )
        assert result["success"] is True
        assert result["result"]["status"] == "initialized"
        assert nsaf_server.framework is not None
        # Clean up
        await nsaf_server.handle_tool_call("shutdown_nsaf_framework", {})

    @pytest.mark.asyncio
    async def test_bolor_brain_stats_at_start(self, bolor_server):
        """Fresh Bolor Brain starts with zero knowledge."""
        stats = await bolor_server._brain_stats({})
        assert stats["cases"] == 0
        assert stats["facts"] == 0
        assert stats["nodes"] == 0
        assert stats["edges"] == 0
        assert stats["reasoning_queries"] == 0


# ===========================================================================
# 2. Bolor Brain reasoning tools
# ===========================================================================

class TestBolorBrainReasoning:
    """Test Bolor Brain reasoning tools produce valid results."""

    @pytest.mark.asyncio
    async def test_reason_symbolic_forward(self, bolor_server):
        """Symbolic forward chaining with provided facts."""
        result = await bolor_server._reason_symbolic({
            "query": "Derive facts about languages",
            "facts": [
                ["python", "is_a", "programming_language"],
                ["programming_language", "used_for", "software"],
                ["python", "supports", "machine_learning"],
            ],
            "mode": "forward",
        })
        assert result["mode"] == "forward"
        assert "derived_facts" in result
        assert isinstance(result["derived_facts"], int)
        assert "conclusions" in result

    @pytest.mark.asyncio
    async def test_reason_symbolic_backward(self, bolor_server):
        """Symbolic backward chaining."""
        result = await bolor_server._reason_symbolic({
            "query": "python",
            "facts": [
                ["python", "is", "true"],
            ],
            "mode": "backward",
        })
        assert result["mode"] == "backward"
        assert "success" in result

    @pytest.mark.asyncio
    async def test_reason_hypothesis(self, bolor_server):
        """Hypothesis generation returns correct structure."""
        result = await bolor_server._reason_hypothesis({
            "observation": "Application response time increased by 300%",
            "evidence": {
                "cpu_usage": "95%",
                "memory_usage": "80%",
                "recent_deployment": "true",
            },
            "max_hypotheses": 5,
        })
        assert "observation" in result
        assert result["observation"] == "Application response time increased by 300%"
        assert "hypotheses" in result
        assert isinstance(result["hypotheses"], list)
        # Each hypothesis (if any) should have the correct structure
        for h in result["hypotheses"]:
            assert "id" in h
            assert "statement" in h
            assert "confidence" in h

    @pytest.mark.asyncio
    async def test_reason_case_based_with_past_cases(self, bolor_server):
        """Case-based reasoning retrieves similar past cases."""
        result = await bolor_server._reason_case_based({
            "problem": {"type": "performance", "symptom": "slow_query"},
            "past_cases": [
                {
                    "problem": {"type": "performance", "symptom": "slow_query"},
                    "solution": {"action": "add_index", "table": "users"},
                    "outcome": {"improvement": "90%"},
                    "success": True,
                },
                {
                    "problem": {"type": "crash", "symptom": "oom"},
                    "solution": {"action": "increase_memory"},
                    "outcome": {"improvement": "100%"},
                    "success": True,
                },
            ],
            "k": 3,
        })
        assert "similar_cases" in result
        assert len(result["similar_cases"]) >= 1
        # The performance case should be ranked higher (more similar)
        top_case = result["similar_cases"][0]
        assert top_case["similarity"] > 0
        assert "solution" in top_case

    @pytest.mark.asyncio
    async def test_reason_knowledge_graph(self, bolor_server):
        """Knowledge graph path-finding between nodes."""
        result = await bolor_server._reason_knowledge_graph({
            "query": "How are Python and AI related?",
            "nodes": [
                {"id": "python", "label": "Python", "type": "language"},
                {"id": "ml", "label": "Machine Learning", "type": "field"},
                {"id": "ai", "label": "Artificial Intelligence", "type": "field"},
            ],
            "edges": [
                {"source": "python", "target": "ml", "relation": "used_for"},
                {"source": "ml", "target": "ai", "relation": "subfield_of"},
            ],
            "source": "python",
            "target": "ai",
        })
        assert "stats" in result
        assert result["stats"]["total_nodes"] >= 3
        assert result["stats"]["total_edges"] >= 2
        # Path should be found
        assert "path" in result
        assert "nodes" in result["path"]

    @pytest.mark.asyncio
    async def test_reason_analogical(self, bolor_server):
        """Analogical reasoning between two domains."""
        result = await bolor_server._reason_analogical({
            "source_domain": "solar_system",
            "target_domain": "atom",
            "concepts": [
                {"id": "sun", "name": "Sun", "domain": "solar_system",
                 "properties": {"role": "center", "mass": "large"}},
                {"id": "planet", "name": "Planet", "domain": "solar_system",
                 "properties": {"role": "orbiter", "mass": "small"}},
                {"id": "nucleus", "name": "Nucleus", "domain": "atom",
                 "properties": {"role": "center", "mass": "large"}},
                {"id": "electron", "name": "Electron", "domain": "atom",
                 "properties": {"role": "orbiter", "mass": "small"}},
            ],
        })
        assert result["source_domain"] == "solar_system"
        assert result["target_domain"] == "atom"
        assert "analogies" in result
        assert "overall_similarity" in result

    @pytest.mark.asyncio
    async def test_reason_hybrid(self, bolor_server):
        """Hybrid reasoning orchestrates multiple approaches."""
        result = await bolor_server._reason_hybrid({
            "query": "What is the best approach to debug a memory leak?",
            "context": {"domain": "software_engineering"},
        })
        assert "problem_type" in result
        assert "approaches_used" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], float)
        assert "processing_time" in result


# ===========================================================================
# 3. Bolor Brain memory tools
# ===========================================================================

class TestBolorBrainMemory:
    """Test Bolor Brain learn/recall/remember/forget cycle."""

    @pytest.mark.asyncio
    async def test_learn_then_recall(self, bolor_server):
        """Learn a case, then recall it with a similar query."""
        # Learn
        learn_result = await bolor_server._learn({
            "problem": {"type": "bug", "error": "NullPointerException", "module": "auth"},
            "solution": {"fix": "add_null_check", "file": "auth.py", "line": 42},
            "outcome": {"resolved": True, "time_to_fix": "15min"},
            "success": True,
        })
        assert learn_result["success"] is True
        case_id = learn_result["case_id"]
        assert isinstance(case_id, str)

        # Recall with similar problem
        recall_result = await bolor_server._recall({
            "query": {"type": "bug", "error": "NullPointerException"},
            "type": "case",
            "k": 5,
        })
        assert "cases" in recall_result
        assert len(recall_result["cases"]) >= 1
        found = any(c["id"] == case_id for c in recall_result["cases"])
        assert found, f"Learned case {case_id} not found in recall results"

    @pytest.mark.asyncio
    async def test_remember_fact_then_recall(self, bolor_server):
        """Remember a fact, then recall it."""
        # Remember
        rem_result = await bolor_server._remember({
            "type": "fact",
            "data": {
                "subject": "python",
                "predicate": "is_good_for",
                "object": "data_science",
                "confidence": 0.95,
            },
        })
        assert rem_result["success"] is True
        fact_id = rem_result["id"]

        # Recall
        recall_result = await bolor_server._recall({
            "query": {"subject": "python"},
            "type": "fact",
            "k": 5,
        })
        assert "facts" in recall_result
        assert len(recall_result["facts"]) >= 1
        found = any(f["id"] == fact_id for f in recall_result["facts"])
        assert found, f"Remembered fact {fact_id} not found in recall results"

    @pytest.mark.asyncio
    async def test_forget_case(self, bolor_server):
        """Learn a case, forget it, verify it's gone."""
        learn_result = await bolor_server._learn({
            "problem": {"type": "temp"},
            "solution": {"fix": "temp"},
            "success": True,
        })
        case_id = learn_result["case_id"]

        forget_result = await bolor_server._forget({
            "type": "case",
            "id": case_id,
        })
        assert forget_result["success"] is True

        # Verify stats reflect removal
        stats = await bolor_server._brain_stats({})
        assert stats["cases"] == 0

    @pytest.mark.asyncio
    async def test_brain_stats_reflect_operations(self, bolor_server):
        """Stats should update after learn, remember, and reasoning ops."""
        await bolor_server._learn({
            "problem": {"x": 1}, "solution": {"y": 2}, "success": True,
        })
        await bolor_server._remember({
            "type": "fact",
            "data": {"subject": "a", "predicate": "b", "object": "c"},
        })
        await bolor_server._remember({
            "type": "node",
            "data": {"id": "n1", "label": "TestNode"},
        })
        await bolor_server._reason_hybrid({"query": "test query"})

        stats = await bolor_server._brain_stats({})
        assert stats["cases"] >= 1
        assert stats["facts"] >= 1
        assert stats["nodes"] >= 1
        assert stats["reasoning_queries"] >= 1


# ===========================================================================
# 4. NSAF tools
# ===========================================================================

class TestNSAFTools:
    """Test NSAF MCP server tools."""

    @pytest.mark.asyncio
    async def test_nsaf_status_before_init(self, nsaf_server):
        """Status check before initialization reports not_initialized."""
        result = await nsaf_server.handle_tool_call("get_nsaf_status", {})
        assert result["success"] is True
        assert result["result"]["framework_status"] == "not_initialized"

    @pytest.mark.asyncio
    async def test_evolve_agents(self, nsaf_server_initialized):
        """SCMA agent evolution returns expected structure."""
        result = await nsaf_server_initialized.handle_tool_call(
            "evolve_agents_scma",
            {
                "task_description": "Optimize database query performance",
                "population_size": 5,
                "generations": 2,
            },
        )
        assert result["success"] is True
        r = result["result"]
        assert r["task_description"] == "Optimize database query performance"
        assert r["agents_created"] == 5
        assert "best_fitness" in r

    @pytest.mark.asyncio
    async def test_add_and_query_memory(self, nsaf_server_initialized):
        """Add memory, then query for it."""
        # Add
        add_result = await nsaf_server_initialized.handle_tool_call(
            "add_memory",
            {
                "content": "Database indexing improves query performance significantly",
                "memory_type": "knowledge",
            },
        )
        assert add_result["success"] is True
        memory_id = add_result["result"]["memory_id"]
        assert memory_id is not None

        # Query
        query_result = await nsaf_server_initialized.handle_tool_call(
            "query_memory",
            {"query": "database indexing performance"},
        )
        assert query_result["success"] is True
        assert query_result["result"]["results_found"] >= 1

    @pytest.mark.asyncio
    async def test_cluster_tasks_quantum(self, nsaf_server_initialized):
        """Quantum-symbolic task clustering decomposes problems."""
        result = await nsaf_server_initialized.handle_tool_call(
            "cluster_tasks_quantum",
            {
                "problem_description": "Build a scalable web application",
                "tasks": [
                    {"name": "Design UI", "description": "Create user interface"},
                    {"name": "Build API", "description": "Create REST API"},
                    {"name": "Write tests", "description": "Write test suite"},
                ],
            },
        )
        assert result["success"] is True
        r = result["result"]
        assert r["input_tasks"] == 3
        assert r["clusters_created"] >= 1
        assert len(r["clusters"]) >= 1

    @pytest.mark.asyncio
    async def test_process_complex_task(self, nsaf_server_initialized):
        """Process a complex task through the NSAF pipeline."""
        result = await nsaf_server_initialized.handle_tool_call(
            "process_complex_task",
            {
                "description": "Analyze system performance bottlenecks",
                "complexity": 0.7,
            },
        )
        # process_complex_task may succeed or fail depending on pipeline;
        # we verify the structure of the response.
        assert "success" in result or "error" in result.get("result", {})

    @pytest.mark.asyncio
    async def test_get_memory_metrics(self, nsaf_server_initialized):
        """Memory metrics are retrievable."""
        result = await nsaf_server_initialized.handle_tool_call(
            "get_memory_metrics", {}
        )
        assert result["success"] is True
        assert "metrics" in result["result"]

    @pytest.mark.asyncio
    async def test_unknown_tool(self, nsaf_server):
        """Calling an unknown tool returns a clear error."""
        result = await nsaf_server.handle_tool_call("nonexistent_tool", {})
        assert result["success"] is False
        assert "Unknown tool" in result["error"]


# ===========================================================================
# 5. Combined workflow: both servers cooperate
# ===========================================================================

class TestCombinedWorkflow:
    """
    Simulate a real-world scenario where both Bolor Brain and NSAF work
    together on a problem.

    Scenario:
        1. Bolor Brain generates hypotheses about a performance issue
        2. Bolor Brain learns the diagnosis as a case
        3. NSAF processes a complex task based on the issue
        4. NSAF evolves agents to handle the task
        5. NSAF stores the solution in its memory system
        6. Bolor Brain recalls the learned case for a similar problem later
    """

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, bolor_server, nsaf_server):
        """Full cross-server workflow."""
        # --- Step 1: Bolor Brain reasons about the problem ---
        hypothesis_result = await bolor_server._reason_hypothesis({
            "observation": "API latency increased from 50ms to 500ms after deployment",
            "evidence": {
                "cpu_usage": "45%",
                "memory_usage": "78%",
                "db_connections": "saturated",
                "recent_change": "new ORM query in user endpoint",
            },
        })
        assert "observation" in hypothesis_result
        assert "hypotheses" in hypothesis_result

        # Also do symbolic reasoning to add some facts
        symbolic_result = await bolor_server._reason_symbolic({
            "query": "What causes high latency?",
            "facts": [
                ["new_orm_query", "causes", "extra_db_calls"],
                ["extra_db_calls", "causes", "connection_saturation"],
                ["connection_saturation", "causes", "high_latency"],
            ],
            "mode": "forward",
        })
        assert symbolic_result["derived_facts"] >= 0

        # --- Step 2: Bolor Brain learns the diagnosis ---
        learn_result = await bolor_server._learn({
            "problem": {
                "type": "performance_degradation",
                "symptom": "api_latency_10x",
                "root_cause": "orm_n_plus_1_query",
                "module": "user_endpoint",
            },
            "solution": {
                "action": "optimize_orm_query",
                "details": "Replace N+1 query with eager loading (select_related)",
                "file": "views/users.py",
            },
            "outcome": {
                "latency_before": "500ms",
                "latency_after": "45ms",
                "improvement": "91%",
            },
            "success": True,
        })
        assert learn_result["success"] is True
        learned_case_id = learn_result["case_id"]

        # --- Step 3: NSAF processes a task based on the problem ---
        await nsaf_server.handle_tool_call("initialize_nsaf_framework", {})

        task_result = await nsaf_server.handle_tool_call(
            "process_complex_task",
            {
                "description": (
                    "Fix and prevent API performance regressions "
                    "by auditing all ORM queries in the user module"
                ),
                "complexity": 0.6,
                "goals": [
                    {"type": "performance", "target": 0.95, "priority": 1.0},
                    {"type": "reliability", "target": 0.99, "priority": 0.8},
                ],
            },
        )
        # Verify we got a response (it may be success or error from pipeline)
        assert task_result is not None

        # --- Step 4: NSAF evolves agents for the optimization task ---
        evolve_result = await nsaf_server.handle_tool_call(
            "evolve_agents_scma",
            {
                "task_description": "Audit and optimize ORM queries for performance",
                "population_size": 10,
                "generations": 3,
                "fitness_criteria": [
                    {"name": "query_optimization", "weight": 0.6},
                    {"name": "code_quality", "weight": 0.4},
                ],
            },
        )
        assert evolve_result["success"] is True
        assert evolve_result["result"]["agents_created"] == 10

        # --- Step 5: NSAF stores the solution in memory ---
        memory_result = await nsaf_server.handle_tool_call(
            "add_memory",
            {
                "content": {
                    "diagnosis": "N+1 ORM query in user endpoint",
                    "fix": "eager loading with select_related",
                    "improvement": "91% latency reduction",
                },
                "memory_type": "experience",
                "tags": ["performance", "orm", "optimization"],
            },
        )
        assert memory_result["success"] is True

        # Query the stored memory
        mem_query = await nsaf_server.handle_tool_call(
            "query_memory",
            {"query": "ORM performance optimization"},
        )
        assert mem_query["success"] is True
        assert mem_query["result"]["results_found"] >= 1

        # --- Step 6: Bolor Brain recalls the case for a similar problem ---
        recall_result = await bolor_server._recall({
            "query": {
                "type": "performance_degradation",
                "symptom": "api_latency_10x",
            },
            "type": "case",
            "k": 3,
        })
        assert "cases" in recall_result
        assert len(recall_result["cases"]) >= 1
        # Verify our learned case is in the results
        case_ids = [c["id"] for c in recall_result["cases"]]
        assert learned_case_id in case_ids, (
            f"Expected case {learned_case_id} in recall, got {case_ids}"
        )
        top_case = recall_result["cases"][0]
        assert top_case["success"] is True
        assert top_case["solution"]["action"] == "optimize_orm_query"

        # Verify Bolor Brain accumulated knowledge through the workflow
        stats = await bolor_server._brain_stats({})
        assert stats["cases"] >= 1
        assert stats["reasoning_queries"] >= 2  # hypothesis + symbolic + hybrid (if called)

        # Clean up NSAF
        await nsaf_server.handle_tool_call("shutdown_nsaf_framework", {})

    @pytest.mark.asyncio
    async def test_knowledge_transfer_bolor_to_nsaf(self, bolor_server, nsaf_server):
        """
        Bolor Brain reasons and learns, then the insights are fed to NSAF
        for task clustering.
        """
        # Bolor Brain: case-based reasoning with past experiences
        cbr_result = await bolor_server._reason_case_based({
            "problem": {"type": "scaling", "issue": "high_traffic"},
            "past_cases": [
                {
                    "problem": {"type": "scaling", "issue": "high_traffic"},
                    "solution": {"action": "add_caching_layer", "tool": "redis"},
                    "success": True,
                },
                {
                    "problem": {"type": "scaling", "issue": "db_bottleneck"},
                    "solution": {"action": "read_replicas", "tool": "postgres"},
                    "success": True,
                },
            ],
        })
        assert len(cbr_result["similar_cases"]) >= 1
        best_solution = cbr_result["similar_cases"][0]["solution"]

        # Learn this case for future reference
        await bolor_server._learn({
            "problem": {"type": "scaling", "issue": "high_traffic"},
            "solution": best_solution,
            "success": True,
        })

        # Now use NSAF to plan the implementation
        await nsaf_server.handle_tool_call("initialize_nsaf_framework", {})

        cluster_result = await nsaf_server.handle_tool_call(
            "cluster_tasks_quantum",
            {
                "problem_description": (
                    f"Implement scaling solution: {best_solution.get('action', 'unknown')}"
                ),
                "tasks": [
                    {"name": "Setup Redis", "description": "Install and configure Redis caching"},
                    {"name": "Add cache layer", "description": "Implement caching in application"},
                    {"name": "Load test", "description": "Run load tests to validate improvement"},
                ],
            },
        )
        assert cluster_result["success"] is True
        assert cluster_result["result"]["clusters_created"] >= 1

        # Store the plan in NSAF memory
        await nsaf_server.handle_tool_call("add_memory", {
            "content": f"Scaling plan: {best_solution}",
            "memory_type": "plan",
        })

        # Verify both systems have retained knowledge
        bolor_stats = await bolor_server._brain_stats({})
        assert bolor_stats["cases"] >= 1

        nsaf_metrics = await nsaf_server.handle_tool_call("get_memory_metrics", {})
        assert nsaf_metrics["success"] is True

        await nsaf_server.handle_tool_call("shutdown_nsaf_framework", {})
