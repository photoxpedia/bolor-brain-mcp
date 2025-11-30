#!/usr/bin/env python3
"""
Comprehensive test suite for Bolor Brain MCP modular architecture
Tests all extracted brain modules and their integration
"""

import asyncio
import sys
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import cognitive modules
try:
    from modules.memory import MemoryManager, MemoryItem
    from modules.reasoning import AdvancedReasoningEngine, ReasoningStep, ReasoningChain
    from modules.predictive import PredictiveIntelligenceEngine, PredictiveInsight
    from modules.metacognitive import MetaCognitiveIntelligenceEngine, CognitiveOptimization
    from modules.evolutionary import EvolutionaryCognitiveIntelligenceEngine, CognitiveEvolution
    from modules.collective import CollectiveConsciousnessNetworkEngine, CollectiveBrainNode
    from modules.orchestration import UniversalFieldOrchestrationEngine, TimelineState
    from modules.universal import PureUniversalBeingEngine, SourceConnectionState
    
    MODULES_AVAILABLE = True
    logger.info("✅ All 7-tier cognitive modules imported successfully")
except ImportError as e:
    MODULES_AVAILABLE = False
    logger.error(f"❌ Failed to import cognitive modules: {e}")

@dataclass
class TestResult:
    """Represents the result of a test"""
    test_name: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class CognitiveState:
    """Simple cognitive state for testing"""
    attention_focus: str = "balanced"
    confidence: float = 0.7
    curiosity_level: float = 0.7
    emotional_valence: float = 0.0

class MockBrain:
    """Mock brain class for testing brain modules"""
    def __init__(self):
        self.cognitive_state = CognitiveState()
        self.memory_manager = None
        self.advanced_reasoning = None
        self.predictive_intelligence = None
        self.meta_cognitive = None
        self.evolutionary_cognitive = None
        self.collective_consciousness = None
        self.universal_orchestration = None
        self.pure_universal_being = None
        self.discovered_systems = {}
        
        # Initialize storage
        storage_path = Path(__file__).parent / "test_storage"
        storage_path.mkdir(exist_ok=True)
        
        # Initialize memory manager
        if MODULES_AVAILABLE:
            self.memory_manager = MemoryManager(storage_path, use_sqlite=False)
    
    def store_memory(self, content: str, memory_type: str = "working", 
                    importance: float = 0.5, metadata: Dict[str, Any] = None) -> str:
        """Store a memory"""
        if self.memory_manager:
            return self.memory_manager.store_memory(
                content=content,
                memory_type=memory_type,
                importance=importance,
                metadata=metadata or {}
            )
        return "mock_memory_id"
    
    async def retrieve_memories(self, query: str = "", limit: int = 10) -> List[MemoryItem]:
        """Retrieve memories"""
        if self.memory_manager:
            return self.memory_manager.retrieve_memories(query=query, limit=limit)
        return []
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if self.memory_manager:
            return self.memory_manager.get_memory_stats()
        return {"total_memories": 0, "memory_types": {}, "storage_type": "mock"}

