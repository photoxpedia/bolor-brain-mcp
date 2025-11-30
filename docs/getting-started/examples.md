# Basic Examples 📚

This guide provides practical, copy-paste examples for common Bolor Brain MCP operations. Perfect for getting started with cognitive operations!

## 🚀 Setup for Examples

All examples assume you have the brain initialized:

```python
import asyncio
from server import BrainMCP

# Initialize brain for examples
async def setup():
    brain = BrainMCP()
    await brain.initialize()
    return brain

brain = asyncio.run(setup())
```

---

## 💾 Memory Operations

### Basic Memory Storage

```python
async def basic_memory_examples():
    # Store different types of memories
    
    # Episodic memory (personal experiences)
    episodic_id = await brain.store_memory(
        content="Had a breakthrough understanding of neural networks today",
        memory_type="episodic",
        importance=0.9,
        metadata={"date": "2024-01-15", "emotion": "excited", "topic": "learning"}
    )
    
    # Semantic memory (facts and knowledge)
    semantic_id = await brain.store_memory(
        content="Neural networks use backpropagation for training",
        memory_type="semantic",
        importance=0.8,
        metadata={"domain": "AI", "concept": "neural_networks"}
    )
    
    # Procedural memory (skills and procedures)
    procedural_id = await brain.store_memory(
        content="To debug neural networks: check data, verify architecture, monitor gradients",
        memory_type="procedural",
        importance=0.85,
        metadata={"skill": "debugging", "domain": "AI"}
    )
    
    print(f"✅ Stored memories: {episodic_id}, {semantic_id}, {procedural_id}")
    return [episodic_id, semantic_id, procedural_id]

memory_ids = asyncio.run(basic_memory_examples())
```

### Memory Retrieval

```python
async def memory_retrieval_examples():
    # Search for memories by content
    neural_memories = await brain.retrieve_memories(
        query="neural networks",
        limit=5
    )
    
    print(f"Found {len(neural_memories)} memories about neural networks:")
    for memory in neural_memories:
        print(f"  • {memory.content[:50]}... (importance: {memory.importance})")
    
    # Search for memories by metadata
    learning_memories = await brain.search_memories(
        query="learning OR breakthrough",
        memory_type="episodic",
        limit=3
    )
    
    print(f"\nFound {len(learning_memories)} learning-related memories:")
    for memory in learning_memories:
        print(f"  • {memory.content}")
        print(f"    Metadata: {memory.metadata}")

asyncio.run(memory_retrieval_examples())
```

---

## 🤔 Reasoning Examples

### Problem Solving with Different Strategies

```python
async def reasoning_examples():
    problems = {
        "analytical": {
            "problem": "How can I optimize the performance of my machine learning model?",
            "expected_strategy": "analytical"
        },
        "creative": {
            "problem": "Design an innovative approach to human-AI collaboration",
            "expected_strategy": "creative"
        },
        "critical": {
            "problem": "Evaluate the potential risks and benefits of artificial general intelligence",
            "expected_strategy": "critical"
        },
        "systems": {
            "problem": "Understand how different AI technologies interconnect in a modern tech stack",
            "expected_strategy": "systems"
        },
        "ethical": {
            "problem": "What are the moral considerations when developing AI that could replace human jobs?",
            "expected_strategy": "ethical"
        },
        "intuitive": {
            "problem": "What does the future of human consciousness look like with AI integration?",
            "expected_strategy": "intuitive"
        }
    }
    
    results = {}
    for strategy_name, problem_data in problems.items():
        print(f"\n🧠 {strategy_name.upper()} REASONING:")
        print(f"Problem: {problem_data['problem']}")
        
        result = await brain.solve_complex_problem(
            problem=problem_data['problem'],
            context={"preferred_strategy": strategy_name}
        )
        
        print(f"Strategy Used: {result.strategy}")
        print(f"Solution: {result.final_conclusion}")
        print(f"Confidence: {result.overall_confidence:.2f}")
        print(f"Steps: {len(result.steps)}")
        
        results[strategy_name] = result
    
    return results

reasoning_results = asyncio.run(reasoning_examples())
```

