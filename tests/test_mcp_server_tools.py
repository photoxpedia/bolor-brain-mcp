"""Test that MCP server tools work end-to-end."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def server(tmp_path):
    """Create server with temp persistence dir."""
    os.environ["BOLOR_PERSISTENCE_DIR"] = str(tmp_path / "brain")
    from mcp_server import BolorBrainServer
    s = BolorBrainServer()
    yield s
    if "BOLOR_PERSISTENCE_DIR" in os.environ:
        del os.environ["BOLOR_PERSISTENCE_DIR"]


class TestReasoningTools:
    @pytest.mark.asyncio
    async def test_reason_hybrid(self, server):
        result = await server._reason_hybrid({"query": "Is Python good for AI?"})
        assert "problem_type" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_reason_symbolic(self, server):
        result = await server._reason_symbolic({
            "query": "test",
            "facts": [["python", "is", "language"]],
            "mode": "forward",
        })
        assert "mode" in result

    @pytest.mark.asyncio
    async def test_reason_hypothesis(self, server):
        result = await server._reason_hypothesis({
            "observation": "Server is slow",
        })
        assert "hypotheses" in result

    @pytest.mark.asyncio
    async def test_reason_knowledge_graph(self, server):
        result = await server._reason_knowledge_graph({
            "query": "test",
            "nodes": [
                {"id": "n1", "label": "Python"},
                {"id": "n2", "label": "AI"},
            ],
            "edges": [
                {"source": "n1", "target": "n2", "relation": "used_for"},
            ],
            "source": "n1",
            "target": "n2",
        })
        assert "stats" in result

    @pytest.mark.asyncio
    async def test_reason_case_based(self, server):
        result = await server._reason_case_based({
            "problem": {"type": "bug", "error": "timeout"},
            "past_cases": [
                {
                    "problem": {"type": "bug", "error": "timeout"},
                    "solution": {"fix": "increase timeout"},
                    "success": True,
                }
            ],
            "k": 3,
        })
        assert "similar_cases" in result

    @pytest.mark.asyncio
    async def test_reason_analogical(self, server):
        result = await server._reason_analogical({
            "source_domain": "solar_system",
            "target_domain": "atom",
        })
        assert "source_domain" in result
        assert "target_domain" in result


class TestMemoryTools:
    @pytest.mark.asyncio
    async def test_learn_and_recall(self, server):
        learn_result = await server._learn({
            "problem": {"type": "bug", "error": "timeout"},
            "solution": {"fix": "increase timeout"},
            "outcome": {"success": True},
            "success": True,
        })
        assert learn_result["success"] is True
        assert "case_id" in learn_result

        recall_result = await server._recall({
            "query": {"type": "bug"},
            "k": 3,
        })
        assert "cases" in recall_result

    @pytest.mark.asyncio
    async def test_remember_fact(self, server):
        result = await server._remember({
            "type": "fact",
            "data": {"subject": "python", "predicate": "is", "object": "language"},
        })
        assert result["success"] is True
        assert result["type"] == "fact"
        assert "id" in result

    @pytest.mark.asyncio
    async def test_remember_node(self, server):
        result = await server._remember({
            "type": "node",
            "data": {"id": "n1", "label": "Python", "type": "language"},
        })
        assert result["success"] is True
        assert result["type"] == "node"

    @pytest.mark.asyncio
    async def test_remember_edge(self, server):
        # First add nodes
        await server._remember({
            "type": "node",
            "data": {"id": "n1", "label": "Python"},
        })
        await server._remember({
            "type": "node",
            "data": {"id": "n2", "label": "AI"},
        })
        # Then add edge
        result = await server._remember({
            "type": "edge",
            "data": {"source": "n1", "target": "n2", "relation": "used_for"},
        })
        assert result["success"] is True
        assert result["type"] == "edge"

    @pytest.mark.asyncio
    async def test_remember_case(self, server):
        result = await server._remember({
            "type": "case",
            "data": {
                "problem": {"type": "test"},
                "solution": {"fix": "test"},
                "success": True,
            },
        })
        assert result["success"] is True
        assert result["type"] == "case"
        assert "id" in result

    @pytest.mark.asyncio
    async def test_recall_facts(self, server):
        await server._remember({
            "type": "fact",
            "data": {"subject": "python", "predicate": "is", "object": "language"},
        })
        result = await server._recall({
            "query": {"subject": "python"},
            "type": "fact",
            "k": 5,
        })
        assert "facts" in result
        assert len(result["facts"]) >= 1

    @pytest.mark.asyncio
    async def test_forget_case(self, server):
        learn_result = await server._learn({
            "problem": {"type": "test"},
            "solution": {"fix": "test"},
            "success": True,
        })
        case_id = learn_result["case_id"]

        forget_result = await server._forget({
            "type": "case",
            "id": case_id,
        })
        assert forget_result["success"] is True

    @pytest.mark.asyncio
    async def test_forget_fact(self, server):
        remember_result = await server._remember({
            "type": "fact",
            "data": {"subject": "test", "predicate": "is", "object": "temporary"},
        })
        fact_id = remember_result["id"]

        forget_result = await server._forget({
            "type": "fact",
            "id": fact_id,
        })
        assert forget_result["success"] is True

    @pytest.mark.asyncio
    async def test_forget_nonexistent(self, server):
        result = await server._forget({
            "type": "case",
            "id": "nonexistent",
        })
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_brain_stats(self, server):
        stats = await server._brain_stats({})
        assert "cases" in stats
        assert "facts" in stats
        assert "nodes" in stats
        assert "edges" in stats
        assert "reasoning_queries" in stats

    @pytest.mark.asyncio
    async def test_brain_stats_after_operations(self, server):
        # Add some data
        await server._learn({
            "problem": {"x": 1},
            "solution": {"y": 2},
            "success": True,
        })
        await server._remember({
            "type": "fact",
            "data": {"subject": "a", "predicate": "b", "object": "c"},
        })
        await server._reason_hybrid({"query": "test"})

        stats = await server._brain_stats({})
        assert stats["cases"] >= 1
        assert stats["facts"] >= 1
        assert stats["reasoning_queries"] >= 1


class TestPersistence:
    @pytest.mark.asyncio
    async def test_data_persists_across_server_restarts(self, tmp_path):
        """Test that data survives server restart."""
        persist_dir = str(tmp_path / "brain")
        os.environ["BOLOR_PERSISTENCE_DIR"] = persist_dir

        from mcp_server import BolorBrainServer

        # First server: store data
        s1 = BolorBrainServer()
        await s1._learn({
            "problem": {"type": "persistence_test"},
            "solution": {"fix": "works"},
            "success": True,
        })
        await s1._remember({
            "type": "fact",
            "data": {"subject": "test", "predicate": "is", "object": "persistent"},
        })

        # Second server: data should be loaded
        s2 = BolorBrainServer()
        stats = await s2._brain_stats({})
        assert stats["cases"] >= 1
        assert stats["facts"] >= 1

        if "BOLOR_PERSISTENCE_DIR" in os.environ:
            del os.environ["BOLOR_PERSISTENCE_DIR"]
