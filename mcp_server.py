#!/usr/bin/env python3
"""
Bolor Brain MCP Server
======================

Model Context Protocol server exposing Bolor Brain reasoning engines to Claude Code.

This server provides 11 tools:
- 6 reasoning tools (hybrid, symbolic, knowledge graph, case-based, hypothesis, analogical)
- 4 memory tools (remember, recall, learn, forget)
- 1 utility tool (brain_stats)

Persists brain state to disk as JSON files.

Author: Bolorerdene Bundgaa
        https://bolor.me

Usage:
    python mcp_server.py
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from modules import (
    HybridReasoner,
    Fact,
    Node,
    Edge,
    Case,
    Concept,
)
from persistence import BrainPersistence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BolorBrainServer:
    """MCP server for Bolor Brain reasoning engines."""

    def __init__(self):
        self.server = Server("bolor-brain")

        # Initialize persistence
        persistence_dir = os.environ.get("BOLOR_PERSISTENCE_DIR", None)
        self.persistence = BrainPersistence(persistence_dir)

        # Initialize brain
        self.brain = HybridReasoner()

        # Load persisted state
        self._load_persisted_state()

        # Track reasoning queries
        self._reasoning_queries = 0

        self.setup_handlers()

    def _load_persisted_state(self):
        """Load persisted cases, facts, and knowledge graph into brain."""
        # Load cases
        for case_data in self.persistence.load_cases():
            case = Case(
                id=case_data.get("id", ""),
                problem=case_data.get("problem", {}),
                solution=case_data.get("solution", {}),
                outcome=case_data.get("outcome", {}),
                success=case_data.get("success", True),
            )
            self.brain.cbr.store_case(case)

        # Load facts
        for fact_data in self.persistence.load_facts():
            fact = Fact(
                subject=fact_data.get("subject", ""),
                predicate=fact_data.get("predicate", ""),
                object=fact_data.get("object", ""),
                confidence=fact_data.get("confidence", 1.0),
            )
            # Preserve original ID if available
            if "id" in fact_data:
                fact.id = fact_data["id"]
            self.brain.symbolic.add_fact(fact)

        # Load knowledge graph
        nodes, edges = self.persistence.load_knowledge()
        for node_data in nodes:
            node = Node(
                id=node_data["id"],
                label=node_data["label"],
                node_type=node_data.get("type", "concept"),
                properties=node_data.get("properties", {}),
            )
            self.brain.kg.add_node(node)

        for edge_data in edges:
            edge = Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                relation=edge_data["relation"],
                weight=edge_data.get("weight", 1.0),
            )
            self.brain.kg.add_edge(edge)

        logger.info(
            f"Loaded persisted state: "
            f"{len(self.brain.cbr.cases)} cases, "
            f"{len(self.brain.symbolic.facts)} facts, "
            f"{len(self.brain.kg.nodes)} nodes, "
            f"{len(self.brain.kg.edges)} edges"
        )

    def _persist_knowledge_graph(self):
        """Save the current knowledge graph to disk."""
        nodes = [
            {
                "id": n.id,
                "label": n.label,
                "type": n.node_type,
                "properties": n.properties,
            }
            for n in self.brain.kg.nodes.values()
        ]
        edges = [
            {
                "source": e.source,
                "target": e.target,
                "relation": e.relation,
                "weight": e.weight,
            }
            for e in self.brain.kg.edges
        ]
        self.persistence.save_knowledge(nodes, edges)

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
                # Memory tools
                Tool(
                    name="remember",
                    description=(
                        "Store a case, fact, node, or edge in the brain's knowledge base. "
                        "Persisted to disk for future sessions."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["case", "fact", "node", "edge"],
                                "description": "Type of knowledge to store",
                            },
                            "data": {
                                "type": "object",
                                "description": "Knowledge data (structure depends on type)",
                            },
                        },
                        "required": ["type", "data"],
                    },
                ),
                Tool(
                    name="recall",
                    description=(
                        "Retrieve matching cases or facts from the brain's knowledge base."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "object",
                                "description": "Query to match against (key-value pairs)",
                            },
                            "type": {
                                "type": "string",
                                "enum": ["case", "fact"],
                                "description": "Type of knowledge to recall (default: case)",
                            },
                            "k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 3)",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="learn",
                    description=(
                        "Store a problem/solution/outcome case. Shortcut for remember(type='case'). "
                        "The brain learns from experience and improves future recommendations."
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
                        },
                        "required": ["problem", "solution"],
                    },
                ),
                Tool(
                    name="forget",
                    description=(
                        "Delete a case or fact by ID from the brain's knowledge base."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["case", "fact"],
                                "description": "Type of knowledge to delete",
                            },
                            "id": {
                                "type": "string",
                                "description": "ID of the case or fact to delete",
                            },
                        },
                        "required": ["type", "id"],
                    },
                ),
                # Utility tools
                Tool(
                    name="brain_stats",
                    description=(
                        "Get statistics about the brain's knowledge base and reasoning activity."
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
                handlers = {
                    "reason_hybrid": self._reason_hybrid,
                    "reason_symbolic": self._reason_symbolic,
                    "reason_knowledge_graph": self._reason_knowledge_graph,
                    "reason_case_based": self._reason_case_based,
                    "reason_hypothesis": self._reason_hypothesis,
                    "reason_analogical": self._reason_analogical,
                    "remember": self._remember,
                    "recall": self._recall,
                    "learn": self._learn,
                    "forget": self._forget,
                    "brain_stats": self._brain_stats,
                }

                handler = handlers.get(name)
                if handler:
                    result = await handler(arguments)
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

    # === Reasoning Tool Implementations ===

    async def _reason_hybrid(self, args: dict) -> dict:
        """Hybrid reasoning - orchestrates all approaches."""
        query = args["query"]
        context = args.get("context", {})

        self._reasoning_queries += 1
        result = self.brain.reason({"query": query, "context": context})

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

        self._reasoning_queries += 1

        # Add facts to brain
        for fact_data in facts_data:
            if len(fact_data) >= 3:
                fact = Fact(
                    subject=fact_data[0],
                    predicate=fact_data[1],
                    object=fact_data[2],
                )
                self.brain.symbolic.add_fact(fact)

        # Run reasoning
        if mode == "backward":
            goal = Fact(subject=query, predicate="is", object="true")
            success, proof_path = self.brain.symbolic.backward_chain(goal)
            return {
                "mode": mode,
                "success": success,
                "derived_facts": len(proof_path),
                "conclusions": [
                    {"subject": f.subject, "predicate": f.predicate, "object": f.object}
                    for f in proof_path[:10]
                ],
                "reasoning_trace": [f"Backward chaining for: {query}"],
            }
        else:
            derived = self.brain.symbolic.forward_chain()
            return {
                "mode": mode,
                "derived_facts": len(derived),
                "conclusions": [
                    {"subject": f.subject, "predicate": f.predicate, "object": f.object}
                    for f in derived[:10]
                ],
                "reasoning_trace": [f"Forward chaining derived {len(derived)} facts"],
            }

    async def _reason_knowledge_graph(self, args: dict) -> dict:
        """Knowledge graph reasoning."""
        query = args["query"]
        nodes_data = args.get("nodes", [])
        edges_data = args.get("edges", [])
        source = args.get("source")
        target = args.get("target")

        self._reasoning_queries += 1

        # Add nodes and edges
        for node_data in nodes_data:
            node = Node(
                id=node_data["id"],
                label=node_data["label"],
                node_type=node_data.get("type", "concept"),
            )
            self.brain.kg.add_node(node)

        for edge_data in edges_data:
            edge = Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                relation=edge_data["relation"],
                weight=edge_data.get("weight", 1.0),
            )
            self.brain.kg.add_edge(edge)

        result = {}

        # Find path if source and target specified
        if source and target:
            path_result = self.brain.kg.find_path(source, target)
            if path_result and path_result.found:
                result["path"] = {
                    "nodes": path_result.path,
                    "total_weight": path_result.total_weight,
                }

        # Get graph stats
        result["stats"] = {
            "total_nodes": len(self.brain.kg.nodes),
            "total_edges": len(self.brain.kg.edges),
        }

        return result

    async def _reason_case_based(self, args: dict) -> dict:
        """Case-based reasoning."""
        problem = args["problem"]
        past_cases = args.get("past_cases", [])
        k = args.get("k", 3)

        self._reasoning_queries += 1

        # Add past cases
        for case_data in past_cases:
            case = Case(
                id=case_data.get("id") or str(uuid.uuid4())[:8],
                problem=case_data["problem"],
                solution=case_data["solution"],
                outcome=case_data.get("outcome", {}),
                success=case_data.get("success", True),
            )
            self.brain.cbr.store_case(case)

        # Retrieve similar cases
        matches = self.brain.cbr.retrieve(problem, k=k)

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

        self._reasoning_queries += 1

        # Generate hypotheses
        hypotheses = self.brain.hypothesis.generate_hypotheses(
            observation, max_hypotheses=max_hypotheses
        )

        # Test against evidence if provided
        if evidence:
            for hyp in hypotheses:
                for key, value in evidence.items():
                    fact = Fact(subject="evidence", predicate=key, object=str(value))
                    self.brain.symbolic.add_fact(fact)

                test_result = self.brain.hypothesis.test_hypothesis(hyp.id)
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

        self._reasoning_queries += 1

        # Add concepts
        for concept_data in concepts_data:
            concept = Concept(
                id=concept_data["id"],
                name=concept_data["name"],
                domain=concept_data["domain"],
                attributes=concept_data.get("properties", {}),
            )
            self.brain.analogical.add_concept(concept)

        # Find analogy
        analogy = self.brain.analogical.find_analogy(source_domain, target_domain)

        analogies_output = []
        if analogy:
            analogies_output = [
                {
                    "source": m.source_concept,
                    "target": m.target_concept,
                    "similarity": round(m.similarity, 3),
                    "mapping_type": m.mapping_type.value,
                }
                for m in analogy.mappings[:5]
            ]

        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "analogies": analogies_output,
            "overall_similarity": round(analogy.overall_similarity, 3) if analogy else 0.0,
        }

    # === Memory Tool Implementations ===

    async def _remember(self, args: dict) -> dict:
        """Store a case, fact, node, or edge."""
        mem_type = args["type"]
        data = args["data"]

        if mem_type == "case":
            case = self.brain.cbr.retain(
                problem=data.get("problem", {}),
                solution=data.get("solution", {}),
                outcome=data.get("outcome", {}),
                success=data.get("success", True),
            )
            self.persistence.save_case({
                "id": case.id,
                "problem": case.problem,
                "solution": case.solution,
                "outcome": case.outcome,
                "success": case.success,
            })
            return {"success": True, "type": "case", "id": case.id}

        elif mem_type == "fact":
            fact = Fact(
                subject=data["subject"],
                predicate=data["predicate"],
                object=data["object"],
                confidence=data.get("confidence", 1.0),
            )
            self.brain.symbolic.add_fact(fact)
            self.persistence.save_fact({
                "id": fact.id,
                "subject": fact.subject,
                "predicate": fact.predicate,
                "object": fact.object,
                "confidence": fact.confidence,
            })
            return {"success": True, "type": "fact", "id": fact.id}

        elif mem_type == "node":
            node = Node(
                id=data["id"],
                label=data["label"],
                node_type=data.get("type", "concept"),
                properties=data.get("properties", {}),
            )
            self.brain.kg.add_node(node)
            self._persist_knowledge_graph()
            return {"success": True, "type": "node", "id": node.id}

        elif mem_type == "edge":
            edge = Edge(
                source=data["source"],
                target=data["target"],
                relation=data["relation"],
                weight=data.get("weight", 1.0),
            )
            self.brain.kg.add_edge(edge)
            self._persist_knowledge_graph()
            return {"success": True, "type": "edge"}

        else:
            return {"error": f"Unknown memory type: {mem_type}"}

    async def _recall(self, args: dict) -> dict:
        """Retrieve matching cases or facts."""
        query = args["query"]
        mem_type = args.get("type", "case")
        k = args.get("k", 3)

        if mem_type == "case":
            matches = self.brain.cbr.retrieve(query, k=k)
            return {
                "cases": [
                    {
                        "id": m.case.id,
                        "similarity": round(m.similarity, 3),
                        "problem": m.case.problem,
                        "solution": m.case.solution,
                        "success": m.case.success,
                    }
                    for m in matches
                ]
            }

        elif mem_type == "fact":
            # Search facts by matching subject/predicate/object
            matching = []
            for fact in self.brain.symbolic.facts.values():
                score = 0
                total = 0
                for key, value in query.items():
                    total += 1
                    if hasattr(fact, key) and str(getattr(fact, key)) == str(value):
                        score += 1
                if total > 0 and score > 0:
                    matching.append({
                        "id": fact.id,
                        "subject": fact.subject,
                        "predicate": fact.predicate,
                        "object": fact.object,
                        "confidence": fact.confidence,
                        "match_score": score / total,
                    })
            matching.sort(key=lambda x: x["match_score"], reverse=True)
            return {"facts": matching[:k]}

        else:
            return {"error": f"Unknown recall type: {mem_type}"}

    async def _learn(self, args: dict) -> dict:
        """Store a problem/solution/outcome case (shortcut for remember)."""
        problem = args["problem"]
        solution = args["solution"]
        outcome = args.get("outcome", {})
        success = args.get("success", True)

        case = self.brain.cbr.retain(
            problem=problem,
            solution=solution,
            outcome=outcome,
            success=success,
        )
        self.persistence.save_case({
            "id": case.id,
            "problem": case.problem,
            "solution": case.solution,
            "outcome": case.outcome,
            "success": case.success,
        })

        return {
            "success": True,
            "case_id": case.id,
            "message": "Case stored successfully for future learning",
        }

    async def _forget(self, args: dict) -> dict:
        """Delete a case or fact by ID."""
        mem_type = args["type"]
        item_id = args["id"]

        if mem_type == "case":
            removed_from_brain = self.brain.cbr.remove_case(item_id)
            removed_from_disk = self.persistence.delete_case(item_id)
            success = removed_from_brain or removed_from_disk
            return {
                "success": success,
                "message": f"Case {item_id} {'deleted' if success else 'not found'}",
            }

        elif mem_type == "fact":
            removed_from_brain = self.brain.symbolic.remove_fact(item_id)
            removed_from_disk = self.persistence.delete_fact(item_id)
            success = removed_from_brain or removed_from_disk
            return {
                "success": success,
                "message": f"Fact {item_id} {'deleted' if success else 'not found'}",
            }

        else:
            return {"error": f"Unknown forget type: {mem_type}"}

    # === Utility Tool Implementations ===

    async def _brain_stats(self, args: dict) -> dict:
        """Get brain statistics."""
        return {
            "cases": len(self.brain.cbr.cases),
            "facts": len(self.brain.symbolic.facts),
            "nodes": len(self.brain.kg.nodes),
            "edges": len(self.brain.kg.edges),
            "reasoning_queries": self._reasoning_queries,
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
