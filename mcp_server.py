#!/usr/bin/env python3
"""
Bolor Brain MCP Server
======================

Model Context Protocol server exposing Bolor Brain reasoning engines to Claude Code.

This server provides tools for:
- Hybrid reasoning (automatic approach selection)
- Symbolic reasoning (rule-based inference)
- Knowledge graph reasoning (relationship exploration)
- Case-based reasoning (learning from experience)
- Hypothesis testing (generating and testing theories)
- Analogical reasoning (cross-domain pattern transfer)

Author: Bolorerdene Bundgaa
        https://bolor.me

Usage:
    python mcp_server.py
"""

import asyncio
import json
import logging
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from modules import (
    HybridReasoner,
    SymbolicReasoner,
    KnowledgeGraph,
    CaseBasedReasoner,
    HypothesisEngine,
    AnalogicalReasoner,
    Fact,
    Rule,
    Node,
    Edge,
    Case,
    Concept,
    ProblemType,
)

# Autonomous agent components
from autonomous_loop import AutonomousAgent, AgentState
from task_scheduler import TaskScheduler
from goal_decomposer import GoalDecomposer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global brain instance
brain = HybridReasoner()

# Global autonomous agent instance
autonomous_agent = None  # Initialized when first needed


class BolorBrainServer:
    """MCP server for Bolor Brain reasoning engines."""

    def __init__(self):
        self.server = Server("bolor-brain")
        self.setup_handlers()

    def setup_handlers(self):
        """Set up MCP request handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available reasoning tools."""
            return [
                Tool(
                    name="reason_hybrid",
                    description=(
                        "Universal reasoning that automatically selects and orchestrates the best "
                        "reasoning approaches for your problem. Detects problem type (deduction, "
                        "diagnosis, planning, analogy, etc.) and combines results from multiple "
                        "reasoning engines. Use this as your default reasoning tool."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The question or problem to reason about",
                            },
                            "context": {
                                "type": "object",
                                "description": "Optional context (domain, goal, constraints, etc.)",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="reason_symbolic",
                    description=(
                        "Symbolic reasoning using forward and backward chaining with facts and rules. "
                        "Best for logical deduction, rule-based inference, and deriving conclusions "
                        "from known facts. Example: 'If X causes Y, and Y causes Z, does X cause Z?'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The logical question or goal",
                            },
                            "facts": {
                                "type": "array",
                                "description": "List of facts as [subject, predicate, object] tuples",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 3,
                                    "maxItems": 3,
                                },
                            },
                            "mode": {
                                "type": "string",
                                "enum": ["forward", "backward"],
                                "description": "Chaining mode (default: forward)",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="reason_knowledge_graph",
                    description=(
                        "Graph-based reasoning using nodes, edges, and traversal algorithms. "
                        "Best for exploring relationships, finding paths between concepts, "
                        "and discovering patterns in knowledge. Example: 'How are Python "
                        "and machine learning related?'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The graph query or relationship question",
                            },
                            "nodes": {
                                "type": "array",
                                "description": "List of nodes as {id, label, type} objects",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "label": {"type": "string"},
                                        "type": {"type": "string"},
                                    },
                                    "required": ["id", "label"],
                                },
                            },
                            "edges": {
                                "type": "array",
                                "description": "List of edges as {source, target, relation} objects",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "source": {"type": "string"},
                                        "target": {"type": "string"},
                                        "relation": {"type": "string"},
                                        "weight": {"type": "number"},
                                    },
                                    "required": ["source", "target", "relation"],
                                },
                            },
                            "source": {
                                "type": "string",
                                "description": "Starting node for path finding",
                            },
                            "target": {
                                "type": "string",
                                "description": "Target node for path finding",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="reason_case_based",
                    description=(
                        "Case-based reasoning using the 4R cycle (Retrieve, Reuse, Revise, Retain). "
                        "Best for learning from past experiences and adapting previous solutions "
                        "to new problems. Example: 'We had a similar bug before, how did we fix it?'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem": {
                                "type": "object",
                                "description": "Current problem description as key-value pairs",
                            },
                            "past_cases": {
                                "type": "array",
                                "description": "Optional past cases to learn from",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "problem": {"type": "object"},
                                        "solution": {"type": "object"},
                                        "outcome": {"type": "object"},
                                        "success": {"type": "boolean"},
                                    },
                                    "required": ["problem", "solution"],
                                },
                            },
                            "k": {
                                "type": "integer",
                                "description": "Number of similar cases to retrieve (default: 3)",
                            },
                        },
                        "required": ["problem"],
                    },
                ),
                Tool(
                    name="reason_hypothesis",
                    description=(
                        "Hypothesis generation and testing for explaining observations. "
                        "Best for diagnostic problems, root cause analysis, and exploring "
                        "possible explanations. Example: 'Why is the system crashing?'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "observation": {
                                "type": "string",
                                "description": "The observation or symptom to explain",
                            },
                            "evidence": {
                                "type": "object",
                                "description": "Available evidence as key-value pairs",
                            },
                            "max_hypotheses": {
                                "type": "integer",
                                "description": "Maximum hypotheses to generate (default: 5)",
                            },
                        },
                        "required": ["observation"],
                    },
                ),
                Tool(
                    name="reason_analogical",
                    description=(
                        "Analogical reasoning using structure-mapping for cross-domain transfer. "
                        "Best for creative problem-solving by finding similar patterns in different "
                        "domains. Example: 'The atom is like the solar system - what can we infer?'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_domain": {
                                "type": "string",
                                "description": "The source domain to map from",
                            },
                            "target_domain": {
                                "type": "string",
                                "description": "The target domain to map to",
                            },
                            "concepts": {
                                "type": "array",
                                "description": "Concepts to map between domains",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "domain": {"type": "string"},
                                        "properties": {"type": "object"},
                                    },
                                    "required": ["id", "name", "domain"],
                                },
                            },
                        },
                        "required": ["source_domain", "target_domain"],
                    },
                ),
                Tool(
                    name="store_case",
                    description=(
                        "Store a new case for future case-based reasoning. Use this to "
                        "help the brain learn from experience and improve future recommendations."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem": {
                                "type": "object",
                                "description": "Problem description as key-value pairs",
                            },
                            "solution": {
                                "type": "object",
                                "description": "Solution that was applied",
                            },
                            "outcome": {
                                "type": "object",
                                "description": "What happened after applying the solution",
                            },
                            "success": {
                                "type": "boolean",
                                "description": "Whether the solution was successful",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorization",
                            },
                        },
                        "required": ["problem", "solution"],
                    },
                ),
                Tool(
                    name="add_knowledge",
                    description=(
                        "Add facts, rules, nodes, or edges to the brain's knowledge base. "
                        "Use this to teach the brain domain-specific knowledge."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "knowledge_type": {
                                "type": "string",
                                "enum": ["fact", "rule", "node", "edge"],
                                "description": "Type of knowledge to add",
                            },
                            "data": {
                                "type": "object",
                                "description": "Knowledge data (structure depends on type)",
                            },
                        },
                        "required": ["knowledge_type", "data"],
                    },
                ),
                Tool(
                    name="get_stats",
                    description=(
                        "Get statistics about the brain's knowledge base and reasoning activity."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                # Autonomous Agent Tools
                Tool(
                    name="run_autonomous",
                    description=(
                        "Run Claude Code in autonomous mode - like OpenClaw, but secure. "
                        "Give a high-level goal and the agent works independently: decomposes "
                        "the goal, creates a schedule, executes tasks, learns from outcomes, "
                        "and evolves strategies. Features 4-tier security guardrails, Bolor Brain "
                        "memory, and NSAF evolution. Use this to turn manual workflows into "
                        "autonomous execution."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "goal": {
                                "type": "string",
                                "description": "High-level goal (e.g., 'Build documentation for Bolor Brain')",
                            },
                            "max_duration_minutes": {
                                "type": "number",
                                "description": "Optional time limit in minutes (default: unlimited)",
                            },
                        },
                        "required": ["goal"],
                    },
                ),
                Tool(
                    name="get_autonomous_status",
                    description=(
                        "Get current status of autonomous execution. Returns progress, "
                        "current task, time elapsed, estimated completion, learnings count, "
                        "and evolution count."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="pause_autonomous",
                    description=(
                        "Pause autonomous execution. Current task will complete, then pause. "
                        "Use resume_autonomous to continue."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="resume_autonomous",
                    description=(
                        "Resume paused autonomous execution."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="stop_autonomous",
                    description=(
                        "Stop autonomous execution immediately. Progress is saved. "
                        "Can resume later with a new run_autonomous call."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "reason_hybrid":
                    result = await self._reason_hybrid(arguments)
                elif name == "reason_symbolic":
                    result = await self._reason_symbolic(arguments)
                elif name == "reason_knowledge_graph":
                    result = await self._reason_knowledge_graph(arguments)
                elif name == "reason_case_based":
                    result = await self._reason_case_based(arguments)
                elif name == "reason_hypothesis":
                    result = await self._reason_hypothesis(arguments)
                elif name == "reason_analogical":
                    result = await self._reason_analogical(arguments)
                elif name == "store_case":
                    result = await self._store_case(arguments)
                elif name == "add_knowledge":
                    result = await self._add_knowledge(arguments)
                elif name == "get_stats":
                    result = await self._get_stats(arguments)
                # Autonomous agent tools
                elif name == "run_autonomous":
                    result = await self._run_autonomous(arguments)
                elif name == "get_autonomous_status":
                    result = await self._get_autonomous_status(arguments)
                elif name == "pause_autonomous":
                    result = await self._pause_autonomous(arguments)
                elif name == "resume_autonomous":
                    result = await self._resume_autonomous(arguments)
                elif name == "stop_autonomous":
                    result = await self._stop_autonomous(arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                logger.exception(f"Error in tool {name}")
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": str(e)}, indent=2)
                    )
                ]

    # === Tool Implementations ===

    async def _reason_hybrid(self, args: dict) -> dict:
        """Hybrid reasoning - orchestrates all approaches."""
        query = args["query"]
        context = args.get("context", {})

        result = brain.reason({"query": query, "context": context})

        return {
            "problem_type": result.problem_type.value,
            "approaches_used": [a.value for a in result.approaches_used],
            "confidence": round(result.confidence, 3),
            "result": result.combined_result,
            "reasoning_trace": result.reasoning_trace,
            "processing_time": round(result.processing_time, 3),
        }

    async def _reason_symbolic(self, args: dict) -> dict:
        """Symbolic reasoning with facts and rules."""
        query = args["query"]
        facts_data = args.get("facts", [])
        mode = args.get("mode", "forward")

        # Add facts to brain
        for fact_data in facts_data:
            if len(fact_data) >= 3:
                fact = Fact(
                    subject=fact_data[0],
                    predicate=fact_data[1],
                    object=fact_data[2],
                )
                brain.symbolic.add_fact(fact)

        # Run reasoning
        if mode == "backward":
            # Parse goal from query (simplified)
            goal = {"query": query}
            result = brain.symbolic.backward_chain(goal)
        else:
            result = brain.symbolic.forward_chain()

        return {
            "mode": mode,
            "derived_facts": len(result.derived),
            "conclusions": [
                {"subject": f.subject, "predicate": f.predicate, "object": f.object}
                for f in result.derived[:10]  # Limit output
            ],
            "reasoning_trace": result.reasoning_trace,
        }

    async def _reason_knowledge_graph(self, args: dict) -> dict:
        """Knowledge graph reasoning."""
        query = args["query"]
        nodes_data = args.get("nodes", [])
        edges_data = args.get("edges", [])
        source = args.get("source")
        target = args.get("target")

        # Add nodes and edges
        for node_data in nodes_data:
            node = Node(
                id=node_data["id"],
                label=node_data["label"],
                node_type=node_data.get("type", "concept"),
            )
            brain.kg.add_node(node)

        for edge_data in edges_data:
            edge = Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                relation=edge_data["relation"],
                weight=edge_data.get("weight", 1.0),
            )
            brain.kg.add_edge(edge)

        result = {}

        # Find path if source and target specified
        if source and target:
            path_result = brain.kg.find_path(source, target)
            if path_result and path_result.found:
                result["path"] = {
                    "nodes": path_result.path,
                    "total_weight": path_result.total_weight,
                }

        # Get graph stats
        result["stats"] = {
            "total_nodes": len(brain.kg.nodes),
            "total_edges": len(brain.kg.edges),
        }

        return result

    async def _reason_case_based(self, args: dict) -> dict:
        """Case-based reasoning."""
        problem = args["problem"]
        past_cases = args.get("past_cases", [])
        k = args.get("k", 3)

        # Add past cases
        for case_data in past_cases:
            case = Case(
                id=case_data.get("id", ""),
                problem=case_data["problem"],
                solution=case_data["solution"],
                outcome=case_data.get("outcome", {}),
                success=case_data.get("success", True),
            )
            brain.cbr.store_case(case)

        # Retrieve similar cases
        matches = brain.cbr.retrieve(problem, k=k)

        return {
            "query": problem,
            "similar_cases": [
                {
                    "case_id": match.case.id,
                    "similarity": round(match.similarity, 3),
                    "problem": match.case.problem,
                    "solution": match.case.solution,
                    "success": match.case.success,
                }
                for match in matches
            ],
        }

    async def _reason_hypothesis(self, args: dict) -> dict:
        """Hypothesis generation and testing."""
        observation = args["observation"]
        evidence = args.get("evidence", {})
        max_hypotheses = args.get("max_hypotheses", 5)

        # Generate hypotheses
        hypotheses = brain.hypothesis.generate_hypotheses(
            observation, max_hypotheses=max_hypotheses
        )

        # Test against evidence if provided
        if evidence:
            for hyp in hypotheses:
                # Add evidence to brain for testing
                for key, value in evidence.items():
                    fact = Fact(subject="evidence", predicate=key, object=str(value))
                    brain.symbolic.add_fact(fact)

                # Test hypothesis
                test_result = brain.hypothesis.test_hypothesis(hyp.id)
                if test_result:
                    hyp.confidence = test_result.confidence

        return {
            "observation": observation,
            "hypotheses": [
                {
                    "id": h.id,
                    "statement": h.statement,
                    "confidence": round(h.confidence, 3),
                    "status": h.status,
                }
                for h in sorted(hypotheses, key=lambda x: x.confidence, reverse=True)
            ],
        }

    async def _reason_analogical(self, args: dict) -> dict:
        """Analogical reasoning."""
        source_domain = args["source_domain"]
        target_domain = args["target_domain"]
        concepts_data = args.get("concepts", [])

        # Add concepts
        for concept_data in concepts_data:
            concept = Concept(
                id=concept_data["id"],
                name=concept_data["name"],
                domain=concept_data["domain"],
                properties=concept_data.get("properties", {}),
            )
            brain.analogical.add_concept(concept)

        # Find analogies
        analogies = brain.analogical.find_analogies(source_domain, target_domain)

        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "analogies": [
                {
                    "source": a.source_concept.name,
                    "target": a.target_concept.name,
                    "similarity": round(a.similarity, 3),
                    "mapping_type": a.mapping_type.value,
                }
                for a in analogies[:5]  # Limit output
            ],
        }

    async def _store_case(self, args: dict) -> dict:
        """Store a case for learning."""
        problem = args["problem"]
        solution = args["solution"]
        outcome = args.get("outcome", {})
        success = args.get("success", True)
        tags = args.get("tags", [])

        case = brain.cbr.retain(
            problem=problem,
            solution=solution,
            outcome=outcome,
            success=success,
            tags=tags,
        )

        return {
            "success": True,
            "case_id": case.id,
            "message": "Case stored successfully for future learning",
        }

    async def _add_knowledge(self, args: dict) -> dict:
        """Add knowledge to the brain."""
        knowledge_type = args["knowledge_type"]
        data = args["data"]

        if knowledge_type == "fact":
            fact = Fact(
                subject=data["subject"],
                predicate=data["predicate"],
                object=data["object"],
                confidence=data.get("confidence", 1.0),
            )
            brain.symbolic.add_fact(fact)
            return {"success": True, "type": "fact", "id": fact.id}

        elif knowledge_type == "node":
            node = Node(
                id=data["id"],
                label=data["label"],
                node_type=data.get("type", "concept"),
                properties=data.get("properties", {}),
            )
            brain.kg.add_node(node)
            return {"success": True, "type": "node", "id": node.id}

        elif knowledge_type == "edge":
            edge = Edge(
                source=data["source"],
                target=data["target"],
                relation=data["relation"],
                weight=data.get("weight", 1.0),
            )
            brain.kg.add_edge(edge)
            return {"success": True, "type": "edge"}

        else:
            return {"error": f"Unknown knowledge type: {knowledge_type}"}

    async def _get_stats(self, args: dict) -> dict:
        """Get brain statistics."""
        stats = brain.get_stats()
        return stats

    # === Autonomous Agent Tool Implementations ===

    async def _run_autonomous(self, args: dict) -> dict:
        """Run autonomous agent with goal."""
        global autonomous_agent

        goal = args["goal"]
        max_duration_minutes = args.get("max_duration_minutes")

        # Initialize agent if not exists
        if autonomous_agent is None:
            autonomous_agent = AutonomousAgent(
                brain_client=brain,
                nsaf_client=None,  # Will connect to NSAF MCP when available
            )

        # Convert max_duration to timedelta
        from datetime import timedelta
        max_duration = None
        if max_duration_minutes:
            max_duration = timedelta(minutes=max_duration_minutes)

        # Run autonomously
        try:
            report = await autonomous_agent.run_autonomous(
                goal=goal,
                max_duration=max_duration
            )

            return {
                "success": True,
                "status": "complete",
                "goal": report["goal"],
                "duration": report["duration"],
                "tasks_completed": report["tasks_completed"],
                "tasks_failed": report["tasks_failed"],
                "success_rate": report["success_rate"],
                "learnings_count": report["learnings_count"],
                "evolutions_count": report["evolutions_count"],
            }

        except Exception as e:
            logger.exception("Error in autonomous execution")
            return {
                "success": False,
                "error": str(e),
                "message": "Autonomous execution failed"
            }

    async def _get_autonomous_status(self, args: dict) -> dict:
        """Get autonomous agent status."""
        global autonomous_agent

        if autonomous_agent is None:
            return {
                "status": "not_started",
                "message": "No autonomous execution running"
            }

        status = autonomous_agent.get_status()

        return {
            "state": status.state.value,
            "current_task": status.current_task,
            "progress": f"{status.progress:.1%}",
            "tasks_completed": status.tasks_completed,
            "tasks_total": status.tasks_total,
            "time_elapsed": str(status.time_elapsed),
            "estimated_completion": str(status.estimated_completion) if status.estimated_completion else None,
            "learnings_count": status.learnings_count,
            "evolutions_count": status.evolutions_count,
        }

    async def _pause_autonomous(self, args: dict) -> dict:
        """Pause autonomous execution."""
        global autonomous_agent

        if autonomous_agent is None:
            return {
                "success": False,
                "message": "No autonomous execution running"
            }

        autonomous_agent.pause()

        return {
            "success": True,
            "message": "Autonomous execution paused. Current task will complete."
        }

    async def _resume_autonomous(self, args: dict) -> dict:
        """Resume autonomous execution."""
        global autonomous_agent

        if autonomous_agent is None:
            return {
                "success": False,
                "message": "No autonomous execution to resume"
            }

        autonomous_agent.resume()

        return {
            "success": True,
            "message": "Autonomous execution resumed"
        }

    async def _stop_autonomous(self, args: dict) -> dict:
        """Stop autonomous execution."""
        global autonomous_agent

        if autonomous_agent is None:
            return {
                "success": False,
                "message": "No autonomous execution running"
            }

        autonomous_agent.stop()

        return {
            "success": True,
            "message": "Autonomous execution stopped. Progress saved."
        }

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    logger.info("Starting Bolor Brain MCP Server...")
    server = BolorBrainServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
