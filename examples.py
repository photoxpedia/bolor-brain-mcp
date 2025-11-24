#!/usr/bin/env python3
"""
Bolor Brain MCP - Usage Examples
Demonstrates all features and use cases

Author: Bolorerdene Bundgaa
Email: bolor@ariunbolor.org  
Website: https://bolor.me
License: MIT
"""

from brain_mcp_server import SimpleBrain
import json
import time

def example_basic_usage():
    """Basic memory storage and retrieval"""
    print("🧠 Example 1: Basic Memory Usage")
    print("-" * 40)
    
    brain = SimpleBrain(storage_path="./examples_storage")
    
    # Store different types of memories
    print("Storing memories...")
    
    # Episodic: Personal experiences
    brain.store_memory(
        "I successfully completed my first React project today",
        "episodic",
        {"project": "portfolio", "outcome": "success"}
    )
    
    # Semantic: Facts and knowledge
    brain.store_memory(
        "React hooks allow functional components to manage state",
        "semantic", 
        {"topic": "react", "concept": "hooks"}
    )
    
    # Procedural: How-to knowledge  
    brain.store_memory(
        "To debug React: 1) Check console, 2) Verify props, 3) Check state",
        "procedural",
        {"skill": "debugging", "framework": "react"}
    )
    
    # Retrieve memories
    print("\nRetrieving memories about 'React development'...")
    memories = brain.retrieve_memories("React development", limit=3)
    
    for i, memory in enumerate(memories, 1):
        print(f"{i}. [{memory.memory_type}] {memory.content}")
        print(f"   Relevance: {getattr(memory, 'relevance_score', 0):.2f}")
        print()

def example_enhanced_features():
    """Advanced cognitive features"""
    print("🚀 Example 2: Enhanced Cognitive Features")
    print("-" * 40)
    
    brain = SimpleBrain(storage_path="./examples_storage")
    
    # Store memories with emotional context and importance
    print("Storing emotionally tagged memories...")
    
    brain.store_memory(
        "I love solving complex programming challenges",
        "emotional",
        {"sentiment": "positive"},
        emotional_valence=0.9,  # Very positive
        importance=0.8          # High importance
    )
    
    brain.store_memory(
        "Debugging CSS issues is frustrating but necessary", 
        "procedural",
        {"skill": "debugging", "domain": "css"},
        emotional_valence=-0.3,  # Slightly negative
        importance=0.6           # Medium importance
    )
    
    # Process with attention mechanism
    print("\nProcessing with attention mechanism...")
    result = brain.process_with_attention("How do I approach challenging programming tasks?")
    
    print(f"Attention Focus: {result['attention_focus']}")
    print(f"Response: {result['response']}")
    print(f"Context Memories: {len(result['context_memories'])}")
    print(f"Confidence: {result['confidence']}")
    
    # Show cognitive state
    print(f"\nCognitive State:")
    print(f"  Curiosity: {brain.cognitive_state.curiosity_level}")
    print(f"  Emotion: {brain.cognitive_state.emotional_state}")
    print(f"  Confidence: {brain.cognitive_state.confidence}")

def example_multimodal_memory():
    """Multi-modal memory storage"""
    print("📁 Example 3: Multi-Modal Memory")
    print("-" * 40)
    
    brain = SimpleBrain(storage_path="./examples_storage")
    
    # Store structured data
    project_data = {
        "name": "Bolor Brain MCP",
        "version": "1.0.0",
        "features": ["memory", "learning", "attention"],
        "performance": {"tests_passed": 13, "success_rate": 100.0}
    }
    
    brain.store_multimodal_memory(
        content="Project statistics for Bolor Brain MCP v1.0.0",
        data=project_data,
        modality="structured", 
        memory_type="semantic"
    )
    
    # Simulate image storage (base64 encoded)
    fake_image_data = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA4nEoxwAAAABJRU5ErkJggg=="
    
    brain.store_multimodal_memory(
        content="Screenshot of successful test results",
        data=fake_image_data,
        modality="image",
        memory_type="episodic"
    )
    
    print("Stored structured data and image memory successfully")
    
    # Retrieve multi-modal memories
    memories = brain.retrieve_memories("project statistics", limit=2)
    for memory in memories:
        print(f"Found {memory.modality} memory: {memory.content}")
        if memory.modality == "structured":
            print(f"  Data hash: {memory.metadata.get('data_hash', 'N/A')}")

def example_learning_and_feedback():
    """Adaptive learning through feedback"""
    print("🎓 Example 4: Adaptive Learning")
    print("-" * 40)
    
    brain = SimpleBrain(storage_path="./examples_storage")
    
    # Store knowledge
    brain.store_memory(
        "Python list comprehensions are faster than loops for simple operations",
        "semantic",
        {"topic": "python", "optimization": "performance"}
    )
    
    # Process query and get interaction
    result = brain.process_with_attention("How can I optimize Python code?")
    interaction_id = result.get("interaction_id", "example_interaction")
    
    print(f"Initial response: {result['response'][:100]}...")
    
    # Provide positive feedback
    print("\nProviding positive feedback...")
    brain.add_feedback(interaction_id, "positive", 0.8)
    
    # Provide correction feedback
    print("Providing correction feedback...")
    brain.add_feedback("correction_example", "correction", 0.5)
    
    # Check feedback history
    print(f"\nFeedback history: {len(brain.feedback_history)} entries")
    for feedback in brain.feedback_history[-2:]:
        print(f"  {feedback['type']}: {feedback['score']}")

