#!/usr/bin/env python3
"""
Quick async test of Advanced Reasoning Engine
"""

import asyncio
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain_mcp_server import SimpleBrain

async def test_async_reasoning():
    """Test async reasoning functionality"""
    
    print("🧠 Quick Async Reasoning Test")
    print("=" * 50)
    
    try:
        # Create brain
        brain = SimpleBrain("./test_async_storage")
        print("✅ Brain created successfully")
        
        # Authenticate brain for testing
        auth_success = brain.authenticate_client("test-client", "test-token", "https://test.com/brain")
        if not auth_success:
            print("❌ Authentication failed")
            return False
        print("✅ Brain authenticated")
        
        # Store some context
        brain.store_memory("Python is a programming language", "semantic", {"domain": "programming"})
        brain.store_memory("When debugging, check the console first", "procedural", {"skill": "debugging"})
        print("✅ Context stored")
        
        # Test reasoning
        problem = "How should I debug a Python error?"
        print(f"\n🔍 Problem: {problem}")
        
        reasoning_chain = await brain.advanced_reasoning.solve_complex_problem(problem)
        
        print(f"✅ Reasoning completed!")
        print(f"   Strategy: {reasoning_chain.strategy}")
        print(f"   Steps: {len(reasoning_chain.steps)}")
        print(f"   Confidence: {reasoning_chain.confidence_score:.3f}")
        print(f"   Time: {reasoning_chain.reasoning_time:.3f}s")
        print(f"   Conclusion: {reasoning_chain.final_conclusion}")
        
        # Show reasoning steps
        for i, step in enumerate(reasoning_chain.steps, 1):
            print(f"\n   Step {i}: {step.step_type}")
            print(f"   Premise: {step.premise}")
            print(f"   Reasoning: {step.reasoning}")
            print(f"   Conclusion: {step.conclusion}")
            print(f"   Confidence: {step.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run async test"""
    
    print("🚀 Advanced Reasoning Engine - Async Test")
    print("=" * 60)
    
    success = await test_async_reasoning()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ASYNC TEST PASSED!")
        print("✅ Advanced Reasoning Engine works asynchronously")
        print("✅ Ready for MCP tool integration")
    else:
        print("❌ Async test failed")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())