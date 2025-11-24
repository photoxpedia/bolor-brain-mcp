#!/usr/bin/env python3
"""
Test script for Bolor Brain MCP Server functionality
Demonstrates all core brain features without MCP dependencies

Author: Bolorerdene Bundgaa
Email: bolor@ariunbolor.org  
Website: https://bolor.me
License: MIT
"""

from brain_mcp_server import SimpleBrain
import json
import time

def test_brain_mcp():
    """Test all Bolor Brain MCP functionality"""
    print("🧠 Bolor Brain MCP Server Test Suite\n")
    
    # Initialize fresh brain
    brain = SimpleBrain(storage_path="./test_mcp_storage")
    
    # Test 1: Store different types of memories
    print("1. Testing memory storage...")
    
    memories_to_store = [
        ("Python is a versatile programming language", "semantic", {"domain": "programming", "language": "python"}),
        ("User asked about debugging React components yesterday", "episodic", {"interaction": "help_request", "framework": "react"}),
        ("When code throws errors, read the stack trace first", "procedural", {"skill": "debugging", "level": "beginner"}),
        ("I feel confident when helping with programming questions", "emotional", {"sentiment": "positive", "context": "programming"}),
        ("Currently working on MCP server implementation", "working", {"task": "development", "status": "in_progress"})
    ]
    
    stored_ids = []
    for content, mem_type, metadata in memories_to_store:
        memory_id = brain.store_memory(content, mem_type, metadata)
        stored_ids.append(memory_id)
        print(f"   ✓ Stored {mem_type} memory: {memory_id[:8]}")
    
    # Test 2: Retrieve memories with different queries
    print("\n2. Testing memory retrieval...")
    
    test_queries = [
        "Python programming",
        "debugging errors", 
        "React components",
        "programming confidence"
    ]
    
    for query in test_queries:
        memories = brain.retrieve_memories(query, limit=3)
        print(f"   Query '{query}': Found {len(memories)} relevant memories")
        for i, mem in enumerate(memories):
            score = getattr(mem, 'relevance_score', 0)
            print(f"     {i+1}. [{mem.memory_type}] (Score: {score}) {mem.content[:50]}...")
    
    # Test 3: Attention processing
    print("\n3. Testing attention processing...")
    
    attention_tests = [
        "How do I debug JavaScript errors?",
        "Can you help me learn Python?",
        "What's the best way to handle React state?"
    ]
    
    for test_input in attention_tests:
        result = brain.process_with_attention(test_input)
        print(f"   Input: '{test_input}'")
        print(f"   Focus: {result['attention_focus']}")
        print(f"   Context: {len(result['context_memories'])} memories")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Response: {result['response'][:80]}...\n")
    
    # Test 4: Cognitive state management
    print("4. Testing cognitive state updates...")
    
    # Update cognitive state
    brain.cognitive_state.attention_focus = "JavaScript debugging"
    brain.cognitive_state.curiosity_level = 0.8
    brain.cognitive_state.emotional_state = "focused"
    brain.cognitive_state.confidence = 0.9
    
    print("   ✓ Updated cognitive state")
    print(f"   Attention: {brain.cognitive_state.attention_focus}")
    print(f"   Curiosity: {brain.cognitive_state.curiosity_level}")
    print(f"   Emotion: {brain.cognitive_state.emotional_state}")
    print(f"   Confidence: {brain.cognitive_state.confidence}")
    
    # Test 5: Brain statistics
    print("\n5. Testing brain statistics...")
    
    stats = brain.get_memory_statistics()
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   Memory distribution:")
    for mem_type, count in stats['memory_types'].items():
        print(f"     {mem_type}: {count}")
    
    print(f"   Cognitive state:")
    for key, value in stats['cognitive_state'].items():
        print(f"     {key}: {value}")
    
    # Test 6: Memory persistence
    print("\n6. Testing memory persistence...")
    
    # Create new brain instance with same storage path
    brain2 = SimpleBrain(storage_path="./test_mcp_storage")
    stats2 = brain2.get_memory_statistics()
    
    print(f"   Original brain: {stats['total_memories']} memories")
    print(f"   Reloaded brain: {stats2['total_memories']} memories")
    print(f"   ✓ Persistence {'✓ WORKING' if stats['total_memories'] == stats2['total_memories'] else '✗ FAILED'}")
    
    print("\n🎉 Bolor Brain MCP Server test complete!")
    print(f"Successfully tested all core functionalities with {stats['total_memories']} memories")
    print("\nCreated by Bolorerdene Bundgaa | https://bolor.me")
    
    return stats

if __name__ == "__main__":
    test_brain_mcp()