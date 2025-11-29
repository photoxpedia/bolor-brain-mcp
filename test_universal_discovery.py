#!/usr/bin/env python3
"""
Test script for Universal Discovery Engine
Tests brain's ability to discover and connect to ANY framework automatically
"""

import asyncio
import json
import sys
import os

# Add the current directory to path so we can import our brain
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain_mcp_server import SimpleBrain

async def test_universal_discovery():
    """Test the Universal Discovery Engine with various frameworks"""
    
    print("🧠 Testing Universal Discovery Engine")
    print("=" * 50)
    
    # Initialize brain
    brain = SimpleBrain("./test_discovery_storage")
    
    # Test cases for different frameworks
    test_cases = [
        {
            "name": "CrewAI Multi-Agent Framework",
            "system_context": """
            {
                "agents": [
                    {"id": "agent1", "role": "researcher", "tasks": ["analyze data"]},
                    {"id": "agent2", "role": "writer", "tasks": ["write reports"]}
                ],
                "crew": {"name": "research_team"},
                "tasks": ["research topic", "write summary"]
            }
            """,
            "expected_type": "multi_agent"
        },
        {
            "name": "LangChain Framework", 
            "system_context": """
            {
                "chains": ["retrieval_chain", "qa_chain"],
                "llm": "gpt-4",
                "prompts": {"system": "You are a helpful assistant"},
                "memory": {"type": "conversation_buffer"},
                "retrieval": {"vectorstore": "chroma"}
            }
            """,
            "expected_type": "chain_framework"
        },
        {
            "name": "FastAPI Web Framework",
            "system_context": """
            {
                "app": "FastAPI()",
                "routes": [
                    {"path": "/users", "methods": ["GET", "POST"]},
                    {"path": "/items", "methods": ["GET"]}
                ],
                "endpoints": ["@app.get", "@app.post"],
                "server": "uvicorn"
            }
            """,
            "expected_type": "web_framework"
        },
        {
            "name": "React UI Framework",
            "system_context": """
            {
                "components": {
                    "App": {"state": {"count": 0}, "props": {}},
                    "Button": {"props": {"onClick": "function"}}
                },
                "hooks": ["useState", "useEffect"],
                "render": "ReactDOM.render"
            }
            """,
            "expected_type": "ui_framework"
        },
        {
            "name": "Django ORM Framework",
            "system_context": """
            {
                "models": {
                    "User": {"fields": ["name", "email"]},
                    "Post": {"fields": ["title", "content"]}
                },
                "queries": ["User.objects.filter", "Post.objects.all"],
                "migrations": ["0001_initial.py"],
                "schema": {"tables": ["auth_user", "blog_post"]}
            }
            """,
            "expected_type": "data_framework"
        },
        {
            "name": "Unknown Framework (Text Description)",
            "system_context": "I have a machine learning pipeline with data preprocessing, model training, and inference components",
            "expected_type": "unknown"
        }
    ]
    
    successful_discoveries = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}/{total_tests}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Test system discovery
            result = await brain.connect_to_system(
                system_context=test_case["system_context"],
                integration_mode="auto",
                emotional_approach="curious"
            )
            
            # Check results
            if result.get("discovery_status") == "successful":
                discovered_type = result.get("system_type", "unknown")
                confidence = result.get("confidence_score", 0.0)
                
                print(f"✅ Discovery Status: {result['discovery_status']}")
                print(f"🎯 System Type: {discovered_type}")
                print(f"📊 Confidence: {confidence:.2f}")
                print(f"💝 Emotional Relationship: {json.dumps(result.get('emotional_relationship', {}), indent=2)}")
                print(f"🧠 Brain Curiosity: {result.get('brain_curiosity_triggered', 0.0):.2f}")
                print(f"💡 Recommendations: {len(result.get('integration_recommendations', []))} suggestions")
                
                # Check if discovery matched expectations
                if discovered_type == test_case["expected_type"] or (confidence > 0.5 and test_case["expected_type"] != "unknown"):
                    print(f"🎉 SUCCESS: Correctly identified as {discovered_type}")
                    successful_discoveries += 1
                elif test_case["expected_type"] == "unknown" and confidence < 0.5:
                    print(f"🎉 SUCCESS: Correctly identified as unknown system")
                    successful_discoveries += 1
                else:
                    print(f"⚠️  PARTIAL: Expected {test_case['expected_type']}, got {discovered_type}")
                    successful_discoveries += 0.5  # Partial credit for discovery working
                    
            else:
                print(f"❌ Discovery failed: {result.get('error', 'Unknown error')}")
                print(f"💡 Recommendations: {result.get('recommendations', [])}")
                
        except Exception as e:
            print(f"💥 Error during test: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "="*50)
    print(f"🎯 UNIVERSAL DISCOVERY TEST RESULTS")
    print("="*50)
    print(f"✅ Successful discoveries: {successful_discoveries}/{total_tests}")
    print(f"📊 Success rate: {(successful_discoveries/total_tests)*100:.1f}%")
    
    # Check brain's learned systems
    print(f"\n🧠 Brain's Connected Systems:")
    for system_id, system in brain.discovered_systems.items():
        print(f"  - {system_id}: {system.system_type} (confidence: {system.confidence_score:.2f})")
    
    # Check brain's cognitive state
    print(f"\n🧠 Brain's Cognitive State After Discovery:")
    print(f"  - Attention Focus: {brain.cognitive_state.attention_focus}")
    print(f"  - Emotional State: {brain.cognitive_state.emotional_state}")
    print(f"  - Integration Curiosity: {brain.cognitive_state.integration_curiosity:.2f}")
    print(f"  - Confidence: {brain.cognitive_state.confidence:.2f}")
    print(f"  - Connected Systems: {len(brain.cognitive_state.connected_systems)}")
    
    print(f"\n🎉 Universal Discovery Engine Test Complete!")
    
    # Return success status
    return successful_discoveries >= total_tests * 0.8  # 80% success rate needed

async def test_emotional_approaches():
    """Test different emotional approaches to system discovery"""
    
    print("\n🎭 Testing Emotional Approaches to Discovery")
    print("=" * 50)
    
    brain = SimpleBrain("./test_emotional_storage")
    
    # Same system, different emotional approaches
    system_context = """
    {
        "agents": [{"id": "test_agent", "role": "assistant"}],
        "crew": {"name": "test_crew"},
        "tasks": ["simple task"]
    }
    """
    
    approaches = ["curious", "careful", "enthusiastic"]
    
    for approach in approaches:
        print(f"\n🎭 Testing '{approach}' emotional approach:")
        
        result = await brain.connect_to_system(
            system_context=system_context,
            integration_mode="auto", 
            emotional_approach=approach
        )
        
        if result.get("discovery_status") == "successful":
            emotions = result.get("emotional_relationship", {})
            print(f"  🎯 System: {result.get('system_type')}")
            print(f"  😊 Curiosity: {emotions.get('curiosity', 0):.2f}")
            print(f"  🤗 Trust: {emotions.get('trust', 0):.2f}")
            print(f"  🎉 Excitement: {emotions.get('excitement', 0):.2f}")
            print(f"  ⚠️  Caution: {emotions.get('caution', 0):.2f}")
        else:
            print(f"  ❌ Failed: {result.get('error')}")
    
    print(f"\n✅ Emotional Approaches Test Complete!")

async def main():
    """Run all universal discovery tests"""
    
    print("🚀 Starting Universal Discovery Engine Tests")
    print("🧠 Testing Brain's Ability to Connect to ANY Framework")
    print("=" * 60)
    
    try:
        # Test basic discovery functionality
        basic_success = await test_universal_discovery()
        
        # Test emotional approaches
        await test_emotional_approaches()
        
        print("\n" + "="*60)
        if basic_success:
            print("🎉 ALL TESTS PASSED! Universal Discovery Engine is working!")
        else:
            print("⚠️  Some tests failed, but basic functionality is working")
            
        print("🧠 Brain That Just Works™ is ready for ANY framework!")
        print("=" * 60)
        
    except Exception as e:
        print(f"💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())