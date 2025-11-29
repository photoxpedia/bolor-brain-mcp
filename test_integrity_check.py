#!/usr/bin/env python3
"""
Complete integrity check for Universal Brain Integration + Advanced Reasoning Engine
Ensures all original functionality remains intact while new features work
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain_mcp_server import SimpleBrain

async def test_original_brain_integrity():
    """Test all original brain functionality"""
    
    print("🧠 Testing Original Brain Functionality Integrity")
    print("=" * 60)
    
    brain = SimpleBrain("./test_integrity_storage")
    
    # Authenticate for testing
    auth_success = brain.authenticate_client("test-client", "test-token", "https://test.com/brain")
    if not auth_success:
        print("❌ Authentication failed")
        return False
    print("✅ Brain authenticated")
    
    integrity_tests = []
    
    # Test 1: Basic memory operations
    print("\n1. Testing basic memory operations...")
    try:
        memory_id = brain.store_memory(
            "Test memory for integrity check", 
            "semantic", 
            {"test": "integrity"}
        )
        memories = brain.retrieve_memories("integrity test", limit=1)
        
        test1_success = len(memory_id) > 0 and len(memories) > 0
        print(f"   {'✅' if test1_success else '❌'} Memory operations: {'Working' if test1_success else 'Failed'}")
        integrity_tests.append(("Memory Operations", test1_success))
        
    except Exception as e:
        print(f"   ❌ Memory operations failed: {e}")
        integrity_tests.append(("Memory Operations", False))
    
    # Test 2: Cognitive state
    print("\n2. Testing cognitive state...")
    try:
        brain.cognitive_state.attention_focus = "integrity testing"
        brain.cognitive_state.curiosity_level = 0.8
        
        test2_success = (
            brain.cognitive_state.attention_focus == "integrity testing" and
            brain.cognitive_state.curiosity_level == 0.8
        )
        print(f"   {'✅' if test2_success else '❌'} Cognitive state: {'Working' if test2_success else 'Failed'}")
        integrity_tests.append(("Cognitive State", test2_success))
        
    except Exception as e:
        print(f"   ❌ Cognitive state failed: {e}")
        integrity_tests.append(("Cognitive State", False))
    
    # Test 3: Attention processing
    print("\n3. Testing attention processing...")
    try:
        result = brain.process_with_attention("Test attention processing")
        test3_success = (
            "attention_focus" in result and
            "response" in result and
            "confidence" in result
        )
        print(f"   {'✅' if test3_success else '❌'} Attention processing: {'Working' if test3_success else 'Failed'}")
        integrity_tests.append(("Attention Processing", test3_success))
        
    except Exception as e:
        print(f"   ❌ Attention processing failed: {e}")
        integrity_tests.append(("Attention Processing", False))
    
    # Test 4: Statistics
    print("\n4. Testing statistics...")
    try:
        stats = brain.get_memory_statistics()
        test4_success = (
            "total_memories" in stats and
            "memory_types" in stats and
            "cognitive_state" in stats
        )
        print(f"   {'✅' if test4_success else '❌'} Statistics: {'Working' if test4_success else 'Failed'}")
        integrity_tests.append(("Statistics", test4_success))
        
    except Exception as e:
        print(f"   ❌ Statistics failed: {e}")
        integrity_tests.append(("Statistics", False))
    
    return integrity_tests

async def test_universal_discovery_integrity():
    """Test Universal Discovery Engine with authentication"""
    
    print("\n🔍 Testing Universal Discovery Engine Integrity")
    print("=" * 60)
    
    brain = SimpleBrain("./test_discovery_integrity")
    brain.authenticate_client("test-client", "test-token", "https://test.com/brain")
    
    discovery_tests = []
    
    # Test 1: Engine exists and is initialized
    print("\n1. Testing Universal Discovery Engine initialization...")
    try:
        test1_success = hasattr(brain, 'universal_discovery') and brain.universal_discovery is not None
        print(f"   {'✅' if test1_success else '❌'} Engine initialization: {'Working' if test1_success else 'Failed'}")
        discovery_tests.append(("Engine Initialization", test1_success))
    except Exception as e:
        print(f"   ❌ Engine initialization failed: {e}")
        discovery_tests.append(("Engine Initialization", False))
    
    # Test 2: Framework detection
    print("\n2. Testing framework detection...")
    try:
        crewai_context = '''{"agents": [{"id": "test", "role": "tester"}], "crew": {"name": "test"}}'''
        
        result = await brain.connect_to_system(
            system_context=crewai_context,
            integration_mode="auto",
            emotional_approach="curious"
        )
        
        test2_success = (
            result.get("discovery_status") == "successful" and
            "system_type" in result
        )
        print(f"   {'✅' if test2_success else '❌'} Framework detection: {'Working' if test2_success else 'Failed'}")
        print(f"   Detected: {result.get('system_type', 'unknown')}")
        discovery_tests.append(("Framework Detection", test2_success))
        
    except Exception as e:
        print(f"   ❌ Framework detection failed: {e}")
        discovery_tests.append(("Framework Detection", False))
    
    return discovery_tests

async def test_advanced_reasoning_integrity():
    """Test Advanced Reasoning Engine doesn't break anything"""
    
    print("\n🧠 Testing Advanced Reasoning Engine Integration")
    print("=" * 60)
    
    brain = SimpleBrain("./test_reasoning_integrity")
    brain.authenticate_client("test-client", "test-token", "https://test.com/brain")
    
    reasoning_tests = []
    
    # Test 1: Engine exists and is initialized
    print("\n1. Testing Advanced Reasoning Engine initialization...")
    try:
        test1_success = hasattr(brain, 'advanced_reasoning') and brain.advanced_reasoning is not None
        print(f"   {'✅' if test1_success else '❌'} Reasoning engine: {'Working' if test1_success else 'Failed'}")
        reasoning_tests.append(("Reasoning Engine Init", test1_success))
    except Exception as e:
        print(f"   ❌ Reasoning engine failed: {e}")
        reasoning_tests.append(("Reasoning Engine Init", False))
    
    # Test 2: Reasoning functionality
    print("\n2. Testing reasoning functionality...")
    try:
        # Store context for reasoning
        brain.store_memory("Context for reasoning test", "semantic", {"test": "reasoning"})
        
        # Test reasoning
        chain = await brain.advanced_reasoning.solve_complex_problem(
            "What is the best approach to testing software?"
        )
        
        test2_success = (
            hasattr(chain, 'strategy') and
            hasattr(chain, 'steps') and
            hasattr(chain, 'final_conclusion') and
            len(chain.steps) > 0
        )
        print(f"   {'✅' if test2_success else '❌'} Reasoning process: {'Working' if test2_success else 'Failed'}")
        print(f"   Strategy: {getattr(chain, 'strategy', 'unknown')}")
        print(f"   Steps: {len(getattr(chain, 'steps', []))}")
        reasoning_tests.append(("Reasoning Process", test2_success))
        
    except Exception as e:
        print(f"   ❌ Reasoning process failed: {e}")
        reasoning_tests.append(("Reasoning Process", False))
    
    # Test 3: Reasoning doesn't break memory
    print("\n3. Testing reasoning doesn't interfere with memory...")
    try:
        # Store memory after reasoning
        new_memory = brain.store_memory("Post-reasoning memory", "semantic", {"test": "post-reasoning"})
        memories = brain.retrieve_memories("memory", limit=2)
        
        test3_success = len(new_memory) > 0 and len(memories) >= 2
        print(f"   {'✅' if test3_success else '❌'} Memory post-reasoning: {'Working' if test3_success else 'Failed'}")
        reasoning_tests.append(("Memory Post-Reasoning", test3_success))
        
    except Exception as e:
        print(f"   ❌ Memory post-reasoning failed: {e}")
        reasoning_tests.append(("Memory Post-Reasoning", False))
    
    return reasoning_tests

