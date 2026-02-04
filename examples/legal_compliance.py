#!/usr/bin/env python3
"""
Legal Compliance Checker
========================

Demonstrates rule-based legal reasoning using:
- Knowledge graph of regulations and requirements
- Symbolic reasoning for compliance logic
- Case-based precedents
- Fully traceable audit trail

DISCLAIMER: This is a demonstration only. Not legal advice.

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
)


def build_regulatory_knowledge(kg: KnowledgeGraph):
    """Build knowledge graph of regulations and requirements."""

    # Regulations
    kg.add_node(Node("gdpr", "GDPR", "regulation", {"jurisdiction": "EU", "type": "privacy"}))
    kg.add_node(Node("ccpa", "CCPA", "regulation", {"jurisdiction": "California", "type": "privacy"}))
    kg.add_node(Node("hipaa", "HIPAA", "regulation", {"jurisdiction": "US", "type": "health"}))
    kg.add_node(Node("pci_dss", "PCI-DSS", "regulation", {"jurisdiction": "global", "type": "payment"}))
    kg.add_node(Node("sox", "SOX", "regulation", {"jurisdiction": "US", "type": "financial"}))

    # Data types
    kg.add_node(Node("pii", "Personal Identifiable Information", "data_type"))
    kg.add_node(Node("phi", "Protected Health Information", "data_type"))
    kg.add_node(Node("payment_data", "Payment Card Data", "data_type"))
    kg.add_node(Node("financial_records", "Financial Records", "data_type"))

    # Requirements
    kg.add_node(Node("consent", "User Consent", "requirement"))
    kg.add_node(Node("encryption", "Data Encryption", "requirement"))
    kg.add_node(Node("access_control", "Access Control", "requirement"))
    kg.add_node(Node("audit_logging", "Audit Logging", "requirement"))
    kg.add_node(Node("data_retention", "Data Retention Policy", "requirement"))
    kg.add_node(Node("breach_notification", "Breach Notification", "requirement"))
    kg.add_node(Node("right_to_delete", "Right to Deletion", "requirement"))
    kg.add_node(Node("data_minimization", "Data Minimization", "requirement"))

    # Business contexts
    kg.add_node(Node("healthcare", "Healthcare", "industry"))
    kg.add_node(Node("ecommerce", "E-Commerce", "industry"))
    kg.add_node(Node("fintech", "Financial Technology", "industry"))
    kg.add_node(Node("saas", "SaaS", "industry"))

    # Regulation -> Data type relationships
    kg.add_edge(Edge("gdpr", "pii", "protects", weight=1.0))
    kg.add_edge(Edge("ccpa", "pii", "protects", weight=1.0))
    kg.add_edge(Edge("hipaa", "phi", "protects", weight=1.0))
    kg.add_edge(Edge("pci_dss", "payment_data", "protects", weight=1.0))
    kg.add_edge(Edge("sox", "financial_records", "protects", weight=1.0))

    # Regulation -> Requirement relationships
    kg.add_edge(Edge("gdpr", "consent", "requires", weight=0.95))
    kg.add_edge(Edge("gdpr", "encryption", "requires", weight=0.9))
    kg.add_edge(Edge("gdpr", "right_to_delete", "requires", weight=0.95))
    kg.add_edge(Edge("gdpr", "breach_notification", "requires", weight=0.95))
    kg.add_edge(Edge("gdpr", "data_minimization", "requires", weight=0.9))

    kg.add_edge(Edge("ccpa", "consent", "requires", weight=0.9))
    kg.add_edge(Edge("ccpa", "right_to_delete", "requires", weight=0.95))

    kg.add_edge(Edge("hipaa", "encryption", "requires", weight=0.95))
    kg.add_edge(Edge("hipaa", "access_control", "requires", weight=0.95))
    kg.add_edge(Edge("hipaa", "audit_logging", "requires", weight=0.95))
    kg.add_edge(Edge("hipaa", "breach_notification", "requires", weight=0.9))

    kg.add_edge(Edge("pci_dss", "encryption", "requires", weight=1.0))
    kg.add_edge(Edge("pci_dss", "access_control", "requires", weight=0.95))
    kg.add_edge(Edge("pci_dss", "audit_logging", "requires", weight=0.95))

    kg.add_edge(Edge("sox", "audit_logging", "requires", weight=1.0))
    kg.add_edge(Edge("sox", "access_control", "requires", weight=0.95))
    kg.add_edge(Edge("sox", "data_retention", "requires", weight=0.9))

    # Industry -> Regulation relationships
    kg.add_edge(Edge("healthcare", "hipaa", "subject_to", weight=1.0))
    kg.add_edge(Edge("ecommerce", "pci_dss", "subject_to", weight=0.9))
    kg.add_edge(Edge("fintech", "pci_dss", "subject_to", weight=0.9))
    kg.add_edge(Edge("fintech", "sox", "subject_to", weight=0.8))


def add_compliance_rules(reasoner: SymbolicReasoner):
    """Add rules for compliance checking."""

    reasoner.add_rule(Rule(
        name="eu_users_need_gdpr",
        conditions=[
            lambda f: any(f[k].predicate == "has_users_in" and f[k].object == "EU" for k in f),
        ],
        conclusion_template={
            "subject": "gdpr",
            "predicate": "applies",
            "object": "eu_presence",
            "confidence": 0.95
        },
        priority=10
    ))

    reasoner.add_rule(Rule(
        name="california_users_need_ccpa",
        conditions=[
            lambda f: any(f[k].predicate == "has_users_in" and f[k].object == "California" for k in f),
        ],
        conclusion_template={
            "subject": "ccpa",
            "predicate": "applies",
            "object": "california_presence",
            "confidence": 0.9
        },
        priority=10
    ))

    reasoner.add_rule(Rule(
        name="health_data_needs_hipaa",
        conditions=[
            lambda f: any(f[k].predicate == "processes" and f[k].object == "health_data" for k in f),
            lambda f: any(f[k].predicate == "operates_in" and f[k].object == "US" for k in f),
        ],
        conclusion_template={
            "subject": "hipaa",
            "predicate": "applies",
            "object": "health_data_us",
            "confidence": 0.95
        },
        priority=15
    ))

    reasoner.add_rule(Rule(
        name="payment_processing_needs_pci",
        conditions=[
            lambda f: any(f[k].predicate == "processes" and f[k].object == "payment_cards" for k in f),
        ],
        conclusion_template={
            "subject": "pci_dss",
            "predicate": "applies",
            "object": "payment_processing",
            "confidence": 1.0
        },
        priority=15
    ))

    reasoner.add_rule(Rule(
        name="public_company_needs_sox",
        conditions=[
            lambda f: any(f[k].predicate == "company_type" and f[k].object == "public" for k in f),
            lambda f: any(f[k].predicate == "operates_in" and f[k].object == "US" for k in f),
        ],
        conclusion_template={
            "subject": "sox",
            "predicate": "applies",
            "object": "public_us_company",
            "confidence": 0.95
        },
        priority=12
    ))

    reasoner.add_rule(Rule(
        name="missing_encryption_violation",
        conditions=[
            lambda f: any(f[k].predicate == "applies" for k in f),
            lambda f: any(f[k].predicate == "missing" and f[k].object == "encryption" for k in f),
        ],
        conclusion_template={
            "subject": "compliance",
            "predicate": "violation",
            "object": "missing_encryption",
            "confidence": 0.9
        },
        priority=20
    ))


def add_compliance_cases(cbr: CaseBasedReasoner):
    """Add compliance case precedents."""

    cbr.store_case(Case(
        id="case_startup_saas",
        problem={
            "company_type": "startup",
            "industry": "saas",
            "data_types": ["pii"],
            "user_regions": ["US", "EU"],
            "processes_payments": False
        },
        solution={
            "applicable_regulations": ["gdpr", "ccpa"],
            "required_controls": ["consent", "encryption", "right_to_delete"],
            "priority": "high"
        },
        outcome={"audit_result": "compliant", "time_to_comply": "3_months"},
        success=True,
        tags=["saas", "gdpr", "ccpa"]
    ))

    cbr.store_case(Case(
        id="case_healthcare_app",
        problem={
            "company_type": "startup",
            "industry": "healthcare",
            "data_types": ["phi", "pii"],
            "user_regions": ["US"],
            "processes_payments": True
        },
        solution={
            "applicable_regulations": ["hipaa", "pci_dss"],
            "required_controls": ["encryption", "access_control", "audit_logging", "breach_notification"],
            "priority": "critical"
        },
        outcome={"audit_result": "compliant", "time_to_comply": "6_months"},
        success=True,
        tags=["healthcare", "hipaa", "pci"]
    ))

    cbr.store_case(Case(
        id="case_ecommerce",
        problem={
            "company_type": "private",
            "industry": "ecommerce",
            "data_types": ["pii", "payment_data"],
            "user_regions": ["US", "EU", "California"],
            "processes_payments": True
        },
        solution={
            "applicable_regulations": ["gdpr", "ccpa", "pci_dss"],
            "required_controls": ["consent", "encryption", "access_control", "right_to_delete"],
            "priority": "high"
        },
        outcome={"audit_result": "compliant", "time_to_comply": "4_months"},
        success=True,
        tags=["ecommerce", "gdpr", "pci"]
    ))

    cbr.store_case(Case(
        id="case_fintech_public",
        problem={
            "company_type": "public",
            "industry": "fintech",
            "data_types": ["pii", "financial_records", "payment_data"],
            "user_regions": ["US"],
            "processes_payments": True
        },
        solution={
            "applicable_regulations": ["sox", "pci_dss"],
            "required_controls": ["encryption", "access_control", "audit_logging", "data_retention"],
            "priority": "critical"
        },
        outcome={"audit_result": "compliant", "time_to_comply": "8_months"},
        success=True,
        tags=["fintech", "sox", "pci"]
    ))


def check_compliance(brain: HybridReasoner, company: dict):
    """Check compliance requirements for a company."""

    print(f"\n{'='*60}")
    print(f"COMPLIANCE CHECK: {company['name']}")
    print('='*60)
    print(f"\nIndustry: {company['industry']}")
    print(f"Company type: {company['company_type']}")
    print(f"User regions: {company['user_regions']}")
    print(f"Data processed: {company['data_types']}")
    print(f"Processes payments: {company['processes_payments']}")
    print(f"Current controls: {company.get('current_controls', [])}")

    # Add facts
    brain.symbolic.add_fact(Fact("company", "industry", company['industry']))
    brain.symbolic.add_fact(Fact("company", "company_type", company['company_type']))

    for region in company['user_regions']:
        brain.symbolic.add_fact(Fact("company", "has_users_in", region))
        brain.symbolic.add_fact(Fact("company", "operates_in", region))

    for data_type in company['data_types']:
        brain.symbolic.add_fact(Fact("company", "processes", data_type))

    if company['processes_payments']:
        brain.symbolic.add_fact(Fact("company", "processes", "payment_cards"))

    # Check for missing controls
    for control in company.get('missing_controls', []):
        brain.symbolic.add_fact(Fact("company", "missing", control))

    # Rule-based analysis
    print("\n--- APPLICABLE REGULATIONS (Rule-Based) ---")
    derived = brain.symbolic.forward_chain()

    applicable_regs = []
    violations = []

    if derived:
        for fact in derived:
            if fact.predicate == "applies":
                applicable_regs.append(fact.subject)
                print(f"  {fact.subject.upper()}: {fact.object} (confidence: {fact.confidence:.0%})")
            elif fact.predicate == "violation":
                violations.append(fact.object)
                print(f"  VIOLATION: {fact.object} (confidence: {fact.confidence:.0%})")

    # Knowledge graph analysis
    print("\n--- REQUIRED CONTROLS ---")
    all_requirements = set()

    for reg in applicable_regs:
        edges = brain.kg.get_edges(source=reg, relation="requires")
        for edge in edges:
            all_requirements.add(edge.target)
            print(f"  {reg.upper()} requires: {edge.target} (weight: {edge.weight:.2f})")

    # Gap analysis
    print("\n--- GAP ANALYSIS ---")
    current = set(company.get('current_controls', []))
    missing = all_requirements - current

    if missing:
        print("  Missing controls:")
        for control in missing:
            print(f"    - {control}")
    else:
        print("  All required controls in place!")

    # Similar cases
    print("\n--- SIMILAR COMPANIES ---")
    problem_features = {
        "industry": company['industry'],
        "company_type": company['company_type'],
        "data_types": company['data_types'],
        "processes_payments": company['processes_payments']
    }

    matches = brain.cbr.retrieve(problem_features, k=2, min_similarity=0.3)

    if matches:
        for match in matches:
            print(f"\n  Case: {match.case.id}")
            print(f"  Similarity: {match.similarity:.0%}")
            print(f"  They needed: {match.case.solution['applicable_regulations']}")
            print(f"  Time to comply: {match.case.outcome['time_to_comply']}")

    # Summary
    print("\n--- COMPLIANCE SUMMARY ---")
    print(f"  Applicable regulations: {len(applicable_regs)}")
    print(f"  Required controls: {len(all_requirements)}")
    print(f"  Current controls: {len(current)}")
    print(f"  Missing controls: {len(missing)}")
    print(f"  Violations detected: {len(violations)}")

    if violations:
        print("\n  *** ACTION REQUIRED: Address violations immediately ***")
    elif missing:
        print("\n  ** Implement missing controls before next audit **")
    else:
        print("\n  Compliance posture: GOOD")

    brain.symbolic.clear_facts()


def main():
    print("="*60)
    print("LEGAL COMPLIANCE CHECKER")
    print("="*60)
    print("\nDISCLAIMER: Demonstration only. Not legal advice.")

    brain = HybridReasoner()

    print("\n[1] Loading regulatory knowledge...")
    build_regulatory_knowledge(brain.kg)
    print(f"    {len(brain.kg.nodes)} concepts, {len(brain.kg.edges)} relationships")

    print("\n[2] Loading compliance rules...")
    add_compliance_rules(brain.symbolic)
    print(f"    {len(brain.symbolic.rules)} rules")

    print("\n[3] Loading case precedents...")
    add_compliance_cases(brain.cbr)
    print(f"    {len(brain.cbr.cases)} precedents")

    # Test companies
    companies = [
        {
            "name": "HealthTech Startup",
            "industry": "healthcare",
            "company_type": "startup",
            "user_regions": ["US"],
            "data_types": ["phi", "pii"],
            "processes_payments": True,
            "current_controls": ["encryption", "access_control"],
            "missing_controls": []
        },
        {
            "name": "Global SaaS Platform",
            "industry": "saas",
            "company_type": "private",
            "user_regions": ["US", "EU", "California"],
            "data_types": ["pii"],
            "processes_payments": False,
            "current_controls": ["encryption"],
            "missing_controls": ["consent"]
        },
        {
            "name": "E-Commerce Store",
            "industry": "ecommerce",
            "company_type": "private",
            "user_regions": ["US", "EU"],
            "data_types": ["pii", "payment_data"],
            "processes_payments": True,
            "current_controls": ["encryption", "consent"],
            "missing_controls": []
        },
        {
            "name": "Public FinTech Corp",
            "industry": "fintech",
            "company_type": "public",
            "user_regions": ["US"],
            "data_types": ["pii", "financial_records", "payment_data"],
            "processes_payments": True,
            "current_controls": ["encryption", "access_control", "audit_logging"],
            "missing_controls": ["encryption"]
        }
    ]

    for company in companies:
        check_compliance(brain, company)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    stats = brain.get_stats()
    print(f"\n  Regulatory concepts: {stats['component_stats']['kg_nodes']}")
    print(f"  Compliance rules: {stats['component_stats']['symbolic_rules']}")
    print(f"  Case precedents: {stats['component_stats']['cbr_cases']}")


if __name__ == "__main__":
    main()
