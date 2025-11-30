"""
Tier 2: Predictive Intelligence Engine
Advanced pattern recognition and future modeling
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
import time

logger = logging.getLogger(__name__)

@dataclass
class PredictiveInsight:
    """A predictive insight about user needs or system behavior"""
    insight_id: str
    prediction_type: str  # "next_action", "likely_problem", "resource_need", "optimization_opportunity"
    predicted_content: str
    confidence: float
    reasoning: str
    supporting_patterns: List[str]
    time_horizon: str  # "immediate", "short_term", "medium_term", "long_term"
    suggested_preparations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

@dataclass
class PredictionPattern:
    """A learned pattern for making predictions"""
    pattern_id: str
    pattern_type: str
    trigger_conditions: Dict[str, Any]
    predicted_outcomes: List[str]
    confidence_history: List[float]
    success_rate: float
    last_updated: float = field(default_factory=time.time)

class PredictiveIntelligenceEngine:
    """Predictive engine that anticipates user needs based on patterns and reasoning history"""
    
    def __init__(self, brain):
        self.brain = brain
        self.prediction_patterns: Dict[str, PredictionPattern] = {}
        self.prediction_history: List[Dict[str, Any]] = []
        self.active_predictions: List[PredictiveInsight] = []
        logger.info("Predictive Intelligence Engine initialized")
        
    async def predict_user_needs(self, current_context: Dict[str, Any], history_depth: int = 10) -> List[PredictiveInsight]:
        """Predict what the user might need next based on patterns and context"""
        
        # Gather prediction context from multiple sources
        reasoning_context = self._analyze_reasoning_patterns(history_depth)
        interaction_context = self._analyze_interaction_patterns(current_context)
        temporal_context = self._analyze_temporal_patterns()
        
        # Generate predictions
        predictions = []
        
        # Predict based on reasoning patterns
        reasoning_predictions = await self._predict_from_reasoning_patterns(reasoning_context, current_context)
        predictions.extend(reasoning_predictions)
        
        # Predict based on interaction patterns  
        interaction_predictions = await self._predict_from_interaction_patterns(interaction_context, current_context)
        predictions.extend(interaction_predictions)
        
        # Predict based on temporal patterns
        temporal_predictions = await self._predict_from_temporal_patterns(temporal_context, current_context)
        predictions.extend(temporal_predictions)
        
        # Rank and filter predictions
        ranked_predictions = self._rank_predictions(predictions)
        
        # Update prediction history
        self._update_prediction_history(current_context, ranked_predictions)
        
        return ranked_predictions[:5]  # Return top 5 predictions
    
    def _analyze_reasoning_patterns(self, depth: int) -> Dict[str, Any]:
        """Analyze patterns from recent reasoning chains"""
        
        if not hasattr(self.brain, 'advanced_reasoning') or not self.brain.advanced_reasoning.reasoning_history:
            return {"patterns": [], "strategies": {}, "confidence_trends": []}
        
        recent_chains = self.brain.advanced_reasoning.reasoning_history[-depth:]
        
        # Analyze strategy usage patterns
        strategy_patterns = {}
        confidence_trends = []
        problem_types = []
        
        for chain in recent_chains:
            # Track strategy usage
            strategy = chain.strategy
            if strategy not in strategy_patterns:
                strategy_patterns[strategy] = {"count": 0, "avg_confidence": 0, "problems": []}
            
            strategy_patterns[strategy]["count"] += 1
            strategy_patterns[strategy]["avg_confidence"] = (
                (strategy_patterns[strategy]["avg_confidence"] * (strategy_patterns[strategy]["count"] - 1) + 
                 chain.overall_confidence) / strategy_patterns[strategy]["count"]
            )
            strategy_patterns[strategy]["problems"].append(chain.problem)
            
            confidence_trends.append(chain.overall_confidence)
            problem_types.append(self._categorize_problem_type(chain.problem))
        
        return {
            "patterns": recent_chains,
            "strategies": strategy_patterns,
            "confidence_trends": confidence_trends,
            "problem_types": problem_types
        }
    
    def _analyze_interaction_patterns(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns from user interactions"""
        
        # Extract patterns from current context
        context_keywords = []
        if "problem" in current_context:
            context_keywords.extend(current_context["problem"].lower().split())
        
        # Analyze memory retrieval patterns
        recent_queries = self._extract_recent_query_patterns()
        
        return {
            "current_keywords": context_keywords,
            "recent_queries": recent_queries,
            "context_type": self._determine_context_type(current_context)
        }
    
    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in usage"""
        
        current_hour = time.localtime().tm_hour
        current_day = time.localtime().tm_wday
        
        return {
            "current_hour": current_hour,
            "current_day": current_day, 
            "usage_time": "morning" if current_hour < 12 else "afternoon" if current_hour < 17 else "evening"
        }
    
    async def _predict_from_reasoning_patterns(self, reasoning_context: Dict[str, Any], current_context: Dict[str, Any]) -> List[PredictiveInsight]:
        """Generate predictions based on reasoning patterns"""
        
        predictions = []
        strategies = reasoning_context.get("strategies", {})
        
        # Predict likely next reasoning strategy
        if strategies:
            most_used_strategy = max(strategies.keys(), key=lambda k: strategies[k]["count"])
            
            prediction = PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                prediction_type="next_action",
                predicted_content=f"User will likely need {most_used_strategy} reasoning for their next problem",
                confidence=min(0.9, strategies[most_used_strategy]["avg_confidence"] + 0.1),
                reasoning=f"User has used {most_used_strategy} strategy {strategies[most_used_strategy]['count']} times recently with {strategies[most_used_strategy]['avg_confidence']:.2f} average confidence",
                supporting_patterns=[f"strategy_usage_{most_used_strategy}"],
                time_horizon="immediate",
                suggested_preparations=[
                    f"Pre-load {most_used_strategy} reasoning context",
                    "Gather relevant memories for reasoning",
                    "Prepare chain-of-thought framework"
                ]
            )
            predictions.append(prediction)
        
        # Predict confidence improvement opportunities
        confidence_trends = reasoning_context.get("confidence_trends", [])
        if len(confidence_trends) >= 3:
            recent_avg = sum(confidence_trends[-3:]) / 3
            if recent_avg < 0.7:
                prediction = PredictiveInsight(
                    insight_id=str(uuid.uuid4()),
                    prediction_type="optimization_opportunity", 
                    predicted_content="User may benefit from additional context or simpler reasoning approach",
                    confidence=0.8,
                    reasoning=f"Recent reasoning confidence is {recent_avg:.2f}, below optimal threshold",
                    supporting_patterns=["confidence_trend_analysis"],
                    time_horizon="short_term",
                    suggested_preparations=[
                        "Suggest breaking complex problems into smaller steps",
                        "Recommend gathering more context before reasoning",
                        "Offer alternative reasoning strategies"
                    ]
                )
                predictions.append(prediction)
        
        return predictions
    
    async def _predict_from_interaction_patterns(self, interaction_context: Dict[str, Any], current_context: Dict[str, Any]) -> List[PredictiveInsight]:
        """Generate predictions based on interaction patterns"""
        
        predictions = []
        keywords = interaction_context.get("current_keywords", [])
        
        # Predict related topics user might ask about
        if keywords:
            related_topics = self._find_related_topics(keywords)
            if related_topics:
                prediction = PredictiveInsight(
                    insight_id=str(uuid.uuid4()),
                    prediction_type="likely_problem",
                    predicted_content=f"User may ask about: {', '.join(related_topics[:3])}",
                    confidence=0.7,
                    reasoning=f"Based on current keywords: {', '.join(keywords[:5])}",
                    supporting_patterns=["keyword_analysis"],
                    time_horizon="short_term", 
                    suggested_preparations=[
                        f"Pre-load knowledge about {topic}" for topic in related_topics[:2]
                    ]
                )
                predictions.append(prediction)
        
        return predictions
    
    async def _predict_from_temporal_patterns(self, temporal_context: Dict[str, Any], current_context: Dict[str, Any]) -> List[PredictiveInsight]:
        """Generate predictions based on temporal patterns"""
        
        predictions = []
        usage_time = temporal_context.get("usage_time", "unknown")
        
        # Predict based on time of day
        if usage_time == "morning":
            prediction = PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                prediction_type="resource_need",
                predicted_content="User may need planning and organizational assistance",
                confidence=0.6,
                reasoning="Morning usage typically involves planning and setup tasks",
                supporting_patterns=["temporal_morning_pattern"],
                time_horizon="immediate",
                suggested_preparations=[
                    "Pre-load planning and organization knowledge",
                    "Prepare task prioritization frameworks",
                    "Ready project management insights"
                ]
            )
            predictions.append(prediction)
        elif usage_time == "evening":
            prediction = PredictiveInsight(
                insight_id=str(uuid.uuid4()),
                prediction_type="resource_need", 
                predicted_content="User may need review, analysis, or troubleshooting help",
                confidence=0.6,
                reasoning="Evening usage typically involves review and problem-solving",
                supporting_patterns=["temporal_evening_pattern"],
                time_horizon="immediate",
                suggested_preparations=[
                    "Pre-load debugging and analysis knowledge",
                    "Prepare troubleshooting frameworks",
                    "Ready review and assessment tools"
                ]
            )
            predictions.append(prediction)
        
        return predictions
    
    def _rank_predictions(self, predictions: List[PredictiveInsight]) -> List[PredictiveInsight]:
        """Rank predictions by confidence and relevance"""
        
        # Sort by confidence score descending
        ranked = sorted(predictions, key=lambda p: p.confidence, reverse=True)
        
        # Remove duplicates based on predicted_content similarity
        unique_predictions = []
        seen_content = set()
        
        for prediction in ranked:
            content_key = prediction.predicted_content.lower()[:50]  # First 50 chars
            if content_key not in seen_content:
                unique_predictions.append(prediction)
                seen_content.add(content_key)
        
        return unique_predictions
    
    def _update_prediction_history(self, context: Dict[str, Any], predictions: List[PredictiveInsight]):
        """Update prediction history for learning"""
        
        prediction_record = {
            "timestamp": time.time(),
            "context": context,
            "predictions_made": len(predictions),
            "top_prediction": predictions[0].predicted_content if predictions else None,
            "confidence_range": [p.confidence for p in predictions] if predictions else []
        }
        
        self.prediction_history.append(prediction_record)
        
        # Keep only recent history (last 100 predictions)
        if len(self.prediction_history) > 100:
            self.prediction_history = self.prediction_history[-100:]
    
    def _categorize_problem_type(self, problem: str) -> str:
        """Categorize the type of problem based on keywords"""
        problem_lower = problem.lower()
        
        if any(word in problem_lower for word in ["debug", "error", "fix", "broken"]):
            return "debugging"
        elif any(word in problem_lower for word in ["how", "learn", "understand", "explain"]):
            return "learning"
        elif any(word in problem_lower for word in ["optimize", "improve", "better", "faster"]):
            return "optimization"
        elif any(word in problem_lower for word in ["design", "create", "build", "implement"]):
            return "creation"
        else:
            return "general"
    
    def _extract_recent_query_patterns(self) -> List[str]:
        """Extract patterns from recent memory queries"""
        return []
    
    def _determine_context_type(self, context: Dict[str, Any]) -> str:
        """Determine the type of current context"""
        if "problem" in context:
            return "problem_solving"
        elif "learning" in context:
            return "learning"
        else:
            return "general"
    
    def _find_related_topics(self, keywords: List[str]) -> List[str]:
        """Find topics related to current keywords"""
        related_map = {
            "debug": ["testing", "logging", "error handling", "troubleshooting"],
            "python": ["programming", "coding", "scripting", "development"],
            "web": ["html", "css", "javascript", "frontend", "backend"],
            "data": ["analysis", "visualization", "databases", "processing"],
            "ai": ["machine learning", "neural networks", "algorithms", "models"]
        }
        
        related_topics = []
        for keyword in keywords:
            if keyword in related_map:
                related_topics.extend(related_map[keyword])
        
        return list(set(related_topics))
    
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get statistics about prediction performance"""
        if not self.prediction_history:
            return {"total_predictions": 0}
        
        total_predictions = len(self.prediction_history)
        avg_predictions_per_session = sum(p["predictions_made"] for p in self.prediction_history) / total_predictions
        
        confidence_scores = []
        for record in self.prediction_history:
            confidence_scores.extend(record["confidence_range"])
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "total_predictions": total_predictions,
            "avg_predictions_per_session": round(avg_predictions_per_session, 2),
            "avg_confidence": round(avg_confidence, 3),
            "active_patterns": len(self.prediction_patterns),
            "recent_predictions": [
                {
                    "context_type": self._determine_context_type(record["context"]),
                    "predictions_made": record["predictions_made"],
                    "top_prediction": record["top_prediction"]
                }
                for record in self.prediction_history[-5:]
            ]
        }