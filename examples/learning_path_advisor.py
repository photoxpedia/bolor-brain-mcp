#!/usr/bin/env python3
"""
Learning Path Advisor
=====================

Recommends personalized learning paths using:
- Knowledge graph of skills and prerequisites
- Case-based reasoning from successful learners
- Analogical reasoning for skill transfer

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
    AnalogicalReasoner, Concept,
)


def build_skill_graph(kg: KnowledgeGraph):
    """Build knowledge graph of skills and prerequisites."""

    # Programming fundamentals
    kg.add_node(Node("programming_basics", "Programming Basics", "skill", {"level": "beginner", "domain": "programming"}))
    kg.add_node(Node("python", "Python", "skill", {"level": "beginner", "domain": "programming"}))
    kg.add_node(Node("javascript", "JavaScript", "skill", {"level": "beginner", "domain": "programming"}))
    kg.add_node(Node("data_structures", "Data Structures", "skill", {"level": "intermediate", "domain": "cs"}))
    kg.add_node(Node("algorithms", "Algorithms", "skill", {"level": "intermediate", "domain": "cs"}))

    # Web development
    kg.add_node(Node("html_css", "HTML/CSS", "skill", {"level": "beginner", "domain": "web"}))
    kg.add_node(Node("react", "React", "skill", {"level": "intermediate", "domain": "web"}))
    kg.add_node(Node("nodejs", "Node.js", "skill", {"level": "intermediate", "domain": "web"}))
    kg.add_node(Node("fullstack", "Full Stack Development", "skill", {"level": "advanced", "domain": "web"}))

    # Data science
    kg.add_node(Node("statistics", "Statistics", "skill", {"level": "intermediate", "domain": "math"}))
    kg.add_node(Node("linear_algebra", "Linear Algebra", "skill", {"level": "intermediate", "domain": "math"}))
    kg.add_node(Node("pandas", "Pandas/NumPy", "skill", {"level": "intermediate", "domain": "data"}))
    kg.add_node(Node("ml_basics", "Machine Learning Basics", "skill", {"level": "intermediate", "domain": "ml"}))
    kg.add_node(Node("deep_learning", "Deep Learning", "skill", {"level": "advanced", "domain": "ml"}))
    kg.add_node(Node("nlp", "Natural Language Processing", "skill", {"level": "advanced", "domain": "ml"}))
    kg.add_node(Node("computer_vision", "Computer Vision", "skill", {"level": "advanced", "domain": "ml"}))

    # DevOps
    kg.add_node(Node("linux", "Linux", "skill", {"level": "beginner", "domain": "devops"}))
    kg.add_node(Node("docker", "Docker", "skill", {"level": "intermediate", "domain": "devops"}))
    kg.add_node(Node("kubernetes", "Kubernetes", "skill", {"level": "advanced", "domain": "devops"}))
    kg.add_node(Node("cloud_aws", "AWS", "skill", {"level": "intermediate", "domain": "cloud"}))

    # Prerequisites (directed edges: prerequisite -> skill)
    kg.add_edge(Edge("programming_basics", "python", "prerequisite_for"))
    kg.add_edge(Edge("programming_basics", "javascript", "prerequisite_for"))
    kg.add_edge(Edge("python", "data_structures", "prerequisite_for"))
    kg.add_edge(Edge("data_structures", "algorithms", "prerequisite_for"))

    kg.add_edge(Edge("html_css", "javascript", "complements"))
    kg.add_edge(Edge("javascript", "react", "prerequisite_for"))
    kg.add_edge(Edge("javascript", "nodejs", "prerequisite_for"))
    kg.add_edge(Edge("react", "fullstack", "prerequisite_for"))
    kg.add_edge(Edge("nodejs", "fullstack", "prerequisite_for"))

    kg.add_edge(Edge("python", "pandas", "prerequisite_for"))
    kg.add_edge(Edge("statistics", "ml_basics", "prerequisite_for"))
    kg.add_edge(Edge("linear_algebra", "ml_basics", "prerequisite_for"))
    kg.add_edge(Edge("pandas", "ml_basics", "prerequisite_for"))
    kg.add_edge(Edge("ml_basics", "deep_learning", "prerequisite_for"))
    kg.add_edge(Edge("deep_learning", "nlp", "prerequisite_for"))
    kg.add_edge(Edge("deep_learning", "computer_vision", "prerequisite_for"))

    kg.add_edge(Edge("linux", "docker", "prerequisite_for"))
    kg.add_edge(Edge("docker", "kubernetes", "prerequisite_for"))
    kg.add_edge(Edge("linux", "cloud_aws", "prerequisite_for"))


def add_learning_rules(reasoner: SymbolicReasoner):
    """Add rules for learning recommendations."""

    reasoner.add_rule(Rule(
        name="ml_needs_math",
        conditions=[
            lambda f: any(f[k].predicate == "goal" and "machine_learning" in str(f[k].object).lower() for k in f),
            lambda f: not any(f[k].predicate == "knows" and "statistics" in str(f[k].object).lower() for k in f),
        ],
        conclusion_template={
            "subject": "statistics",
            "predicate": "should_learn_first",
            "object": "required_for_ml",
            "confidence": 0.9
        },
        priority=10
    ))

    reasoner.add_rule(Rule(
        name="web_path",
        conditions=[
            lambda f: any(f[k].predicate == "goal" and "web" in str(f[k].object).lower() for k in f),
            lambda f: any(f[k].predicate == "knows" and "python" in str(f[k].object).lower() for k in f),
        ],
        conclusion_template={
            "subject": "javascript",
            "predicate": "recommended_next",
            "object": "web_development_path",
            "confidence": 0.85
        },
        priority=8
    ))

    reasoner.add_rule(Rule(
        name="devops_foundation",
        conditions=[
            lambda f: any(f[k].predicate == "goal" and "devops" in str(f[k].object).lower() for k in f),
        ],
        conclusion_template={
            "subject": "linux",
            "predicate": "start_with",
            "object": "devops_foundation",
            "confidence": 0.9
        },
        priority=9
    ))


def add_learner_cases(cbr: CaseBasedReasoner):
    """Add successful learner journeys."""

    cbr.store_case(Case(
        id="learner_ml_engineer",
        problem={
            "background": "software_developer",
            "current_skills": ["python", "data_structures"],
            "goal": "machine_learning",
            "time_available": "6_months",
            "learning_style": "project_based"
        },
        solution={
            "path": ["statistics", "linear_algebra", "pandas", "ml_basics", "deep_learning"],
            "duration": "6_months",
            "resources": ["fast.ai", "coursera_ml", "kaggle"]
        },
        outcome={"success": True, "job_transition": True, "time_actual": "7_months"},
        success=True,
        tags=["ml", "career_change"]
    ))

    cbr.store_case(Case(
        id="learner_fullstack",
        problem={
            "background": "designer",
            "current_skills": ["html_css"],
            "goal": "fullstack_developer",
            "time_available": "12_months",
            "learning_style": "structured"
        },
        solution={
            "path": ["javascript", "react", "nodejs", "docker"],
            "duration": "12_months",
            "resources": ["freecodecamp", "udemy", "buildspace"]
        },
        outcome={"success": True, "job_transition": True, "time_actual": "10_months"},
        success=True,
        tags=["web", "career_change"]
    ))

    cbr.store_case(Case(
        id="learner_data_scientist",
        problem={
            "background": "analyst",
            "current_skills": ["statistics", "excel"],
            "goal": "data_science",
            "time_available": "6_months",
            "learning_style": "theory_first"
        },
        solution={
            "path": ["python", "pandas", "ml_basics", "deep_learning"],
            "duration": "6_months",
            "resources": ["datacamp", "kaggle", "coursera"]
        },
        outcome={"success": True, "job_transition": True, "time_actual": "8_months"},
        success=True,
        tags=["data", "analytics"]
    ))

    cbr.store_case(Case(
        id="learner_devops",
        problem={
            "background": "developer",
            "current_skills": ["python", "linux"],
            "goal": "devops_engineer",
            "time_available": "6_months",
            "learning_style": "hands_on"
        },
        solution={
            "path": ["docker", "kubernetes", "cloud_aws"],
            "duration": "6_months",
            "resources": ["acloudguru", "kodekloud", "aws_training"]
        },
        outcome={"success": True, "job_transition": True, "time_actual": "5_months"},
        success=True,
        tags=["devops", "cloud"]
    ))


def recommend_path(brain: HybridReasoner, learner: dict):
    """Generate personalized learning recommendations."""

    print(f"\n{'='*60}")
    print(f"LEARNER: {learner['name']}")
    print('='*60)
    print(f"\nBackground: {learner['background']}")
    print(f"Current skills: {learner['current_skills']}")
    print(f"Goal: {learner['goal']}")
    print(f"Time available: {learner['time_available']}")

    # Add learner facts
    brain.symbolic.add_fact(Fact("learner", "goal", learner['goal']))
    for skill in learner['current_skills']:
        brain.symbolic.add_fact(Fact("learner", "knows", skill))

    # Find prerequisite gaps
    print("\n--- PREREQUISITE ANALYSIS ---")
    goal_skill = learner['goal'].lower().replace(" ", "_")

    # Find what's needed for the goal
    prereqs_needed = []
    for node_id in brain.kg.nodes:
        if brain.kg.has_edge(node_id, goal_skill, "prerequisite_for"):
            if node_id not in [s.lower().replace(" ", "_") for s in learner['current_skills']]:
                prereqs_needed.append(node_id)

    # Also check transitive prerequisites
    incoming = brain.kg.get_neighbors(goal_skill, direction="incoming")
    for prereq in incoming:
        node = brain.kg.get_node(prereq)
        if node and prereq not in [s.lower().replace(" ", "_") for s in learner['current_skills']]:
            if prereq not in prereqs_needed:
                prereqs_needed.append(prereq)

    if prereqs_needed:
        print(f"  Missing prerequisites: {prereqs_needed}")
    else:
        print("  All prerequisites met!")

    # Apply rules
    print("\n--- RULE-BASED RECOMMENDATIONS ---")
    derived = brain.symbolic.forward_chain()
    if derived:
        for fact in derived:
            print(f"  * {fact.subject}: {fact.object} (confidence: {fact.confidence:.0%})")
    else:
        print("  No specific rule recommendations")

    # Find similar learners
    print("\n--- SIMILAR LEARNER JOURNEYS ---")
    problem_features = {
        "background": learner['background'],
        "current_skills": learner['current_skills'],
        "goal": learner['goal'],
        "time_available": learner['time_available']
    }

    matches = brain.cbr.retrieve(problem_features, k=2, min_similarity=0.3)

    if matches:
        for match in matches:
            print(f"\n  Learner: {match.case.id}")
            print(f"  Similarity: {match.similarity:.0%}")
            print(f"  Their path: {' -> '.join(match.case.solution['path'])}")
            print(f"  Resources: {match.case.solution['resources']}")
            print(f"  Outcome: {'Success' if match.case.success else 'Ongoing'}")
            if match.case.outcome.get('time_actual'):
                print(f"  Time taken: {match.case.outcome['time_actual']}")

    # Generate recommended path
    print("\n--- RECOMMENDED LEARNING PATH ---")
    if matches and matches[0].similarity > 0.4:
        best = matches[0]
        print(f"  Based on {best.case.id}'s journey:")
        path = best.case.solution['path']

        # Filter out already known skills
        known_lower = [s.lower().replace(" ", "_") for s in learner['current_skills']]
        remaining = [s for s in path if s.lower() not in known_lower]

        for i, skill in enumerate(remaining, 1):
            node = brain.kg.get_node(skill)
            level = node.properties.get('level', 'unknown') if node else 'unknown'
            print(f"  {i}. {skill.replace('_', ' ').title()} ({level})")

        print(f"\n  Suggested resources: {best.case.solution['resources']}")
    else:
        print("  Building custom path from prerequisites...")
        if prereqs_needed:
            for i, skill in enumerate(prereqs_needed, 1):
                node = brain.kg.get_node(skill)
                level = node.properties.get('level', 'unknown') if node else 'unknown'
                print(f"  {i}. {skill.replace('_', ' ').title()} ({level})")

    brain.symbolic.clear_facts()


def main():
    print("="*60)
    print("LEARNING PATH ADVISOR")
    print("="*60)

    brain = HybridReasoner()

    print("\n[1] Building skill graph...")
    build_skill_graph(brain.kg)
    print(f"    {len(brain.kg.nodes)} skills, {len(brain.kg.edges)} relationships")

    print("\n[2] Loading learning rules...")
    add_learning_rules(brain.symbolic)
    print(f"    {len(brain.symbolic.rules)} rules")

    print("\n[3] Loading learner journeys...")
    add_learner_cases(brain.cbr)
    print(f"    {len(brain.cbr.cases)} successful journeys")

    # Test learners
    learners = [
        {
            "name": "Alex - Developer wanting ML",
            "background": "software_developer",
            "current_skills": ["Python", "Data Structures"],
            "goal": "machine_learning",
            "time_available": "6_months"
        },
        {
            "name": "Sam - Designer going Full Stack",
            "background": "designer",
            "current_skills": ["HTML/CSS"],
            "goal": "fullstack_developer",
            "time_available": "12_months"
        },
        {
            "name": "Jordan - Analyst to Data Scientist",
            "background": "analyst",
            "current_skills": ["Statistics", "Excel"],
            "goal": "data_science",
            "time_available": "6_months"
        },
        {
            "name": "Taylor - Dev to DevOps",
            "background": "developer",
            "current_skills": ["Python", "Linux"],
            "goal": "devops_engineer",
            "time_available": "6_months"
        }
    ]

    for learner in learners:
        recommend_path(brain, learner)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    stats = brain.get_stats()
    print(f"\n  Skills in graph: {stats['component_stats']['kg_nodes']}")
    print(f"  Prerequisite relationships: {stats['component_stats']['kg_edges']}")
    print(f"  Learning rules: {stats['component_stats']['symbolic_rules']}")
    print(f"  Learner journeys: {stats['component_stats']['cbr_cases']}")


if __name__ == "__main__":
    main()
