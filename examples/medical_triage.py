#!/usr/bin/env python3
"""
Medical Triage Assistant
========================

Demonstrates explainable medical reasoning using:
- Knowledge graph of symptoms, conditions, and treatments
- Rule-based inference for triage decisions
- Case-based reasoning from patient history
- Fully traceable reasoning chains

DISCLAIMER: This is a demonstration only. Not for actual medical use.

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


def build_medical_knowledge(kg: KnowledgeGraph):
    """Build knowledge graph of medical concepts."""

    # Symptoms
    kg.add_node(Node("fever", "Fever", "symptom", {"severity": "moderate"}))
    kg.add_node(Node("cough", "Cough", "symptom", {"severity": "mild"}))
    kg.add_node(Node("fatigue", "Fatigue", "symptom", {"severity": "mild"}))
    kg.add_node(Node("headache", "Headache", "symptom", {"severity": "mild"}))
    kg.add_node(Node("chest_pain", "Chest Pain", "symptom", {"severity": "severe"}))
    kg.add_node(Node("shortness_breath", "Shortness of Breath", "symptom", {"severity": "severe"}))
    kg.add_node(Node("sore_throat", "Sore Throat", "symptom", {"severity": "mild"}))
    kg.add_node(Node("body_aches", "Body Aches", "symptom", {"severity": "moderate"}))
    kg.add_node(Node("nausea", "Nausea", "symptom", {"severity": "moderate"}))
    kg.add_node(Node("dizziness", "Dizziness", "symptom", {"severity": "moderate"}))

    # Conditions
    kg.add_node(Node("flu", "Influenza", "condition", {"urgency": "moderate"}))
    kg.add_node(Node("common_cold", "Common Cold", "condition", {"urgency": "low"}))
    kg.add_node(Node("covid", "COVID-19", "condition", {"urgency": "moderate"}))
    kg.add_node(Node("pneumonia", "Pneumonia", "condition", {"urgency": "high"}))
    kg.add_node(Node("migraine", "Migraine", "condition", {"urgency": "moderate"}))
    kg.add_node(Node("cardiac_event", "Cardiac Event", "condition", {"urgency": "emergency"}))
    kg.add_node(Node("anxiety", "Anxiety", "condition", {"urgency": "moderate"}))

    # Triage levels
    kg.add_node(Node("emergency", "Emergency", "triage", {"response_time": "immediate"}))
    kg.add_node(Node("urgent", "Urgent Care", "triage", {"response_time": "hours"}))
    kg.add_node(Node("standard", "Standard Care", "triage", {"response_time": "days"}))
    kg.add_node(Node("self_care", "Self Care", "triage", {"response_time": "monitor"}))

    # Symptom -> Condition relationships
    kg.add_edge(Edge("fever", "flu", "indicates", weight=0.7))
    kg.add_edge(Edge("cough", "flu", "indicates", weight=0.6))
    kg.add_edge(Edge("fatigue", "flu", "indicates", weight=0.5))
    kg.add_edge(Edge("body_aches", "flu", "indicates", weight=0.7))

    kg.add_edge(Edge("cough", "common_cold", "indicates", weight=0.8))
    kg.add_edge(Edge("sore_throat", "common_cold", "indicates", weight=0.7))

    kg.add_edge(Edge("fever", "covid", "indicates", weight=0.6))
    kg.add_edge(Edge("cough", "covid", "indicates", weight=0.7))
    kg.add_edge(Edge("fatigue", "covid", "indicates", weight=0.6))
    kg.add_edge(Edge("shortness_breath", "covid", "indicates", weight=0.8))

    kg.add_edge(Edge("fever", "pneumonia", "indicates", weight=0.7))
    kg.add_edge(Edge("cough", "pneumonia", "indicates", weight=0.8))
    kg.add_edge(Edge("shortness_breath", "pneumonia", "indicates", weight=0.9))
    kg.add_edge(Edge("chest_pain", "pneumonia", "indicates", weight=0.7))

    kg.add_edge(Edge("chest_pain", "cardiac_event", "indicates", weight=0.9))
    kg.add_edge(Edge("shortness_breath", "cardiac_event", "indicates", weight=0.8))
    kg.add_edge(Edge("dizziness", "cardiac_event", "indicates", weight=0.6))

    kg.add_edge(Edge("headache", "migraine", "indicates", weight=0.8))
    kg.add_edge(Edge("nausea", "migraine", "indicates", weight=0.6))

    # Condition -> Triage relationships
    kg.add_edge(Edge("cardiac_event", "emergency", "requires", weight=1.0))
    kg.add_edge(Edge("pneumonia", "urgent", "requires", weight=0.9))
    kg.add_edge(Edge("covid", "urgent", "requires", weight=0.7))
    kg.add_edge(Edge("flu", "standard", "requires", weight=0.7))
    kg.add_edge(Edge("common_cold", "self_care", "requires", weight=0.9))
    kg.add_edge(Edge("migraine", "standard", "requires", weight=0.6))


def add_triage_rules(reasoner: SymbolicReasoner):
    """Add rules for triage decisions."""

    reasoner.add_rule(Rule(
        name="emergency_chest_pain",
        conditions=[
            lambda f: any(f[k].object == "chest_pain" for k in f),
            lambda f: any(f[k].object == "shortness_breath" for k in f),
        ],
        conclusion_template={
            "subject": "triage",
            "predicate": "level",
            "object": "EMERGENCY",
            "confidence": 0.95
        },
        priority=100,
        description="Chest pain + shortness of breath = Emergency"
    ))

    reasoner.add_rule(Rule(
        name="urgent_respiratory",
        conditions=[
            lambda f: any(f[k].object == "fever" for k in f),
            lambda f: any(f[k].object == "shortness_breath" for k in f),
        ],
        conclusion_template={
            "subject": "triage",
            "predicate": "level",
            "object": "URGENT",
            "confidence": 0.85
        },
        priority=90,
        description="Fever + breathing difficulty = Urgent"
    ))

    reasoner.add_rule(Rule(
        name="flu_symptoms",
        conditions=[
            lambda f: any(f[k].object == "fever" for k in f),
            lambda f: any(f[k].object == "cough" for k in f),
            lambda f: any(f[k].object == "body_aches" for k in f),
        ],
        conclusion_template={
            "subject": "likely_condition",
            "predicate": "is",
            "object": "influenza",
            "confidence": 0.75
        },
        priority=50,
        description="Fever + cough + body aches suggests flu"
    ))

    reasoner.add_rule(Rule(
        name="cold_symptoms",
        conditions=[
            lambda f: any(f[k].object == "cough" for k in f),
            lambda f: any(f[k].object == "sore_throat" for k in f),
            lambda f: not any(f[k].object == "fever" for k in f),
        ],
        conclusion_template={
            "subject": "likely_condition",
            "predicate": "is",
            "object": "common_cold",
            "confidence": 0.8
        },
        priority=40,
        description="Cough + sore throat without fever suggests cold"
    ))

    reasoner.add_rule(Rule(
        name="self_care_mild",
        conditions=[
            lambda f: not any(f[k].object == "chest_pain" for k in f),
            lambda f: not any(f[k].object == "shortness_breath" for k in f),
            lambda f: not any(f[k].object == "fever" for k in f),
        ],
        conclusion_template={
            "subject": "triage",
            "predicate": "level",
            "object": "SELF_CARE",
            "confidence": 0.7
        },
        priority=20,
        description="Mild symptoms without red flags = self care"
    ))


def add_patient_cases(cbr: CaseBasedReasoner):
    """Add historical patient cases."""

    cbr.store_case(Case(
        id="patient_001",
        problem={
            "symptoms": ["fever", "cough", "body_aches"],
            "duration": "3_days",
            "age_group": "adult",
            "pre_conditions": []
        },
        solution={
            "diagnosis": "influenza",
            "triage": "standard",
            "treatment": "rest_fluids_antivirals"
        },
        outcome={"recovery": "7_days", "complications": False},
        success=True,
        tags=["flu", "standard"]
    ))

    cbr.store_case(Case(
        id="patient_002",
        problem={
            "symptoms": ["chest_pain", "shortness_breath", "dizziness"],
            "duration": "sudden",
            "age_group": "elderly",
            "pre_conditions": ["hypertension"]
        },
        solution={
            "diagnosis": "cardiac_event",
            "triage": "emergency",
            "treatment": "immediate_er"
        },
        outcome={"recovery": "hospitalized", "complications": True},
        success=True,
        tags=["cardiac", "emergency"]
    ))

    cbr.store_case(Case(
        id="patient_003",
        problem={
            "symptoms": ["fever", "cough", "shortness_breath"],
            "duration": "5_days",
            "age_group": "adult",
            "pre_conditions": ["diabetes"]
        },
        solution={
            "diagnosis": "pneumonia",
            "triage": "urgent",
            "treatment": "antibiotics_monitoring"
        },
        outcome={"recovery": "14_days", "complications": False},
        success=True,
        tags=["respiratory", "urgent"]
    ))

    cbr.store_case(Case(
        id="patient_004",
        problem={
            "symptoms": ["cough", "sore_throat"],
            "duration": "2_days",
            "age_group": "adult",
            "pre_conditions": []
        },
        solution={
            "diagnosis": "common_cold",
            "triage": "self_care",
            "treatment": "rest_fluids"
        },
        outcome={"recovery": "5_days", "complications": False},
        success=True,
        tags=["cold", "self_care"]
    ))


def triage_patient(brain: HybridReasoner, patient: dict):
    """Perform triage assessment with full reasoning trace."""

    print(f"\n{'='*60}")
    print(f"PATIENT ASSESSMENT")
    print('='*60)
    print(f"\nSymptoms: {patient['symptoms']}")
    print(f"Duration: {patient['duration']}")
    print(f"Age group: {patient['age_group']}")
    print(f"Pre-existing conditions: {patient.get('pre_conditions', [])}")

    # Add symptoms as facts
    for symptom in patient['symptoms']:
        brain.symbolic.add_fact(Fact("patient", "has_symptom", symptom))

    # Run rule-based inference
    print("\n--- RULE-BASED ANALYSIS ---")
    derived = brain.symbolic.forward_chain()

    triage_level = None
    likely_conditions = []

    if derived:
        for fact in derived:
            if fact.predicate == "level":
                triage_level = fact.object
                print(f"  TRIAGE: {fact.object} (confidence: {fact.confidence:.0%})")
            elif fact.predicate == "is":
                likely_conditions.append((fact.object, fact.confidence))
                print(f"  Likely: {fact.object} (confidence: {fact.confidence:.0%})")

    # Knowledge graph analysis
    print("\n--- SYMPTOM-CONDITION MAPPING ---")
    condition_scores = {}

    for symptom in patient['symptoms']:
        edges = brain.kg.get_edges(source=symptom, relation="indicates")
        for edge in edges:
            condition = edge.target
            if condition not in condition_scores:
                condition_scores[condition] = 0
            condition_scores[condition] += edge.weight

    if condition_scores:
        sorted_conditions = sorted(condition_scores.items(), key=lambda x: x[1], reverse=True)
        for condition, score in sorted_conditions[:3]:
            node = brain.kg.get_node(condition)
            urgency = node.properties.get('urgency', 'unknown') if node else 'unknown'
            print(f"  {condition}: score={score:.2f} (urgency: {urgency})")

    # Case-based reasoning
    print("\n--- SIMILAR CASES ---")
    problem_features = {
        "symptoms": patient['symptoms'],
        "age_group": patient['age_group'],
        "pre_conditions": patient.get('pre_conditions', [])
    }

    matches = brain.cbr.retrieve(problem_features, k=2, min_similarity=0.3)

    if matches:
        for match in matches:
            print(f"\n  Case: {match.case.id}")
            print(f"  Similarity: {match.similarity:.0%}")
            print(f"  Diagnosis: {match.case.solution['diagnosis']}")
            print(f"  Triage was: {match.case.solution['triage']}")
            print(f"  Treatment: {match.case.solution['treatment']}")
            print(f"  Recovery: {match.case.outcome['recovery']}")

    # Final recommendation
    print("\n--- RECOMMENDATION ---")
    if triage_level == "EMERGENCY":
        print("  *** EMERGENCY - SEEK IMMEDIATE CARE ***")
        print("  Call emergency services or go to ER immediately")
    elif triage_level == "URGENT":
        print("  ** URGENT - See a doctor within hours **")
        print("  Visit urgent care or contact your doctor today")
    elif matches and matches[0].similarity > 0.5:
        best = matches[0]
        print(f"  Based on similar case ({best.similarity:.0%} match):")
        print(f"  Suggested triage: {best.case.solution['triage'].upper()}")
        print(f"  Suggested action: {best.case.solution['treatment']}")
    else:
        print("  Standard care recommended - schedule appointment")

    print("\n  REASONING TRACE:")
    print(f"  - Symptoms analyzed: {len(patient['symptoms'])}")
    print(f"  - Rules triggered: {len(derived) if derived else 0}")
    print(f"  - Conditions considered: {len(condition_scores)}")
    print(f"  - Similar cases found: {len(matches)}")

    brain.symbolic.clear_facts()


def main():
    print("="*60)
    print("MEDICAL TRIAGE ASSISTANT")
    print("="*60)
    print("\nDISCLAIMER: Demonstration only. Not for actual medical use.")

    brain = HybridReasoner()

    print("\n[1] Loading medical knowledge graph...")
    build_medical_knowledge(brain.kg)
    print(f"    {len(brain.kg.nodes)} concepts, {len(brain.kg.edges)} relationships")

    print("\n[2] Loading triage rules...")
    add_triage_rules(brain.symbolic)
    print(f"    {len(brain.symbolic.rules)} rules")

    print("\n[3] Loading patient cases...")
    add_patient_cases(brain.cbr)
    print(f"    {len(brain.cbr.cases)} historical cases")

    # Test patients
    patients = [
        {
            "symptoms": ["chest_pain", "shortness_breath", "dizziness"],
            "duration": "30_minutes",
            "age_group": "elderly",
            "pre_conditions": ["hypertension"]
        },
        {
            "symptoms": ["fever", "cough", "body_aches", "fatigue"],
            "duration": "3_days",
            "age_group": "adult",
            "pre_conditions": []
        },
        {
            "symptoms": ["cough", "sore_throat"],
            "duration": "2_days",
            "age_group": "adult",
            "pre_conditions": []
        },
        {
            "symptoms": ["fever", "cough", "shortness_breath"],
            "duration": "5_days",
            "age_group": "adult",
            "pre_conditions": ["diabetes"]
        }
    ]

    for patient in patients:
        triage_patient(brain, patient)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    stats = brain.get_stats()
    print(f"\n  Medical concepts: {stats['component_stats']['kg_nodes']}")
    print(f"  Triage rules: {stats['component_stats']['symbolic_rules']}")
    print(f"  Patient cases: {stats['component_stats']['cbr_cases']}")


if __name__ == "__main__":
    main()
