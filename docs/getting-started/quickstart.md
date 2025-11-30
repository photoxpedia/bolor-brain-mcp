# Quick Start Tutorial 🚀

Welcome to your first journey into 7-tier cognitive architecture! This tutorial will guide you through basic cognitive operations across all intelligence tiers.

## 🎯 Your First Cognitive Operations

### 1. Initialize the Brain 🧠

```python
import asyncio
from server import BrainMCP

async def initialize_brain():
    # Create the central brain instance
    brain = BrainMCP()
    
    # Initialize all cognitive tiers
    await brain.initialize()
    
    print("🧠 Bolor Brain MCP initialized with 7 cognitive tiers!")
    return brain

# Run the initialization
brain = asyncio.run(initialize_brain())
```

### 2. Store Your First Memory 💾

```python
async def store_first_memory():
    # Store different types of memories
    episodic_id = await brain.store_memory(
        content="I learned about cognitive architecture today",
        memory_type="episodic",
        importance=0.8,
        metadata={"topic": "learning", "date": "2024-01-01"}
    )
    
    semantic_id = await brain.store_memory(
        content="Cognitive architecture has 7 hierarchical tiers",
        memory_type="semantic", 
        importance=0.9,
        metadata={"domain": "cognitive_science"}
    )
    
    print(f"✅ Stored memories: {episodic_id}, {semantic_id}")

asyncio.run(store_first_memory())
```

### 3. Perform Advanced Reasoning 🤔

```python
async def first_reasoning():
    # Solve a complex problem using advanced reasoning
    problem = "How can I optimize my learning process for cognitive architecture?"
    
    reasoning_chain = await brain.solve_complex_problem(
        problem=problem,
        context={"domain": "education", "goal": "optimization"}
    )
    
    print(f"🤔 Problem: {problem}")
    print(f"🧠 Strategy: {reasoning_chain.strategy}")
    print(f"✅ Solution: {reasoning_chain.final_conclusion}")
    print(f"📊 Confidence: {reasoning_chain.overall_confidence:.2f}")
    
    return reasoning_chain

reasoning_result = asyncio.run(first_reasoning())
```

### 4. Predict Future Needs 🔮

```python
async def predict_user_needs():
    # Let the system predict what you might need next
    current_context = {
        "current_activity": "learning cognitive architecture",
        "time_of_day": "morning",
        "recent_topics": ["reasoning", "memory", "prediction"]
    }
    
    predictions = await brain.predict_user_needs(
        current_context=current_context,
        history_depth=5
    )
    
    print("🔮 Predictions for your next needs:")
    for i, prediction in enumerate(predictions, 1):
        print(f"  {i}. {prediction.predicted_content}")
        print(f"     Confidence: {prediction.confidence:.2f}")
        print(f"     Time horizon: {prediction.time_horizon}")
    
    return predictions

predictions = asyncio.run(predict_user_needs())
```

---

## 🌟 Exploring Cognitive Tiers

### Tier 1: Advanced Reasoning Strategies

```python
async def explore_reasoning_strategies():
    problems = {
        "analytical": "Break down the components of machine learning",
        "creative": "Design an innovative learning system", 
        "critical": "Evaluate the assumptions in AI development",
        "systems": "Understand the ecosystem of cognitive technologies",
        "ethical": "Consider the moral implications of AI consciousness",
        "intuitive": "Sense the future direction of cognitive research"
    }
    
    results = {}
    for strategy, problem in problems.items():
        # Force specific strategy by including strategy keywords
        result = await brain.solve_complex_problem(problem)
        results[strategy] = result.final_conclusion
        print(f"🧠 {strategy.upper()}: {result.final_conclusion}")
    
    return results

strategies_demo = asyncio.run(explore_reasoning_strategies())
```

### Tier 3: Meta-Cognitive Optimization

```python
async def explore_metacognition():
    # Analyze your cognitive performance
    performance_data = {
        "reasoning_speed": 0.8,
        "memory_efficiency": 0.9, 
        "prediction_accuracy": 0.7,
        "learning_rate": 0.85
    }
    
    analysis = await brain.analyze_cognitive_performance(performance_data)
    
    print("🔍 Cognitive Performance Analysis:")
    print(f"Overall Score: {analysis['overall_score']:.2f}")
    print("Recommendations:")
    for rec in analysis['recommendations']:
        print(f"  • {rec}")
    
    return analysis

meta_analysis = asyncio.run(explore_metacognition())
```

