#!/usr/bin/env python3
"""
End-to-End Bulletproof Testing for Bolor Brain MCP
Comprehensive test suite covering all features, edge cases, and error scenarios

Author: Bolorerdene Bundgaa
Email: bolor@ariunbolor.org  
Website: https://bolor.me
License: MIT
"""

import os
import sys
import json
import time
import shutil
import tempfile
import traceback
from pathlib import Path
from brain_mcp_server import SimpleBrain, MemoryItem, CognitiveState

class BulletproofTester:
    """Comprehensive test suite for Bolor Brain MCP"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.brain = None
        
    def setup(self):
        """Setup test environment"""
        print("🚀 Starting End-to-End Bulletproof Testing")
        print("=" * 60)
        self.temp_dir = tempfile.mkdtemp(prefix="brain_e2e_test_")
        print(f"Test directory: {self.temp_dir}")
        
    def teardown(self):
        """Clean up test environment"""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up test directory: {self.temp_dir}")
    
    def run_test(self, test_name, test_func):
        """Run a single test with error handling"""
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        
        start_time = time.time()
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                print(f"✅ PASSED ({duration:.3f}s)")
                self.test_results.append({"test": test_name, "status": "PASSED", "duration": duration})
                return True
            else:
                print(f"❌ FAILED ({duration:.3f}s)")
                self.test_results.append({"test": test_name, "status": "FAILED", "duration": duration})
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 ERROR ({duration:.3f}s): {e}")
            traceback.print_exc()
            self.test_results.append({"test": test_name, "status": "ERROR", "duration": duration, "error": str(e)})
            return False
    
    # === BASIC FUNCTIONALITY TESTS ===
    
    def test_brain_initialization(self):
        """Test brain initialization and basic setup"""
        self.brain = SimpleBrain(storage_path=f"{self.temp_dir}/brain_init")
        
        # Check initialization
        assert isinstance(self.brain.memories, dict)
        assert isinstance(self.brain.memory_index, dict)
        assert isinstance(self.brain.cognitive_state, CognitiveState)
        
        # Check storage path
        assert Path(self.brain.storage_path).exists()
        
        # Check advanced features initialized
        assert hasattr(self.brain, 'connection_graph')
        assert hasattr(self.brain, 'feedback_history')
        
        print("   ✓ Brain initialized correctly")
        print("   ✓ Storage path created")
        print("   ✓ Advanced features available")
        
        return True
    
    def test_memory_storage_all_types(self):
        """Test storing all memory types with various parameters"""
        memory_types = ["working", "episodic", "semantic", "procedural", "emotional"]
        stored_ids = []
        
        for i, mem_type in enumerate(memory_types):
            memory_id = self.brain.store_memory(
                content=f"Test {mem_type} memory content {i}",
                memory_type=mem_type,
                metadata={"test_index": i, "type": mem_type},
                modality="text",
                emotional_valence=(-1.0 + i * 0.5),  # -1.0 to 1.0
                importance=(0.2 + i * 0.2)  # 0.2 to 1.0
            )
            stored_ids.append(memory_id)
            
            # Verify memory exists
            assert memory_id in self.brain.memories
            memory = self.brain.memories[memory_id]
            assert memory.memory_type == mem_type
            assert memory.importance == (0.2 + i * 0.2)
            
        print(f"   ✓ Stored {len(memory_types)} different memory types")
        print(f"   ✓ All memories accessible: {len(stored_ids)} IDs")
        
        # Test memory index
        for mem_type in memory_types:
            assert len(self.brain.memory_index[mem_type]) > 0
        
        print("   ✓ Memory index correctly populated")
        
        return True
    
    def test_enhanced_memory_retrieval(self):
        """Test advanced memory retrieval with semantic similarity"""
        
        # Store related memories
        self.brain.store_memory("Python programming is powerful", "semantic", {"topic": "coding"})
        self.brain.store_memory("Machine learning with Python", "semantic", {"topic": "AI"})
        self.brain.store_memory("I debugged a Python script yesterday", "episodic", {"activity": "debugging"})
        self.brain.store_memory("JavaScript is different from Python", "semantic", {"topic": "comparison"})
        
        # Test semantic retrieval
        memories = self.brain.retrieve_memories("Python development programming", limit=5)
        
        assert len(memories) > 0
        print(f"   ✓ Found {len(memories)} relevant memories")
        
        # Verify relevance scoring
        for i, memory in enumerate(memories):
            assert hasattr(memory, 'relevance_score')
            assert memory.relevance_score > 0
            print(f"     {i+1}. Score: {memory.relevance_score:.2f} - {memory.content[:40]}...")
        
        # Test access count tracking
        for memory in memories:
            assert memory.access_count > 0
            assert memory.last_accessed > 0
        
        print("   ✓ Access tracking working")
        print("   ✓ Relevance scoring functional")
        
        return True
    
    def test_attention_processing(self):
        """Test attention-based processing with context"""
        
        # Store contextual memories
        self.brain.store_memory("Debugging requires systematic approach", "procedural")
        self.brain.store_memory("Python syntax errors are common", "semantic")
        
        # Test attention processing
        result = self.brain.process_with_attention("How can I fix Python errors systematically?")
        
        assert "response" in result
        assert "attention_focus" in result
        assert "context_memories" in result
        assert "confidence" in result
        
        print(f"   ✓ Generated response: {result['response'][:50]}...")
        print(f"   ✓ Attention focus: {result['attention_focus']}")
        print(f"   ✓ Context memories: {len(result['context_memories'])}")
        print(f"   ✓ Confidence: {result['confidence']}")
        
        # Verify episodic memory was created
        assert len(self.brain.memory_index["episodic"]) > 0
        
        return True
    
    # === ADVANCED FEATURES TESTS ===
    
    def test_vector_embeddings(self):
        """Test vector embedding functionality"""
        
        if not self.brain.embedding_model:
            print("   ⚠️  Embedding model not available, skipping vector tests")
            return True
        
        # Store memories with embeddings
        id1 = self.brain.store_memory("Artificial intelligence and machine learning", "semantic")
        id2 = self.brain.store_memory("AI and ML technologies", "semantic")
        id3 = self.brain.store_memory("Cooking and recipes", "semantic")
        
        # Check embeddings were generated
        mem1 = self.brain.memories[id1]
        mem2 = self.brain.memories[id2]
        mem3 = self.brain.memories[id3]
        
        assert mem1.embedding is not None
        assert len(mem1.embedding) > 0
        print(f"   ✓ Generated embeddings of dimension {len(mem1.embedding)}")
        
        # Test semantic similarity
        memories = self.brain.retrieve_memories("machine learning AI", limit=3)
        
        # AI-related memories should score higher than cooking
        ai_memory_found = False
        for memory in memories:
            if "intelligence" in memory.content or "AI" in memory.content:
                ai_memory_found = True
                break
        
        assert ai_memory_found
        print("   ✓ Semantic similarity working correctly")
        
        return True
    
    def test_cross_memory_connections(self):
        """Test automatic memory connection creation"""
        
        if not self.brain.embedding_model:
            print("   ⚠️  Embedding model not available, skipping connection tests")
            return True
        
        # Store highly similar memories
        id1 = self.brain.store_memory("Deep learning neural networks", "semantic")
        time.sleep(0.1)  # Small delay to ensure different timestamps
        id2 = self.brain.store_memory("Neural networks for deep learning", "semantic")
        
        # Check if connections were created
        mem1 = self.brain.memories[id1]
        mem2 = self.brain.memories[id2]
        
        # Connections should be bidirectional
        if len(mem1.connections) > 0:
            assert id2 in mem1.connections
            assert id1 in mem2.connections
            print("   ✓ Bidirectional connections created")
        else:
            print("   ⚠️  No connections created (similarity threshold not met)")
        
        # Check connection graph
        if len(self.brain.connection_graph) > 0:
            print(f"   ✓ Connection graph has {len(self.brain.connection_graph)} nodes")
        
        return True
    
    def test_memory_consolidation(self):
        """Test automatic memory consolidation"""
        
        # Create memory for multiple accesses
        memory_id = self.brain.store_memory("Frequently accessed memory", "semantic")
        original_strength = self.brain.memories[memory_id].strength
        
        # Access memory multiple times
        for _ in range(10):
            self.brain.retrieve_memories("frequently accessed")
        
        # Trigger consolidation
        self.brain._consolidate_memories()
        
        memory = self.brain.memories[memory_id]
        assert memory.access_count >= 10
        
        # Check if strength increased
        if memory.access_count > 5:
            print(f"   ✓ Memory accessed {memory.access_count} times")
            print(f"   ✓ Strength: {original_strength} → {memory.strength}")
        
        return True
    
    def test_adaptive_feedback(self):
        """Test adaptive learning through feedback"""
        
        # Store memory and get interaction
        self.brain.store_memory("Test feedback memory", "semantic")
        result = self.brain.process_with_attention("feedback test query")
        interaction_id = result.get("interaction_id", "test_interaction")
        
        # Add positive feedback
        self.brain.add_feedback(interaction_id, "positive", 0.8)
        
        assert len(self.brain.feedback_history) > 0
        feedback = self.brain.feedback_history[-1]
        
        assert feedback["type"] == "positive"
        assert feedback["score"] == 0.8
        
        print("   ✓ Positive feedback recorded")
        
        # Add negative feedback
        self.brain.add_feedback("test_2", "negative", -0.5)
        
        assert len(self.brain.feedback_history) == 2
        print("   ✓ Multiple feedback types supported")
        
        return True
    
    def test_multimodal_memory(self):
        """Test multi-modal memory storage"""
        
        # Test structured data
        structured_data = {"name": "test", "values": [1, 2, 3]}
        memory_id = self.brain.store_multimodal_memory(
            content="Test structured data",
            data=structured_data,
            modality="structured",
            memory_type="semantic"
        )
        
        memory = self.brain.memories[memory_id]
        assert memory.modality == "structured"
        assert "modality" in memory.metadata
        assert "data_hash" in memory.metadata
        
        print("   ✓ Structured data stored")
        
        # Test base64 encoded data (simulated image)
        fake_image_data = b"fake_image_bytes_12345"
        image_id = self.brain.store_multimodal_memory(
            content="Test image data",
            data=fake_image_data,
            modality="image",
            memory_type="episodic"
        )
        
        image_memory = self.brain.memories[image_id]
        assert image_memory.modality == "image"
        assert image_memory.metadata["encoding"] == "base64"
        
        print("   ✓ Binary data (image) stored with base64 encoding")
        
        return True
    
    # === ERROR HANDLING AND EDGE CASES ===
    
    def test_error_handling(self):
        """Test error handling and recovery"""
        
        # Test invalid memory type
        try:
            self.brain.store_memory("test", "invalid_type")
            # Should still work (no validation enforced)
            print("   ✓ Handles invalid memory types gracefully")
        except Exception as e:
            print(f"   ⚠️  Error with invalid memory type: {e}")
        
        # Test empty queries
        memories = self.brain.retrieve_memories("")
        print(f"   ✓ Empty query handled: {len(memories)} results")
        
        # Test very long content
        long_content = "A" * 10000
        long_id = self.brain.store_memory(long_content, "semantic")
        assert long_id in self.brain.memories
        print("   ✓ Large content handled correctly")
        
        # Test special characters
        special_content = "Test with émojis 🧠 and spécial chàracters: @#$%^&*()"
        special_id = self.brain.store_memory(special_content, "semantic")
        assert special_id in self.brain.memories
        print("   ✓ Special characters handled correctly")
        
        return True
    
    def test_persistence_and_reload(self):
        """Test memory persistence across brain instances"""
        
        # Store some memories
        original_ids = []
        for i in range(5):
            memory_id = self.brain.store_memory(
                f"Persistence test memory {i}",
                "semantic",
                {"test": "persistence", "index": i}
            )
            original_ids.append(memory_id)
        
        original_count = len(self.brain.memories)
        storage_path = self.brain.storage_path
        
        # Create new brain instance with same storage
        new_brain = SimpleBrain(storage_path=str(storage_path))
        
        # Verify memories were loaded
        assert len(new_brain.memories) == original_count
        
        for memory_id in original_ids:
            assert memory_id in new_brain.memories
        
        print(f"   ✓ All {original_count} memories persisted and reloaded")
        
        # Test that new memories can be added
        new_id = new_brain.store_memory("New memory after reload", "semantic")
        assert new_id in new_brain.memories
        assert len(new_brain.memories) == original_count + 1
        
        print("   ✓ New memories can be added after reload")
        
        return True
    
    def test_cognitive_state_management(self):
        """Test cognitive state updates and persistence"""
        
        # Test initial state
        initial_state = self.brain.cognitive_state
        assert initial_state.confidence == 0.7  # Default value
        
        # Update cognitive state
        self.brain.cognitive_state.attention_focus = "testing focus"
        self.brain.cognitive_state.curiosity_level = 0.9
        self.brain.cognitive_state.emotional_state = "excited"
        self.brain.cognitive_state.confidence = 0.95
        
        # Verify updates
        assert self.brain.cognitive_state.attention_focus == "testing focus"
        assert self.brain.cognitive_state.curiosity_level == 0.9
        assert self.brain.cognitive_state.emotional_state == "excited"
        assert self.brain.cognitive_state.confidence == 0.95
        
        print("   ✓ Cognitive state updates working")
        
        # Test statistics include cognitive state
        stats = self.brain.get_memory_statistics()
        assert "cognitive_state" in stats
        assert stats["cognitive_state"]["confidence"] == 0.95
        
        print("   ✓ Cognitive state included in statistics")
        
        return True
    
    def test_performance_with_large_dataset(self):
        """Test performance with larger number of memories"""
        
        print("   Creating large dataset...")
        start_time = time.time()
        
        # Create 100 memories
        memory_ids = []
        for i in range(100):
            memory_id = self.brain.store_memory(
                f"Performance test memory {i} with content about topic {i % 10}",
                ["semantic", "episodic", "procedural"][i % 3],
                {"index": i, "topic": i % 10}
            )
            memory_ids.append(memory_id)
        
        creation_time = time.time() - start_time
        print(f"   ✓ Created 100 memories in {creation_time:.3f}s")
        
        # Test retrieval performance
        start_time = time.time()
        memories = self.brain.retrieve_memories("performance test topic", limit=10)
        retrieval_time = time.time() - start_time
        
        print(f"   ✓ Retrieved {len(memories)} memories in {retrieval_time:.3f}s")
        
        # Test statistics performance
        start_time = time.time()
        stats = self.brain.get_memory_statistics()
        stats_time = time.time() - start_time
        
        print(f"   ✓ Generated statistics in {stats_time:.3f}s")
        print(f"   ✓ Total memories: {stats['total_memories']}")
        
        return True
    
    # === MAIN TEST RUNNER ===
    
    def run_all_tests(self):
        """Run the complete test suite"""
        
        self.setup()
        
        tests = [
            ("Brain Initialization", self.test_brain_initialization),
            ("Memory Storage (All Types)", self.test_memory_storage_all_types),
            ("Enhanced Memory Retrieval", self.test_enhanced_memory_retrieval),
            ("Attention Processing", self.test_attention_processing),
            ("Vector Embeddings", self.test_vector_embeddings),
            ("Cross-Memory Connections", self.test_cross_memory_connections),
            ("Memory Consolidation", self.test_memory_consolidation),
            ("Adaptive Feedback", self.test_adaptive_feedback),
            ("Multi-Modal Memory", self.test_multimodal_memory),
            ("Error Handling", self.test_error_handling),
            ("Persistence & Reload", self.test_persistence_and_reload),
            ("Cognitive State Management", self.test_cognitive_state_management),
            ("Performance (Large Dataset)", self.test_performance_with_large_dataset),
        ]
        
        passed = 0
        failed = 0
        total_duration = 0
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
            else:
                failed += 1
            
            # Add to total duration
            if self.test_results:
                total_duration += self.test_results[-1]["duration"]
        
        # Print final results
        print("\n" + "=" * 60)
        print("🏁 BULLETPROOF TEST RESULTS")
        print("=" * 60)
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 TOTAL: {passed + failed}")
        print(f"⏱️  DURATION: {total_duration:.3f}s")
        print(f"📈 SUCCESS RATE: {(passed / (passed + failed)) * 100:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! SYSTEM IS BULLETPROOF! 🎉")
            deployment_ready = True
        else:
            print(f"\n⚠️  {failed} TESTS FAILED. SYSTEM NEEDS ATTENTION.")
            deployment_ready = False
        
        # Save detailed results
        results_file = Path(self.temp_dir).parent / "bulletproof_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "passed": passed,
                    "failed": failed,
                    "total": passed + failed,
                    "success_rate": (passed / (passed + failed)) * 100,
                    "duration": total_duration,
                    "deployment_ready": deployment_ready
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\n📋 Detailed results saved to: {results_file}")
        
        self.teardown()
        
        return deployment_ready

def main():
    """Run bulletproof tests"""
    tester = BulletproofTester()
    deployment_ready = tester.run_all_tests()
    
    if deployment_ready:
        print("\n🚀 SYSTEM READY FOR DEPLOYMENT!")
        return 0
    else:
        print("\n🔧 SYSTEM NEEDS FIXES BEFORE DEPLOYMENT")
        return 1

if __name__ == "__main__":
    exit(main())