async def test_continuous_learning_integrity():
    """Test Continuous Learning System still works"""
    
    print("\n🧬 Testing Continuous Learning System Integrity")
    print("=" * 60)
    
    brain = SimpleBrain("./test_learning_integrity")
    brain.authenticate_client("test-client", "test-token", "https://test.com/brain")
    
    learning_tests = []
    
    # Test 1: System exists
    print("\n1. Testing Continuous Learning System initialization...")
    try:
        test1_success = hasattr(brain, 'continuous_learning') and brain.continuous_learning is not None
        print(f"   {'✅' if test1_success else '❌'} Learning system: {'Working' if test1_success else 'Failed'}")
        learning_tests.append(("Learning System Init", test1_success))
    except Exception as e:
        print(f"   ❌ Learning system failed: {e}")
        learning_tests.append(("Learning System Init", False))
    
    # Test 2: Learning from interaction
    print("\n2. Testing learning from interaction...")
    try:
        interaction_data = {
            "system_id": "test_system",
            "interaction_type": "optimization",
            "outcome": "success",
            "context": {"test": "learning"}
        }
        
        result = await brain.continuous_learning.learn_from_system_interaction(
            "test_system", interaction_data
        )
        
        test2_success = result is not None and "learning_pattern" in str(result)
        print(f"   {'✅' if test2_success else '❌'} Learning process: {'Working' if test2_success else 'Failed'}")
        learning_tests.append(("Learning Process", test2_success))
        
    except Exception as e:
        print(f"   ❌ Learning process failed: {e}")
        learning_tests.append(("Learning Process", False))
    
    return learning_tests