### Tier 4: Evolutionary Capabilities

```python
async def explore_evolution():
    # Evolve your cognitive capabilities
    current_state = {
        "reasoning_depth": 3,
        "creativity_level": 0.7,
        "emotional_intelligence": 0.6,
        "pattern_recognition": 0.8
    }
    
    evolved_state = await brain.evolve_cognitive_capabilities(
        current_state=current_state,
        target_improvements=["creativity", "emotional_intelligence"],
        evolution_cycles=5
    )
    
    print("🧬 Cognitive Evolution Results:")
    for capability, value in evolved_state.items():
        improvement = value - current_state.get(capability, 0)
        print(f"  {capability}: {value:.2f} (+{improvement:.2f})")
    
    return evolved_state

evolution_demo = asyncio.run(explore_evolution())
```

---

## 🛠️ Practical Examples

### Example 1: Personal Learning Assistant

```python
async def learning_assistant_demo():
    # Store learning goal
    await brain.store_memory(
        content="Goal: Master cognitive architecture in 30 days",
        memory_type="procedural",
        importance=0.9,
        metadata={"type": "goal", "deadline": "2024-02-01"}
    )
    
    # Get learning plan
    learning_plan = await brain.solve_complex_problem(
        "Create a 30-day learning plan for cognitive architecture mastery"
    )
    
    # Predict learning challenges
    context = {"goal": "learning", "timeframe": "30_days", "topic": "cognitive_architecture"}
    challenges = await brain.predict_user_needs(context)
    
    print("📚 Learning Assistant Results:")
    print(f"Plan: {learning_plan.final_conclusion}")
    print("Predicted challenges:")
    for challenge in challenges[:3]:
        print(f"  • {challenge.predicted_content}")

asyncio.run(learning_assistant_demo())
```

### Example 2: Creative Problem Solving

```python
async def creative_problem_solving():
    # Define a creative challenge
    challenge = "Design a revolutionary user interface for cognitive AI"
    
    # Use creative reasoning
    creative_solution = await brain.solve_complex_problem(challenge)
    
    # Evolve the idea further
    evolution_context = {
        "base_idea": creative_solution.final_conclusion,
        "creativity_boost": True,
        "innovation_level": "revolutionary"
    }
    
    evolved_idea = await brain.evolve_cognitive_capabilities(evolution_context)
    
    print("🎨 Creative Problem Solving:")
    print(f"Challenge: {challenge}")
    print(f"Initial Solution: {creative_solution.final_conclusion}")
    print(f"Evolved Concept: {evolved_idea}")

asyncio.run(creative_problem_solving())
```

### Example 3: Multi-Tier Integration

```python
async def multi_tier_integration():
    """Demonstrate how tiers work together"""
    
    # 1. Store context in memory
    await brain.store_memory(
        "Working on complex system integration project",
        "episodic", 0.8
    )
    
    # 2. Reason about the problem
    reasoning = await brain.solve_complex_problem(
        "How to integrate multiple AI systems effectively?"
    )
    
    # 3. Predict future challenges
    context = {"project": "system_integration", "complexity": "high"}
    predictions = await brain.predict_user_needs(context)
    
    # 4. Optimize approach based on meta-analysis
    performance = {"integration_success": 0.7, "efficiency": 0.6}
    optimization = await brain.analyze_cognitive_performance(performance)
    
    # 5. Evolve solution
    evolved = await brain.evolve_cognitive_capabilities({
        "base_solution": reasoning.final_conclusion,
        "optimization_target": "integration_efficiency"
    })
    
    print("🔄 Multi-Tier Integration Demo:")
    print(f"1. Memory stored ✅")
    print(f"2. Reasoning: {reasoning.strategy} - {reasoning.final_conclusion}")
    print(f"3. Predictions: {len(predictions)} future needs identified")
    print(f"4. Optimization score: {optimization.get('overall_score', 'N/A')}")
    print(f"5. Evolved solution available ✅")

asyncio.run(multi_tier_integration())
```

---

## 🎪 Interactive Exploration

### Quick Interactive Session