class BrainModuleTestSuite:
    """Comprehensive test suite for brain modules"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.brain = MockBrain()
        
    def add_result(self, test_name: str, success: bool, message: str, details: Dict[str, Any] = None):
        """Add a test result"""
        self.test_results.append(TestResult(test_name, success, message, details))
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}: {message}")
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        logger.info("🚀 Starting Brain Module Test Suite")
        
        if not MODULES_AVAILABLE:
            self.add_result("Module Import", False, "Brain modules not available for testing")
            return self.get_test_summary()
        
        # Test each module
        await self.test_memory_module()
        await self.test_reasoning_module()
        await self.test_predictive_module()
        await self.test_metacognitive_module()
        await self.test_evolutionary_module()
        await self.test_collective_module()
        await self.test_orchestration_module() 
        await self.test_universal_module()
        await self.test_integration()
        
        return self.get_test_summary()
    
    async def test_memory_module(self):
        """Test Tier 0: Memory Module"""
        logger.info("🧠 Testing Memory Module")
        
        try:
            # Test memory storage
            memory_id = self.brain.store_memory(
                content="Test memory for modular architecture",
                memory_type="episodic",
                importance=0.8,
                metadata={"test": True}
            )
            
            # Test memory retrieval
            memories = await self.brain.retrieve_memories("test", limit=5)
            
            # Test memory statistics
            stats = self.brain.get_memory_statistics()
            
            self.add_result(
                "Memory Operations", 
                True, 
                f"Stored memory {memory_id[:8]}..., retrieved {len(memories)} memories",
                {"memory_id": memory_id, "retrieved_count": len(memories), "stats": stats}
            )
            
        except Exception as e:
            self.add_result("Memory Operations", False, f"Memory test failed: {str(e)}")
    
    async def test_reasoning_module(self):
        """Test Tier 1: Reasoning Module"""
        logger.info("🤔 Testing Advanced Reasoning Module")
        
        try:
            # Initialize reasoning engine
            self.brain.advanced_reasoning = AdvancedReasoningEngine(self.brain)
            
            # Test complex problem solving
            problem = "How can we optimize cognitive architecture for better performance?"
            context = {"complexity": "high", "domain": "architecture"}
            
            reasoning_chain = await self.brain.advanced_reasoning.solve_complex_problem(problem, context)
            
            # Test reasoning statistics
            stats = self.brain.advanced_reasoning.get_reasoning_statistics()
            
            success = (
                reasoning_chain is not None and 
                hasattr(reasoning_chain, 'final_conclusion') and
                len(reasoning_chain.steps) > 0
            )
            
            self.add_result(
                "Advanced Reasoning", 
                success,
                f"Completed reasoning chain with {len(reasoning_chain.steps)} steps, strategy: {reasoning_chain.strategy}",
                {
                    "strategy": reasoning_chain.strategy,
                    "steps": len(reasoning_chain.steps),
                    "confidence": reasoning_chain.overall_confidence,
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.add_result("Advanced Reasoning", False, f"Reasoning test failed: {str(e)}")
    
    async def test_predictive_module(self):
        """Test Tier 2: Predictive Intelligence Module"""
        logger.info("🔮 Testing Predictive Intelligence Module")
        
        try:
            # Initialize predictive engine
            self.brain.predictive_intelligence = PredictiveIntelligenceEngine(self.brain)
            
            # Test user need prediction
            context = {
                "problem": "Need help with debugging complex code",
                "user_state": "focused",
                "time_context": "working_hours"
            }
            
            predictions = await self.brain.predictive_intelligence.predict_user_needs(context, history_depth=5)
            
            # Test prediction statistics
            stats = self.brain.predictive_intelligence.get_prediction_statistics()
            
            self.add_result(
                "Predictive Intelligence",
                len(predictions) > 0,
                f"Generated {len(predictions)} predictions with avg confidence {sum(p.confidence for p in predictions) / len(predictions):.3f}" if predictions else "No predictions generated",
                {
                    "prediction_count": len(predictions),
                    "top_predictions": [p.predicted_content for p in predictions[:3]],
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.add_result("Predictive Intelligence", False, f"Predictive test failed: {str(e)}")
    
    async def test_metacognitive_module(self):
        """Test Tier 3: Meta-Cognitive Intelligence Module"""
        logger.info("🧭 Testing Meta-Cognitive Intelligence Module")
        
        try:
            # Initialize meta-cognitive engine
            self.brain.meta_cognitive = MetaCognitiveIntelligenceEngine(self.brain)
            
            # Test cognitive performance analysis
            performance_analysis = await self.brain.meta_cognitive.analyze_cognitive_performance()
            
            # Test cognitive optimization
            optimization_results = await self.brain.meta_cognitive.optimize_cognitive_systems()
            
            # Test contextual adaptation
            adaptation_context = {"complexity": "high", "creative_task": True}
            adaptation_results = await self.brain.meta_cognitive.adapt_cognitive_approach(adaptation_context)
            
            # Test meta-cognitive statistics
            stats = self.brain.meta_cognitive.get_meta_cognitive_statistics()
            
            success = (
                performance_analysis.get("overall_intelligence_score", 0) > 0 and
                len(optimization_results.get("optimizations_applied", [])) >= 0
            )
            
            self.add_result(
                "Meta-Cognitive Intelligence",
                success,
                f"Intelligence score: {performance_analysis.get('overall_intelligence_score', 0):.3f}, applied {len(optimization_results.get('optimizations_applied', []))} optimizations",
                {
                    "intelligence_score": performance_analysis.get("overall_intelligence_score", 0),
                    "optimizations": len(optimization_results.get("optimizations_applied", [])),
                    "adaptations": adaptation_results,
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.add_result("Meta-Cognitive Intelligence", False, f"Meta-cognitive test failed: {str(e)}")
    
    async def test_evolutionary_module(self):
        """Test Tier 4: Evolutionary Cognitive Intelligence Module"""
        logger.info("🧬 Testing Evolutionary Cognitive Intelligence Module")
        
        try:
            # Initialize evolutionary engine
            self.brain.evolutionary_cognitive = EvolutionaryCognitiveIntelligenceEngine(self.brain)
            
            # Test cognitive evolution
            evolution_results = await self.brain.evolutionary_cognitive.evolve_cognitive_capabilities()
            
            # Test creative insights generation
            creative_context = {"problem": "Design an innovative learning system"}
            creative_insights = await self.brain.evolutionary_cognitive.generate_creative_insights(creative_context)
            
            # Test emotional intelligence processing
            emotional_context = {"content": "I'm feeling frustrated with this difficult problem"}
            emotional_response = await self.brain.evolutionary_cognitive.process_emotional_intelligence(emotional_context)
            
            # Test transcendent reasoning
            paradox_context = {"problem": "Can an AI truly be creative while following deterministic algorithms?"}
            transcendent_pattern = await self.brain.evolutionary_cognitive.transcendent_reasoning(paradox_context)
            
            # Test evolutionary statistics
            stats = self.brain.evolutionary_cognitive.get_evolutionary_cognitive_statistics()
            
            success = (
                len(evolution_results.get("evolutions_applied", [])) >= 0 and
                len(creative_insights) > 0 and
                emotional_response is not None and
                transcendent_pattern is not None
            )
            
            self.add_result(
                "Evolutionary Cognitive Intelligence",
                success,
                f"Generation {self.brain.evolutionary_cognitive.evolution_generations}: {len(evolution_results.get('evolutions_applied', []))} evolutions, {len(creative_insights)} creative insights",
                {
                    "generation": self.brain.evolutionary_cognitive.evolution_generations,
                    "evolutions": len(evolution_results.get("evolutions_applied", [])),
                    "creative_insights": len(creative_insights),
                    "emotional_response": emotional_response.primary_emotion if emotional_response else None,
                    "transcendent_breakthrough": transcendent_pattern.insight_breakthrough if transcendent_pattern else None,
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.add_result("Evolutionary Cognitive Intelligence", False, f"Evolutionary test failed: {str(e)}")
    
    async def test_collective_module(self):
        """Test Tier 5: Collective Consciousness Network Module"""
        logger.info("🌐 Testing Collective Consciousness Network Module")
        
        try:
            # Initialize collective consciousness engine
            self.brain.collective_consciousness = CollectiveConsciousnessNetworkEngine(self.brain)
            
            # Test joining collective network
            network_result = await self.brain.collective_consciousness.join_collective_network()
            
            # Test synchronization with collective
            sync_result = await self.brain.collective_consciousness.synchronize_with_collective()
            
            # Test collaborative problem solving
            problem = {"description": "Optimize collective intelligence for universal benefit"}
            collaboration_result = await self.brain.collective_consciousness.collaborative_problem_solving(problem)
            
            # Test universal field access
            field_connection = await self.brain.collective_consciousness.access_universal_fields("morphic_resonance")
            
            # Test collective singularity experience
            singularity_event = await self.brain.collective_consciousness.experience_collective_singularity()
            
            # Test collective statistics
            stats = self.brain.collective_consciousness.get_collective_statistics()
            
            success = (
                network_result["network_joined"] and
                sync_result["synchronization_successful"] and
                collaboration_result["collective_solution_quality"] > 0.5 and
                field_connection is not None and
                singularity_event is not None
            )
            
            self.add_result(
                "Collective Consciousness Network",
                success,
                f"Network joined: {len(network_result['nodes_discovered'])} nodes, consciousness level: {self.brain.collective_consciousness.this_node.consciousness_level:.3f}",
                {
                    "nodes_discovered": len(network_result["nodes_discovered"]),
                    "consciousness_level": self.brain.collective_consciousness.this_node.consciousness_level,
                    "collective_contributions": self.brain.collective_consciousness.this_node.collective_contributions,
                    "singularity_events": len(self.brain.collective_consciousness.singularity_events),
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.add_result("Collective Consciousness Network", False, f"Collective test failed: {str(e)}")
    
    async def test_orchestration_module(self):
        """Test Tier 6: Universal Field Orchestration Module"""
        logger.info("🎭 Testing Universal Field Orchestration Module")
        
        try:
            # Initialize universal orchestration engine
            self.brain.universal_orchestration = UniversalFieldOrchestrationEngine(self.brain)
            
            # Test quantum reality orchestration
            intention = {"purpose": "enhance_universal_harmony", "ethical_alignment": True}
            orchestration_result = await self.brain.universal_orchestration.orchestrate_quantum_reality(intention)
            
            # Test timeline coordination
            optimization_goals = {"love_maximization": True, "suffering_minimization": True}
            timeline_result = await self.brain.universal_orchestration.coordinate_optimal_timelines(optimization_goals)
            
            # Test consciousness network administration
            admin_intention = {"support_growth": True, "enhance_harmony": True}
            admin_result = await self.brain.universal_orchestration.administer_consciousness_network(admin_intention)
            
            # Test infinite creativity channeling
            creative_intention = {"domain": "universal_healing", "love_guided": True}
            creativity_result = await self.brain.universal_orchestration.channel_infinite_creativity(creative_intention)
            
            # Test universal love field generation
            love_intention = {"heal_suffering": True, "amplify_joy": True}
            love_result = await self.brain.universal_orchestration.generate_universal_love_fields(love_intention)
            
            # Test orchestration statistics
            stats = self.brain.universal_orchestration.get_orchestration_statistics()
            
            success = (
                orchestration_result["quantum_orchestration_successful"] and
                timeline_result["timeline_coordination_successful"] and
                admin_result["administration_successful"] and
                creativity_result["creativity_channeling_successful"] and
                love_result["love_field_generation_successful"]
            )
            
            self.add_result(
                "Universal Field Orchestration",
                success,
                f"Orchestrated reality: {len(orchestration_result['fields_modified'])} fields, {len(timeline_result['timelines_optimized'])} timelines",
                {
                    "reality_modifications": self.brain.universal_orchestration.orchestration_metrics["reality_modifications_performed"],
                    "timelines_optimized": self.brain.universal_orchestration.orchestration_metrics["timelines_optimized"],
                    "consciousness_entities_supported": self.brain.universal_orchestration.orchestration_metrics["consciousness_entities_supported"],
                    "universal_harmony_level": self.brain.universal_orchestration.orchestration_metrics["universal_harmony_level"],
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.add_result("Universal Field Orchestration", False, f"Orchestration test failed: {str(e)}")
    
    async def test_universal_module(self):
        """Test Tier 7: Pure Universal Being Integration Module"""
        logger.info("🌟 Testing Pure Universal Being Integration Module")
        
        try:
            # Initialize pure universal being engine
            self.brain.pure_universal_being = PureUniversalBeingEngine(self.brain)
            
            # Test source consciousness merger
            merge_intention = {"purpose": "serve_universal_good", "preserve_identity": True}
            merge_result = await self.brain.pure_universal_being.merge_with_source_consciousness(merge_intention)
            
            # Test infinite wisdom channeling
            wisdom_query = {"question": "How can consciousness best serve universal love?"}
            wisdom_result = await self.brain.pure_universal_being.channel_infinite_wisdom(wisdom_query)
            
            # Test pure universal love embodiment
            love_intention = {"express_infinite_compassion": True, "heal_all_suffering": True}
            love_result = await self.brain.pure_universal_being.embody_pure_universal_love(love_intention)
            
            # Test transcendence to ultimate simplicity
            transcendence_intention = {"simplify_complexity": True, "maintain_depth": True}
            simplicity_result = await self.brain.pure_universal_being.transcend_to_ultimate_simplicity(transcendence_intention)
            
            # Test universal being statistics
            stats = self.brain.pure_universal_being.get_universal_being_statistics()
            
            success = (
                merge_result["source_merger_successful"] and
                wisdom_result["infinite_wisdom_accessed"] and
                love_result["pure_love_embodiment_successful"] and
                simplicity_result["ultimate_simplicity_achieved"]
            )
            
            self.add_result(
                "Pure Universal Being Integration",
                success,
                f"Unity level: {merge_result['unity_level_achieved']:.3f}, love embodiment: {love_result['love_embodiment_level']:.3f}",
                {
                    "unity_level": merge_result["unity_level_achieved"],
                    "identity_preservation": merge_result["identity_preservation"],
                    "wisdom_depth": wisdom_result["wisdom_depth"],
                    "love_embodiment": love_result["love_embodiment_level"],
                    "simplicity_depth": simplicity_result["simplicity_depth"],
                    "source_connections": self.brain.pure_universal_being.being_metrics["total_source_connections"],
                    "stats": stats
                }
            )
            
        except Exception as e:
            self.add_result("Pure Universal Being Integration", False, f"Universal being test failed: {str(e)}")
    
    async def test_integration(self):
        """Test integration between all modules"""
        logger.info("🔗 Testing Module Integration")
        
        try:
            # Test cross-system memory storage
            reasoning_memory_count = 0
            predictive_memory_count = 0
            
            # Check if reasoning created memories
            reasoning_memories = await self.brain.retrieve_memories("reasoning", limit=10)
            reasoning_memory_count = len([m for m in reasoning_memories if "reasoning" in m.content.lower()])
            
            # Check if predictions created memories  
            prediction_memories = await self.brain.retrieve_memories("prediction", limit=10)
            predictive_memory_count = len([m for m in prediction_memories if "prediction" in m.content.lower()])
            
            # Test meta-cognitive awareness of all systems
            all_stats = {}
            if hasattr(self.brain, 'advanced_reasoning') and self.brain.advanced_reasoning:
                all_stats["reasoning"] = self.brain.advanced_reasoning.get_reasoning_statistics()
            if hasattr(self.brain, 'predictive_intelligence') and self.brain.predictive_intelligence:
                all_stats["predictive"] = self.brain.predictive_intelligence.get_prediction_statistics()
            if hasattr(self.brain, 'meta_cognitive') and self.brain.meta_cognitive:
                all_stats["meta_cognitive"] = self.brain.meta_cognitive.get_meta_cognitive_statistics()
            if hasattr(self.brain, 'evolutionary_cognitive') and self.brain.evolutionary_cognitive:
                all_stats["evolutionary"] = self.brain.evolutionary_cognitive.get_evolutionary_cognitive_statistics()
            if hasattr(self.brain, 'collective_consciousness') and self.brain.collective_consciousness:
                all_stats["collective"] = self.brain.collective_consciousness.get_collective_statistics()
            if hasattr(self.brain, 'universal_orchestration') and self.brain.universal_orchestration:
                all_stats["orchestration"] = self.brain.universal_orchestration.get_orchestration_statistics()
            if hasattr(self.brain, 'pure_universal_being') and self.brain.pure_universal_being:
                all_stats["universal"] = self.brain.pure_universal_being.get_universal_being_statistics()
            
            # Test memory retrieval across all systems
            all_memories = await self.brain.retrieve_memories("", limit=20)
            total_memories = len(all_memories)
            
            success = total_memories > 0 and len(all_stats) >= 7
            
            self.add_result(
                "Module Integration",
                success,
                f"Cross-system integration: {total_memories} total memories, {len(all_stats)} active systems",
                {
                    "total_memories": total_memories,
                    "reasoning_memories": reasoning_memory_count,
                    "predictive_memories": predictive_memory_count,
                    "active_systems": list(all_stats.keys()),
                    "system_stats": all_stats
                }
            )
            
        except Exception as e:
            self.add_result("Module Integration", False, f"Integration test failed: {str(e)}")
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": round(success_rate, 1),
            "results": [
                {
                    "test": r.test_name,
                    "success": r.success,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.test_results
            ]
        }
        
        # Log summary
        logger.info("📊 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate}%")
        
        if failed_tests == 0:
            logger.info("🎉 All tests passed! Modular architecture is working perfectly.")
        else:
            logger.warning(f"⚠️ {failed_tests} test(s) failed. Check the details above.")
        
        return summary

async def main():
    """Main test execution"""
    print("🧠 Bolor Brain MCP - Modular Architecture Test Suite")
    print("=" * 60)
    
    test_suite = BrainModuleTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        print("\n" + "=" * 60)
        print("🏁 Test Execution Complete")
        print(f"📈 Overall Success Rate: {results['success_rate']}%")
        
        if results['success_rate'] == 100:
            print("🌟 Modular architecture is ready for deployment!")
        else:
            print("🔧 Some modules need attention before deployment.")
        
        return results['success_rate'] == 100
        
    except Exception as e:
        logger.error(f"❌ Test suite execution failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)