# Core Brain API Reference 🧠

The Core Brain API provides the central orchestration interface for all cognitive operations across the 7-tier architecture. This is your primary entry point for interacting with Bolor Brain MCP.

## 🎯 Overview

The `BrainMCP` class serves as the central orchestrator that coordinates all cognitive tiers and provides a unified interface for cognitive operations.

```python
from server import BrainMCP

# Initialize the brain
brain = BrainMCP()
await brain.initialize()
```

---

## 🏗️ Core Class Structure

### BrainMCP Class

```python
class BrainMCP:
    """Central orchestrator for 7-tier cognitive architecture"""
    
    def __init__(self):
        self.memory = None              # Tier 0: Memory Foundation
        self.advanced_reasoning = None  # Tier 1: Advanced Reasoning
        self.predictive = None         # Tier 2: Predictive Intelligence  
        self.metacognitive = None      # Tier 3: Meta-Cognitive Intelligence
        self.evolutionary = None       # Tier 4: Evolutionary Intelligence
        self.collective = None         # Tier 5: Collective Consciousness
        self.orchestration = None      # Tier 6: Universal Orchestration
        self.universal = None          # Tier 7: Universal Being Integration
        self.cognitive_state = CognitiveState()
        self.is_initialized = False
```

---

## 🚀 Initialization

### initialize()

Initializes all cognitive tiers and establishes inter-tier connections.

```python
async def initialize() -> bool
```

**Returns**: `bool` - True if initialization successful

**Example**:
```python
brain = BrainMCP()
success = await brain.initialize()
if success:
    print("🧠 Brain initialized successfully!")
else:
    print("❌ Initialization failed")
```

**What happens during initialization**:
1. Initializes memory system with SQLite database
2. Sets up all 7 cognitive tiers
3. Establishes inter-tier communication channels
4. Loads configuration and settings
5. Performs self-diagnostic checks

---

## 💾 Memory Operations (Tier 0)

### store_memory()

Store information in the brain's memory system.

```python
async def store_memory(
    content: str,
    memory_type: str = "episodic",
    importance: float = 0.5,
    metadata: Dict[str, Any] = None
) -> str
```

**Parameters**:
- `content` (str): The content to store
- `memory_type` (str): Type of memory ("episodic", "semantic", "procedural")
- `importance` (float): Importance score (0.0 - 1.0)
- `metadata` (Dict): Additional metadata

**Returns**: `str` - Unique memory ID

**Example**:
```python
# Store different types of memories
episodic_id = await brain.store_memory(
    content="Had a breakthrough in understanding neural networks",
    memory_type="episodic",
    importance=0.9,
    metadata={"topic": "learning", "emotion": "excited"}
)

semantic_id = await brain.store_memory(
    content="Neural networks use backpropagation for training",
    memory_type="semantic", 
    importance=0.8,
    metadata={"domain": "AI", "concept": "training"}
)

procedural_id = await brain.store_memory(
    content="To debug neural networks: check data, verify architecture, monitor gradients",
    memory_type="procedural",
    importance=0.85,
    metadata={"skill": "debugging"}
)
```

### retrieve_memories()

Retrieve memories based on content similarity.

```python
async def retrieve_memories(
    query: str,
    limit: int = 10,
    memory_type: str = None
) -> List[Memory]
```

**Parameters**:
- `query` (str): Search query
- `limit` (int): Maximum number of memories to return
- `memory_type` (str, optional): Filter by memory type

**Returns**: `List[Memory]` - List of matching memories

**Example**:
```python
# Search for memories about machine learning
memories = await brain.retrieve_memories(
    query="machine learning neural networks",
    limit=5,
    memory_type="semantic"
)

for memory in memories:
    print(f"Memory: {memory.content}")
    print(f"Importance: {memory.importance}")
    print(f"Metadata: {memory.metadata}")
```

### search_memories()

Advanced memory search with FTS5 full-text search.

```python
async def search_memories(
    query: str,
    memory_type: str = None,
    limit: int = 10,
    min_importance: float = 0.0
) -> List[Memory]
```

**Parameters**:
- `query` (str): FTS5 search query (supports AND, OR, NOT operators)
- `memory_type` (str, optional): Filter by memory type
- `limit` (int): Maximum results
- `min_importance` (float): Minimum importance threshold

