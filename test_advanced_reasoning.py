#!/usr/bin/env python3
"""
Comprehensive test suite for Advanced Reasoning Engine
Tests all reasoning strategies and chain-of-thought capabilities

Author: Bolorerdene Bundgaa
Email: bolor@ariunbolor.org  
Website: https://bolor.me
License: MIT
"""

import asyncio
import json
import sys
import os
import time

# Add the current directory to path so we can import our brain
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain_mcp_server import SimpleBrain

async def test_reasoning_strategies():
    """Test all 6 reasoning strategies"""
    
    print("🧠 Testing Advanced Reasoning Engine - All Strategies")
    print("=" * 60)
    
    # Initialize brain
    brain = SimpleBrain("./test_reasoning_storage")
    
    # Store some sample knowledge for reasoning context
    print("📚 Storing sample knowledge for reasoning context...")
    
    sample_knowledge = [
        ("All programming languages have syntax rules", "semantic", {"domain": "programming"}),
        ("When I debug code, I first check the console for errors", "procedural", {"skill": "debugging"}),
        ("I successfully fixed a React component yesterday by checking props", "episodic", {"outcome": "success"}),
        ("Similar problems often have similar solutions", "semantic", {"pattern": "analogy"}),
        ("Code errors usually happen because of syntax or logic mistakes", "semantic", {"causality": "programming"})
    ]
    
    for content, mem_type, metadata in sample_knowledge:
        brain.store_memory(content, mem_type, metadata)
    
    print(f"✅ Stored {len(sample_knowledge)} knowledge pieces for context\n")
    
    # Test cases for different reasoning strategies
    test_cases = [
        {
            "name": "Deductive Reasoning",
            "problem": "If all programming languages have syntax rules, and Python is a programming language, what can we conclude about Python?",
            "expected_strategy": "deductive",
            "context": {"domain": "logic"}
        },
        {
            "name": "Inductive Reasoning", 
            "problem": "I've seen several React debugging cases where checking props solved the issue. What pattern does this suggest?",
            "expected_strategy": "inductive",
            "context": {"domain": "pattern_recognition"}
        },
        {
            "name": "Abductive Reasoning",
            "problem": "Why is my JavaScript code throwing an undefined error?",
            "expected_strategy": "abductive", 
            "context": {"domain": "problem_diagnosis"}
        },
        {
            "name": "Analogical Reasoning",
            "problem": "How is debugging code similar to solving a mystery?",
            "expected_strategy": "analogical",
            "context": {"domain": "comparison"}
        },
        {
            "name": "Causal Reasoning",
            "problem": "What happens when you forget to close a bracket in your code?",
            "expected_strategy": "causal",
            "context": {"domain": "cause_effect"}
        },
        {
            "name": "Meta Reasoning",
            "problem": "What reasoning strategy should I use to approach a complex debugging problem?",
            "expected_strategy": "meta",
            "context": {"domain": "reasoning_about_reasoning"}
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}/6: {test_case['name']}")
        print(f"Problem: {test_case['problem']}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Solve the problem using advanced reasoning
            reasoning_chain = await brain.advanced_reasoning.solve_complex_problem(
                problem=test_case['problem'],
                context=test_case['context']
            )
            
            reasoning_time = time.time() - start_time
            
            # Analyze results
            strategy_correct = reasoning_chain.strategy == test_case['expected_strategy']
            
            print(f"✅ Strategy Used: {reasoning_chain.strategy}")
            print(f"🎯 Expected: {test_case['expected_strategy']} | {'✓ MATCH' if strategy_correct else '✗ DIFFERENT'}")
            print(f"📊 Confidence: {reasoning_chain.confidence_score:.3f}")
            print(f"⏱️  Time: {reasoning_time:.3f}s")
            print(f"🔗 Steps: {len(reasoning_chain.steps)}")
            print(f"💭 Final Conclusion: {reasoning_chain.final_conclusion}")
            
            # Show reasoning steps
            print(f"\n🧩 Reasoning Steps:")
            for j, step in enumerate(reasoning_chain.steps, 1):
                print(f"  {j}. [{step.step_type.upper()}] {step.premise}")
                print(f"     Reasoning: {step.reasoning}")
                print(f"     Conclusion: {step.conclusion}")
                print(f"     Confidence: {step.confidence}")
                print()
            
            results.append({
                "test_name": test_case['name'],
                "strategy_used": reasoning_chain.strategy,
                "expected_strategy": test_case['expected_strategy'], 
                "strategy_correct": strategy_correct,
                "confidence": reasoning_chain.confidence_score,
                "reasoning_time": reasoning_time,
                "steps_count": len(reasoning_chain.steps),
                "success": True
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "test_name": test_case['name'],
                "success": False,
                "error": str(e)
            })
        
        print("\n" + "=" * 60 + "\n")
    
    return results

async def test_reasoning_performance():
    """Test reasoning engine performance and statistics"""
    
    print("📊 Testing Reasoning Engine Performance")
    print("=" * 50)
    
    brain = SimpleBrain("./test_reasoning_storage")
    
    # Performance test problems
    performance_problems = [
        "How do I optimize database queries?",
        "What causes memory leaks in JavaScript?",
        "Why do some algorithms run faster than others?",
        "How can I improve code readability?",
        "What makes a good API design?"
    ]
    
    print(f"🚀 Running {len(performance_problems)} reasoning tasks...")
    
    total_time = 0
    successful_reasonings = 0
    
    for i, problem in enumerate(performance_problems, 1):
        print(f"  {i}. {problem[:50]}...")
        
        start_time = time.time()
        try:
            chain = await brain.advanced_reasoning.solve_complex_problem(problem)
            reasoning_time = time.time() - start_time
            total_time += reasoning_time
            successful_reasonings += 1
            
            print(f"     ✅ {chain.strategy} | {reasoning_time:.3f}s | {len(chain.steps)} steps")
            
        except Exception as e:
            print(f"     ❌ Failed: {e}")
    
    # Get reasoning statistics
    stats = brain.advanced_reasoning.get_reasoning_statistics()
    
    print(f"\n📈 Performance Results:")
    print(f"   Total reasoning tasks: {len(performance_problems)}")
    print(f"   Successful: {successful_reasonings}")
    print(f"   Success rate: {(successful_reasonings/len(performance_problems)*100):.1f}%")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Average time per task: {(total_time/successful_reasonings if successful_reasonings > 0 else 0):.3f}s")
    
    print(f"\n🧠 Reasoning Engine Statistics:")
    print(f"   Total reasoning chains: {stats['total_chains']}")
    print(f"   Average confidence: {stats.get('average_confidence', 0):.3f}")
    print(f"   Average time: {stats.get('average_time', 0):.3f}s")
    
    if 'strategy_usage' in stats:
        print(f"   Strategy usage:")
        for strategy, count in stats['strategy_usage'].items():
            print(f"     {strategy}: {count} times")
    
    return {
        "success_rate": successful_reasonings/len(performance_problems),
        "avg_time": total_time/successful_reasonings if successful_reasonings > 0 else 0,
        "statistics": stats
    }

async def test_chain_of_thought():
    """Test detailed chain-of-thought reasoning process"""
    
    print("🔗 Testing Chain-of-Thought Reasoning")
    print("=" * 50)
    
    brain = SimpleBrain("./test_reasoning_storage")
    
    # Complex problem requiring multi-step reasoning
    complex_problem = """
    I'm building a web application and users are complaining about slow page loads. 
    The database queries seem fine, but the frontend is taking 5-10 seconds to render.
    I'm using React with a lot of components. What could be causing this and how should I approach debugging it?
    """
    
    print("🎯 Complex Problem:")
    print(complex_problem.strip())
    print("\n🔍 Starting chain-of-thought reasoning...\n")
    
    try:
        reasoning_chain = await brain.advanced_reasoning.solve_complex_problem(
            problem=complex_problem,
            context={"domain": "web_development", "urgency": "high"}
        )
        
        print(f"🧩 Chain-of-Thought Analysis:")
        print(f"   Strategy: {reasoning_chain.strategy}")
        print(f"   Total steps: {len(reasoning_chain.steps)}")
        print(f"   Reasoning time: {reasoning_chain.reasoning_time:.3f}s")
        print(f"   Confidence: {reasoning_chain.confidence_score:.3f}")
        print(f"   Chain ID: {reasoning_chain.chain_id}")
        
        print(f"\n📋 Detailed Reasoning Steps:")
        for i, step in enumerate(reasoning_chain.steps, 1):
            print(f"\n  Step {i}: {step.step_type.upper()}")
            print(f"    Premise: {step.premise}")
            print(f"    Reasoning: {step.reasoning}")
            print(f"    Conclusion: {step.conclusion}")
            print(f"    Confidence: {step.confidence}")
            
            if step.memory_references:
                print(f"    Memory references: {len(step.memory_references)}")
        
        print(f"\n🎉 Final Conclusion:")
        print(f"   {reasoning_chain.final_conclusion}")
        
        return {
            "success": True,
            "chain_length": len(reasoning_chain.steps),
            "confidence": reasoning_chain.confidence_score,
            "strategy": reasoning_chain.strategy
        }
        
    except Exception as e:
        print(f"❌ Chain-of-thought reasoning failed: {e}")
        return {"success": False, "error": str(e)}

async def test_reasoning_with_memory():
    """Test how reasoning integrates with memory system"""
    
    print("🧠 Testing Reasoning + Memory Integration")
    print("=" * 50)
    
    brain = SimpleBrain("./test_reasoning_storage")
    
    # Store specific knowledge for reasoning
    print("📚 Storing domain-specific knowledge...")
    
    knowledge_base = [
        ("React components re-render when props or state change", "semantic", {"framework": "react"}),
        ("Large bundle sizes cause slow initial page loads", "semantic", {"performance": "frontend"}),
        ("Too many DOM elements slow down rendering", "semantic", {"performance": "rendering"}),
        ("Network requests can be cached to improve performance", "procedural", {"optimization": "caching"}),
        ("I once fixed slow React rendering by using React.memo", "episodic", {"solution": "memoization"})
    ]
    
    for content, mem_type, metadata in knowledge_base:
        memory_id = brain.store_memory(content, mem_type, metadata)
        print(f"  ✅ Stored: {memory_id[:8]} | {content[:50]}...")
    
    print(f"\n🔍 Testing memory-informed reasoning...")
    
    # Problem that should leverage stored knowledge
    memory_problem = "My React app is slow. Based on what I know about React performance, what should I check first?"
    
    try:
        reasoning_chain = await brain.advanced_reasoning.solve_complex_problem(memory_problem)
        
        print(f"💭 Memory-Informed Reasoning Results:")
        print(f"   Strategy: {reasoning_chain.strategy}")
        print(f"   Memory context used: {len(reasoning_chain.memory_context)}")
        print(f"   Confidence: {reasoning_chain.confidence_score:.3f}")
        print(f"   Final answer: {reasoning_chain.final_conclusion}")
        
        # Check if reasoning used memory effectively
        memory_integration_score = 0
        for step in reasoning_chain.steps:
            if step.memory_references:
                memory_integration_score += len(step.memory_references)
        
        print(f"\n📊 Memory Integration Analysis:")
        print(f"   Memory references across steps: {memory_integration_score}")
        print(f"   Context memories available: {len(reasoning_chain.memory_context)}")
        print(f"   Integration effectiveness: {'High' if memory_integration_score > 0 else 'Low'}")
        
        return {
            "success": True,
            "memory_references": memory_integration_score,
            "memory_context_count": len(reasoning_chain.memory_context),
            "integration_effective": memory_integration_score > 0
        }
        
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Run all advanced reasoning tests"""
    
    print("🚀 Advanced Reasoning Engine - Comprehensive Test Suite")
    print("=" * 80)
    print("Testing Tier 1 High-Impact Intelligence Upgrade")
    print("=" * 80)
    
    all_results = {}
    
    try:
        # Test 1: All reasoning strategies
        print("\n" + "🔥" * 20 + " STRATEGY TESTS " + "🔥" * 20)
        strategy_results = await test_reasoning_strategies()
        all_results["strategies"] = strategy_results
        
        # Test 2: Performance testing
        print("\n" + "⚡" * 20 + " PERFORMANCE TESTS " + "⚡" * 20)
        performance_results = await test_reasoning_performance()
        all_results["performance"] = performance_results
        
        # Test 3: Chain-of-thought
        print("\n" + "🔗" * 20 + " CHAIN-OF-THOUGHT " + "🔗" * 20)
        cot_results = await test_chain_of_thought()
        all_results["chain_of_thought"] = cot_results
        
        # Test 4: Memory integration
        print("\n" + "🧠" * 20 + " MEMORY INTEGRATION " + "🧠" * 20)
        memory_results = await test_reasoning_with_memory()
        all_results["memory_integration"] = memory_results
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 ADVANCED REASONING ENGINE - TEST SUMMARY")
        print("=" * 80)
        
        # Strategy test summary
        if "strategies" in all_results:
            successful_strategies = sum(1 for r in all_results["strategies"] if r.get("success", False))
            total_strategies = len(all_results["strategies"])
            print(f"📊 Strategy Tests: {successful_strategies}/{total_strategies} passed ({successful_strategies/total_strategies*100:.1f}%)")
            
            correct_strategies = sum(1 for r in all_results["strategies"] if r.get("strategy_correct", False))
            print(f"🎯 Strategy Accuracy: {correct_strategies}/{total_strategies} correct ({correct_strategies/total_strategies*100:.1f}%)")
        
        # Performance summary
        if "performance" in all_results:
            success_rate = all_results["performance"]["success_rate"]
            avg_time = all_results["performance"]["avg_time"]
            print(f"⚡ Performance: {success_rate*100:.1f}% success rate, {avg_time:.3f}s avg time")
        
        # Chain-of-thought summary
        if "chain_of_thought" in all_results and all_results["chain_of_thought"]["success"]:
            cot = all_results["chain_of_thought"]
            print(f"🔗 Chain-of-Thought: ✅ Success | {cot['chain_length']} steps | {cot['confidence']:.3f} confidence")
        else:
            print(f"🔗 Chain-of-Thought: ❌ Failed")
        
        # Memory integration summary
        if "memory_integration" in all_results and all_results["memory_integration"]["success"]:
            mem = all_results["memory_integration"]
            print(f"🧠 Memory Integration: ✅ Success | {mem['memory_references']} references | {'Effective' if mem['integration_effective'] else 'Needs improvement'}")
        else:
            print(f"🧠 Memory Integration: ❌ Failed")
        
        # Overall assessment
        test_categories = ["strategies", "performance", "chain_of_thought", "memory_integration"]
        successful_categories = sum(1 for cat in test_categories if all_results.get(cat, {}).get("success", False))
        
        print(f"\n🏆 Overall Assessment:")
        print(f"   Test Categories Passed: {successful_categories}/{len(test_categories)}")
        
        if successful_categories >= 3:
            print(f"   🎉 ADVANCED REASONING ENGINE: FULLY FUNCTIONAL!")
            print(f"   ✅ Tier 1 High-Impact Upgrade: SUCCESSFUL")
        elif successful_categories >= 2:
            print(f"   ⚠️  ADVANCED REASONING ENGINE: PARTIALLY FUNCTIONAL")
            print(f"   🔧 Some features need adjustment")
        else:
            print(f"   ❌ ADVANCED REASONING ENGINE: NEEDS WORK")
            print(f"   🚨 Major issues detected")
        
        print(f"\n💾 Detailed results saved to: advanced_reasoning_test_results.json")
        
        # Save detailed results
        with open("advanced_reasoning_test_results.json", "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        
        return successful_categories >= 3
        
    except Exception as e:
        print(f"💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(main())