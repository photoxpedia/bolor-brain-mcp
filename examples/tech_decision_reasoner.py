#!/usr/bin/env python3
"""
Tech Decision Reasoner - Bolor Brain MCP Example
=================================================

Demonstrates hybrid reasoning for technology decisions using:
- Knowledge Graph: Structured relationships between concepts
- Symbolic Reasoning: Rule-based inference with forward/backward chaining
- Case-Based Reasoning: Learning from historical outcomes
- Hypothesis Generation: Testing potential solutions

This example builds a reasoning system that helps choose ML frameworks
based on your specific context, constraints, and goals.

Author: Bolorerdene Bundgaa
        https://bolor.me

Usage:
    python examples/tech_decision_reasoner.py
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules import (
    HybridReasoner,
    SymbolicReasoner, Fact, Rule, FactType,
    KnowledgeGraph, Node, Edge,
    CaseBasedReasoner, Case,
    HypothesisEngine,
)


def build_tech_knowledge_graph(kg: KnowledgeGraph):
    """
    Build a knowledge graph of ML framework concepts and relationships.
    """
    print("\n[1] Building Knowledge Graph...")

    # === ML Frameworks ===
    kg.add_node(Node("pytorch", "PyTorch", "framework",
                     {"type": "ml", "paradigm": "eager", "company": "meta"}))
    kg.add_node(Node("jax", "JAX", "framework",
                     {"type": "ml", "paradigm": "functional", "company": "google"}))
    kg.add_node(Node("tensorflow", "TensorFlow", "framework",
                     {"type": "ml", "paradigm": "graph", "company": "google"}))

    # === Hardware ===
    kg.add_node(Node("gpu_nvidia", "NVIDIA GPU", "hardware", {"vendor": "nvidia"}))
    kg.add_node(Node("tpu", "Google TPU", "hardware", {"vendor": "google"}))
    kg.add_node(Node("cpu", "CPU", "hardware", {"vendor": "various"}))

    # === Use Cases ===
    kg.add_node(Node("research", "Research/Experimentation", "use_case"))
    kg.add_node(Node("production", "Production Deployment", "use_case"))
    kg.add_node(Node("prototyping", "Rapid Prototyping", "use_case"))
    kg.add_node(Node("scaling", "Large Scale Training", "use_case"))

    # === Characteristics ===
    kg.add_node(Node("debugging", "Easy Debugging", "characteristic"))
    kg.add_node(Node("performance", "High Performance", "characteristic"))
    kg.add_node(Node("ecosystem", "Large Ecosystem", "characteristic"))
    kg.add_node(Node("functional", "Functional Paradigm", "characteristic"))

    # === Relationships ===
    kg.add_edge(Edge("pytorch", "gpu_nvidia", "optimized_for", weight=0.9))
    kg.add_edge(Edge("jax", "tpu", "optimized_for", weight=0.95))
    kg.add_edge(Edge("jax", "gpu_nvidia", "optimized_for", weight=0.8))
    kg.add_edge(Edge("tensorflow", "tpu", "optimized_for", weight=0.9))

    kg.add_edge(Edge("pytorch", "research", "suited_for", weight=0.9))
    kg.add_edge(Edge("pytorch", "prototyping", "suited_for", weight=0.85))
    kg.add_edge(Edge("jax", "research", "suited_for", weight=0.85))
    kg.add_edge(Edge("jax", "scaling", "suited_for", weight=0.95))
    kg.add_edge(Edge("tensorflow", "production", "suited_for", weight=0.85))

    kg.add_edge(Edge("pytorch", "debugging", "provides", weight=0.9))
    kg.add_edge(Edge("pytorch", "ecosystem", "provides", weight=0.9))
    kg.add_edge(Edge("jax", "performance", "provides", weight=0.9))
    kg.add_edge(Edge("jax", "functional", "provides", weight=0.95))

    print(f"    {len(kg.nodes)} nodes, {len(kg.edges)} edges")


def add_reasoning_rules(reasoner: SymbolicReasoner):
    """
    Add inference rules for symbolic reasoning.
    Rules derive new conclusions from existing facts.
    """
    print("\n[2] Adding Reasoning Rules...")

    reasoner.add_rule(Rule(
        name="tpu_suggests_jax",
        conditions=[
            lambda f: any(
                fact.subject == "user" and fact.predicate == "has_hardware" and fact.object == "tpu"
                for fact in f.values()
            )
        ],
        conclusion_template={
            "subject": "jax",
            "predicate": "recommended_because",
            "object": "tpu_optimization",
            "confidence": 0.85
        },
        priority=10,
        description="TPU access suggests JAX for best performance"
    ))

    reasoner.add_rule(Rule(
        name="research_suggests_pytorch",
        conditions=[
            lambda f: any(
                fact.subject == "user" and fact.predicate == "focus" and fact.object == "research"
                for fact in f.values()
            ),
            lambda f: not any(
                fact.subject == "user" and fact.predicate == "has_hardware" and fact.object == "tpu"
                for fact in f.values()
            )
        ],
        conclusion_template={
            "subject": "pytorch",
            "predicate": "recommended_because",
            "object": "research_ecosystem",
            "confidence": 0.8
        },
        priority=5,
        description="Research focus without TPU suggests PyTorch"
    ))

    reasoner.add_rule(Rule(
        name="scaling_suggests_jax",
        conditions=[
            lambda f: any(
                fact.subject == "user" and fact.predicate == "needs" and fact.object == "scaling"
                for fact in f.values()
            )
        ],
        conclusion_template={
            "subject": "jax",
            "predicate": "recommended_because",
            "object": "scaling_capability",
            "confidence": 0.9
        },
        priority=8,
        description="Large scale training needs suggest JAX"
    ))

    reasoner.add_rule(Rule(
        name="debugging_suggests_pytorch",
        conditions=[
            lambda f: any(
                fact.subject == "user" and fact.predicate == "priority" and fact.object == "debugging"
                for fact in f.values()
            )
        ],
        conclusion_template={
            "subject": "pytorch",
            "predicate": "recommended_because",
            "object": "eager_execution_debugging",
            "confidence": 0.85
        },
        priority=7,
        description="Debugging priority suggests PyTorch's eager execution"
    ))

    print(f"    {len(reasoner.rules)} rules added")


def add_historical_cases(cbr: CaseBasedReasoner):
    """
    Add cases from past decisions and outcomes.
    The system learns patterns from historical data.
    """
    print("\n[3] Adding Historical Cases...")

    cbr.store_case(Case(
        id="deepmind_alphafold",
        problem={
            "team_size": "large",
            "hardware": "tpu",
            "focus": "research",
            "scale": "massive",
            "paradigm_preference": "functional"
        },
        solution={"framework": "jax", "approach": "custom_layers"},
        outcome={"success": True, "impact": "breakthrough"},
        success=True,
        tags=["research", "scaling", "tpu"]
    ))

    cbr.store_case(Case(
        id="fastai_course",
        problem={
            "team_size": "small",
            "hardware": "gpu_nvidia",
            "focus": "education",
            "scale": "medium",
            "paradigm_preference": "eager"
        },
        solution={"framework": "pytorch", "approach": "high_level_api"},
        outcome={"success": True, "impact": "widely_adopted"},
        success=True,
        tags=["education", "prototyping", "gpu"]
    ))

    cbr.store_case(Case(
        id="startup_mvp",
        problem={
            "team_size": "small",
            "hardware": "gpu_nvidia",
            "focus": "product",
            "scale": "small",
            "time_pressure": "high"
        },
        solution={"framework": "pytorch", "approach": "pretrained_models"},
        outcome={"success": True, "time_to_market": "fast"},
        success=True,
        tags=["startup", "prototyping", "speed"]
    ))

    cbr.store_case(Case(
        id="failed_tf_migration",
        problem={
            "team_size": "medium",
            "hardware": "gpu_nvidia",
            "focus": "research",
            "existing_codebase": "pytorch",
            "reason": "management_decision"
        },
        solution={"framework": "tensorflow", "approach": "full_rewrite"},
        outcome={"success": False, "reason": "ecosystem_mismatch"},
        success=False,
        tags=["migration", "failure", "lesson"]
    ))

    print(f"    {len(cbr.cases)} cases added")


def run_scenario(brain: HybridReasoner, name: str, facts: list, query: dict):
    """Run a reasoning scenario and display results."""
    print(f"\n{'='*60}")
    print(f"SCENARIO: {name}")
    print('='*60)

    # Add context facts
    for fact in facts:
        brain.symbolic.add_fact(fact)
        print(f"  Context: {fact.subject} {fact.predicate} {fact.object}")

    # Run hybrid reasoning
    result = brain.reason(query)

    print(f"\n  Problem type: {result.problem_type.value}")
    print(f"  Approaches: {[a.value for a in result.approaches_used]}")
    print(f"  Confidence: {result.confidence:.2f}")

    print("\n  Reasoning trace:")
    for step in result.reasoning_trace:
        print(f"    - {step}")

    # Show derived facts
    derived = brain.symbolic.query_facts(predicate="recommended_because")
    if derived:
        print("\n  Derived conclusions:")
        for fact in derived:
            print(f"    * {fact.subject}: {fact.object} (confidence: {fact.confidence})")

    # Clear for next scenario
    brain.symbolic.clear_facts()

    return result


def demonstrate_case_based_reasoning(brain: HybridReasoner):
    """Show case-based reasoning with similar past experiences."""
    print(f"\n{'='*60}")
    print("CASE-BASED REASONING: Finding Similar Experiences")
    print('='*60)

    problem = {
        "team_size": "small",
        "hardware": "gpu_nvidia",
        "time_pressure": "high"
    }

    print(f"\n  Current problem: {problem}")

    matches = brain.cbr.retrieve(problem, k=3)

    print("\n  Similar historical cases:")
    for match in matches:
        status = "SUCCESS" if match.case.success else "FAILURE"
        print(f"\n    Case: {match.case.id}")
        print(f"    Similarity: {match.similarity:.2f}")
        print(f"    Solution: {match.case.solution}")
        print(f"    Outcome: {status}")


def demonstrate_knowledge_graph(brain: HybridReasoner):
    """Show knowledge graph traversal and inference."""
    print(f"\n{'='*60}")
    print("KNOWLEDGE GRAPH: Relationship Discovery")
    print('='*60)

    # Path finding
    print("\n  Finding path: JAX -> Scaling")
    path = brain.kg.find_path("jax", "scaling")
    if path.found:
        print(f"    Path: {' -> '.join(path.path)}")
        print(f"    Weight: {path.total_weight:.2f}")

    # Pattern inference
    print("\n  JAX relationships (inferred):")
    patterns = brain.kg.infer({
        "subject": "jax",
        "predicate": "?relation",
        "object": "?target"
    })
    for p in patterns:
        print(f"    - jax {p.get('?relation')} {p.get('?target')}")

    # Neighbors
    print("\n  Frameworks suited for research:")
    for node_id in brain.kg.nodes:
        if brain.kg.has_edge(node_id, "research", "suited_for"):
            node = brain.kg.get_node(node_id)
            print(f"    - {node.label}")


def demonstrate_learning(brain: HybridReasoner):
    """Show how the system learns from new outcomes."""
    print(f"\n{'='*60}")
    print("LEARNING: Recording New Experience")
    print('='*60)

    print("\n  Recording: Small team tried JAX without experience - struggled")

    new_case = brain.cbr.retain(
        problem={
            "team_size": "small",
            "hardware": "gpu_nvidia",
            "focus": "product",
            "jax_experience": "none"
        },
        solution={"framework": "jax", "approach": "from_scratch"},
        outcome={"success": False, "reason": "learning_curve_too_steep"},
        success=False,
        tags=["lesson", "small_team", "jax"]
    )

    print(f"  Stored as case: {new_case.id}")
    print(f"  Total cases now: {len(brain.cbr.cases)}")

    # Show it affects future queries
    print("\n  Future query for similar situation now includes this warning.")


def main():
    """
    Main entry point - demonstrates the hybrid reasoning system.
    """
    print("="*60)
    print("BOLOR BRAIN: Tech Decision Reasoner")
    print("="*60)
    print("\nHybrid reasoning for ML framework selection using:")
    print("  - Knowledge graphs (structured relationships)")
    print("  - Symbolic rules (logical inference)")
    print("  - Case-based learning (historical outcomes)")
    print("  - Hypothesis generation (testing solutions)")

    # Initialize
    brain = HybridReasoner()

    # Build knowledge base
    build_tech_knowledge_graph(brain.kg)
    add_reasoning_rules(brain.symbolic)
    add_historical_cases(brain.cbr)

    # Scenario 1: Research with TPU
    run_scenario(
        brain,
        "Research project with TPU access",
        [
            Fact("user", "has_hardware", "tpu"),
            Fact("user", "focus", "research"),
        ],
        {"query": "What ML framework should I use?", "type": "diagnosis"}
    )

    # Scenario 2: Startup MVP
    run_scenario(
        brain,
        "Startup needs fast MVP",
        [
            Fact("user", "has_hardware", "gpu_nvidia"),
            Fact("user", "priority", "debugging"),
            Fact("user", "context", "startup"),
        ],
        {"query": "Best framework for rapid development?", "type": "diagnosis"}
    )

    # Additional demonstrations
    demonstrate_case_based_reasoning(brain)
    demonstrate_knowledge_graph(brain)
    demonstrate_learning(brain)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    stats = brain.get_stats()
    print(f"\n  Knowledge Graph: {stats['component_stats']['kg_nodes']} nodes, {stats['component_stats']['kg_edges']} edges")
    print(f"  Reasoning Rules: {stats['component_stats']['symbolic_rules']}")
    print(f"  Historical Cases: {stats['component_stats']['cbr_cases']}")
    print(f"  Problems Solved: {stats['total_problems']}")
    print(f"  Average Confidence: {stats['avg_confidence']:.2f}")


if __name__ == "__main__":
    main()