**Example**:
```python
# Advanced search with boolean operators
memories = await brain.search_memories(
    query="(neural AND networks) OR (deep AND learning)",
    min_importance=0.7,
    limit=10
)
```

---

## 🤔 Reasoning Operations (Tier 1)

### solve_complex_problem()

Solve complex problems using advanced reasoning strategies.

```python
async def solve_complex_problem(
    problem: str,
    context: Dict[str, Any] = None
) -> ReasoningChain
```

**Parameters**:
- `problem` (str): Problem statement to solve
- `context` (Dict, optional): Additional context for reasoning

**Returns**: `ReasoningChain` - Complete reasoning chain with solution

**Example**:
```python
# Basic problem solving
result = await brain.solve_complex_problem(
    "How can I optimize the performance of my machine learning model?"
)

print(f"Strategy used: {result.strategy}")
print(f"Solution: {result.final_conclusion}")
print(f"Confidence: {result.overall_confidence:.2f}")
print(f"Reasoning time: {result.reasoning_time:.2f}s")

# Problem solving with rich context
context = {
    "model_type": "neural_network",
    "dataset_size": "large",
    "current_accuracy": 0.85,
    "target_accuracy": 0.95,
    "constraints": ["memory_limited", "inference_speed"]
}

result = await brain.solve_complex_problem(
    "Optimize ML model performance within constraints",
    context=context
)
```

**ReasoningChain Structure**:
```python
@dataclass
class ReasoningChain:
    chain_id: str              # Unique identifier
    problem: str              # Original problem
    strategy: str             # Reasoning strategy used
    steps: List[ReasoningStep]  # Detailed reasoning steps
    final_conclusion: str     # Final solution
    overall_confidence: float # Confidence score (0-1)
    reasoning_time: float     # Processing time in seconds
    timestamp: float          # Creation timestamp
```

### Available Reasoning Strategies

The system automatically selects from 6 reasoning strategies:

1. **Analytical**: Systematic logical analysis
2. **Creative**: Innovation and novel solutions  
3. **Critical**: Assumption validation and bias detection
4. **Systems**: Holistic relationship modeling
5. **Ethical**: Value-based decision frameworks
6. **Intuitive**: Pattern recognition beyond explicit logic

**Strategy Selection Examples**:
```python
# These problems will trigger different strategies:

# Analytical strategy
await brain.solve_complex_problem("Analyze the components of a microservices architecture")

# Creative strategy  
await brain.solve_complex_problem("Brainstorm innovative features for mobile app engagement")

# Critical strategy
await brain.solve_complex_problem("Evaluate the assumptions behind this business model")

# Systems strategy
await brain.solve_complex_problem("Understand the interconnections in a complex distributed system")

# Ethical strategy
await brain.solve_complex_problem("What are the moral implications of AI in healthcare?")

# Intuitive strategy
await brain.solve_complex_problem("What does my gut feeling say about this decision?")
```

---

## 🔮 Predictive Operations (Tier 2)

### predict_user_needs()

Predict user needs and future requirements based on patterns and context.

```python
async def predict_user_needs(
    current_context: Dict[str, Any],
    history_depth: int = 10
) -> List[PredictiveInsight]
```

**Parameters**:
- `current_context` (Dict): Current user/system context
- `history_depth` (int): How many recent interactions to analyze

**Returns**: `List[PredictiveInsight]` - List of predictions with confidence scores

**Example**:
```python
# Predict needs based on current activity
context = {
    "current_activity": "debugging_neural_network",
    "time_of_day": "afternoon",
    "recent_topics": ["training", "optimization", "validation"],
    "difficulty_level": "intermediate",
    "available_time": "2_hours"
}

predictions = await brain.predict_user_needs(
    current_context=context,
    history_depth=15
)

print("🔮 Predictions:")
for prediction in predictions:
    print(f"• {prediction.predicted_content}")
    print(f"  Confidence: {prediction.confidence:.2f}")
    print(f"  Time horizon: {prediction.time_horizon}")
    print(f"  Type: {prediction.prediction_type}")
    
    if prediction.suggested_preparations:
        print(f"  Preparations: {', '.join(prediction.suggested_preparations[:2])}")
```

