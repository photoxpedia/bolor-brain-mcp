# Bolor Brain MCP 🧠

A lightweight Model Context Protocol (MCP) server that exposes core brain cognitive architecture as tools for Claude Code integration.

**Author:** Bolorerdene Bundgaa  
**Email:** bolor@ariunbolor.org  
**Website:** https://bolor.me  
**License:** MIT

## Features

### 🧠 Core Brain Architecture
- **5 Memory Systems**: Working, Episodic, Semantic, Procedural, Emotional
- **Cognitive State**: Attention, Curiosity, Emotional state, Confidence tracking
- **Persistent Storage**: JSON-based memory persistence across sessions

### 🛠️ Available MCP Tools

1. **`store_memory`** - Enhanced memory storage with advanced features
   - Parameters: content, memory_type, metadata, modality, emotional_valence, importance
   - Memory types: working, episodic, semantic, procedural, emotional
   - Modalities: text, image, audio, structured

2. **`retrieve_memories`** - Semantic similarity-based memory retrieval
   - Parameters: query, memory_types (optional), limit (default: 5)
   - Returns: Memories with vector similarity scoring and cross-connections

3. **`process_with_attention`** - Cognitive attention processing
   - Parameters: input_text
   - Returns: Contextual response with attention focus and relevant memories

4. **`get_brain_status`** - Comprehensive brain analytics
   - Returns: Memory counts, cognitive state, connection graph, consolidation stats

5. **`update_cognitive_state`** - Dynamic cognitive parameter adjustment
   - Parameters: attention_focus, curiosity_level, emotional_state, confidence

6. **`add_feedback`** - Adaptive learning through user feedback
   - Parameters: interaction_id, feedback_type, score
   - Enables continuous improvement of response quality

7. **`store_multimodal_memory`** - Multi-modal data storage
   - Parameters: content, data, modality, memory_type, metadata
   - Supports images, audio, and structured data with base64 encoding

## Installation

### Prerequisites
```bash
pip install mcp numpy
```

### Setup
1. The server automatically creates a `./brain_mcp_storage/` directory for persistence
2. Memories are stored in `brain_mcp_storage/memories.json`

## Usage

### As MCP Server (with Claude Code)
```bash
python brain_mcp_server.py
```

### Standalone Demo
```bash
python brain_mcp_server.py
# Shows brain functionality without MCP dependencies
```

## Core Components Extracted

### Brain System:
- **Unified Memory Architecture**: Simplified but maintains all 5 memory types
- **Cognitive Processing**: Attention mechanism and contextual retrieval
- **Persistent Learning**: Memory persistence across sessions
- **Contextual Responses**: Using retrieved memories to inform responses

### Lightweight Design:
- **No Heavy Dependencies**: Works without TensorFlow, PyTorch, or FastAPI
- **JSON Storage**: Simple file-based persistence (can be upgraded to databases)
- **Modular Architecture**: Easy to extend with additional cognitive features

## Memory Types

- **Working**: Active, temporary information (short-term)
- **Episodic**: Events and experiences with temporal context
- **Semantic**: Facts, knowledge, and concepts
- **Procedural**: Skills, procedures, and how-to knowledge
- **Emotional**: Feelings, preferences, and emotional associations

## Cognitive State Parameters

- **Attention Focus**: Current focus keywords/concepts
- **Curiosity Level**: 0.0-1.0, drives exploration behavior
- **Emotional State**: Current emotional context (neutral, excited, focused, etc.)
- **Confidence**: 0.0-1.0, confidence in responses and decisions

## Example Usage

```python
# Store procedural knowledge
brain.store_memory(
    "When debugging, check syntax first, then logic", 
    "procedural", 
    {"domain": "programming", "skill_level": "beginner"}
)

# Store episodic memory
brain.store_memory(
    "User asked about Python debugging at 2pm", 
    "episodic", 
    {"interaction_type": "help_request", "topic": "debugging"}
)

# Process with attention and context
result = brain.process_with_attention("How do I debug my code?")
print(result["response"])  # Uses retrieved memories for context
```

## Integration with Claude Code

This MCP server allows Claude Code to:
1. **Remember Context**: Store conversation history and learned information
2. **Retrieve Relevant Information**: Access past interactions and knowledge
3. **Focus Attention**: Process inputs with cognitive attention mechanisms
4. **Learn Over Time**: Build up knowledge through interactions
5. **Maintain State**: Persistent cognitive state across sessions

## Advanced Features (Implemented)

- ✅ **Vector Embeddings**: Semantic similarity using SentenceTransformers for enhanced memory retrieval
- ✅ **Memory Consolidation**: Automatic memory strength updates based on access patterns
- ✅ **Cross-Memory Connections**: Automatic bidirectional connections between similar memories  
- ✅ **Adaptive Responses**: Learning from user feedback to improve response quality
- ✅ **Multi-Modal Memory**: Support for text, images, audio, and structured data storage

## Bolor Brain MCP Architecture

This IS the complete brain system, optimized for MCP integration:

| Component | Status |
|-----------|--------|
| **5 Memory Systems** | ✅ Complete (Working, Episodic, Semantic, Procedural, Emotional) |
| **Cognitive Architecture** | ✅ Attention, Curiosity, Executive Control, Risk Assessment |
| **MCP Integration** | ✅ Native Claude Code compatibility |
| **Persistent Storage** | ✅ JSON-based with upgrade path to databases |
| **Real-time Learning** | ✅ Memory updates and contextual responses |
| **Lightweight Design** | ✅ Optimized for production use |

This Bolor Brain MCP represents the complete cognitive architecture designed specifically for seamless Claude Code integration.

---

**Bolor Brain MCP** - Created by Bolorerdene Bundgaa  
🌐 Visit: https://bolor.me | 📧 Contact: bolor@ariunbolor.org