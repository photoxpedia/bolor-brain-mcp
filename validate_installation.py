#!/usr/bin/env python3
"""
Final validation script for Bolor Brain MCP installation
Tests all components and generates installation report

Author: Bolorerdene Bundgaa
Email: bolor@ariunbolor.org  
Website: https://bolor.me
License: MIT
"""

import os
import sys
import json
import time
from pathlib import Path

def run_validation():
    """Run complete validation of the Bolor Brain MCP installation"""
    
    print("🚀 Bolor Brain MCP Installation Validation")
    print("=" * 50)
    print("Author: Bolorerdene Bundgaa | https://bolor.me")
    print("=" * 50)
    
    results = {
        "timestamp": time.time(),
        "tests": {},
        "overall_status": "unknown",
        "summary": {}
    }
    
    # Test 1: File Structure
    print("\n1. Checking file structure...")
    required_files = [
        "brain_mcp_server.py",
        "README_MCP.md", 
        "requirements_mcp.txt",
        "mcp_config.json",
        "test_mcp_brain.py"
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    results["tests"]["file_structure"] = {
        "passed": len(missing_files) == 0,
        "missing_files": missing_files
    }
    
    # Test 2: Import Tests
    print("\n2. Testing Python imports...")
    try:
        from brain_mcp_server import SimpleBrain, MemoryItem, CognitiveState
        print("   ✅ Core classes import successfully")
        results["tests"]["imports"] = {"passed": True, "error": None}
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        results["tests"]["imports"] = {"passed": False, "error": str(e)}
    
    # Test 3: Basic Functionality
    print("\n3. Testing basic brain functionality...")
    try:
        brain = SimpleBrain(storage_path="./validation_test")
        
        # Store memory
        memory_id = brain.store_memory("Validation test memory", "semantic", {"test": "validation"})
        
        # Retrieve memory
        memories = brain.retrieve_memories("validation", limit=1)
        
        # Process with attention
        result = brain.process_with_attention("Test validation processing")
        
        # Get statistics
        stats = brain.get_memory_statistics()
        
        success = (
            len(memory_id) > 0 and
            len(memories) > 0 and
            "response" in result and
            stats["total_memories"] > 0
        )
        
        if success:
            print("   ✅ All basic functions working")
        else:
            print("   ❌ Basic functionality issues detected")
        
        results["tests"]["basic_functionality"] = {
            "passed": success,
            "memory_stored": len(memory_id) > 0,
            "memory_retrieved": len(memories) > 0,
            "attention_processing": "response" in result,
            "statistics": stats["total_memories"] > 0
        }
        
        # Clean up
        import shutil
        if Path("./validation_test").exists():
            shutil.rmtree("./validation_test")
            
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
        results["tests"]["basic_functionality"] = {"passed": False, "error": str(e)}
    
    # Test 4: Memory Persistence
    print("\n4. Testing memory persistence...")
    try:
        # Create brain and store memory
        brain1 = SimpleBrain(storage_path="./persistence_test")
        id1 = brain1.store_memory("Persistence test", "semantic", {"test": "persistence"})
        count1 = len(brain1.memories)
        
        # Create new brain instance
        brain2 = SimpleBrain(storage_path="./persistence_test")
        count2 = len(brain2.memories)
        has_memory = id1 in brain2.memories
        
        persistence_working = (count1 == count2 and has_memory and count1 > 0)
        
        if persistence_working:
            print("   ✅ Memory persistence working")
        else:
            print(f"   ❌ Persistence failed: {count1} -> {count2}, memory found: {has_memory}")
        
        results["tests"]["persistence"] = {
            "passed": persistence_working,
            "original_count": count1,
            "reloaded_count": count2,
            "memory_found": has_memory
        }
        
        # Clean up
        import shutil
        if Path("./persistence_test").exists():
            shutil.rmtree("./persistence_test")
            
    except Exception as e:
        print(f"   ❌ Persistence test failed: {e}")
        results["tests"]["persistence"] = {"passed": False, "error": str(e)}
    
    # Test 5: MCP Server Structure
    print("\n5. Validating MCP server structure...")
    try:
        # Check if MCP tools are properly defined (structure only)
        import brain_mcp_server
        
        # Test the module has the right structure
        has_brain_instance = hasattr(brain_mcp_server, 'brain')
        has_simple_brain_class = hasattr(brain_mcp_server, 'SimpleBrain')
        
        structure_valid = has_brain_instance and has_simple_brain_class
        
        if structure_valid:
            print("   ✅ MCP server module structure valid")
        else:
            print("   ❌ MCP server missing required components")
        
        results["tests"]["mcp_structure"] = {"passed": structure_valid}
        
    except Exception as e:
        print(f"   ❌ MCP structure validation failed: {e}")
        results["tests"]["mcp_structure"] = {"passed": False, "error": str(e)}
    
    # Test 6: Configuration Files
    print("\n6. Validating configuration files...")
    try:
        # Test JSON config
        with open("mcp_config.json", "r") as f:
            config = json.load(f)
        
        has_mcp_servers = "mcpServers" in config
        has_brain_config = "bolor-brain-mcp" in config.get("mcpServers", {})
        
        # Test requirements
        with open("requirements_mcp.txt", "r") as f:
            requirements = f.read()
        
        has_mcp_req = "mcp" in requirements
        
        config_valid = has_mcp_servers and has_brain_config and has_mcp_req
        
        if config_valid:
            print("   ✅ Configuration files valid")
        else:
            print("   ❌ Configuration issues detected")
        
        results["tests"]["configuration"] = {
            "passed": config_valid,
            "mcp_config_valid": has_mcp_servers and has_brain_config,
            "requirements_valid": has_mcp_req
        }
        
    except Exception as e:
        print(f"   ❌ Configuration validation failed: {e}")
        results["tests"]["configuration"] = {"passed": False, "error": str(e)}
    
    # Calculate overall results
    passed_tests = sum(1 for test in results["tests"].values() if test["passed"])
    total_tests = len(results["tests"])
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    results["overall_status"] = "PASSED" if success_rate >= 1.0 else "PARTIAL" if success_rate >= 0.8 else "FAILED"
    results["summary"] = {
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "success_rate": round(success_rate * 100, 1)
    }
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Tests Passed: {passed_tests}/{total_tests} ({results['summary']['success_rate']}%)")
    
    if results['overall_status'] == "PASSED":
        print("\n🎉 Bolor Brain MCP is fully functional and ready for use!")
        print("\nNext steps:")
        print("1. Install MCP: pip install mcp")
        print("2. Add to Claude Code using mcp_config.json")
        print("3. Start using brain cognitive tools!")
        print("\nCreated by Bolorerdene Bundgaa | https://bolor.me")
        
    elif results['overall_status'] == "PARTIAL":
        print("\n⚠️  Bolor Brain MCP is mostly functional but has some issues.")
        print("Check the failed tests above and address any issues.")
        
    else:
        print("\n❌ Bolor Brain MCP has significant issues that need to be resolved.")
        print("Please check all failed tests and fix the problems.")
    
    # Save detailed results
    with open("validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to validation_results.json")
    
    return results

if __name__ == "__main__":
    run_validation()