### Custom Reasoning with Context

```python
async def custom_reasoning_example():
    # Provide rich context for better reasoning
    problem = "How should I approach learning advanced mathematics as a software developer?"
    
    context = {
        "background": "software_developer",
        "experience_level": "intermediate",
        "time_available": "2_hours_per_day",
        "goal": "understand_AI_mathematics",
        "learning_style": "hands_on_practical"
    }
    
    result = await brain.solve_complex_problem(problem, context)
    
    print("🎯 Custom Reasoning with Rich Context:")
    print(f"Problem: {problem}")
    print(f"Context: {context}")
    print(f"Strategy: {result.strategy}")
    print(f"Solution: {result.final_conclusion}")
    
    # Examine reasoning steps
    print("\nDetailed Reasoning Steps:")
    for i, step in enumerate(result.steps, 1):
        print(f"  {i}. {step.description}")
        print(f"     Type: {step.reasoning_type}")
        print(f"     Confidence: {step.confidence:.2f}")
    
    return result

custom_result = asyncio.run(custom_reasoning_example())
```

---

## 🔮 Predictive Intelligence

### User Need Prediction

```python
async def prediction_examples():
    # Different context scenarios
    contexts = [
        {
            "name": "Learning Session",
            "context": {
                "current_activity": "studying machine learning",
                "time_of_day": "morning",
                "recent_topics": ["neural networks", "optimization", "debugging"],
                "difficulty_level": "intermediate"
            }
        },
        {
            "name": "Work Project",
            "context": {
                "current_activity": "developing AI application",
                "time_of_day": "afternoon", 
                "recent_topics": ["API design", "model deployment", "testing"],
                "deadline_pressure": "high"
            }
        },
        {
            "name": "Research Mode", 
            "context": {
                "current_activity": "exploring new concepts",
                "time_of_day": "evening",
                "recent_topics": ["consciousness", "quantum computing", "philosophy"],
                "exploration_mode": "deep_dive"
            }
        }
    ]
    
    for scenario in contexts:
        print(f"\n🔮 Predictions for: {scenario['name']}")
        print(f"Context: {scenario['context']}")
        
        predictions = await brain.predict_user_needs(
            current_context=scenario['context'],
            history_depth=10
        )
        
        print("Predictions:")
        for i, pred in enumerate(predictions, 1):
            print(f"  {i}. {pred.predicted_content}")
            print(f"     Confidence: {pred.confidence:.2f}")
            print(f"     Time horizon: {pred.time_horizon}")
            print(f"     Type: {pred.prediction_type}")
            
            if pred.suggested_preparations:
                print(f"     Preparations: {', '.join(pred.suggested_preparations[:2])}")

asyncio.run(prediction_examples())
```

### Pattern-Based Predictions

```python
async def pattern_prediction_example():
    # First, establish some patterns by storing related memories
    pattern_memories = [
        "Every morning I start with coffee and check emails",
        "I'm most productive with coding between 9-11 AM",
        "I prefer visual learning materials over text-heavy content", 
        "When stuck on problems, I take breaks and come back with fresh perspective",
        "I learn best when I can immediately apply new concepts to real projects"
    ]
    
    # Store these pattern memories
    for memory in pattern_memories:
        await brain.store_memory(
            content=memory,
            memory_type="procedural",
            importance=0.7,
            metadata={"type": "personal_pattern"}
        )
    
    # Now predict based on current morning context
    morning_context = {
        "time_of_day": "morning",
        "current_activity": "starting_work_day",
        "energy_level": "high",
        "available_time": "3_hours"
    }
    
    predictions = await brain.predict_user_needs(morning_context, history_depth=5)
    
    print("🌅 Morning Productivity Predictions:")
    for pred in predictions:
        print(f"• {pred.predicted_content}")
        print(f"  Reasoning: {pred.reasoning}")

asyncio.run(pattern_prediction_example())
```

