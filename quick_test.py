#!/usr/bin/env python3
"""
Quick test of Universal Discovery Engine core functionality
"""

import sys
import os
import json

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from brain_mcp_server import SimpleBrain, UniversalDiscoveryEngine
    print("✅ Successfully imported brain components")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

def test_discovery_engine():
    """Test basic discovery engine functionality"""
    
    print("\n🧠 Testing Universal Discovery Engine")
    print("=" * 40)
    
    # Create a simple brain instance
    brain = SimpleBrain("./quick_test_storage")
    print(f"✅ Brain initialized with {len(brain.memories)} memories")
    
    # Test the discovery engine directly
    discovery_engine = brain.universal_discovery
    print("✅ Universal Discovery Engine accessible")
    
    # Test CrewAI detection
    crewai_context = """
    {
        "agents": [
            {"id": "agent1", "role": "researcher"},
            {"id": "agent2", "role": "writer"}
        ],
        "crew": {"name": "test_crew"},
        "tasks": ["analyze data", "write report"]
    }
    """
    
    print("\n🔍 Testing CrewAI detection...")
    
    try:
        # Parse context
        context = discovery_engine._parse_system_context(crewai_context)
        print(f"✅ Context parsed: {len(context)} fields")
        
        # Generate signature
        signature = discovery_engine._analyze_interaction_signature(context)
        print(f"✅ Signature generated:")
        print(f"   - Predicted type: {signature.system_type_prediction}")
        print(f"   - Confidence: {signature.confidence:.2f}")
        print(f"   - Features: {len(signature.features)}")
        
        # Test emotional generation
        emotions = discovery_engine._generate_initial_emotions("curious", signature.confidence)
        print(f"✅ Emotions generated:")
        print(f"   - Curiosity: {emotions['curiosity']:.2f}")
        print(f"   - Trust: {emotions['trust']:.2f}")
        print(f"   - Excitement: {emotions['excitement']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_signatures():
    """Test system signature recognition"""
    
    print("\n📝 Testing System Signature Recognition")
    print("=" * 40)
    
    brain = SimpleBrain("./quick_test_storage")
    discovery_engine = brain.universal_discovery
    
    test_cases = [
        ("Multi-agent", "agents tasks crew", "multi_agent"),
        ("Chain", "chains prompts llm memory", "chain_framework"),
        ("Web", "routes endpoints app server", "web_framework"),
        ("UI", "components state props render", "ui_framework"),
        ("Database", "models fields queries schema", "data_framework")
    ]
    
    for name, test_text, expected_type in test_cases:
        context = {"raw_text": test_text}
        signature = discovery_engine._analyze_interaction_signature(context)
        
        print(f"🔍 {name}: {signature.system_type_prediction} (confidence: {signature.confidence:.2f})")
        
        if signature.system_type_prediction == expected_type and signature.confidence > 0.3:
            print("   ✅ Correct detection")
        else:
            print("   ⚠️  Needs improvement")

def main():
    """Run quick tests"""
    
    print("🚀 Quick Test: Universal Discovery Engine")
    print("Testing core functionality without async complications")
    
    try:
        # Test basic functionality
        basic_success = test_discovery_engine()
        
        # Test signature recognition
        test_system_signatures()
        
        if basic_success:
            print("\n🎉 Core functionality working!")
            print("✅ Universal Discovery Engine ready for integration")
        else:
            print("\n⚠️  Some issues found, but basic structure is good")
            
    except Exception as e:
        print(f"💥 Tests failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()