def example_memory_connections():
    """Automatic memory connections"""
    print("🔗 Example 5: Memory Connections")
    print("-" * 40)
    
    brain = SimpleBrain(storage_path="./examples_storage")
    
    # Store related memories that should connect
    print("Storing related memories...")
    
    brain.store_memory(
        "Machine learning algorithms learn patterns from data",
        "semantic",
        {"field": "ai", "concept": "learning"}
    )
    
    brain.store_memory(
        "Neural networks are a type of machine learning model",
        "semantic", 
        {"field": "ai", "concept": "neural_networks"}
    )
    
    brain.store_memory(
        "Deep learning uses multiple layers in neural networks",
        "semantic",
        {"field": "ai", "concept": "deep_learning"}
    )
    
    # Check connections
    print(f"\nConnection graph has {len(brain.connection_graph)} nodes")
    
    # Show connections for each memory
    for memory_id, memory in brain.memories.items():
        if memory.connections:
            print(f"Memory: {memory.content[:50]}...")
            print(f"  Connected to {len(memory.connections)} other memories")

def example_cognitive_analytics():
    """Brain analytics and statistics"""
    print("📊 Example 6: Cognitive Analytics")
    print("-" * 40)
    
    brain = SimpleBrain(storage_path="./examples_storage")
    
    # Get comprehensive statistics
    stats = brain.get_memory_statistics()
    
    print("Brain Statistics:")
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  Memory distribution:")
    for mem_type, count in stats['memory_types'].items():
        print(f"    {mem_type}: {count}")
    
    print(f"\nCognitive state:")
    for key, value in stats['cognitive_state'].items():
        print(f"    {key}: {value}")
    
    # Show memory age range
    if stats['total_memories'] > 0:
        oldest = time.time() - stats['oldest_memory']
        newest = time.time() - stats['newest_memory']
        print(f"\nMemory age range:")
        print(f"  Oldest: {oldest/60:.1f} minutes ago")
        print(f"  Newest: {newest/60:.1f} minutes ago")

def example_developer_workflow():
    """Real-world developer workflow example"""
    print("💻 Example 7: Developer Workflow")
    print("-" * 40)
    
    brain = SimpleBrain(storage_path="./examples_storage")
    
    # Day 1: Learning new concept
    brain.store_memory(
        "Learned about FastAPI for building Python APIs",
        "episodic",
        {"date": "2024-11-24", "activity": "learning"},
        emotional_valence=0.7,
        importance=0.8
    )
    
    brain.store_memory(
        "FastAPI automatically generates OpenAPI documentation",
        "semantic",
        {"framework": "fastapi", "feature": "documentation"}
    )
    
    # Day 2: Applying knowledge
    brain.store_memory(
        "Successfully built my first FastAPI endpoint with type hints",
        "episodic", 
        {"date": "2024-11-25", "achievement": "first_endpoint"},
        emotional_valence=0.9,
        importance=0.9
    )
    
    brain.store_memory(
        "To create FastAPI endpoint: use @app.get() decorator with function",
        "procedural",
        {"framework": "fastapi", "task": "create_endpoint"}
    )
    
    # Day 3: Problem solving
    result = brain.process_with_attention("How do I debug FastAPI validation errors?")
    
    print("Developer asking for help:")
    print(f"Query: 'How do I debug FastAPI validation errors?'")
    print(f"Brain response: {result['response']}")
    print(f"Context from: {len(result['context_memories'])} related memories")
    
    # Provide feedback on helpfulness
    brain.add_feedback(result.get('interaction_id', 'dev_help'), "positive", 0.8)
    
    print("\nDeveloper workflow complete - brain learned and adapted!")

def main():
    """Run all examples"""
    print("🧠 Bolor Brain MCP - Usage Examples")
    print("=" * 50)
    print("Created by Bolorerdene Bundgaa | https://bolor.me")
    print("=" * 50)
    
    examples = [
        example_basic_usage,
        example_enhanced_features,
        example_multimodal_memory, 
        example_learning_and_feedback,
        example_memory_connections,
        example_cognitive_analytics,
        example_developer_workflow
    ]
    
    for i, example_func in enumerate(examples, 1):
        print(f"\n{'='*60}")
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example {i} failed: {e}")
        
        if i < len(examples):
            input("\nPress Enter to continue to next example...")
    
    print("\n" + "="*60)
    print("🎉 All examples completed!")
    print("Your brain now contains rich, connected memories.")
    print("\nTo explore your brain:")
    print("  python3 -c \"from brain_mcp_server import SimpleBrain; brain = SimpleBrain('./examples_storage'); print(brain.get_memory_statistics())\"")

if __name__ == "__main__":
    main()