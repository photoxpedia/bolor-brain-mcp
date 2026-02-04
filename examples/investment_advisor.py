#!/usr/bin/env python3
"""
Investment Strategy Advisor
===========================

Personalized investment reasoning using:
- Knowledge graph of investment instruments and relationships
- Rule-based strategy selection
- Case-based learning from historical portfolios
- Risk profiling with traceable logic

DISCLAIMER: This is a demonstration only. Not financial advice.

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


def build_investment_knowledge(kg: KnowledgeGraph):
    """Build knowledge graph of investment concepts."""

    # Asset classes
    kg.add_node(Node("stocks", "Stocks", "asset_class", {"risk": "high", "liquidity": "high"}))
    kg.add_node(Node("bonds", "Bonds", "asset_class", {"risk": "low", "liquidity": "medium"}))
    kg.add_node(Node("real_estate", "Real Estate", "asset_class", {"risk": "medium", "liquidity": "low"}))
    kg.add_node(Node("commodities", "Commodities", "asset_class", {"risk": "high", "liquidity": "medium"}))
    kg.add_node(Node("crypto", "Cryptocurrency", "asset_class", {"risk": "very_high", "liquidity": "high"}))
    kg.add_node(Node("cash", "Cash/Money Market", "asset_class", {"risk": "very_low", "liquidity": "very_high"}))

    # Investment vehicles
    kg.add_node(Node("index_funds", "Index Funds", "vehicle", {"cost": "low", "diversification": "high"}))
    kg.add_node(Node("etfs", "ETFs", "vehicle", {"cost": "low", "diversification": "high"}))
    kg.add_node(Node("mutual_funds", "Mutual Funds", "vehicle", {"cost": "medium", "diversification": "high"}))
    kg.add_node(Node("individual_stocks", "Individual Stocks", "vehicle", {"cost": "low", "diversification": "low"}))
    kg.add_node(Node("reits", "REITs", "vehicle", {"cost": "low", "diversification": "medium"}))
    kg.add_node(Node("treasury_bonds", "Treasury Bonds", "vehicle", {"cost": "very_low", "diversification": "low"}))

    # Strategies
    kg.add_node(Node("growth", "Growth Strategy", "strategy", {"horizon": "long", "risk": "high"}))
    kg.add_node(Node("value", "Value Strategy", "strategy", {"horizon": "long", "risk": "medium"}))
    kg.add_node(Node("income", "Income Strategy", "strategy", {"horizon": "any", "risk": "low"}))
    kg.add_node(Node("balanced", "Balanced Strategy", "strategy", {"horizon": "medium", "risk": "medium"}))
    kg.add_node(Node("aggressive", "Aggressive Growth", "strategy", {"horizon": "long", "risk": "very_high"}))
    kg.add_node(Node("conservative", "Conservative", "strategy", {"horizon": "short", "risk": "low"}))

    # Risk profiles
    kg.add_node(Node("risk_averse", "Risk Averse", "risk_profile"))
    kg.add_node(Node("moderate", "Moderate Risk", "risk_profile"))
    kg.add_node(Node("risk_tolerant", "Risk Tolerant", "risk_profile"))
    kg.add_node(Node("aggressive_investor", "Aggressive Investor", "risk_profile"))

    # Goals
    kg.add_node(Node("retirement", "Retirement", "goal", {"horizon": "long"}))
    kg.add_node(Node("emergency_fund", "Emergency Fund", "goal", {"horizon": "short"}))
    kg.add_node(Node("house_down_payment", "House Down Payment", "goal", {"horizon": "medium"}))
    kg.add_node(Node("wealth_building", "Wealth Building", "goal", {"horizon": "long"}))
    kg.add_node(Node("passive_income", "Passive Income", "goal", {"horizon": "medium"}))

    # Asset class -> Strategy relationships
    kg.add_edge(Edge("stocks", "growth", "suited_for", weight=0.9))
    kg.add_edge(Edge("stocks", "aggressive", "suited_for", weight=0.85))
    kg.add_edge(Edge("bonds", "income", "suited_for", weight=0.9))
    kg.add_edge(Edge("bonds", "conservative", "suited_for", weight=0.85))
    kg.add_edge(Edge("real_estate", "income", "suited_for", weight=0.8))
    kg.add_edge(Edge("crypto", "aggressive", "suited_for", weight=0.7))

    # Strategy -> Risk profile relationships
    kg.add_edge(Edge("conservative", "risk_averse", "matches", weight=0.95))
    kg.add_edge(Edge("balanced", "moderate", "matches", weight=0.9))
    kg.add_edge(Edge("growth", "risk_tolerant", "matches", weight=0.85))
    kg.add_edge(Edge("aggressive", "aggressive_investor", "matches", weight=0.9))

    # Goal -> Strategy relationships
    kg.add_edge(Edge("retirement", "growth", "suggests", weight=0.8))
    kg.add_edge(Edge("retirement", "balanced", "suggests", weight=0.85))
    kg.add_edge(Edge("emergency_fund", "conservative", "suggests", weight=0.95))
    kg.add_edge(Edge("house_down_payment", "balanced", "suggests", weight=0.8))
    kg.add_edge(Edge("wealth_building", "growth", "suggests", weight=0.9))
    kg.add_edge(Edge("passive_income", "income", "suggests", weight=0.9))

    # Vehicle -> Asset class relationships
    kg.add_edge(Edge("index_funds", "stocks", "provides_exposure", weight=0.9))
    kg.add_edge(Edge("etfs", "stocks", "provides_exposure", weight=0.9))
    kg.add_edge(Edge("reits", "real_estate", "provides_exposure", weight=0.85))
    kg.add_edge(Edge("treasury_bonds", "bonds", "provides_exposure", weight=0.95))


def add_investment_rules(reasoner: SymbolicReasoner):
    """Add rules for investment recommendations."""

    reasoner.add_rule(Rule(
        name="young_long_horizon",
        conditions=[
            lambda f: any(f[k].predicate == "age_group" and f[k].object == "young" for k in f),
            lambda f: any(f[k].predicate == "horizon" and f[k].object == "long" for k in f),
        ],
        conclusion_template={
            "subject": "allocation",
            "predicate": "recommend",
            "object": "high_stock_allocation",
            "confidence": 0.85
        },
        priority=10
    ))

    reasoner.add_rule(Rule(
        name="near_retirement",
        conditions=[
            lambda f: any(f[k].predicate == "age_group" and f[k].object == "near_retirement" for k in f),
        ],
        conclusion_template={
            "subject": "allocation",
            "predicate": "recommend",
            "object": "shift_to_bonds",
            "confidence": 0.9
        },
        priority=15
    ))

    reasoner.add_rule(Rule(
        name="emergency_fund_first",
        conditions=[
            lambda f: any(f[k].predicate == "has_emergency_fund" and f[k].object == "no" for k in f),
        ],
        conclusion_template={
            "subject": "priority",
            "predicate": "recommend",
            "object": "build_emergency_fund_first",
            "confidence": 0.95
        },
        priority=20
    ))

    reasoner.add_rule(Rule(
        name="high_debt_caution",
        conditions=[
            lambda f: any(f[k].predicate == "debt_level" and f[k].object == "high" for k in f),
        ],
        conclusion_template={
            "subject": "priority",
            "predicate": "recommend",
            "object": "pay_down_debt_first",
            "confidence": 0.9
        },
        priority=18
    ))

    reasoner.add_rule(Rule(
        name="diversification_rule",
        conditions=[
            lambda f: any(f[k].predicate == "current_allocation" and "single" in str(f[k].object) for k in f),
        ],
        conclusion_template={
            "subject": "action",
            "predicate": "recommend",
            "object": "diversify_holdings",
            "confidence": 0.85
        },
        priority=12
    ))

    reasoner.add_rule(Rule(
        name="tax_advantaged_first",
        conditions=[
            lambda f: any(f[k].predicate == "tax_advantaged_maxed" and f[k].object == "no" for k in f),
        ],
        conclusion_template={
            "subject": "action",
            "predicate": "recommend",
            "object": "max_401k_ira_first",
            "confidence": 0.9
        },
        priority=16
    ))


def add_portfolio_cases(cbr: CaseBasedReasoner):
    """Add successful portfolio cases."""

    cbr.store_case(Case(
        id="young_professional",
        problem={
            "age_group": "young",
            "income_level": "medium",
            "risk_tolerance": "high",
            "goal": "retirement",
            "horizon": "30_years",
            "current_savings": "low"
        },
        solution={
            "strategy": "aggressive_growth",
            "allocation": {"stocks": 90, "bonds": 10},
            "vehicles": ["index_funds", "etfs"],
            "monthly_contribution": "15%_of_income"
        },
        outcome={"10_year_return": "12%_annualized", "on_track": True},
        success=True,
        tags=["young", "growth", "retirement"]
    ))

    cbr.store_case(Case(
        id="mid_career_balanced",
        problem={
            "age_group": "middle",
            "income_level": "high",
            "risk_tolerance": "moderate",
            "goal": "retirement",
            "horizon": "20_years",
            "current_savings": "medium"
        },
        solution={
            "strategy": "balanced",
            "allocation": {"stocks": 70, "bonds": 20, "real_estate": 10},
            "vehicles": ["index_funds", "reits", "treasury_bonds"],
            "monthly_contribution": "20%_of_income"
        },
        outcome={"10_year_return": "9%_annualized", "on_track": True},
        success=True,
        tags=["balanced", "diversified", "retirement"]
    ))

    cbr.store_case(Case(
        id="near_retirement_conservative",
        problem={
            "age_group": "near_retirement",
            "income_level": "high",
            "risk_tolerance": "low",
            "goal": "retirement",
            "horizon": "5_years",
            "current_savings": "high"
        },
        solution={
            "strategy": "conservative",
            "allocation": {"stocks": 30, "bonds": 60, "cash": 10},
            "vehicles": ["treasury_bonds", "dividend_etfs"],
            "focus": "capital_preservation"
        },
        outcome={"5_year_return": "5%_annualized", "on_track": True},
        success=True,
        tags=["conservative", "preservation", "retirement"]
    ))

    cbr.store_case(Case(
        id="income_focused",
        problem={
            "age_group": "retired",
            "income_level": "fixed",
            "risk_tolerance": "low",
            "goal": "passive_income",
            "horizon": "ongoing",
            "current_savings": "high"
        },
        solution={
            "strategy": "income",
            "allocation": {"bonds": 50, "dividend_stocks": 30, "reits": 20},
            "vehicles": ["dividend_etfs", "reits", "treasury_bonds"],
            "withdrawal_rate": "4%"
        },
        outcome={"annual_income": "4%_of_portfolio", "sustainable": True},
        success=True,
        tags=["income", "retirement", "dividends"]
    ))

    cbr.store_case(Case(
        id="house_saver",
        problem={
            "age_group": "young",
            "income_level": "medium",
            "risk_tolerance": "moderate",
            "goal": "house_down_payment",
            "horizon": "5_years",
            "current_savings": "low"
        },
        solution={
            "strategy": "balanced_short",
            "allocation": {"stocks": 40, "bonds": 40, "cash": 20},
            "vehicles": ["balanced_funds", "high_yield_savings"],
            "monthly_contribution": "25%_of_income"
        },
        outcome={"goal_reached": True, "time_to_goal": "4.5_years"},
        success=True,
        tags=["short_term", "house", "saving"]
    ))


def advise_investor(brain: HybridReasoner, investor: dict):
    """Generate personalized investment advice."""

    print(f"\n{'='*60}")
    print(f"INVESTOR PROFILE: {investor['name']}")
    print('='*60)
    print(f"\nAge group: {investor['age_group']}")
    print(f"Income level: {investor['income_level']}")
    print(f"Risk tolerance: {investor['risk_tolerance']}")
    print(f"Primary goal: {investor['goal']}")
    print(f"Time horizon: {investor['horizon']}")
    print(f"Has emergency fund: {investor.get('has_emergency_fund', 'unknown')}")
    print(f"Debt level: {investor.get('debt_level', 'unknown')}")

    # Add facts
    brain.symbolic.add_fact(Fact("investor", "age_group", investor['age_group']))
    brain.symbolic.add_fact(Fact("investor", "risk_tolerance", investor['risk_tolerance']))
    brain.symbolic.add_fact(Fact("investor", "goal", investor['goal']))
    brain.symbolic.add_fact(Fact("investor", "horizon", investor['horizon']))

    if investor.get('has_emergency_fund'):
        brain.symbolic.add_fact(Fact("investor", "has_emergency_fund", investor['has_emergency_fund']))
    if investor.get('debt_level'):
        brain.symbolic.add_fact(Fact("investor", "debt_level", investor['debt_level']))
    if investor.get('tax_advantaged_maxed'):
        brain.symbolic.add_fact(Fact("investor", "tax_advantaged_maxed", investor['tax_advantaged_maxed']))
    if investor.get('current_allocation'):
        brain.symbolic.add_fact(Fact("investor", "current_allocation", investor['current_allocation']))

    # Rule-based analysis
    print("\n--- RULE-BASED RECOMMENDATIONS ---")
    derived = brain.symbolic.forward_chain()

    priorities = []
    allocations = []
    actions = []

    if derived:
        for fact in derived:
            if fact.subject == "priority":
                priorities.append(fact.object)
                print(f"  PRIORITY: {fact.object} (confidence: {fact.confidence:.0%})")
            elif fact.subject == "allocation":
                allocations.append(fact.object)
                print(f"  Allocation: {fact.object} (confidence: {fact.confidence:.0%})")
            elif fact.subject == "action":
                actions.append(fact.object)
                print(f"  Action: {fact.object} (confidence: {fact.confidence:.0%})")

    # Knowledge graph: Goal -> Strategy mapping
    print("\n--- STRATEGY ANALYSIS ---")
    goal_id = investor['goal'].lower().replace(" ", "_")
    strategies = brain.kg.get_edges(source=goal_id, relation="suggests")

    if strategies:
        for edge in strategies:
            strategy = brain.kg.get_node(edge.target)
            if strategy:
                print(f"  {investor['goal']} suggests: {strategy.label} (weight: {edge.weight:.2f})")
                print(f"    - Risk level: {strategy.properties.get('risk', 'unknown')}")
                print(f"    - Time horizon: {strategy.properties.get('horizon', 'unknown')}")

    # Similar investor cases
    print("\n--- SIMILAR INVESTOR PROFILES ---")
    problem_features = {
        "age_group": investor['age_group'],
        "risk_tolerance": investor['risk_tolerance'],
        "goal": investor['goal'],
        "income_level": investor['income_level']
    }

    matches = brain.cbr.retrieve(problem_features, k=2, min_similarity=0.4)

    recommended_allocation = None
    recommended_vehicles = None

    if matches:
        for match in matches:
            print(f"\n  Profile: {match.case.id}")
            print(f"  Similarity: {match.similarity:.0%}")
            print(f"  Their strategy: {match.case.solution['strategy']}")
            print(f"  Allocation: {match.case.solution['allocation']}")
            print(f"  Vehicles: {match.case.solution['vehicles']}")
            print(f"  Outcome: {match.case.outcome}")

            if match.similarity > 0.5 and not recommended_allocation:
                recommended_allocation = match.case.solution['allocation']
                recommended_vehicles = match.case.solution['vehicles']

    # Final recommendation
    print("\n--- PERSONALIZED RECOMMENDATION ---")

    if priorities:
        print(f"\n  First priorities:")
        for p in priorities:
            print(f"    1. {p.replace('_', ' ').title()}")

    if recommended_allocation:
        print(f"\n  Suggested allocation:")
        for asset, pct in recommended_allocation.items():
            print(f"    - {asset.title()}: {pct}%")

        print(f"\n  Suggested vehicles:")
        for v in recommended_vehicles:
            print(f"    - {v.replace('_', ' ').title()}")
    else:
        print("\n  General guidance based on profile:")
        if investor['risk_tolerance'] == 'high' and investor['horizon'] == 'long':
            print("    - Consider 80-90% stocks, 10-20% bonds")
            print("    - Focus on low-cost index funds")
        elif investor['risk_tolerance'] == 'low':
            print("    - Consider 30-40% stocks, 50-60% bonds, 10% cash")
            print("    - Focus on capital preservation")

    print("\n  REASONING TRACE:")
    print(f"  - Rules triggered: {len(derived) if derived else 0}")
    print(f"  - Strategies considered: {len(strategies) if strategies else 0}")
    print(f"  - Similar profiles found: {len(matches)}")

    brain.symbolic.clear_facts()


def main():
    print("="*60)
    print("INVESTMENT STRATEGY ADVISOR")
    print("="*60)
    print("\nDISCLAIMER: Demonstration only. Not financial advice.")

    brain = HybridReasoner()

    print("\n[1] Loading investment knowledge...")
    build_investment_knowledge(brain.kg)
    print(f"    {len(brain.kg.nodes)} concepts, {len(brain.kg.edges)} relationships")

    print("\n[2] Loading investment rules...")
    add_investment_rules(brain.symbolic)
    print(f"    {len(brain.symbolic.rules)} rules")

    print("\n[3] Loading portfolio cases...")
    add_portfolio_cases(brain.cbr)
    print(f"    {len(brain.cbr.cases)} successful portfolios")

    # Test investors
    investors = [
        {
            "name": "Alex - Young Professional",
            "age_group": "young",
            "income_level": "medium",
            "risk_tolerance": "high",
            "goal": "retirement",
            "horizon": "long",
            "has_emergency_fund": "no",
            "debt_level": "low",
            "tax_advantaged_maxed": "no"
        },
        {
            "name": "Sam - Mid-Career Saver",
            "age_group": "middle",
            "income_level": "high",
            "risk_tolerance": "moderate",
            "goal": "retirement",
            "horizon": "long",
            "has_emergency_fund": "yes",
            "debt_level": "low",
            "tax_advantaged_maxed": "yes"
        },
        {
            "name": "Jordan - Near Retirement",
            "age_group": "near_retirement",
            "income_level": "high",
            "risk_tolerance": "low",
            "goal": "retirement",
            "horizon": "short",
            "has_emergency_fund": "yes",
            "debt_level": "none"
        },
        {
            "name": "Taylor - House Saver",
            "age_group": "young",
            "income_level": "medium",
            "risk_tolerance": "moderate",
            "goal": "house_down_payment",
            "horizon": "medium",
            "has_emergency_fund": "yes",
            "debt_level": "medium"
        }
    ]

    for investor in investors:
        advise_investor(brain, investor)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    stats = brain.get_stats()
    print(f"\n  Investment concepts: {stats['component_stats']['kg_nodes']}")
    print(f"  Advisory rules: {stats['component_stats']['symbolic_rules']}")
    print(f"  Portfolio cases: {stats['component_stats']['cbr_cases']}")


if __name__ == "__main__":
    main()