**PredictiveInsight Structure**:
```python
@dataclass
class PredictiveInsight:
    insight_id: str                    # Unique identifier
    prediction_type: str               # "next_action", "likely_problem", etc.
    predicted_content: str            # What is predicted
    confidence: float                 # Confidence score (0-1)
    reasoning: str                    # Why this prediction was made
    supporting_patterns: List[str]    # Patterns that support prediction
    time_horizon: str                 # "immediate", "short_term", etc.
    suggested_preparations: List[str] # Recommended preparations
    timestamp: float                  # Creation timestamp
```

---

## 🔍 Meta-Cognitive Operations (Tier 3)

### analyze_cognitive_performance()

Analyze and optimize cognitive performance across all tiers.

```python
async def analyze_cognitive_performance(
    performance_data: Dict[str, float]
) -> Dict[str, Any]
```

**Parameters**:
- `performance_data` (Dict): Performance metrics to analyze

**Returns**: `Dict[str, Any]` - Analysis results with recommendations

**Example**:
```python
# Analyze learning session performance
performance_metrics = {
    "reasoning_speed": 0.8,
    "memory_retention": 0.9,
    "problem_solving_accuracy": 0.7,
    "creativity_score": 0.6,
    "confidence_level": 0.8,
    "learning_efficiency": 0.75
}

analysis = await brain.analyze_cognitive_performance(performance_metrics)

print("🔍 Performance Analysis:")
print(f"Overall Score: {analysis['overall_score']:.2f}")

print("Strengths:")
for strength in analysis.get('strengths', []):
    print(f"  ✅ {strength}")

print("Improvement Areas:")
for area in analysis.get('improvement_areas', []):
    print(f"  🎯 {area}")

print("Recommendations:")
for rec in analysis.get('recommendations', []):
    print(f"  💡 {rec}")
```

---

## 🧬 Evolutionary Operations (Tier 4)

### evolve_cognitive_capabilities()

Evolve and enhance cognitive capabilities through adaptive processes.

```python
async def evolve_cognitive_capabilities(
    current_state: Dict[str, float],
    target_improvements: List[str] = None,
    evolution_cycles: int = 5
) -> Dict[str, float]
```

**Parameters**:
- `current_state` (Dict): Current capability levels
- `target_improvements` (List, optional): Specific areas to improve
- `evolution_cycles` (int): Number of evolution iterations

**Returns**: `Dict[str, float]` - Evolved capability levels

**Example**:
```python
# Define current capabilities
current_capabilities = {
    "programming_skill": 0.7,
    "mathematical_understanding": 0.5,
    "creative_thinking": 0.6,
    "problem_solving": 0.8,
    "communication": 0.7,
    "learning_speed": 0.6
}

# Evolve specific capabilities
evolved = await brain.evolve_cognitive_capabilities(
    current_state=current_capabilities,
    target_improvements=["mathematical_understanding", "creative_thinking"],
    evolution_cycles=3
)

print("🧬 Evolution Results:")
for capability, new_level in evolved.items():
    old_level = current_capabilities.get(capability, 0)
    improvement = new_level - old_level
    print(f"{capability}: {old_level:.2f} → {new_level:.2f} (+{improvement:.2f})")
```

---

## 🌐 Collective Operations (Tier 5)

### join_collective_network()

Join a collective consciousness network for distributed intelligence.

```python
async def join_collective_network(
    network_id: str = "default",
    contribution_level: float = 0.8
) -> Dict[str, Any]
```

**Parameters**:
- `network_id` (str): Network identifier to join
- `contribution_level` (float): How much to contribute to collective

**Returns**: `Dict[str, Any]` - Network status and connection info

### synchronize_collective_consciousness()

Synchronize with collective consciousness for shared insights.

```python
async def synchronize_collective_consciousness(
    sync_depth: str = "moderate"
) -> Dict[str, Any]
```

**Example**:
```python
# Join collective network
network_status = await brain.join_collective_network(
    network_id="research_collective",
    contribution_level=0.9
)

print(f"Network status: {network_status['status']}")
print(f"Connected nodes: {network_status['connected_nodes']}")

# Synchronize consciousness  
sync_result = await brain.synchronize_collective_consciousness(
    sync_depth="deep"
)

print(f"Synchronization quality: {sync_result['sync_quality']}")
print(f"Shared insights: {len(sync_result['insights'])}")
```

---

## 🎭 Universal Operations (Tiers 6 & 7)

### orchestrate_reality()

Orchestrate reality through quantum field coordination.