---

## 🧬 Evolutionary Intelligence

### Capability Evolution

```python
async def evolution_examples():
    # Define current capabilities
    current_capabilities = {
        "programming_skill": 0.7,
        "mathematical_understanding": 0.5,
        "creative_thinking": 0.6,
        "problem_solving": 0.8,
        "communication": 0.7,
        "learning_speed": 0.6
    }
    
    # Define improvement goals
    improvement_goals = [
        "mathematical_understanding",
        "creative_thinking", 
        "learning_speed"
    ]
    
    print("🧬 Current Capabilities:")
    for skill, level in current_capabilities.items():
        print(f"  {skill}: {level:.2f}")
    
    # Evolve capabilities
    evolved_capabilities = await brain.evolve_cognitive_capabilities(
        current_state=current_capabilities,
        target_improvements=improvement_goals,
        evolution_cycles=3
    )
    
    print("\n🚀 Evolved Capabilities:")
    for skill, new_level in evolved_capabilities.items():
        old_level = current_capabilities.get(skill, 0)
        improvement = new_level - old_level
        status = "📈" if improvement > 0 else "📊"
        print(f"  {skill}: {new_level:.2f} {status} (+{improvement:.2f})")
    
    return evolved_capabilities

evolution_result = asyncio.run(evolution_examples())
```

### Creative Insight Generation

```python
async def creative_insight_example():
    # Generate insights for different domains
    domains = [
        "artificial intelligence",
        "sustainable technology", 
        "human psychology",
        "educational methods",
        "creative arts"
    ]
    
    insights = {}
    for domain in domains:
        insight = await brain.generate_creative_insights(
            domain=domain,
            inspiration_sources=["nature", "philosophy", "technology"],
            creativity_level=0.8
        )
        insights[domain] = insight
        
        print(f"💡 Creative Insight for {domain}:")
        print(f"  {insight.get('insight', 'Generating...')}")
        print(f"  Novelty: {insight.get('novelty_score', 0):.2f}")
        print(f"  Practicality: {insight.get('practicality_score', 0):.2f}")
    
    return insights

# Note: This function might not exist in current implementation
# creative_insights = asyncio.run(creative_insight_example())
```

---

## 🌐 Meta-Cognitive Operations

### Performance Analysis

```python
async def metacognitive_examples():
    # Simulate performance data from various activities
    performance_scenarios = [
        {
            "name": "Learning Session",
            "data": {
                "reasoning_speed": 0.8,
                "memory_retention": 0.9,
                "problem_solving_accuracy": 0.7,
                "creativity_score": 0.6,
                "confidence_level": 0.8,
                "learning_efficiency": 0.75
            }
        },
        {
            "name": "Work Project",
            "data": {
                "reasoning_speed": 0.6,
                "memory_retention": 0.8,
                "problem_solving_accuracy": 0.9,
                "creativity_score": 0.8,
                "confidence_level": 0.7,
                "focus_duration": 0.5
            }
        }
    ]
    
    for scenario in performance_scenarios:
        print(f"\n🔍 Meta-Cognitive Analysis: {scenario['name']}")
        
        analysis = await brain.analyze_cognitive_performance(scenario['data'])
        
        print(f"Overall Score: {analysis.get('overall_score', 0):.2f}")
        print("Strengths:")
        for strength in analysis.get('strengths', [])[:3]:
            print(f"  ✅ {strength}")
        
        print("Improvement Areas:")
        for area in analysis.get('improvement_areas', [])[:3]:
            print(f"  🎯 {area}")
            
        print("Recommendations:")
        for rec in analysis.get('recommendations', [])[:2]:
            print(f"  💡 {rec}")

asyncio.run(metacognitive_examples())
```

### Adaptive Strategy Selection

