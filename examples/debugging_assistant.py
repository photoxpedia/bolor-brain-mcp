#!/usr/bin/env python3
"""
Debugging Assistant - Root Cause Analysis
==========================================

Diagnoses system issues using:
- Knowledge graph of system dependencies
- Historical incident cases
- Hypothesis generation and testing
- Rule-based inference

Author: Bolorerdene Bundgaa
        https://bolor.me
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules import (
    HybridReasoner, SymbolicReasoner, Fact, Rule,
    KnowledgeGraph, Node, Edge,
    CaseBasedReasoner, Case,
    HypothesisEngine,
)


def build_system_architecture(kg: KnowledgeGraph):
    """Build knowledge graph of system components and dependencies."""

    # Services
    kg.add_node(Node("api_gateway", "API Gateway", "service", {"tier": "frontend"}))
    kg.add_node(Node("auth_service", "Auth Service", "service", {"tier": "middleware"}))
    kg.add_node(Node("user_service", "User Service", "service", {"tier": "backend"}))
    kg.add_node(Node("order_service", "Order Service", "service", {"tier": "backend"}))
    kg.add_node(Node("payment_service", "Payment Service", "service", {"tier": "backend"}))
    kg.add_node(Node("notification_service", "Notification Service", "service", {"tier": "backend"}))

    # Infrastructure
    kg.add_node(Node("postgres_main", "PostgreSQL Main", "database", {"type": "relational"}))
    kg.add_node(Node("redis_cache", "Redis Cache", "cache", {"type": "in-memory"}))
    kg.add_node(Node("rabbitmq", "RabbitMQ", "queue", {"type": "message-broker"}))
    kg.add_node(Node("kubernetes", "Kubernetes", "orchestrator", {"type": "container"}))

    # Failure modes
    kg.add_node(Node("connection_pool", "Connection Pool", "resource"))
    kg.add_node(Node("memory_limit", "Memory Limit", "resource"))
    kg.add_node(Node("cpu_throttle", "CPU Throttle", "resource"))

    # Dependencies
    kg.add_edge(Edge("api_gateway", "auth_service", "calls", weight=1.0))
    kg.add_edge(Edge("api_gateway", "user_service", "calls", weight=0.8))
    kg.add_edge(Edge("api_gateway", "order_service", "calls", weight=0.9))
    kg.add_edge(Edge("auth_service", "redis_cache", "uses", weight=0.95))
    kg.add_edge(Edge("user_service", "postgres_main", "queries", weight=1.0))
    kg.add_edge(Edge("order_service", "postgres_main", "queries", weight=1.0))
    kg.add_edge(Edge("order_service", "payment_service", "calls", weight=0.9))
    kg.add_edge(Edge("order_service", "rabbitmq", "publishes", weight=0.7))
    kg.add_edge(Edge("payment_service", "postgres_main", "queries", weight=1.0))
    kg.add_edge(Edge("notification_service", "rabbitmq", "consumes", weight=0.8))

    # Failure relationships
    kg.add_edge(Edge("postgres_main", "connection_pool", "limited_by", weight=0.9))
    kg.add_edge(Edge("kubernetes", "memory_limit", "enforces", weight=0.95))
    kg.add_edge(Edge("kubernetes", "cpu_throttle", "enforces", weight=0.9))


def add_diagnostic_rules(reasoner: SymbolicReasoner):
    """Add rules for diagnosing issues."""

    reasoner.add_rule(Rule(
        name="db_timeout_indicates_pool",
        conditions=[
            lambda f: any(f[k].predicate == "symptom" and "timeout" in str(f[k].object).lower() for k in f),
            lambda f: any(f[k].predicate == "component" and "database" in str(f[k].object).lower() for k in f),
        ],
        conclusion_template={
            "subject": "connection_pool_exhaustion",
            "predicate": "likely_cause",
            "object": "database_timeout",
            "confidence": 0.85
        },
        priority=10
    ))

    reasoner.add_rule(Rule(
        name="oom_after_deploy",
        conditions=[
            lambda f: any(f[k].predicate == "symptom" and "oom" in str(f[k].object).lower() for k in f),
            lambda f: any(f[k].predicate == "event" and "deploy" in str(f[k].object).lower() for k in f),
        ],
        conclusion_template={
            "subject": "memory_leak",
            "predicate": "likely_cause",
            "object": "oom_after_deployment",
            "confidence": 0.8
        },
        priority=9
    ))

    reasoner.add_rule(Rule(
        name="cascade_failure",
        conditions=[
            lambda f: any(f[k].predicate == "symptom" and "multiple_services" in str(f[k].object).lower() for k in f),
        ],
        conclusion_template={
            "subject": "shared_dependency",
            "predicate": "likely_cause",
            "object": "cascade_failure",
            "confidence": 0.75
        },
        priority=8
    ))

    reasoner.add_rule(Rule(
        name="high_latency_cache_miss",
        conditions=[
            lambda f: any(f[k].predicate == "symptom" and "latency" in str(f[k].object).lower() for k in f),
            lambda f: any(f[k].predicate == "metric" and "cache_miss" in str(f[k].object).lower() for k in f),
        ],
        conclusion_template={
            "subject": "cache_invalidation",
            "predicate": "likely_cause",
            "object": "high_latency",
            "confidence": 0.7
        },
        priority=7
    ))


def add_incident_history(cbr: CaseBasedReasoner):
    """Add historical incidents for case-based learning."""

    cbr.store_case(Case(
        id="INC-2024-001",
        problem={
            "symptom": "api_500_errors",
            "affected_service": "order_service",
            "time_pattern": "peak_hours",
            "recent_change": "none"
        },
        solution={
            "root_cause": "connection_pool_exhausted",
            "fix": "increase_pool_size",
            "config_change": "max_connections: 100 -> 200"
        },
        outcome={"resolved": True, "time_to_resolve": "45min"},
        success=True,
        tags=["database", "connection", "scaling"]
    ))

    cbr.store_case(Case(
        id="INC-2024-002",
        problem={
            "symptom": "oom_kills",
            "affected_service": "user_service",
            "time_pattern": "after_deployment",
            "recent_change": "new_feature_branch"
        },
        solution={
            "root_cause": "memory_leak_in_cache",
            "fix": "fix_cache_eviction",
            "code_change": "add TTL to user cache"
        },
        outcome={"resolved": True, "time_to_resolve": "2hours"},
        success=True,
        tags=["memory", "deployment", "cache"]
    ))

    cbr.store_case(Case(
        id="INC-2024-003",
        problem={
            "symptom": "cascade_failure",
            "affected_service": "multiple",
            "time_pattern": "sudden",
            "recent_change": "database_maintenance"
        },
        solution={
            "root_cause": "postgres_failover_slow",
            "fix": "improve_circuit_breaker",
            "config_change": "circuit_breaker_timeout: 30s -> 5s"
        },
        outcome={"resolved": True, "time_to_resolve": "1hour"},
        success=True,
        tags=["database", "cascade", "circuit-breaker"]
    ))

    cbr.store_case(Case(
        id="INC-2024-004",
        problem={
            "symptom": "high_latency",
            "affected_service": "auth_service",
            "time_pattern": "gradual_increase",
            "recent_change": "redis_version_upgrade"
        },
        solution={
            "root_cause": "redis_serialization_change",
            "fix": "rollback_redis_version",
            "note": "incompatible serialization format"
        },
        outcome={"resolved": True, "time_to_resolve": "30min"},
        success=True,
        tags=["cache", "upgrade", "compatibility"]
    ))


def diagnose_incident(brain: HybridReasoner, incident: dict):
    """Diagnose an incident and show reasoning."""

    print(f"\n{'='*60}")
    print(f"INCIDENT: {incident['title']}")
    print('='*60)
    print(f"\nSymptoms: {incident['symptoms']}")
    print(f"Affected: {incident['affected_services']}")
    print(f"Context: {incident.get('context', 'none')}")

    # Add facts about the incident
    for symptom in incident['symptoms']:
        brain.symbolic.add_fact(Fact("incident", "symptom", symptom))
    for service in incident['affected_services']:
        brain.symbolic.add_fact(Fact("incident", "component", service))
    if incident.get('recent_event'):
        brain.symbolic.add_fact(Fact("incident", "event", incident['recent_event']))
    if incident.get('metrics'):
        for metric in incident['metrics']:
            brain.symbolic.add_fact(Fact("incident", "metric", metric))

    # Run forward chaining to derive conclusions
    derived = brain.symbolic.forward_chain()

    print("\n--- RULE-BASED ANALYSIS ---")
    if derived:
        print("Derived conclusions:")
        for fact in derived:
            print(f"  * {fact.subject} ({fact.predicate}: {fact.object}) - confidence: {fact.confidence}")
    else:
        print("  No direct rule matches")

    # Find similar past incidents
    print("\n--- SIMILAR PAST INCIDENTS ---")
    problem_features = {
        "symptom": incident['symptoms'][0] if incident['symptoms'] else "",
        "affected_service": incident['affected_services'][0] if incident['affected_services'] else "",
        "recent_change": incident.get('recent_event', 'none')
    }

    matches = brain.cbr.retrieve(problem_features, k=3, min_similarity=0.2)

    if matches:
        for match in matches:
            print(f"\n  Case: {match.case.id}")
            print(f"  Similarity: {match.similarity:.0%}")
            print(f"  Root cause was: {match.case.solution.get('root_cause', 'unknown')}")
            print(f"  Fix applied: {match.case.solution.get('fix', 'unknown')}")
    else:
        print("  No similar incidents found")

    # Trace dependency paths
    print("\n--- DEPENDENCY ANALYSIS ---")
    if incident['affected_services']:
        service = incident['affected_services'][0]
        service_id = service.lower().replace(" ", "_")

        # Find what this service depends on
        deps = brain.kg.get_neighbors(service_id, direction="outgoing")
        if deps:
            print(f"  {service} depends on: {deps}")

            # Check paths to infrastructure
            for infra in ["postgres_main", "redis_cache", "rabbitmq"]:
                path = brain.kg.find_path(service_id, infra)
                if path.found:
                    print(f"  Path to {infra}: {' -> '.join(path.path)}")

    # Generate hypothesis
    print("\n--- HYPOTHESIS ---")
    if matches and matches[0].similarity > 0.5:
        best = matches[0]
        print(f"  Based on {best.case.id} ({best.similarity:.0%} similar):")
        print(f"  Likely root cause: {best.case.solution.get('root_cause')}")
        print(f"  Suggested action: {best.case.solution.get('fix')}")
        if best.case.solution.get('config_change'):
            print(f"  Config change: {best.case.solution.get('config_change')}")
    elif derived:
        top = derived[0]
        print(f"  Rule-based hypothesis: {top.subject}")
        print(f"  Confidence: {top.confidence:.0%}")
    else:
        print("  Insufficient data for hypothesis")

    # Clear for next incident
    brain.symbolic.clear_facts()


def main():
    print("="*60)
    print("DEBUGGING ASSISTANT - Root Cause Analysis")
    print("="*60)

    brain = HybridReasoner()

    print("\n[1] Loading system architecture...")
    build_system_architecture(brain.kg)
    print(f"    {len(brain.kg.nodes)} components, {len(brain.kg.edges)} dependencies")

    print("\n[2] Loading diagnostic rules...")
    add_diagnostic_rules(brain.symbolic)
    print(f"    {len(brain.symbolic.rules)} rules")

    print("\n[3] Loading incident history...")
    add_incident_history(brain.cbr)
    print(f"    {len(brain.cbr.cases)} past incidents")

    # Test incidents
    incidents = [
        {
            "title": "Order API returning 500 during peak hours",
            "symptoms": ["api_500_errors", "database_timeout"],
            "affected_services": ["order_service"],
            "context": "Black Friday traffic spike"
        },
        {
            "title": "User service OOM killed after deployment",
            "symptoms": ["oom_kills", "service_restart"],
            "affected_services": ["user_service"],
            "recent_event": "deploy_new_feature",
            "context": "Deployed user avatar caching feature"
        },
        {
            "title": "Multiple services timing out",
            "symptoms": ["multiple_services_down", "cascade_failure"],
            "affected_services": ["order_service", "payment_service", "user_service"],
            "context": "Started during database maintenance window"
        },
        {
            "title": "Auth service high latency",
            "symptoms": ["high_latency", "slow_login"],
            "affected_services": ["auth_service"],
            "metrics": ["cache_miss_rate_high"],
            "context": "After Redis cluster upgrade"
        }
    ]

    for incident in incidents:
        diagnose_incident(brain, incident)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    stats = brain.get_stats()
    print(f"\n  System components: {stats['component_stats']['kg_nodes']}")
    print(f"  Diagnostic rules: {stats['component_stats']['symbolic_rules']}")
    print(f"  Historical incidents: {stats['component_stats']['cbr_cases']}")


if __name__ == "__main__":
    main()