```python
async def orchestrate_reality(
    intention: str,
    scope: str = "local"
) -> Dict[str, Any]
```

### access_universal_wisdom()

Access universal wisdom and consciousness.

```python
async def access_universal_wisdom(
    query: str = None,
    wisdom_level: str = "intermediate"
) -> Dict[str, Any]
```

**Example**:
```python
# Reality orchestration
orchestration_result = await brain.orchestrate_reality(
    intention="optimize learning environment for deep focus",
    scope="personal"
)

# Universal wisdom access
wisdom = await brain.access_universal_wisdom(
    query="What is the nature of consciousness?",
    wisdom_level="advanced"
)

print(f"Universal insight: {wisdom['insight']}")
print(f"Wisdom quality: {wisdom['quality_level']}")
```

---

## 📊 System Information

### get_cognitive_state()

Get current cognitive state across all tiers.

```python
def get_cognitive_state() -> CognitiveState
```

**Returns**: `CognitiveState` - Current system state

### get_system_statistics()

Get comprehensive system performance statistics.

```python
def get_system_statistics() -> Dict[str, Any]
```

**Example**:
```python
# Get current cognitive state
state = brain.get_cognitive_state()
print(f"Attention focus: {state.attention_focus}")
print(f"Confidence level: {state.confidence}")
print(f"Processing load: {state.processing_load}")

# Get system statistics
stats = brain.get_system_statistics()
print(f"Total memories: {stats['memory_count']}")
print(f"Reasoning chains: {stats['reasoning_chains']}")
print(f"System uptime: {stats['uptime']}")
print(f"Performance score: {stats['overall_performance']:.2f}")
```

---

## 🔧 Configuration

### update_configuration()

Update system configuration settings.

```python
async def update_configuration(
    config_updates: Dict[str, Any]
) -> bool
```

**Example**:
```python
# Update system settings
config_updates = {
    "max_memory_size": 15000,
    "reasoning_timeout": 45,
    "prediction_horizon": 14,
    "evolution_mutation_rate": 0.15
}

success = await brain.update_configuration(config_updates)
if success:
    print("✅ Configuration updated successfully")
```

---

## 🛠️ Error Handling

### Common Exceptions

```python
class BrainException(Exception):
    """Base exception for brain operations"""
    pass

class InitializationError(BrainException):
    """Raised when brain initialization fails"""
    pass

class MemoryError(BrainException): 
    """Raised for memory operation errors"""
    pass

class ReasoningError(BrainException):
    """Raised for reasoning operation errors"""
    pass

class NetworkError(BrainException):
    """Raised for collective network errors"""
    pass
```

**Error Handling Example**:
```python
try:
    result = await brain.solve_complex_problem(problem)
except ReasoningError as e:
    print(f"Reasoning failed: {e}")
    # Fallback to simpler reasoning
    result = await brain.solve_complex_problem(problem, {"strategy": "analytical"})
except BrainException as e:
    print(f"Brain operation failed: {e}")
    # Handle gracefully
```

---

## 📈 Performance Optimization

### Best Practices

1. **Initialize Once**: Create and initialize brain instance once, reuse across operations
2. **Batch Operations**: Group related operations for efficiency
3. **Context Reuse**: Provide rich context to improve reasoning quality
4. **Memory Management**: Regularly clean up old, low-importance memories
5. **Async Operations**: Always use async/await for brain operations

**Optimized Usage Pattern**:
```python
class OptimizedBrainUsage:
    def __init__(self):
        self.brain = None
    
    async def initialize(self):
        """Initialize once, reuse everywhere"""
        if not self.brain:
            self.brain = BrainMCP()
            await self.brain.initialize()
    
    async def batch_memory_operations(self, memories):
        """Batch multiple memory operations"""
        memory_ids = []
        for memory_data in memories:
            memory_id = await self.brain.store_memory(**memory_data)
            memory_ids.append(memory_id)
        return memory_ids
    
    async def context_aware_reasoning(self, problem, context_history):
        """Use accumulated context for better reasoning"""
        enriched_context = self._build_context(context_history)
        return await self.brain.solve_complex_problem(problem, enriched_context)
```

---

**🚀 Ready to explore specific cognitive tiers? Check out [Memory Operations](memory.md), [Reasoning Functions](reasoning.md), or [Advanced Topics](../advanced/)! 🧠✨**