```python
async def adaptive_strategy_example():
    # Different problem types requiring strategy adaptation
    problems_with_hints = [
        {
            "problem": "Debug a complex distributed system failure",
            "hint": "systematic analysis needed",
            "expected_strategy": "analytical"
        },
        {
            "problem": "Come up with a breakthrough product idea",
            "hint": "innovation and creativity required", 
            "expected_strategy": "creative"
        },
        {
            "problem": "Evaluate whether to adopt a new technology",
            "hint": "careful evaluation of pros and cons",
            "expected_strategy": "critical"
        }
    ]
    
    print("🔄 Adaptive Strategy Selection:")
    for item in problems_with_hints:
        print(f"\nProblem: {item['problem']}")
        print(f"Context hint: {item['hint']}")
        
        # Let the system adapt its strategy
        result = await brain.solve_complex_problem(
            problem=item['problem'],
            context={"hint": item['hint'], "adaptation_mode": True}
        )
        
        print(f"Selected strategy: {result.strategy}")
        print(f"Expected strategy: {item['expected_strategy']}")
        match = "✅" if result.strategy == item['expected_strategy'] else "🔄"
        print(f"Strategy match: {match}")

asyncio.run(adaptive_strategy_example())
```

---

## 🔗 Multi-Tier Integration Examples

### Complete Cognitive Pipeline

```python
async def complete_cognitive_pipeline():
    """Demonstrates how all tiers work together in a realistic scenario"""
    
    print("🌟 Complete Cognitive Pipeline: Learning Assistant Scenario")
    
    # Scenario: Help user learn a new programming language
    goal = "Learn Rust programming language effectively"
    
    # Step 1: Store the learning goal (Memory)
    goal_id = await brain.store_memory(
        content=f"Learning goal: {goal}",
        memory_type="procedural",
        importance=0.9,
        metadata={"type": "goal", "domain": "programming", "language": "rust"}
    )
    print(f"1. 💾 Goal stored in memory: {goal_id}")
    
    # Step 2: Reason about the best learning approach (Reasoning)
    learning_strategy = await brain.solve_complex_problem(
        problem=f"What's the most effective way to {goal.lower()}?",
        context={"domain": "programming", "learning_context": True}
    )
    print(f"2. 🧠 Learning strategy: {learning_strategy.strategy}")
    print(f"   Solution: {learning_strategy.final_conclusion}")
    
    # Step 3: Predict likely challenges (Predictive)
    learning_context = {
        "goal": "learn_rust",
        "background": "experienced_programmer",
        "time_available": "limited"
    }
    challenges = await brain.predict_user_needs(learning_context)
    print(f"3. 🔮 Predicted challenges:")
    for challenge in challenges[:2]:
        print(f"   • {challenge.predicted_content}")
    
    # Step 4: Analyze learning approach effectiveness (Meta-Cognitive)
    learning_performance = {
        "comprehension_speed": 0.7,
        "retention_rate": 0.8,
        "practical_application": 0.6,
        "motivation_level": 0.9
    }
    performance_analysis = await brain.analyze_cognitive_performance(learning_performance)
    print(f"4. 🔍 Performance analysis score: {performance_analysis.get('overall_score', 'N/A')}")
    
    # Step 5: Evolve learning capabilities (Evolutionary)
    current_learning_state = {
        "rust_knowledge": 0.1,
        "systems_programming": 0.4,
        "learning_efficiency": 0.7,
        "problem_solving": 0.8
    }
    evolved_state = await brain.evolve_cognitive_capabilities(current_learning_state)
    print(f"5. 🧬 Learning capabilities evolved")
    
    # Step 6: Store insights for future reference
    pipeline_insights = f"Completed learning pipeline for {goal}. Strategy: {learning_strategy.strategy}. Key insights: {', '.join([c.predicted_content for c in challenges[:2]])}"
    
    insights_id = await brain.store_memory(
        content=pipeline_insights,
        memory_type="semantic",
        importance=0.8,
        metadata={"type": "pipeline_result", "goal": goal}
    )
    print(f"6. 💾 Pipeline insights stored: {insights_id}")
    
    print("\n✅ Complete cognitive pipeline executed successfully!")
    
    return {
        "goal_id": goal_id,
        "strategy": learning_strategy,
        "challenges": challenges,
        "performance": performance_analysis,
        "evolved_state": evolved_state,
        "insights_id": insights_id
    }

pipeline_result = asyncio.run(complete_cognitive_pipeline())
```

