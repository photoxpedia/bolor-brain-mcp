"""
Advanced Reasoning Engine Module
Tier 1 cognitive capabilities with 6-strategy reasoning
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
import time
import asyncio
import inspect

logger = logging.getLogger(__name__)

@dataclass
class ReasoningStep:
    """A single step in a reasoning process"""
    step_id: str
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning_type: str
    confidence: float
    timestamp: float = field(default_factory=time.time)

@dataclass 
class ReasoningChain:
    """A complete reasoning chain with multiple steps"""
    chain_id: str
    problem: str
    strategy: str
    steps: List[ReasoningStep]
    final_conclusion: str
    overall_confidence: float
    reasoning_time: float
    timestamp: float = field(default_factory=time.time)

class AdvancedReasoningEngine:
    """Tier 1: Multi-strategy reasoning system with chain-of-thought capabilities"""

    def __init__(self, brain):
        self.brain = brain
        self.reasoning_strategies = {
            "analytical": self._analytical_reasoning,
            "creative": self._creative_reasoning,
            "critical": self._critical_reasoning,
            "systems": self._systems_reasoning,
            "ethical": self._ethical_reasoning,
            "intuitive": self._intuitive_reasoning
        }
        self.reasoning_history: List[ReasoningChain] = []
        logger.info("Advanced Reasoning Engine initialized with 6 strategies")

    def _get_drive_manager(self):
        """Get drive manager from brain's memory bridge if available"""
        if hasattr(self.brain, 'memory_bridge') and self.brain.memory_bridge:
            return self.brain.memory_bridge.drives
        return None

    def _get_dominant_drive(self) -> tuple:
        """Get the current dominant drive and its urgency"""
        drives = self._get_drive_manager()
        if drives:
            return drives.get_state().get_dominant_drive()
        return None, 0.0

    def _record_drive_action(self, action: str):
        """Record an action for drive satisfaction"""
        drives = self._get_drive_manager()
        if drives:
            drives.record_action(action)

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

    def _weight_strategies_by_drives(self) -> Dict[str, float]:
        """
        Score each strategy by how well it satisfies current drives.
        Returns a dict of strategy -> drive-weighted score.
        """
        drive_state = self._get_drive_state()
        if not drive_state:
            # No drive state - return neutral weights
            return {s: 0.5 for s in self.reasoning_strategies.keys()}

        # Define how each strategy aligns with each drive
        # Higher alignment = strategy better satisfies that drive
        strategy_drive_alignment = {
            "analytical": {"competence": 0.8, "stability": 0.6, "curiosity": 0.3},
            "creative": {"curiosity": 0.9, "novelty": 0.8, "competence": 0.2},
            "critical": {"competence": 0.7, "stability": 0.5, "curiosity": 0.4},
            "systems": {"stability": 0.8, "competence": 0.6, "curiosity": 0.5},
            "ethical": {"connection": 0.9, "stability": 0.4, "competence": 0.3},
            "intuitive": {"novelty": 0.7, "curiosity": 0.6, "connection": 0.4}
        }

        weights = {}
        for strategy, alignments in strategy_drive_alignment.items():
            score = 0.0
            alignment_count = 0
            for drive_name, alignment_strength in alignments.items():
                drive_info = drive_state.get(drive_name, {})
                drive_urgency = drive_info.get("urgency", 0.0)
                score += alignment_strength * drive_urgency
                alignment_count += 1
            # Normalize by number of alignments
            weights[strategy] = score / max(alignment_count, 1)
        return weights

    def _get_keyword_strategy_scores(self, problem: str) -> Dict[str, float]:
        """
        Score strategies based on keyword matches in the problem.
        Returns a dict of strategy -> keyword match score (0.0 to 1.0).
        """
        problem_lower = problem.lower()

        # Keywords for each strategy
        strategy_keywords = {
            "analytical": ["analyze", "break down", "components", "structure", "examine", "detail"],
            "creative": ["create", "innovative", "new", "brainstorm", "imagine", "invent", "design"],
            "critical": ["evaluate", "critique", "assess", "judge", "validate", "question", "challenge"],
            "systems": ["system", "holistic", "interconnected", "relationships", "whole", "dynamics"],
            "ethical": ["ethical", "moral", "right", "wrong", "should", "fair", "just"],
            "intuitive": ["feel", "sense", "intuition", "gut", "instinct", "hunch"]
        }

        scores = {}
        for strategy, keywords in strategy_keywords.items():
            matches = sum(1 for kw in keywords if kw in problem_lower)
            # Normalize: 2+ matches = full score, 1 match = 0.5, 0 = 0
            if matches >= 2:
                scores[strategy] = 1.0
            elif matches == 1:
                scores[strategy] = 0.5
            else:
                scores[strategy] = 0.0
        return scores

    async def solve_complex_problem(self, problem: str, context: Dict[str, Any] = None) -> ReasoningChain:
        """Main entry point for complex problem solving"""
        start_time = time.time()
        
        # Step 1: Problem analysis and strategy selection
        strategy = self._select_reasoning_strategy(problem, context)
        
        # Step 2: Gather relevant memory context
        memory_context = await self._gather_reasoning_context(problem, context)
        
        # Step 3: Execute reasoning chain
        reasoning_steps = await self._execute_reasoning_strategy(problem, strategy, memory_context, context)
        
        # Step 4: Synthesize final conclusion
        final_conclusion = self._synthesize_conclusion(reasoning_steps)
        
        # Step 5: Calculate confidence
        confidence = self._calculate_reasoning_confidence(reasoning_steps)
        
        reasoning_time = time.time() - start_time
        
        # Create reasoning chain
        chain = ReasoningChain(
            chain_id=str(uuid.uuid4()),
            problem=problem,
            strategy=strategy,
            steps=reasoning_steps,
            final_conclusion=final_conclusion,
            overall_confidence=confidence,
            reasoning_time=reasoning_time
        )
        
        self.reasoning_history.append(chain)

        # Store reasoning in memory for future reference
        memory_content = f"Reasoning: {problem} -> {final_conclusion} (strategy: {strategy}, confidence: {confidence:.2f})"
        await self._store_reasoning_memory(memory_content, chain)

        # Record drive satisfaction - reasoning satisfies curiosity and competence
        if confidence >= 0.7:
            self._record_drive_action("reason_successfully")
        else:
            self._record_drive_action("reason")

        return chain
    
    def _select_reasoning_strategy(self, problem: str, context: Dict[str, Any] = None) -> str:
        """
        Select the most appropriate reasoning strategy for the problem.

        Uses a blended scoring approach:
        - 60% weight on keyword matches in the problem text
        - 40% weight on current drive state alignment

        This ensures drives actively influence strategy selection, not just as fallback.
        """
        # Get keyword-based scores (0.0 to 1.0 for each strategy)
        keyword_scores = self._get_keyword_strategy_scores(problem)

        # Get drive-based weights (0.0 to 1.0 for each strategy)
        drive_weights = self._weight_strategies_by_drives()

        # Blend scores: 60% keywords, 40% drives
        KEYWORD_WEIGHT = 0.6
        DRIVE_WEIGHT = 0.4

        final_scores = {}
        for strategy in self.reasoning_strategies.keys():
            kw_score = keyword_scores.get(strategy, 0.0)
            drive_score = drive_weights.get(strategy, 0.5)
            final_scores[strategy] = KEYWORD_WEIGHT * kw_score + DRIVE_WEIGHT * drive_score

        # Select strategy with highest blended score
        best_strategy = max(final_scores, key=final_scores.get)
        best_score = final_scores[best_strategy]

        # Log the selection for debugging
        logger.debug(
            f"Strategy selection - keywords: {keyword_scores}, "
            f"drives: {drive_weights}, final: {final_scores}, "
            f"selected: {best_strategy} ({best_score:.3f})"
        )

        # If all scores are very low (no clear signal), default to analytical
        if best_score < 0.15:
            return "analytical"

        return best_strategy
    
    async def _gather_reasoning_context(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gather relevant memories and context for reasoning"""
        try:
            # Get relevant memories from brain's memory system
            relevant_memories = []
            if hasattr(self.brain, 'retrieve_memories'):
                memories = await self.brain.retrieve_memories(problem[:100], limit=5)
                relevant_memories = [m.content for m in memories]
            
            return {
                "problem": problem,
                "relevant_memories": relevant_memories,
                "user_context": context or {},
                "cognitive_state": {
                    "attention_focus": getattr(self.brain.cognitive_state, 'attention_focus', ''),
                    "confidence": getattr(self.brain.cognitive_state, 'confidence', 0.7),
                    "emotional_valence": getattr(self.brain.cognitive_state, 'emotional_valence', 0.0)
                }
            }
        except Exception as e:
            logger.error(f"Error gathering reasoning context: {e}")
            return {"problem": problem, "user_context": context or {}}
    
    async def _execute_reasoning_strategy(self, problem: str, strategy: str, 
                                        memory_context: Dict[str, Any], 
                                        user_context: Dict[str, Any] = None) -> List[ReasoningStep]:
        """Execute the selected reasoning strategy"""
        try:
            strategy_func = self.reasoning_strategies.get(strategy, self._analytical_reasoning)
            return await strategy_func(problem, memory_context, user_context)
        except Exception as e:
            logger.error(f"Error executing reasoning strategy {strategy}: {e}")
            # Fallback to basic analytical reasoning
            return await self._analytical_reasoning(problem, memory_context, user_context)
    
    async def _analytical_reasoning(self, problem: str, memory_context: Dict[str, Any], 
                                   user_context: Dict[str, Any] = None) -> List[ReasoningStep]:
        """Analytical reasoning: systematic breakdown and analysis"""
        steps = []
        
        # Step 1: Problem decomposition
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Decompose problem into components",
            input_data={"problem": problem},
            output_data={"components": ["main_issue", "constraints", "requirements", "stakeholders"]},
            reasoning_type="decomposition",
            confidence=0.8
        ))
        
        # Step 2: Component analysis
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Analyze each component systematically",
            input_data={"components": ["main_issue", "constraints", "requirements", "stakeholders"]},
            output_data={"analysis": "Systematic analysis of problem components"},
            reasoning_type="analysis",
            confidence=0.75
        ))
        
        # Step 3: Solution synthesis
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Synthesize solution from component analysis",
            input_data={"analysis": "Systematic analysis of problem components"},
            output_data={"solution": "Logically derived solution based on component analysis"},
            reasoning_type="synthesis",
            confidence=0.7
        ))
        
        return steps
    
    async def _creative_reasoning(self, problem: str, memory_context: Dict[str, Any], 
                                 user_context: Dict[str, Any] = None) -> List[ReasoningStep]:
        """Creative reasoning: novel pattern generation and synthesis"""
        steps = []
        
        # Step 1: Divergent thinking
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Generate multiple diverse perspectives",
            input_data={"problem": problem},
            output_data={"perspectives": ["perspective_1", "perspective_2", "perspective_3"]},
            reasoning_type="divergent",
            confidence=0.85
        ))
        
        # Step 2: Pattern connection
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Connect patterns across different domains",
            input_data={"perspectives": ["perspective_1", "perspective_2", "perspective_3"]},
            output_data={"connections": "Novel connections between disparate concepts"},
            reasoning_type="pattern_connection",
            confidence=0.7
        ))
        
        # Step 3: Innovation synthesis
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Synthesize innovative solution",
            input_data={"connections": "Novel connections between disparate concepts"},
            output_data={"innovation": "Creative solution combining novel patterns"},
            reasoning_type="innovation",
            confidence=0.75
        ))
        
        return steps
    
    async def _critical_reasoning(self, problem: str, memory_context: Dict[str, Any], 
                                 user_context: Dict[str, Any] = None) -> List[ReasoningStep]:
        """Critical reasoning: assumption validation and bias detection"""
        steps = []
        
        # Step 1: Assumption identification
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Identify underlying assumptions",
            input_data={"problem": problem},
            output_data={"assumptions": ["assumption_1", "assumption_2", "assumption_3"]},
            reasoning_type="assumption_analysis",
            confidence=0.8
        ))
        
        # Step 2: Bias detection
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Detect potential cognitive biases",
            input_data={"assumptions": ["assumption_1", "assumption_2", "assumption_3"]},
            output_data={"biases": "Identified potential confirmation and availability biases"},
            reasoning_type="bias_detection",
            confidence=0.75
        ))
        
        # Step 3: Evidence evaluation
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Evaluate evidence quality and reliability",
            input_data={"biases": "Identified potential confirmation and availability biases"},
            output_data={"evaluation": "Critical assessment of evidence and reasoning quality"},
            reasoning_type="evidence_evaluation",
            confidence=0.8
        ))
        
        return steps
    
    async def _systems_reasoning(self, problem: str, memory_context: Dict[str, Any], 
                                user_context: Dict[str, Any] = None) -> List[ReasoningStep]:
        """Systems reasoning: holistic relationship modeling"""
        steps = []
        
        # Step 1: System mapping
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Map system components and relationships",
            input_data={"problem": problem},
            output_data={"system_map": "Holistic view of interconnected components"},
            reasoning_type="system_mapping",
            confidence=0.8
        ))
        
        # Step 2: Feedback loop analysis
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Analyze feedback loops and emergent properties",
            input_data={"system_map": "Holistic view of interconnected components"},
            output_data={"dynamics": "Understanding of system dynamics and emergence"},
            reasoning_type="dynamics_analysis",
            confidence=0.7
        ))
        
        # Step 3: Leverage point identification
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Identify highest leverage intervention points",
            input_data={"dynamics": "Understanding of system dynamics and emergence"},
            output_data={"leverage_points": "Strategic intervention points for maximum impact"},
            reasoning_type="leverage_identification",
            confidence=0.75
        ))
        
        return steps
    
    async def _ethical_reasoning(self, problem: str, memory_context: Dict[str, Any], 
                                user_context: Dict[str, Any] = None) -> List[ReasoningStep]:
        """Ethical reasoning: value-based decision frameworks"""
        steps = []
        
        # Step 1: Stakeholder analysis
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Identify all affected stakeholders",
            input_data={"problem": problem},
            output_data={"stakeholders": ["primary_stakeholders", "secondary_stakeholders", "future_generations"]},
            reasoning_type="stakeholder_analysis",
            confidence=0.85
        ))
        
        # Step 2: Value assessment
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Assess competing values and principles",
            input_data={"stakeholders": ["primary_stakeholders", "secondary_stakeholders", "future_generations"]},
            output_data={"values": "Analysis of competing ethical principles and values"},
            reasoning_type="value_assessment",
            confidence=0.75
        ))
        
        # Step 3: Ethical decision synthesis
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Synthesize ethically grounded decision",
            input_data={"values": "Analysis of competing ethical principles and values"},
            output_data={"ethical_decision": "Decision that balances multiple ethical considerations"},
            reasoning_type="ethical_synthesis",
            confidence=0.8
        ))
        
        return steps
    
    async def _intuitive_reasoning(self, problem: str, memory_context: Dict[str, Any], 
                                  user_context: Dict[str, Any] = None) -> List[ReasoningStep]:
        """Intuitive reasoning: pattern recognition beyond explicit logic"""
        steps = []
        
        # Step 1: Pattern sensing
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Sense implicit patterns and connections",
            input_data={"problem": problem},
            output_data={"patterns": "Subconscious pattern recognition"},
            reasoning_type="pattern_sensing",
            confidence=0.6
        ))
        
        # Step 2: Holistic integration
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Integrate multiple information sources holistically",
            input_data={"patterns": "Subconscious pattern recognition"},
            output_data={"integration": "Holistic understanding beyond logical analysis"},
            reasoning_type="holistic_integration",
            confidence=0.65
        ))
        
        # Step 3: Insight emergence
        steps.append(ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="Allow insight to emerge from integration",
            input_data={"integration": "Holistic understanding beyond logical analysis"},
            output_data={"insight": "Intuitive understanding that transcends analytical reasoning"},
            reasoning_type="insight_emergence",
            confidence=0.7
        ))
        
        return steps
    
    def _synthesize_conclusion(self, steps: List[ReasoningStep]) -> str:
        """Synthesize final conclusion from reasoning steps"""
        if not steps:
            return "No reasoning steps completed"
        
        # Extract key outputs from reasoning steps
        key_outputs = [step.output_data for step in steps]
        
        # Simple synthesis based on the last step's output
        final_step = steps[-1]
        conclusion = f"Based on {final_step.reasoning_type}, "
        
        if 'solution' in final_step.output_data:
            conclusion += final_step.output_data['solution']
        elif 'innovation' in final_step.output_data:
            conclusion += final_step.output_data['innovation']
        elif 'evaluation' in final_step.output_data:
            conclusion += final_step.output_data['evaluation']
        elif 'leverage_points' in final_step.output_data:
            conclusion += final_step.output_data['leverage_points']
        elif 'ethical_decision' in final_step.output_data:
            conclusion += final_step.output_data['ethical_decision']
        elif 'insight' in final_step.output_data:
            conclusion += final_step.output_data['insight']
        else:
            conclusion += "reasoning process completed successfully"
        
        return conclusion
    
    def _calculate_reasoning_confidence(self, steps: List[ReasoningStep]) -> float:
        """Calculate overall confidence based on reasoning steps"""
        if not steps:
            return 0.0
        
        # Average confidence across all steps
        total_confidence = sum(step.confidence for step in steps)
        return total_confidence / len(steps)
    
    async def _store_reasoning_memory(self, content: str, chain: ReasoningChain):
        """Store reasoning chain as memory for future reference"""
        try:
            if hasattr(self.brain, 'store_memory'):
                result = self.brain.store_memory(
                    content=content,
                    memory_type="procedural",
                    importance=min(chain.overall_confidence, 1.0),
                    metadata={
                        "reasoning_chain_id": chain.chain_id,
                        "strategy": chain.strategy,
                        "reasoning_time": chain.reasoning_time
                    }
                )
                # Handle both sync and async store_memory
                if inspect.iscoroutine(result):
                    await result
        except Exception as e:
            logger.error(f"Error storing reasoning memory: {e}")
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get reasoning engine statistics"""
        if not self.reasoning_history:
            return {
                "total_reasoning_chains": 0,
                "strategy_usage": {},
                "average_confidence": 0.0,
                "average_reasoning_time": 0.0
            }
        
        strategy_counts = {}
        total_confidence = 0
        total_time = 0
        
        for chain in self.reasoning_history:
            strategy_counts[chain.strategy] = strategy_counts.get(chain.strategy, 0) + 1
            total_confidence += chain.overall_confidence
            total_time += chain.reasoning_time
        
        return {
            "total_reasoning_chains": len(self.reasoning_history),
            "strategy_usage": strategy_counts,
            "average_confidence": total_confidence / len(self.reasoning_history),
            "average_reasoning_time": total_time / len(self.reasoning_history),
            "available_strategies": list(self.reasoning_strategies.keys())
        }