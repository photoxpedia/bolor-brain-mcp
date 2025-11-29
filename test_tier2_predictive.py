#!/usr/bin/env python3
"""
Test Tier 2: Predictive Intelligence Engine
Verify it works without breaking existing functionality
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain_mcp_server import SimpleBrain

async def test_tier2_integration():
    """Test that Tier 2 Predictive Intelligence integrates perfectly"""
    
    print("🔮 Testing Tier 2: Predictive Intelligence Engine")
    print("=" * 60)
    print("Ensuring ZERO disruption to existing functionality")
    print("=" * 60)
    
    tests_results = []
    
    # Initialize brain
    brain = SimpleBrain("./test_tier2_storage")
    brain.authenticate_client("test-client", "test-token", "https://test.com/brain")
    
    # Test 1: Verify existing systems still work
    print("\n1. Testing existing systems are intact...")
    try:
        # Test basic memory
        memory_id = brain.store_memory("Test memory for Tier 2", "semantic", {"test": "tier2"})
        
        # Test advanced reasoning (Tier 1)
        reasoning_chain = await brain.advanced_reasoning.solve_complex_problem("How do I test software effectively?")
        
        # Test universal discovery
        has_discovery = hasattr(brain, 'universal_discovery') and brain.universal_discovery is not None
        
        # Test continuous learning  
        has_learning = hasattr(brain, 'continuous_learning') and brain.continuous_learning is not None
        
        existing_systems_ok = (
            len(memory_id) > 0 and
            reasoning_chain is not None and
            has_discovery and
            has_learning
        )
        
        print(f"   {'✅' if existing_systems_ok else '❌'} Existing systems: {'All intact' if existing_systems_ok else 'Issues detected'}")
        tests_results.append(("Existing Systems Intact", existing_systems_ok))
        
    except Exception as e:
        print(f"   ❌ Existing systems test failed: {e}")
        tests_results.append(("Existing Systems Intact", False))
    
    # Test 2: Verify Tier 2 Predictive Intelligence is initialized
    print("\n2. Testing Tier 2 Predictive Intelligence initialization...")
    try:
        has_predictive = hasattr(brain, 'predictive_intelligence') and brain.predictive_intelligence is not None
        print(f"   {'✅' if has_predictive else '❌'} Predictive engine: {'Initialized' if has_predictive else 'Missing'}")
        tests_results.append(("Predictive Intelligence Init", has_predictive))
        
    except Exception as e:
        print(f"   ❌ Predictive intelligence test failed: {e}")
        tests_results.append(("Predictive Intelligence Init", False))
    
    # Test 3: Test basic prediction functionality  
    print("\n3. Testing prediction functionality...")
    try:
        # Create some reasoning history first for predictions to analyze
        await brain.advanced_reasoning.solve_complex_problem("How do I debug Python code?")
        await brain.advanced_reasoning.solve_complex_problem("What's the best way to test APIs?") 
        
        # Test predictions
        context = {"problem": "I'm working on a web application with authentication issues"}
        predictions = await brain.predictive_intelligence.predict_user_needs(context, history_depth=5)
        
        prediction_success = (
            isinstance(predictions, list) and
            len(predictions) > 0 and
            all(hasattr(pred, 'predicted_content') for pred in predictions) and
            all(hasattr(pred, 'confidence') for pred in predictions)
        )
        
        print(f"   {'✅' if prediction_success else '❌'} Predictions: {'Working' if prediction_success else 'Failed'}")
        print(f"   Generated {len(predictions)} predictions")
        
        if predictions:
            print(f"   Top prediction: {predictions[0].predicted_content}")
            print(f"   Confidence: {predictions[0].confidence:.2f}")
            print(f"   Type: {predictions[0].prediction_type}")
        
        tests_results.append(("Prediction Functionality", prediction_success))
        
    except Exception as e:
        print(f"   ❌ Prediction test failed: {e}")
        import traceback
        traceback.print_exc()
        tests_results.append(("Prediction Functionality", False))
    
    # Test 4: Test prediction statistics
    print("\n4. Testing prediction statistics...")
    try:
        stats = brain.predictive_intelligence.get_prediction_statistics()
        stats_success = (
            isinstance(stats, dict) and
            "total_predictions" in stats
        )
        
        print(f"   {'✅' if stats_success else '❌'} Statistics: {'Working' if stats_success else 'Failed'}")
        print(f"   Total predictions: {stats.get('total_predictions', 0)}")
        
        tests_results.append(("Prediction Statistics", stats_success))
        
    except Exception as e:
        print(f"   ❌ Statistics test failed: {e}")
        tests_results.append(("Prediction Statistics", False))
    
    # Test 5: Verify no interference with Tier 1 Advanced Reasoning
    print("\n5. Testing no interference with Advanced Reasoning...")
    try:
        # Test reasoning still works after predictions
        reasoning_chain2 = await brain.advanced_reasoning.solve_complex_problem("How do I optimize database queries?")
        reasoning_stats = brain.advanced_reasoning.get_reasoning_statistics()
        
        no_interference = (
            reasoning_chain2 is not None and
            reasoning_stats.get("total_chains", 0) > 0
        )
        
        print(f"   {'✅' if no_interference else '❌'} Reasoning integrity: {'Preserved' if no_interference else 'Compromised'}")
        print(f"   Total reasoning chains: {reasoning_stats.get('total_chains', 0)}")
        
        tests_results.append(("No Reasoning Interference", no_interference))
        
    except Exception as e:
        print(f"   ❌ No interference test failed: {e}")
        tests_results.append(("No Reasoning Interference", False))
    
    # Test 6: Test memory operations still work
    print("\n6. Testing memory operations after Tier 2 addition...")
    try:
        # Store additional memory
        new_memory = brain.store_memory("Post-Tier2 memory", "procedural", {"test": "post_tier2"})
        
        # Retrieve memories
        memories = brain.retrieve_memories("test", limit=5)
        
        # Get statistics
        stats = brain.get_memory_statistics()
        
        memory_integrity = (
            len(new_memory) > 0 and
            len(memories) >= 2 and  # Should have at least the memories we stored
            stats.get("total_memories", 0) >= 2
        )
        
        print(f"   {'✅' if memory_integrity else '❌'} Memory operations: {'Working' if memory_integrity else 'Failed'}")
        print(f"   Total memories: {stats.get('total_memories', 0)}")
        
        tests_results.append(("Memory Operations Intact", memory_integrity))
        
    except Exception as e:
        print(f"   ❌ Memory integrity test failed: {e}")
        tests_results.append(("Memory Operations Intact", False))
    
    return tests_results

async def main():
    """Run Tier 2 integration tests"""
    
    print("🚀 TIER 2: PREDICTIVE INTELLIGENCE ENGINE")
    print("Testing safe integration with existing Universal Brain")
    print("=" * 80)
    
    try:
        test_results = await test_tier2_integration()
        
        # Analyze results
        total_tests = len(test_results)
        passed_tests = sum(1 for test_name, passed in test_results if passed)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 TIER 2 INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        for test_name, passed in test_results:
            print(f"{'✅' if passed else '❌'} {test_name}")
        
        print(f"\n📊 Overall Success: {passed_tests}/{total_tests} tests passed ({success_rate*100:.1f}%)")
        
        if success_rate >= 0.95:
            print("🎉 TIER 2 PERFECT INTEGRATION!")
            print("✅ Predictive Intelligence Engine successfully added")
            print("✅ All existing functionality preserved")
            print("✅ Zero disruption to Universal Brain Integration")
            print("🔮 Brain now PREDICTS user needs proactively!")
            
        elif success_rate >= 0.8:
            print("✅ TIER 2 GOOD INTEGRATION!")
            print("✅ Predictive Intelligence mostly working")
            print("🔧 Minor issues to address")
            
        else:
            print("❌ TIER 2 INTEGRATION ISSUES!")
            print("🚨 Problems detected - needs investigation")
        
        return success_rate >= 0.95
        
    except Exception as e:
        print(f"💥 Tier 2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(main())