### Cross-Tier Learning Example

```python
async def cross_tier_learning():
    """Show how the system learns and improves across tiers"""
    
    print("🔄 Cross-Tier Learning Example: Improving Problem Solving")
    
    # Initial problem solving attempt
    problem = "Design an efficient algorithm for real-time data processing"
    
    print("Phase 1: Initial Problem Solving")
    initial_solution = await brain.solve_complex_problem(problem)
    print(f"Initial strategy: {initial_solution.strategy}")
    print(f"Initial confidence: {initial_solution.overall_confidence:.2f}")
    
    # Store the experience
    await brain.store_memory(
        content=f"Solved algorithm design problem using {initial_solution.strategy} strategy",
        memory_type="episodic",
        importance=initial_solution.overall_confidence,
        metadata={"problem_type": "algorithm_design", "strategy": initial_solution.strategy}
    )
    
    # Analyze performance and get recommendations
    performance_data = {
        "solution_quality": initial_solution.overall_confidence,
        "reasoning_time": initial_solution.reasoning_time,
        "strategy_effectiveness": 0.7
    }
    
    analysis = await brain.analyze_cognitive_performance(performance_data)
    print(f"\nPhase 2: Performance Analysis")
    print(f"Recommendations: {analysis.get('recommendations', [])[:2]}")
    
    # Evolve problem-solving capabilities based on analysis
    evolved_capabilities = await brain.evolve_cognitive_capabilities({
        "algorithm_design": initial_solution.overall_confidence,
        "systems_thinking": 0.7,
        "optimization_skills": 0.6
    })
    
    print(f"\nPhase 3: Capability Evolution")
    print("Evolved capabilities:")
    for skill, level in evolved_capabilities.items():
        print(f"  {skill}: {level:.2f}")
    
    # Attempt the same type of problem again with learned experience
    similar_problem = "Design an efficient algorithm for distributed data processing"
    
    print(f"\nPhase 4: Improved Problem Solving")
    improved_solution = await brain.solve_complex_problem(
        problem=similar_problem,
        context={"learning_context": "algorithm_design", "previous_experience": True}
    )
    
    print(f"Improved strategy: {improved_solution.strategy}")
    print(f"Improved confidence: {improved_solution.overall_confidence:.2f}")
    
    # Compare improvement
    confidence_improvement = improved_solution.overall_confidence - initial_solution.overall_confidence
    print(f"\nImprovement Analysis:")
    print(f"Confidence improvement: +{confidence_improvement:.2f}")
    print(f"Learning effect: {'Positive' if confidence_improvement > 0 else 'Needs adjustment'}")
    
    return {
        "initial": initial_solution,
        "improved": improved_solution,
        "improvement": confidence_improvement
    }

learning_result = asyncio.run(cross_tier_learning())
```

---

## 🎯 Common Use Patterns

### Pattern 1: Daily Learning Assistant

```python
async def daily_learning_assistant():
    """A practical daily learning workflow"""
    
    # Morning: Set learning intention
    today_goal = "Understand transformer architecture in deep learning"
    
    await brain.store_memory(
        content=f"Today's learning goal: {today_goal}",
        memory_type="procedural",
        importance=0.8,
        metadata={"date": "today", "type": "daily_goal"}
    )
    
    # Get learning strategy
    strategy = await brain.solve_complex_problem(
        f"What's the best approach to {today_goal.lower()} in one focused session?"
    )
    
    # Predict potential obstacles
    context = {"learning_goal": today_goal, "available_time": "2_hours"}
    obstacles = await brain.predict_user_needs(context)
    
    print("📚 Daily Learning Plan:")
    print(f"Goal: {today_goal}")
    print(f"Strategy: {strategy.final_conclusion}")
    print("Potential obstacles:")
    for obs in obstacles[:2]:
        print(f"  • {obs.predicted_content}")

asyncio.run(daily_learning_assistant())
```

