"""
Tier 3: Meta-Cognitive Intelligence Engine  
Self-reflection, optimization, and cognitive adaptation
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
import time

logger = logging.getLogger(__name__)

@dataclass
class CognitiveOptimization:
    """Represents a cognitive optimization decision"""
    optimization_id: str
    optimization_type: str  # "strategy_adjustment", "threshold_tuning", "pattern_enhancement"
    target_component: str   # Which part of the brain to optimize
    current_performance: float
    target_performance: float
    optimization_actions: List[str]
    confidence: float
    expected_benefit: str
    implementation_priority: str  # "immediate", "high", "normal", "low"

@dataclass
class MetaInsight:
    """Represents meta-cognitive insights about brain performance"""
    insight_id: str
    insight_type: str  # "performance_pattern", "learning_opportunity", "cognitive_drift"
    affected_systems: List[str]
    insight_description: str
    confidence: float
    actionable_recommendations: List[str]
    supporting_evidence: List[str]
    timestamp: float = field(default_factory=time.time)


@dataclass
class CognitiveStateBus:
    """
    Shared state for cross-tier communication.

    This is the central coordination mechanism that allows all cognitive tiers
    to share context, drive state, and outputs. The metacognitive tier acts
    as coordinator, updating and reading this bus to orchestrate cognition.
    """
    # Current focus and context
    active_problem: str = ""
    problem_domain: str = ""

    # Drive state (cached, updated by coordinator)
    drive_snapshot: Dict[str, float] = field(default_factory=dict)
    dominant_drive: str = ""

    # Tier outputs (set by each tier, read by others)
    reasoning_conclusion: str = ""
    reasoning_confidence: float = 0.0
    reasoning_strategy_used: str = ""

    predictions_active: List[Dict] = field(default_factory=list)
    prediction_confidence: float = 0.0

    evolution_generation: int = 0
    creative_insights: List[str] = field(default_factory=list)

    # Coordination signals
    attention_shift_requested: bool = False
    attention_target: str = ""

    # Performance feedback
    last_action_success: bool = True
    performance_trend: str = "stable"  # "improving", "stable", "declining"

    # Timestamps
    last_updated: float = field(default_factory=time.time)


class MetaCognitiveIntelligenceEngine:
    """Tier 3: Unified Meta-Cognitive Intelligence Engine
    
    A single integrated system that thinks about how it thinks, optimizes itself,
    learns across contexts, and coordinates all cognitive processes seamlessly.
    Just like a human brain - everything interconnected and working together.
    """
    
    def __init__(self, brain):
        self.brain = brain

        # Performance tracking for all brain systems
        self.performance_history = {
            "reasoning": [],      # Track reasoning chain success rates
            "predictions": [],    # Track prediction accuracy
            "discovery": [],      # Track system discovery success
            "learning": [],       # Track learning effectiveness
            "guidance": [],       # Track guidance quality
            "memory": [],         # Track memory retrieval quality
            "drives": []          # Track drive satisfaction levels
        }

        # Meta-cognitive insights storage
        self.meta_insights = []

        # Optimization history
        self.optimizations_applied = []

        # Cross-system learning patterns
        self.cross_system_patterns = {}

        # Real-time cognitive state monitoring
        self.cognitive_monitoring = {
            "current_focus": "balanced",
            "performance_trend": "stable",
            "optimization_opportunities": [],
            "active_adjustments": [],
            "drive_satisfaction": {}  # Track drive states
        }

        # Adaptation parameters (self-tuning)
        self.adaptation_parameters = {
            "reasoning_confidence_threshold": 0.7,
            "prediction_confidence_threshold": 0.6,
            "discovery_aggressiveness": 0.5,
            "learning_rate": 0.1,
            "attention_focus_strength": 0.8
        }

        # Cognitive State Bus - shared state for cross-tier coordination
        self.state_bus = CognitiveStateBus()

        logger.info("Meta-Cognitive Intelligence Engine initialized with Coordinator - Brain can now think about thinking")

    def _get_drive_manager(self):
        """Get drive manager from brain's memory bridge if available"""
        if hasattr(self.brain, 'memory_bridge') and self.brain.memory_bridge:
            return self.brain.memory_bridge.drives
        return None

    def _get_drive_state(self) -> Dict[str, Dict[str, float]]:
        """Get full drive state with urgency values for all drives"""
        drives = self._get_drive_manager()
        if not drives:
            return {}
        try:
            state = drives.get_state()
            result = {}
            for drive_type in state.drives:
                drive = state.drives[drive_type]
                result[drive_type.value] = {
                    "level": drive.level,
                    "urgency": drive.urgency
                }
            return result
        except Exception as e:
            logger.debug(f"Error getting drive state: {e}")
            return {}

    def _calculate_optimization_priority(self, component: str, performance: float) -> str:
        """
        Calculate optimization priority based on both performance gap and drive urgency.

        Combines:
        - Performance gap: how far below optimal (1.0 - performance)
        - Drive urgency: how much relevant drives need this component

        Returns: "immediate", "high", "normal", or "low"
        """
        drive_state = self._get_drive_state()

        # Map components to drives they satisfy when performing well
        component_drives = {
            "reasoning": ["competence", "curiosity"],
            "predictions": ["stability", "curiosity"],
            "discovery": ["novelty", "curiosity"],
            "learning": ["competence", "novelty"],
            "memory": ["stability"]
        }

        # Calculate drive urgency for this component
        relevant_drives = component_drives.get(component, [])
        if relevant_drives and drive_state:
            drive_urgency = sum(
                drive_state.get(d, {}).get("urgency", 0.0)
                for d in relevant_drives
            ) / len(relevant_drives)
        else:
            drive_urgency = 0.5  # Default neutral urgency

        # Combined score: performance gap + drive urgency
        performance_gap = 1.0 - performance
        combined_score = 0.5 * performance_gap + 0.5 * drive_urgency

        # Map combined score to priority level
        if combined_score > 0.7:
            return "immediate"
        elif combined_score > 0.5:
            return "high"
        elif combined_score > 0.3:
            return "normal"
        return "low"

    def _adjust_adaptation_parameters(self):
        """
        Dynamically adjust adaptation parameters based on current drive state.

        - High competence drive: lower thresholds (more willing to try new things)
        - High stability drive: higher thresholds (more conservative)
        - High curiosity drive: increase discovery aggressiveness
        - High novelty drive: increase learning rate
        """
        drive_state = self._get_drive_state()
        if not drive_state:
            return

        # Get drive urgencies
        competence_urgency = drive_state.get("competence", {}).get("urgency", 0.5)
        stability_urgency = drive_state.get("stability", {}).get("urgency", 0.5)
        curiosity_urgency = drive_state.get("curiosity", {}).get("urgency", 0.5)
        novelty_urgency = drive_state.get("novelty", {}).get("urgency", 0.5)

        # Adjust reasoning confidence threshold
        # High competence drive → lower threshold (more willing to reason)
        # High stability drive → higher threshold (more conservative)
        base_threshold = 0.7
        threshold_adjustment = -competence_urgency * 0.15 + stability_urgency * 0.1
        self.adaptation_parameters["reasoning_confidence_threshold"] = max(
            0.5, min(0.85, base_threshold + threshold_adjustment)
        )

        # Adjust prediction confidence threshold
        base_pred_threshold = 0.6
        pred_adjustment = -curiosity_urgency * 0.1 + stability_urgency * 0.1
        self.adaptation_parameters["prediction_confidence_threshold"] = max(
            0.4, min(0.8, base_pred_threshold + pred_adjustment)
        )

        # Adjust discovery aggressiveness based on curiosity
        self.adaptation_parameters["discovery_aggressiveness"] = max(
            0.3, min(0.9, 0.5 + curiosity_urgency * 0.3)
        )

        # Adjust learning rate based on novelty and competence drives
        self.adaptation_parameters["learning_rate"] = max(
            0.05, min(0.3, 0.1 + novelty_urgency * 0.1 + competence_urgency * 0.1)
        )

        logger.debug(
            f"Adaptation parameters adjusted: {self.adaptation_parameters}"
        )

    def _record_drive_action(self, action: str):
        """Record an action for drive satisfaction"""
        drives = self._get_drive_manager()
        if drives:
            drives.record_action(action)
    
    async def analyze_cognitive_performance(self) -> Dict[str, Any]:
        """Analyze overall brain performance across all systems"""
        
        performance_analysis = {
            "overall_intelligence_score": 0.0,
            "component_scores": {},
            "optimization_opportunities": [],
            "meta_insights": [],
            "adaptive_recommendations": []
        }
        
        # Analyze reasoning performance
        reasoning_score = await self._analyze_reasoning_performance()
        performance_analysis["component_scores"]["reasoning"] = reasoning_score
        
        # Analyze prediction accuracy
        prediction_score = await self._analyze_prediction_performance()
        performance_analysis["component_scores"]["predictions"] = prediction_score
        
        # Analyze discovery effectiveness
        discovery_score = await self._analyze_discovery_performance()
        performance_analysis["component_scores"]["discovery"] = discovery_score
        
        # Analyze learning effectiveness
        learning_score = await self._analyze_learning_performance()
        performance_analysis["component_scores"]["learning"] = learning_score
        
        # Analyze memory efficiency
        memory_score = await self._analyze_memory_performance()
        performance_analysis["component_scores"]["memory"] = memory_score
        
        # Calculate overall intelligence score
        scores = list(performance_analysis["component_scores"].values())
        performance_analysis["overall_intelligence_score"] = sum(scores) / len(scores) if scores else 0.0
        
        # Generate meta-insights about cognitive patterns
        meta_insights = await self._generate_meta_insights(performance_analysis)
        performance_analysis["meta_insights"] = meta_insights
        
        # Identify optimization opportunities
        optimizations = await self._identify_optimization_opportunities(performance_analysis)
        performance_analysis["optimization_opportunities"] = optimizations
        
        # Generate adaptive recommendations
        recommendations = await self._generate_adaptive_recommendations(performance_analysis)
        performance_analysis["adaptive_recommendations"] = recommendations
        
        return performance_analysis
    
    async def optimize_cognitive_systems(self) -> Dict[str, Any]:
        """Automatically optimize all cognitive systems based on performance analysis"""
        
        optimization_results = {
            "optimizations_applied": [],
            "performance_improvements": {},
            "failed_optimizations": [],
            "next_optimization_cycle": time.time() + 3600  # Next optimization in 1 hour
        }
        
        # Get current performance analysis
        performance = await self.analyze_cognitive_performance()
        
        # Apply reasoning optimizations
        reasoning_opts = await self._optimize_reasoning_system(performance)
        optimization_results["optimizations_applied"].extend(reasoning_opts)
        
        # Apply prediction optimizations
        prediction_opts = await self._optimize_prediction_system(performance)
        optimization_results["optimizations_applied"].extend(prediction_opts)
        
        # Apply cross-system learning optimizations
        cross_system_opts = await self._optimize_cross_system_learning(performance)
        optimization_results["optimizations_applied"].extend(cross_system_opts)
        
        # Apply cognitive state optimizations
        cognitive_opts = await self._optimize_cognitive_state(performance)
        optimization_results["optimizations_applied"].extend(cognitive_opts)
        
        # Apply memory system optimizations
        memory_opts = await self._optimize_memory_system(performance)
        optimization_results["optimizations_applied"].extend(memory_opts)
        
        # Store optimization history
        self.optimizations_applied.extend(optimization_results["optimizations_applied"])
        
        logger.info(f"Applied {len(optimization_results['optimizations_applied'])} cognitive optimizations")
        
        return optimization_results
    
    async def adapt_cognitive_approach(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically adapt cognitive approach based on current context"""
        
        adaptation = {
            "context_analysis": context,
            "recommended_adjustments": [],
            "cognitive_state_changes": {},
            "strategy_modifications": {},
            "attention_focus_adjustments": {}
        }
        
        # Analyze current context to determine optimal cognitive approach
        context_type = self._analyze_context_type(context)
        
        # Adjust reasoning strategy selection based on context
        reasoning_adjustments = await self._adapt_reasoning_approach(context_type, context)
        adaptation["strategy_modifications"]["reasoning"] = reasoning_adjustments
        
        # Adjust prediction algorithms based on context
        prediction_adjustments = await self._adapt_prediction_approach(context_type, context)
        adaptation["strategy_modifications"]["predictions"] = prediction_adjustments
        
        # Adjust attention focus based on context complexity
        attention_adjustments = await self._adapt_attention_focus(context_type, context)
        adaptation["attention_focus_adjustments"] = attention_adjustments
        
        # Adjust cognitive state for optimal performance
        state_adjustments = await self._adapt_cognitive_state(context_type, context)
        adaptation["cognitive_state_changes"] = state_adjustments
        
        # Apply the adaptations
        await self._apply_cognitive_adaptations(adaptation)
        
        return adaptation
    
    async def learn_across_systems(self, system_interactions: List[Dict]) -> Dict[str, Any]:
        """Learn patterns and optimizations from interactions across different systems"""
        
        cross_learning = {
            "patterns_discovered": [],
            "knowledge_transfers": [],
            "optimization_insights": [],
            "performance_correlations": {}
        }
        
        # Analyze patterns across different discovered systems
        for interaction in system_interactions:
            pattern_analysis = await self._analyze_cross_system_pattern(interaction)
            cross_learning["patterns_discovered"].extend(pattern_analysis.get("patterns", []))
            
        # Find knowledge that can be transferred between systems
        knowledge_transfers = await self._identify_knowledge_transfers(system_interactions)
        cross_learning["knowledge_transfers"] = knowledge_transfers
        
        # Discover optimization insights that apply across systems
        optimization_insights = await self._discover_cross_system_optimizations(system_interactions)
        cross_learning["optimization_insights"] = optimization_insights
        
        # Analyze performance correlations between systems
        correlations = await self._analyze_performance_correlations(system_interactions)
        cross_learning["performance_correlations"] = correlations
        
        # Apply the cross-system learnings
        await self._apply_cross_system_learnings(cross_learning)
        
        return cross_learning
    
    def get_meta_cognitive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about meta-cognitive performance"""
        
        return {
            "meta_cognitive_engine": {
                "total_performance_analyses": len([h for histories in self.performance_history.values() for h in histories]),
                "optimizations_applied": len(self.optimizations_applied),
                "meta_insights_generated": len(self.meta_insights),
                "cross_system_patterns": len(self.cross_system_patterns),
                "current_intelligence_score": self._calculate_current_intelligence_score(),
                "adaptation_parameters": self.adaptation_parameters.copy(),
                "cognitive_monitoring_status": self.cognitive_monitoring.copy()
            },
            "system_performance_scores": {
                "reasoning_effectiveness": self._get_recent_performance_score("reasoning"),
                "prediction_accuracy": self._get_recent_performance_score("predictions"),  
                "discovery_success": self._get_recent_performance_score("discovery"),
                "learning_efficiency": self._get_recent_performance_score("learning"),
                "memory_quality": self._get_recent_performance_score("memory")
            },
            "optimization_history": [
                {
                    "optimization_type": opt.optimization_type,
                    "target": opt.target_component,
                    "performance_improvement": f"{opt.current_performance:.2f} -> {opt.target_performance:.2f}",
                    "confidence": opt.confidence
                }
                for opt in self.optimizations_applied[-10:]  # Last 10 optimizations
            ],
            "recent_meta_insights": [
                {
                    "type": insight.insight_type,
                    "description": insight.insight_description,
                    "affected_systems": insight.affected_systems,
                    "confidence": insight.confidence
                }
                for insight in self.meta_insights[-5:]  # Last 5 insights
            ]
        }
    
    # Performance analysis methods
    async def _analyze_reasoning_performance(self) -> float:
        """Analyze effectiveness of reasoning chains"""
        if not hasattr(self.brain, 'advanced_reasoning') or not self.brain.advanced_reasoning.reasoning_history:
            return 0.8
            
        recent_chains = self.brain.advanced_reasoning.reasoning_history[-10:]
        if not recent_chains:
            return 0.8
            
        # Calculate average confidence and success metrics
        confidence_scores = [chain.overall_confidence for chain in recent_chains]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Factor in reasoning time efficiency
        avg_time = sum(chain.reasoning_time for chain in recent_chains) / len(recent_chains)
        time_efficiency = max(0.1, min(1.0, 5.0 / avg_time))  # Optimal around 2-5 seconds
        
        # Combine metrics
        performance_score = (avg_confidence * 0.7) + (time_efficiency * 0.3)
        
        # Store performance data
        self.performance_history["reasoning"].append({
            "timestamp": time.time(),
            "score": performance_score,
            "confidence": avg_confidence,
            "efficiency": time_efficiency,
            "chains_analyzed": len(recent_chains)
        })
        
        return min(1.0, performance_score)
    
    async def _analyze_prediction_performance(self) -> float:
        """Analyze accuracy of predictions"""
        if not hasattr(self.brain, 'predictive_intelligence'):
            return 0.8
            
        prediction_stats = self.brain.predictive_intelligence.get_prediction_statistics()
        
        # Calculate prediction accuracy if we have feedback data
        total_predictions = prediction_stats.get("total_predictions", 0)
        if total_predictions == 0:
            return 0.8
            
        # For now, estimate based on confidence scores
        estimated_accuracy = 0.75  # Placeholder - would be calculated from feedback
        
        # Store performance data
        self.performance_history["predictions"].append({
            "timestamp": time.time(), 
            "score": estimated_accuracy,
            "total_predictions": total_predictions,
            "estimated_accuracy": estimated_accuracy
        })
        
        return estimated_accuracy
    
    async def _analyze_discovery_performance(self) -> float:
        """Analyze effectiveness of system discovery"""
        if not hasattr(self.brain, 'discovered_systems'):
            return 0.8
            
        # Count successful discoveries
        discovered_systems_count = len(self.brain.discovered_systems)
        discovery_score = min(1.0, 0.7 + (discovered_systems_count * 0.1))
        
        # Store performance data
        self.performance_history["discovery"].append({
            "timestamp": time.time(),
            "score": discovery_score,
            "systems_discovered": discovered_systems_count
        })
        
        return discovery_score
    
    async def _analyze_learning_performance(self) -> float:
        """Analyze effectiveness of continuous learning"""
        learning_score = 0.8  # Would be based on actual metrics in production
        
        # Store performance data  
        self.performance_history["learning"].append({
            "timestamp": time.time(),
            "score": learning_score
        })
        
        return learning_score
    
    async def _analyze_memory_performance(self) -> float:
        """Analyze memory system efficiency"""
        memory_stats = self.brain.get_memory_statistics()
        total_memories = memory_stats.get("total_memories", 0)
        
        # Calculate memory efficiency score
        if total_memories == 0:
            return 0.5
            
        # Factor in memory diversity and access patterns
        memory_types = len(memory_stats.get("memory_types", {}))
        type_diversity = min(1.0, memory_types / 5.0)  # Optimal at 5 types
        
        memory_score = (0.6 + (type_diversity * 0.4))
        
        # Store performance data
        self.performance_history["memory"].append({
            "timestamp": time.time(),
            "score": memory_score,
            "total_memories": total_memories,
            "type_diversity": type_diversity
        })
        
        return memory_score
    
    async def _generate_meta_insights(self, performance: Dict) -> List[MetaInsight]:
        """Generate insights about cognitive performance patterns"""
        insights = []
        
        # Analyze overall performance trend
        overall_score = performance["overall_intelligence_score"]
        if overall_score > 0.9:
            insights.append(MetaInsight(
                insight_id=f"meta_{uuid.uuid4().hex[:12]}",
                insight_type="performance_pattern",
                affected_systems=list(performance["component_scores"].keys()),
                insight_description="Cognitive systems operating at peak efficiency",
                confidence=0.9,
                actionable_recommendations=[
                    "Maintain current optimization parameters",
                    "Focus on knowledge expansion and learning"
                ],
                supporting_evidence=[f"Overall intelligence score: {overall_score:.2f}"]
            ))
        elif overall_score < 0.6:
            insights.append(MetaInsight(
                insight_id=f"meta_{uuid.uuid4().hex[:12]}",
                insight_type="learning_opportunity", 
                affected_systems=list(performance["component_scores"].keys()),
                insight_description="Multiple cognitive systems showing suboptimal performance",
                confidence=0.8,
                actionable_recommendations=[
                    "Implement comprehensive system optimization",
                    "Review and adjust adaptation parameters",
                    "Increase learning rate temporarily"
                ],
                supporting_evidence=[f"Overall intelligence score: {overall_score:.2f}"]
            ))
        
        # Analyze component-specific patterns
        for component, score in performance["component_scores"].items():
            if score < 0.5:
                insights.append(MetaInsight(
                    insight_id=f"meta_{uuid.uuid4().hex[:12]}",
                    insight_type="cognitive_drift",
                    affected_systems=[component],
                    insight_description=f"{component.title()} system showing performance degradation",
                    confidence=0.85,
                    actionable_recommendations=[
                        f"Recalibrate {component} system parameters",
                        f"Analyze {component} system for bottlenecks",
                        f"Consider {component} system architecture review"
                    ],
                    supporting_evidence=[f"{component} performance score: {score:.2f}"]
                ))
        
        # Store insights
        self.meta_insights.extend(insights)
        
        return insights
    
    async def _identify_optimization_opportunities(self, performance: Dict) -> List[CognitiveOptimization]:
        """
        Identify specific optimization opportunities.

        Uses drive-informed priority calculation to determine which optimizations
        are most urgent based on both performance gaps AND drive state.
        """
        # First, adjust adaptation parameters based on current drives
        self._adjust_adaptation_parameters()

        optimizations = []

        for component, score in performance["component_scores"].items():
            if score < 0.8:  # Room for improvement
                target_score = min(1.0, score + 0.2)

                # Calculate priority based on drives + performance
                priority = self._calculate_optimization_priority(component, score)

                optimizations.append(CognitiveOptimization(
                    optimization_id=f"opt_{uuid.uuid4().hex[:12]}",
                    optimization_type="performance_enhancement",
                    target_component=component,
                    current_performance=score,
                    target_performance=target_score,
                    optimization_actions=[
                        f"Tune {component} system parameters",
                        f"Optimize {component} algorithms",
                        f"Enhance {component} feedback loops"
                    ],
                    confidence=0.75,
                    expected_benefit=f"Improve {component} performance by {(target_score - score)*100:.1f}%",
                    implementation_priority=priority
                ))

        # Sort by priority (immediate > high > normal > low)
        priority_order = {"immediate": 0, "high": 1, "normal": 2, "low": 3}
        optimizations.sort(key=lambda o: priority_order.get(o.implementation_priority, 3))

        return optimizations
    
    async def _generate_adaptive_recommendations(self, performance: Dict) -> List[str]:
        """Generate recommendations for cognitive adaptation"""
        recommendations = []
        
        overall_score = performance["overall_intelligence_score"]
        
        if overall_score > 0.85:
            recommendations.extend([
                "Increase cognitive challenge level for continued growth",
                "Explore advanced reasoning strategies",
                "Enhance cross-system learning capabilities"
            ])
        elif overall_score < 0.65:
            recommendations.extend([
                "Implement immediate performance optimization",
                "Simplify cognitive processes temporarily",
                "Focus on core competency development"
            ])
        else:
            recommendations.extend([
                "Maintain balanced cognitive development",
                "Gradually increase system complexity",
                "Monitor performance trends closely"
            ])
        
        return recommendations
    
    # Context adaptation methods
    def _analyze_context_type(self, context: Dict[str, Any]) -> str:
        """Analyze context to determine optimal cognitive approach"""
        if "problem" in context and "complex" in str(context.get("problem", "")).lower():
            return "complex_problem_solving"
        elif "creative" in str(context).lower():
            return "creative_thinking"
        elif "analysis" in str(context).lower():
            return "analytical_thinking"
        else:
            return "general_processing"
    
    async def _adapt_reasoning_approach(self, context_type: str, context: Dict) -> Dict[str, Any]:
        """Adapt reasoning approach based on context"""
        if context_type == "complex_problem_solving":
            return {
                "preferred_strategies": ["analytical", "critical", "systems"],
                "confidence_adjustment": -0.1,
                "max_reasoning_depth": 8
            }
        elif context_type == "creative_thinking":
            return {
                "preferred_strategies": ["creative", "intuitive"],
                "confidence_adjustment": 0.1,
                "max_reasoning_depth": 6
            }
        else:
            return {
                "preferred_strategies": ["analytical", "critical"],
                "confidence_adjustment": 0.0,
                "max_reasoning_depth": 5
            }
    
    async def _adapt_prediction_approach(self, context_type: str, context: Dict) -> Dict[str, Any]:
        """Adapt prediction approach based on context"""
        if context_type == "complex_problem_solving":
            return {
                "prediction_horizon": "medium_term",
                "confidence_threshold": 0.7,
                "focus_areas": ["likely_problem", "resource_need"]
            }
        else:
            return {
                "prediction_horizon": "short_term",
                "confidence_threshold": 0.6,
                "focus_areas": ["next_action", "optimization_opportunity"]
            }
    
    async def _adapt_attention_focus(self, context_type: str, context: Dict) -> Dict[str, Any]:
        """Adapt attention focus based on context"""
        if context_type == "complex_problem_solving":
            focus_adjustments = {
                "attention_intensity": 0.9,
                "focus_breadth": "narrow",
                "distraction_filtering": "high"
            }
        elif context_type == "creative_thinking":
            focus_adjustments = {
                "attention_intensity": 0.7,
                "focus_breadth": "wide", 
                "distraction_filtering": "low"
            }
        else:
            focus_adjustments = {
                "attention_intensity": 0.8,
                "focus_breadth": "balanced",
                "distraction_filtering": "medium"
            }
        
        # Apply focus adjustments to cognitive state
        if hasattr(self.brain, 'cognitive_state'):
            self.brain.cognitive_state.attention_focus = context_type
        
        return focus_adjustments
    
    async def _adapt_cognitive_state(self, context_type: str, context: Dict) -> Dict[str, Any]:
        """Adapt overall cognitive state based on context"""
        if context_type == "complex_problem_solving":
            state_adjustments = {
                "confidence": 0.7,
                "curiosity_level": 0.9,
                "processing_speed": 0.6
            }
        elif context_type == "creative_thinking":
            state_adjustments = {
                "confidence": 0.8,
                "curiosity_level": 1.0,
                "processing_speed": 0.8
            }
        else:
            state_adjustments = {
                "confidence": 0.75,
                "curiosity_level": 0.7,
                "processing_speed": 0.7
            }
        
        # Apply state adjustments
        if hasattr(self.brain, 'cognitive_state'):
            for key, value in state_adjustments.items():
                if hasattr(self.brain.cognitive_state, key):
                    setattr(self.brain.cognitive_state, key, value)
        
        return state_adjustments
    
    async def _apply_cognitive_adaptations(self, adaptation: Dict) -> None:
        """Apply the cognitive adaptations to the brain systems"""
        self.cognitive_monitoring["active_adjustments"].append({
            "timestamp": time.time(),
            "adaptation_type": "context_based",
            "adjustments": adaptation
        })
        
        # Keep only recent adjustments
        if len(self.cognitive_monitoring["active_adjustments"]) > 10:
            self.cognitive_monitoring["active_adjustments"] = self.cognitive_monitoring["active_adjustments"][-10:]
    
    # Utility methods
    def _calculate_current_intelligence_score(self) -> float:
        """Calculate current overall intelligence score"""
        recent_scores = []
        for system, history in self.performance_history.items():
            if history:
                recent_scores.append(history[-1]["score"])
        
        return sum(recent_scores) / len(recent_scores) if recent_scores else 0.8
    
    def _get_recent_performance_score(self, system: str) -> float:
        """Get most recent performance score for a system"""
        history = self.performance_history.get(system, [])
        return history[-1]["score"] if history else 0.8
    
    # Optimization methods (simplified for brevity)
    async def _optimize_reasoning_system(self, performance: Dict) -> List[CognitiveOptimization]:
        """Optimize the reasoning system based on performance data"""
        optimizations = []
        reasoning_score = performance["component_scores"].get("reasoning", 0.8)
        
        if reasoning_score < 0.8:
            current_threshold = self.adaptation_parameters["reasoning_confidence_threshold"]
            new_threshold = max(0.5, min(0.8, current_threshold + (0.8 - reasoning_score) * 0.1))
            self.adaptation_parameters["reasoning_confidence_threshold"] = new_threshold
            
            optimizations.append(CognitiveOptimization(
                optimization_id=f"reasoning_opt_{uuid.uuid4().hex[:12]}",
                optimization_type="threshold_tuning",
                target_component="reasoning",
                current_performance=reasoning_score,
                target_performance=min(1.0, reasoning_score + 0.15),
                optimization_actions=[f"Adjusted confidence threshold to {new_threshold}"],
                confidence=0.8,
                expected_benefit="Improved reasoning chain quality",
                implementation_priority="high" if reasoning_score < 0.6 else "normal"
            ))
        
        return optimizations
    
    async def _optimize_prediction_system(self, performance: Dict) -> List[CognitiveOptimization]:
        """Optimize the prediction system"""
        return []  # Simplified for brevity
    
    async def _optimize_cross_system_learning(self, performance: Dict) -> List[CognitiveOptimization]:
        """Optimize cross-system learning"""
        return []  # Simplified for brevity
    
    async def _optimize_cognitive_state(self, performance: Dict) -> List[CognitiveOptimization]:
        """Optimize cognitive state management"""
        return []  # Simplified for brevity
    
    async def _optimize_memory_system(self, performance: Dict) -> List[CognitiveOptimization]:
        """Optimize memory system performance"""
        return []  # Simplified for brevity
    
    # Cross-system learning methods (simplified)
    async def _analyze_cross_system_pattern(self, interaction: Dict) -> Dict[str, Any]:
        """Analyze patterns in cross-system interactions"""
        return {"patterns": []}
    
    async def _identify_knowledge_transfers(self, interactions: List[Dict]) -> List[Dict]:
        """Identify knowledge that can be transferred between systems"""
        return []
    
    async def _discover_cross_system_optimizations(self, interactions: List[Dict]) -> List[Dict]:
        """Discover optimization insights that apply across systems"""
        return []
    
    async def _analyze_performance_correlations(self, interactions: List[Dict]) -> Dict[str, float]:
        """Analyze performance correlations between different systems"""
        return {}
    
    async def _apply_cross_system_learnings(self, learning: Dict) -> None:
        """Apply insights from cross-system learning"""
        pass

    # =========================================================================
    # COGNITIVE COORDINATOR METHODS
    # =========================================================================

    async def coordinate_cognitive_cycle(self, problem: str,
                                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main coordination method - orchestrates a full cognitive cycle.

        Called before major decisions to sync all tiers:
        1. Updates state bus with current context
        2. Snapshots drive state
        3. Determines which tiers should be involved
        4. Coordinates tier execution
        5. Synthesizes results

        Args:
            problem: The problem/question to process
            context: Additional context for processing

        Returns:
            Coordinated result from all involved tiers
        """
        # 1. Update state bus with current context
        self.state_bus.active_problem = problem
        self.state_bus.problem_domain = self._categorize_problem_domain(problem)
        self.state_bus.last_updated = time.time()

        # 2. Snapshot drive state
        self._update_drive_snapshot()

        # 3. Determine which tiers should be involved
        tier_involvement = self._determine_tier_involvement(problem, context)

        # 4. Coordinate tier execution order
        results = {
            "problem": problem,
            "tiers_involved": [],
            "reasoning_result": None,
            "prediction_result": None,
            "evolution_result": None,
            "coordination_metadata": {
                "drive_snapshot": self.state_bus.drive_snapshot.copy(),
                "dominant_drive": self.state_bus.dominant_drive,
                "problem_domain": self.state_bus.problem_domain
            }
        }

        if tier_involvement.get("reasoning"):
            results["tiers_involved"].append("reasoning")
            results["reasoning_result"] = await self._coordinate_reasoning(problem, context)

        if tier_involvement.get("prediction"):
            results["tiers_involved"].append("prediction")
            results["prediction_result"] = await self._coordinate_prediction(context)

        if tier_involvement.get("evolution"):
            results["tiers_involved"].append("evolution")
            results["evolution_result"] = await self._coordinate_evolution()

        # 5. Synthesize coordinated result
        results["synthesis"] = self._synthesize_coordinated_result(results)

        # Record coordination action
        self._record_drive_action("coordinate")

        return results

    def _categorize_problem_domain(self, problem: str) -> str:
        """Categorize the domain of a problem for coordination"""
        problem_lower = problem.lower()

        if any(w in problem_lower for w in ["code", "program", "function", "bug", "error"]):
            return "technical"
        elif any(w in problem_lower for w in ["feel", "emotion", "happy", "sad", "angry"]):
            return "emotional"
        elif any(w in problem_lower for w in ["plan", "strategy", "goal", "achieve"]):
            return "planning"
        elif any(w in problem_lower for w in ["create", "design", "invent", "new"]):
            return "creative"
        elif any(w in problem_lower for w in ["why", "how", "explain", "understand"]):
            return "analytical"
        return "general"

    def _update_drive_snapshot(self):
        """Update cached drive state in bus"""
        drive_state = self._get_drive_state()
        for drive, info in drive_state.items():
            self.state_bus.drive_snapshot[drive] = info.get("urgency", 0.0)

        # Find dominant drive
        if self.state_bus.drive_snapshot:
            self.state_bus.dominant_drive = max(
                self.state_bus.drive_snapshot,
                key=self.state_bus.drive_snapshot.get
            )
        else:
            self.state_bus.dominant_drive = ""

    def _determine_tier_involvement(self, problem: str,
                                     context: Dict[str, Any] = None) -> Dict[str, bool]:
        """Decide which tiers should participate based on problem type and drives"""
        involvement = {
            "reasoning": True,  # Always involved
            "prediction": False,
            "evolution": False
        }

        problem_lower = problem.lower()

        # Prediction if asking about future or needs
        if any(w in problem_lower for w in ["will", "might", "expect", "need", "next", "predict"]):
            involvement["prediction"] = True

        # Evolution if creative or novel solution needed
        if any(w in problem_lower for w in ["new", "creative", "different", "innovate", "evolve"]):
            involvement["evolution"] = True

        # High novelty drive -> involve evolution
        if self.state_bus.drive_snapshot.get("novelty", 0) > 0.7:
            involvement["evolution"] = True

        # High curiosity drive -> involve prediction
        if self.state_bus.drive_snapshot.get("curiosity", 0) > 0.7:
            involvement["prediction"] = True

        return involvement

    async def _coordinate_reasoning(self, problem: str,
                                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordinate reasoning tier execution"""
        if not hasattr(self.brain, 'advanced_reasoning'):
            return {"status": "unavailable", "reason": "Reasoning tier not initialized"}

        try:
            result = await self.brain.advanced_reasoning.solve_complex_problem(problem, context)

            # Update state bus with reasoning output
            self.state_bus.reasoning_conclusion = result.final_conclusion
            self.state_bus.reasoning_confidence = result.overall_confidence
            self.state_bus.reasoning_strategy_used = result.strategy

            return {
                "status": "success",
                "conclusion": result.final_conclusion,
                "confidence": result.overall_confidence,
                "strategy": result.strategy,
                "reasoning_time": result.reasoning_time
            }
        except Exception as e:
            logger.error(f"Reasoning coordination failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _coordinate_prediction(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordinate prediction tier execution"""
        if not hasattr(self.brain, 'predictive_intelligence'):
            return {"status": "unavailable", "reason": "Prediction tier not initialized"}

        try:
            predictions = await self.brain.predictive_intelligence.predict_user_needs(
                context or {}
            )

            # Update state bus with prediction output
            self.state_bus.predictions_active = [
                {"type": p.prediction_type, "content": p.predicted_content, "confidence": p.confidence}
                for p in predictions
            ]
            if predictions:
                self.state_bus.prediction_confidence = predictions[0].confidence

            return {
                "status": "success",
                "predictions": [
                    {
                        "type": p.prediction_type,
                        "content": p.predicted_content,
                        "confidence": p.confidence
                    }
                    for p in predictions
                ]
            }
        except Exception as e:
            logger.error(f"Prediction coordination failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _coordinate_evolution(self) -> Dict[str, Any]:
        """Coordinate evolution tier execution"""
        if not hasattr(self.brain, 'evolutionary_cognitive'):
            return {"status": "unavailable", "reason": "Evolution tier not initialized"}

        try:
            result = await self.brain.evolutionary_cognitive.evolve_cognitive_capabilities()

            # Update state bus with evolution output
            self.state_bus.evolution_generation = self.brain.evolutionary_cognitive.evolution_generations
            self.state_bus.creative_insights = [
                insight.creative_solution[:100]
                for insight in self.brain.evolutionary_cognitive.creative_insights[-3:]
            ]

            return {
                "status": "success",
                "evolutions_applied": len(result.get("evolutions_applied", [])),
                "emergent_capabilities": result.get("emergent_capabilities", []),
                "generation": self.state_bus.evolution_generation
            }
        except Exception as e:
            logger.error(f"Evolution coordination failed: {e}")
            return {"status": "error", "error": str(e)}

    def _synthesize_coordinated_result(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from all coordinated tiers"""
        synthesis = {
            "primary_conclusion": "",
            "confidence": 0.0,
            "supporting_predictions": [],
            "evolution_contribution": ""
        }

        # Get primary conclusion from reasoning
        reasoning = results.get("reasoning_result", {})
        if reasoning.get("status") == "success":
            synthesis["primary_conclusion"] = reasoning.get("conclusion", "")
            synthesis["confidence"] = reasoning.get("confidence", 0.0)

        # Add supporting predictions
        prediction = results.get("prediction_result", {})
        if prediction.get("status") == "success":
            synthesis["supporting_predictions"] = prediction.get("predictions", [])[:3]

        # Note evolution contribution
        evolution = results.get("evolution_result", {})
        if evolution.get("status") == "success":
            evolutions = evolution.get("evolutions_applied", 0)
            if evolutions > 0:
                synthesis["evolution_contribution"] = f"Applied {evolutions} cognitive evolutions"

        return synthesis

    def get_state_bus(self) -> CognitiveStateBus:
        """Allow other tiers to read shared state"""
        return self.state_bus

    def report_tier_output(self, tier: str, output: Dict[str, Any]):
        """Allow tiers to report their outputs to the bus"""
        self.state_bus.last_updated = time.time()

        if tier == "reasoning":
            self.state_bus.reasoning_conclusion = output.get("conclusion", "")
            self.state_bus.reasoning_confidence = output.get("confidence", 0.0)
            self.state_bus.reasoning_strategy_used = output.get("strategy", "")

        elif tier == "prediction":
            self.state_bus.predictions_active = output.get("predictions", [])
            self.state_bus.prediction_confidence = output.get("confidence", 0.0)

        elif tier == "evolution":
            self.state_bus.evolution_generation = output.get("generation", 0)
            self.state_bus.creative_insights = output.get("insights", [])

    def report_action_result(self, success: bool):
        """Report the result of the last action for performance tracking"""
        self.state_bus.last_action_success = success

        # Update performance trend
        recent_successes = sum(1 for _ in range(5) if self.state_bus.last_action_success)
        if recent_successes >= 4:
            self.state_bus.performance_trend = "improving"
        elif recent_successes <= 1:
            self.state_bus.performance_trend = "declining"
        else:
            self.state_bus.performance_trend = "stable"

    def request_attention_shift(self, target: str):
        """Request an attention shift to a specific area"""
        self.state_bus.attention_shift_requested = True
        self.state_bus.attention_target = target
        logger.debug(f"Attention shift requested to: {target}")