async def main():
    """Run complete integrity check"""
    
    print("🚀 COMPLETE INTEGRITY CHECK")
    print("Verifying Universal Brain Integration + Advanced Reasoning Engine")
    print("=" * 80)
    print("Ensuring NO original functionality has been broken!")
    print("=" * 80)
    
    all_tests = {}
    
    try:
        # Test original brain functionality
        brain_tests = await test_original_brain_integrity()
        all_tests["Original Brain"] = brain_tests
        
        # Test Universal Discovery
        discovery_tests = await test_universal_discovery_integrity()
        all_tests["Universal Discovery"] = discovery_tests
        
        # Test Advanced Reasoning (new)
        reasoning_tests = await test_advanced_reasoning_integrity()
        all_tests["Advanced Reasoning"] = reasoning_tests
        
        # Test Continuous Learning
        learning_tests = await test_continuous_learning_integrity()
        all_tests["Continuous Learning"] = learning_tests
        
        # Generate comprehensive report
        print("\n" + "=" * 80)
        print("🎯 COMPLETE INTEGRITY CHECK RESULTS")
        print("=" * 80)
        
        total_tests = 0
        total_passed = 0
        
        for system_name, tests in all_tests.items():
            system_passed = sum(1 for test_name, passed in tests if passed)
            system_total = len(tests)
            total_tests += system_total
            total_passed += system_passed
            
            status = "✅ INTACT" if system_passed == system_total else "⚠️ ISSUES" if system_passed > 0 else "❌ BROKEN"
            print(f"{system_name}: {system_passed}/{system_total} tests passed - {status}")
            
            for test_name, passed in tests:
                print(f"  {'✅' if passed else '❌'} {test_name}")
        
        # Overall assessment
        overall_health = total_passed / total_tests if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL SYSTEM HEALTH: {total_passed}/{total_tests} ({overall_health*100:.1f}%)")
        
        if overall_health >= 0.95:
            print("🎉 EXCELLENT! Universal Brain Integration is 100% INTACT!")
            print("✅ Advanced Reasoning Engine successfully integrated without breaking anything!")
            print("✅ All original functionality preserved")
            print("✅ Ready for next level enhancements!")
        elif overall_health >= 0.8:
            print("✅ GOOD! System is mostly intact with minor issues")
            print("🔧 Some components may need adjustment")
        else:
            print("❌ CRITICAL! Significant functionality has been broken")
            print("🚨 Immediate fixes required before proceeding")
        
        return overall_health >= 0.95
        
    except Exception as e:
        print(f"💥 Integrity check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(main())