### Pattern 2: Decision Making Framework

```python
async def decision_making_framework():
    """Structured approach to important decisions"""
    
    decision = "Should I switch from my current job to a startup?"
    
    # Gather different perspectives
    perspectives = [
        "Analyze pros and cons systematically",
        "Consider creative possibilities and potential",
        "Evaluate ethical implications and values alignment",
        "Understand systemic impact on career and life"
    ]
    
    results = []
    for perspective in perspectives:
        result = await brain.solve_complex_problem(
            f"{perspective}: {decision}"
        )
        results.append(result)
        
        print(f"🤔 {perspective}:")
        print(f"   {result.final_conclusion}")
    
    # Meta-analyze the decision process
    decision_quality = {
        "perspective_diversity": 0.9,
        "analysis_depth": 0.8,
        "confidence_level": sum(r.overall_confidence for r in results) / len(results)
    }
    
    meta_analysis = await brain.analyze_cognitive_performance(decision_quality)
    print(f"\n📊 Decision Quality Score: {meta_analysis.get('overall_score', 'N/A')}")

asyncio.run(decision_making_framework())
```

### Pattern 3: Creative Problem Solving

```python
async def creative_problem_solving():
    """Enhanced creativity for innovation challenges"""
    
    challenge = "Design a novel approach to reduce food waste in cities"
    
    # Use creative reasoning
    creative_solution = await brain.solve_complex_problem(challenge)
    
    # Evolve the creative capabilities
    creativity_boost = await brain.evolve_cognitive_capabilities({
        "creative_thinking": 0.7,
        "systems_design": 0.6,
        "environmental_awareness": 0.8
    })
    
    # Generate enhanced solution
    enhanced_solution = await brain.solve_complex_problem(
        f"Enhance and innovate upon this idea: {creative_solution.final_conclusion}"
    )
    
    print("🎨 Creative Problem Solving:")
    print(f"Challenge: {challenge}")
    print(f"Initial solution: {creative_solution.final_conclusion}")
    print(f"Enhanced solution: {enhanced_solution.final_conclusion}")

asyncio.run(creative_problem_solving())
```

---

## 🔧 Utility Functions

### Custom Analysis Function

```python
async def analyze_cognitive_session():
    """Analyze your cognitive session performance"""
    
    # Retrieve recent memories
    recent_memories = await brain.retrieve_memories("", limit=10)
    
    # Analyze memory patterns
    memory_types = {}
    total_importance = 0
    
    for memory in recent_memories:
        memory_types[memory.memory_type] = memory_types.get(memory.memory_type, 0) + 1
        total_importance += memory.importance
    
    avg_importance = total_importance / len(recent_memories) if recent_memories else 0
    
    print("🔍 Cognitive Session Analysis:")
    print(f"Total memories: {len(recent_memories)}")
    print(f"Memory distribution: {memory_types}")
    print(f"Average importance: {avg_importance:.2f}")
    
    # Get predictions for session optimization
    session_context = {
        "session_type": "analysis",
        "memory_count": len(recent_memories),
        "avg_importance": avg_importance
    }
    
    optimization_tips = await brain.predict_user_needs(session_context)
    
    print("Optimization suggestions:")
    for tip in optimization_tips[:3]:
        print(f"  💡 {tip.predicted_content}")

asyncio.run(analyze_cognitive_session())
```

---

**🚀 Ready to explore more advanced features? Check out the [Architecture Overview](../architecture/overview.md) or dive into specific [Cognitive Tiers](../tiers/) documentation! 🧠✨**