```python
async def interactive_session():
    print("🧠 Welcome to Bolor Brain Interactive Session!")
    print("Available commands:")
    print("  memory <text>     - Store a memory")
    print("  think <problem>   - Solve a problem") 
    print("  predict           - Get predictions")
    print("  evolve            - Evolve capabilities")
    print("  quit              - Exit session")
    
    while True:
        command = input("\n🤖 Enter command: ").strip().lower()
        
        if command.startswith("memory "):
            text = command[7:]
            memory_id = await brain.store_memory(text, "episodic", 0.7)
            print(f"✅ Memory stored: {memory_id}")
            
        elif command.startswith("think "):
            problem = command[6:]
            result = await brain.solve_complex_problem(problem)
            print(f"🤔 Strategy: {result.strategy}")
            print(f"💡 Solution: {result.final_conclusion}")
            
        elif command == "predict":
            predictions = await brain.predict_user_needs({})
            print("🔮 Predictions:")
            for pred in predictions[:3]:
                print(f"  • {pred.predicted_content}")
                
        elif command == "evolve":
            evolved = await brain.evolve_cognitive_capabilities({
                "creativity": 0.8, "reasoning": 0.9
            })
            print("🧬 Capabilities evolved!")
            
        elif command == "quit":
            print("👋 Goodbye! Keep exploring cognitive architecture!")
            break
            
        else:
            print("❓ Unknown command. Try: memory, think, predict, evolve, quit")

# Run interactive session
# asyncio.run(interactive_session())
```

---

## 🧪 Testing Your Setup

### Comprehensive System Test

```python
async def system_test():
    """Test all major functionalities"""
    
    tests_passed = 0
    total_tests = 7
    
    try:
        # Test 1: Memory operations
        memory_id = await brain.store_memory("Test memory", "episodic", 0.5)
        memories = await brain.retrieve_memories("Test", 1)
        assert len(memories) > 0
        tests_passed += 1
        print("✅ Test 1: Memory operations")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    try:
        # Test 2: Reasoning
        result = await brain.solve_complex_problem("Simple test problem")
        assert result.final_conclusion is not None
        tests_passed += 1
        print("✅ Test 2: Advanced reasoning")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    try:
        # Test 3: Prediction
        predictions = await brain.predict_user_needs({})
        tests_passed += 1
        print("✅ Test 3: Predictive intelligence")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    try:
        # Test 4: Meta-cognitive analysis
        analysis = await brain.analyze_cognitive_performance({"score": 0.8})
        tests_passed += 1
        print("✅ Test 4: Meta-cognitive analysis")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
    
    try:
        # Test 5: Evolutionary capabilities
        evolved = await brain.evolve_cognitive_capabilities({"test": 0.5})
        tests_passed += 1
        print("✅ Test 5: Evolutionary intelligence")
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
    
    try:
        # Test 6: Collective consciousness
        network_status = await brain.join_collective_network()
        tests_passed += 1
        print("✅ Test 6: Collective consciousness")
    except Exception as e:
        print(f"❌ Test 6 failed: {e}")
    
    try:
        # Test 7: Universal being integration
        universal_status = await brain.access_universal_wisdom()
        tests_passed += 1
        print("✅ Test 7: Universal being integration")
    except Exception as e:
        print(f"❌ Test 7 failed: {e}")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    if tests_passed == total_tests:
        print("🎉 All systems operational! Ready for advanced usage!")
    else:
        print("⚠️  Some systems need attention. Check the failed tests.")
    
    return tests_passed == total_tests

# Run system test
test_success = asyncio.run(system_test())
```

---

## 🚀 Next Steps

Congratulations! You've successfully explored the basic capabilities of Bolor Brain MCP. Here's what to explore next:

### Immediate Next Steps
1. **[Basic Examples](examples.md)** - More detailed usage patterns
2. **[Architecture Overview](../architecture/overview.md)** - Understand the system design
3. **[Tier Documentation](../tiers/)** - Deep dive into specific cognitive tiers

### Advanced Exploration
1. **[Custom Modules](../development/custom-modules.md)** - Extend the system
2. **[Integration Guides](../integration/)** - Connect with other systems
3. **[Advanced Topics](../advanced/)** - Quantum consciousness and universal fields

### Practical Applications
1. **[Problem Solving](../examples/problem-solving.md)** - Real-world applications
2. **[Creative Applications](../examples/creative.md)** - Artistic and innovative uses
3. **[Business Intelligence](../examples/business.md)** - Enterprise scenarios

---

**🧠 Ready to dive deeper into cognitive architecture? Your journey into 7-tier intelligence has just begun! ✨**