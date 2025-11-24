#!/usr/bin/env python3
"""
Bolor Brain MCP - Core cognitive architecture exposed as MCP tools
Lightweight extraction of brain functionality for Claude Code integration

Author: Bolorerdene Bundgaa
Email: bolor@ariunbolor.org  
Website: https://bolor.me
License: MIT
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import sys
import os
from pathlib import Path

# MCP imports
try:
    import mcp.types as types
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not available. Install with: pip install mcp")

# Core brain components (simplified)
from dataclasses import dataclass, field
from collections import defaultdict, deque
import sqlite3
import uuid
import time
import hashlib
import base64

# Enhanced cognitive features
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Vector embeddings for semantic similarity  
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryItem:
    """Enhanced memory item with advanced cognitive features"""
    id: str
    content: str
    memory_type: str  # working, episodic, semantic, procedural, emotional
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    strength: float = 1.0
    connections: List[str] = field(default_factory=list)
    
    # Advanced features
    embedding: Optional[List[float]] = None  # Vector embedding for semantic similarity
    access_count: int = 0  # For memory consolidation
    last_accessed: float = field(default_factory=time.time)
    feedback_score: float = 0.0  # For adaptive responses
    modality: str = "text"  # text, image, audio, structured
    emotional_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    importance: float = 0.5  # 0.0 to 1.0

@dataclass
class CognitiveState:
    """Current cognitive state of the brain"""
    attention_focus: str = ""
    curiosity_level: float = 0.5
    emotional_state: str = "neutral"
    confidence: float = 0.7
    active_memories: List[str] = field(default_factory=list)

class SimpleBrain:
    """Enhanced brain implementation with advanced cognitive features"""
    
    def __init__(self, storage_path: str = "./brain_mcp_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize memory systems
        self.memories: Dict[str, MemoryItem] = {}
        self.memory_index: Dict[str, List[str]] = defaultdict(list)
        self.cognitive_state = CognitiveState()
        
        # Advanced features
        self.embedding_model = None
        self.connection_graph: Dict[str, List[str]] = defaultdict(list)
        self.feedback_history: List[Dict[str, Any]] = []
        
        # Initialize embedding model if available
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Vector embedding model loaded")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.embedding_model = None
        
        # Load existing memories
        self._load_memories()
        
        logger.info(f"Enhanced Brain initialized with {len(self.memories)} memories")
    
    def _load_memories(self):
        """Load memories from persistent storage"""
        memory_file = self.storage_path / "memories.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    for item_data in data:
                        memory = MemoryItem(**item_data)
                        self.memories[memory.id] = memory
                        self.memory_index[memory.memory_type].append(memory.id)
            except Exception as e:
                logger.warning(f"Failed to load memories: {e}")
    
    def _save_memories(self):
        """Save memories to persistent storage"""
        memory_file = self.storage_path / "memories.json"
        try:
            data = []
            for memory in self.memories.values():
                data.append({
                    'id': memory.id,
                    'content': memory.content,
                    'memory_type': memory.memory_type,
                    'metadata': memory.metadata,
                    'timestamp': memory.timestamp,
                    'strength': memory.strength,
                    'connections': memory.connections
                })
            with open(memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")
    
    def store_memory(self, content: str, memory_type: str, metadata: Dict[str, Any] = None, 
                    modality: str = "text", emotional_valence: float = 0.0, importance: float = 0.5) -> str:
        """Store new memory with advanced features"""
        memory_id = str(uuid.uuid4())
        
        # Generate embedding if model available
        embedding = None
        if self.embedding_model and modality == "text":
            try:
                embedding = self.embedding_model.encode(content).tolist()
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        memory = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            metadata=metadata or {},
            timestamp=time.time(),
            embedding=embedding,
            modality=modality,
            emotional_valence=emotional_valence,
            importance=importance
        )
        
        self.memories[memory_id] = memory
        self.memory_index[memory_type].append(memory_id)
        
        # Create cross-memory connections
        self._create_connections(memory_id)
        
        # Update cognitive state
        self.cognitive_state.active_memories.append(memory_id)
        if len(self.cognitive_state.active_memories) > 10:
            self.cognitive_state.active_memories.pop(0)
        
        # Memory consolidation
        self._consolidate_memories()
        
        self._save_memories()
        return memory_id
    
    def retrieve_memories(self, query: str, memory_types: List[str] = None, limit: int = 5) -> List[MemoryItem]:
        """Enhanced memory retrieval with vector similarity"""
        if memory_types is None:
            memory_types = ["working", "episodic", "semantic", "procedural", "emotional"]
        
        relevant_memories = []
        query_words = query.lower().split()
        
        # Generate query embedding for semantic similarity
        query_embedding = None
        if self.embedding_model:
            try:
                query_embedding = self.embedding_model.encode(query).tolist()
            except Exception as e:
                logger.warning(f"Failed to generate query embedding: {e}")
        
        for memory_type in memory_types:
            for memory_id in self.memory_index.get(memory_type, []):
                memory = self.memories[memory_id]
                content_lower = memory.content.lower()
                
                # Update access tracking for consolidation
                memory.access_count += 1
                memory.last_accessed = time.time()
                
                # Calculate relevance score
                relevance_score = 0
                
                # Semantic similarity using embeddings
                if query_embedding and memory.embedding and NUMPY_AVAILABLE:
                    try:
                        similarity = np.dot(query_embedding, memory.embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(memory.embedding)
                        )
                        relevance_score += similarity * 10  # Weight semantic similarity
                    except:
                        pass
                
                # Exact phrase match
                if query.lower() in content_lower:
                    relevance_score += 5
                
                # Word matches
                for word in query_words:
                    if word in content_lower:
                        relevance_score += 1
                
                # Metadata matches
                for value in memory.metadata.values():
                    if any(word in str(value).lower() for word in query_words):
                        relevance_score += 1
                
                # Importance and strength boosting
                relevance_score *= memory.importance * memory.strength
                
                # Connection boosting
                if memory_id in self.connection_graph:
                    relevance_score += len(self.connection_graph[memory_id]) * 0.1
                
                if relevance_score > 0:
                    memory.relevance_score = relevance_score
                    relevant_memories.append(memory)
        
        # Sort by enhanced relevance scoring
        relevant_memories.sort(
            key=lambda m: (
                getattr(m, 'relevance_score', 0) + 
                max(0, 1 - (time.time() - m.timestamp) / 86400) +  # Recent boost
                m.feedback_score  # Adaptive learning boost
            ), 
            reverse=True
        )
        
        return relevant_memories[:limit]
    
    def process_with_attention(self, input_text: str) -> Dict[str, Any]:
        """Process input with attention mechanism"""
        # Simple attention: focus on key terms
        key_terms = [word for word in input_text.split() if len(word) > 3]
        self.cognitive_state.attention_focus = " ".join(key_terms[:5])
        
        # Retrieve relevant context
        context_memories = self.retrieve_memories(input_text, limit=3)
        
        # Generate response with context
        response = self._generate_response(input_text, context_memories)
        
        # Store interaction in episodic memory
        interaction_id = self.store_memory(
            f"User: {input_text}\nBrain: {response}",
            "episodic",
            {"interaction_type": "conversation", "attention_focus": self.cognitive_state.attention_focus}
        )
        
        return {
            "response": response,
            "attention_focus": self.cognitive_state.attention_focus,
            "context_memories": [{"id": m.id, "content": m.content, "type": m.memory_type} for m in context_memories],
            "interaction_id": interaction_id,
            "confidence": self.cognitive_state.confidence
        }
    
    def _generate_response(self, input_text: str, context_memories: List[MemoryItem]) -> str:
        """Generate response using context"""
        if not context_memories:
            return f"I understand you're asking about '{input_text}'. I'll remember this for future reference."
        
        context_summary = " | ".join([m.content[:100] + "..." if len(m.content) > 100 else m.content 
                                     for m in context_memories[:2]])
        
        return f"Based on my memory of {context_summary}, I can help with '{input_text}'. This builds on my previous understanding."
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get brain memory statistics"""
        stats = {
            "total_memories": len(self.memories),
            "memory_types": {},
            "cognitive_state": {
                "attention_focus": self.cognitive_state.attention_focus,
                "curiosity_level": self.cognitive_state.curiosity_level,
                "emotional_state": self.cognitive_state.emotional_state,
                "confidence": self.cognitive_state.confidence,
                "active_memories_count": len(self.cognitive_state.active_memories)
            },
            "oldest_memory": min([m.timestamp for m in self.memories.values()]) if self.memories else 0,
            "newest_memory": max([m.timestamp for m in self.memories.values()]) if self.memories else 0
        }
        
        for memory_type in ["working", "episodic", "semantic", "procedural", "emotional"]:
            stats["memory_types"][memory_type] = len(self.memory_index[memory_type])
        
        return stats
    
    def _create_connections(self, memory_id: str) -> None:
        """Create cross-memory connections based on content similarity"""
        if not self.embedding_model or not NUMPY_AVAILABLE:
            return
            
        new_memory = self.memories[memory_id]
        if not new_memory.embedding:
            return
            
        # Find similar memories
        for existing_id, existing_memory in self.memories.items():
            if existing_id == memory_id or not existing_memory.embedding:
                continue
                
            try:
                similarity = np.dot(new_memory.embedding, existing_memory.embedding) / (
                    np.linalg.norm(new_memory.embedding) * np.linalg.norm(existing_memory.embedding)
                )
                
                # Create bidirectional connections for high similarity
                if similarity > 0.7:  # Threshold for connection
                    if existing_id not in new_memory.connections:
                        new_memory.connections.append(existing_id)
                    if memory_id not in existing_memory.connections:
                        existing_memory.connections.append(memory_id)
                        
                    # Update connection graph
                    self.connection_graph[memory_id].append(existing_id)
                    self.connection_graph[existing_id].append(memory_id)
                    
            except Exception as e:
                logger.debug(f"Connection creation failed: {e}")
    
    def _consolidate_memories(self) -> None:
        """Memory consolidation - strengthen frequently accessed memories"""
        current_time = time.time()
        
        for memory in self.memories.values():
            # Strengthen memories based on access pattern
            if memory.access_count > 5:
                memory.strength = min(2.0, memory.strength * 1.1)
            
            # Decay unused memories (but keep important ones)
            days_since_access = (current_time - memory.last_accessed) / 86400
            if days_since_access > 7 and memory.importance < 0.5:
                memory.strength = max(0.1, memory.strength * 0.95)
    
    def add_feedback(self, interaction_id: str, feedback_type: str, score: float) -> None:
        """Add feedback for adaptive responses"""
        feedback = {
            "interaction_id": interaction_id,
            "type": feedback_type,  # 'positive', 'negative', 'correction'
            "score": score,  # -1.0 to 1.0
            "timestamp": time.time()
        }
        
        self.feedback_history.append(feedback)
        
        # Update memory feedback scores for related memories
        if hasattr(self, '_last_retrieved_memories'):
            for memory in self._last_retrieved_memories:
                if feedback_type == 'positive':
                    memory.feedback_score = min(1.0, memory.feedback_score + 0.1)
                elif feedback_type == 'negative':
                    memory.feedback_score = max(-1.0, memory.feedback_score - 0.1)
    
    def store_multimodal_memory(self, content: str, data: Any, modality: str, 
                               memory_type: str, metadata: Dict[str, Any] = None) -> str:
        """Store multi-modal memory (images, audio, structured data)"""
        
        # Encode non-text data
        encoded_data = None
        if modality == "image":
            # For images, store base64 encoded
            if isinstance(data, bytes):
                encoded_data = base64.b64encode(data).decode('utf-8')
            else:
                encoded_data = str(data)  # Assume already encoded
                
        elif modality == "audio":
            # For audio, store base64 encoded
            if isinstance(data, bytes):
                encoded_data = base64.b64encode(data).decode('utf-8')
            else:
                encoded_data = str(data)
                
        elif modality == "structured":
            # For structured data, store as JSON
            encoded_data = json.dumps(data) if not isinstance(data, str) else data
        else:
            encoded_data = str(data)
        
        # Create enhanced metadata
        enhanced_metadata = metadata or {}
        enhanced_metadata.update({
            "modality": modality,
            "data_hash": hashlib.md5(str(encoded_data).encode()).hexdigest(),
            "encoding": "base64" if modality in ["image", "audio"] else "json"
        })
        
        # Store with original content but enhanced metadata
        return self.store_memory(
            content=content,
            memory_type=memory_type,
            metadata=enhanced_metadata,
            modality=modality
        )

# Initialize brain
brain = SimpleBrain()

# MCP Server setup
if MCP_AVAILABLE:
    server = Server("bolor-brain-mcp")
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available brain tools"""
        return [
            types.Tool(
                name="store_memory",
                description="Store information in the brain's memory system",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to store in memory"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["working", "episodic", "semantic", "procedural", "emotional"],
                            "description": "Type of memory to store in"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata for the memory",
                            "additionalProperties": True
                        },
                        "modality": {
                            "type": "string",
                            "enum": ["text", "image", "audio", "structured"],
                            "description": "Type of content modality",
                            "default": "text"
                        },
                        "emotional_valence": {
                            "type": "number",
                            "minimum": -1.0,
                            "maximum": 1.0,
                            "description": "Emotional valence (-1.0 negative to 1.0 positive)",
                            "default": 0.0
                        },
                        "importance": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Memory importance level (0.0 to 1.0)",
                            "default": 0.5
                        }
                    },
                    "required": ["content", "memory_type"]
                }
            ),
            types.Tool(
                name="retrieve_memories",
                description="Search and retrieve relevant memories from the brain",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to find relevant memories"
                        },
                        "memory_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["working", "episodic", "semantic", "procedural", "emotional"]
                            },
                            "description": "Types of memory to search in (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of memories to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="process_with_attention",
                description="Process input using the brain's attention mechanism and contextual memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input_text": {
                            "type": "string",
                            "description": "Text input to process with attention"
                        }
                    },
                    "required": ["input_text"]
                }
            ),
            types.Tool(
                name="get_brain_status",
                description="Get current brain status including memory statistics and cognitive state",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            types.Tool(
                name="update_cognitive_state",
                description="Update the brain's cognitive state parameters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "attention_focus": {
                            "type": "string",
                            "description": "New attention focus"
                        },
                        "curiosity_level": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Curiosity level (0.0 to 1.0)"
                        },
                        "emotional_state": {
                            "type": "string",
                            "description": "Current emotional state"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence level (0.0 to 1.0)"
                        }
                    }
                }
            ),
            types.Tool(
                name="add_feedback",
                description="Add feedback to improve adaptive responses",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "interaction_id": {
                            "type": "string",
                            "description": "ID of the interaction to provide feedback on"
                        },
                        "feedback_type": {
                            "type": "string",
                            "enum": ["positive", "negative", "correction"],
                            "description": "Type of feedback"
                        },
                        "score": {
                            "type": "number",
                            "minimum": -1.0,
                            "maximum": 1.0,
                            "description": "Feedback score (-1.0 to 1.0)"
                        }
                    },
                    "required": ["interaction_id", "feedback_type", "score"]
                }
            ),
            types.Tool(
                name="store_multimodal_memory",
                description="Store multi-modal memory (images, audio, structured data)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Text description of the content"
                        },
                        "data": {
                            "type": "string",
                            "description": "The actual data (base64 encoded for binary data)"
                        },
                        "modality": {
                            "type": "string",
                            "enum": ["image", "audio", "structured"],
                            "description": "Type of data being stored"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["working", "episodic", "semantic", "procedural", "emotional"],
                            "description": "Type of memory to store in"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata",
                            "additionalProperties": True
                        }
                    },
                    "required": ["content", "data", "modality", "memory_type"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls"""
        try:
            if name == "store_memory":
                memory_id = brain.store_memory(
                    content=arguments["content"],
                    memory_type=arguments["memory_type"],
                    metadata=arguments.get("metadata", {}),
                    modality=arguments.get("modality", "text"),
                    emotional_valence=arguments.get("emotional_valence", 0.0),
                    importance=arguments.get("importance", 0.5)
                )
                result = {
                    "memory_id": memory_id,
                    "status": "stored",
                    "memory_type": arguments["memory_type"]
                }
                
            elif name == "retrieve_memories":
                memories = brain.retrieve_memories(
                    query=arguments["query"],
                    memory_types=arguments.get("memory_types"),
                    limit=arguments.get("limit", 5)
                )
                result = {
                    "query": arguments["query"],
                    "memories_found": len(memories),
                    "memories": [
                        {
                            "id": m.id,
                            "content": m.content,
                            "memory_type": m.memory_type,
                            "metadata": m.metadata,
                            "timestamp": m.timestamp,
                            "strength": m.strength
                        } for m in memories
                    ]
                }
                
            elif name == "process_with_attention":
                result = brain.process_with_attention(arguments["input_text"])
                
            elif name == "get_brain_status":
                result = brain.get_memory_statistics()
                
            elif name == "update_cognitive_state":
                for key, value in arguments.items():
                    if hasattr(brain.cognitive_state, key):
                        setattr(brain.cognitive_state, key, value)
                result = {
                    "status": "updated",
                    "cognitive_state": {
                        "attention_focus": brain.cognitive_state.attention_focus,
                        "curiosity_level": brain.cognitive_state.curiosity_level,
                        "emotional_state": brain.cognitive_state.emotional_state,
                        "confidence": brain.cognitive_state.confidence
                    }
                }
                
            elif name == "add_feedback":
                brain.add_feedback(
                    interaction_id=arguments["interaction_id"],
                    feedback_type=arguments["feedback_type"],
                    score=arguments["score"]
                )
                result = {
                    "status": "feedback_added",
                    "interaction_id": arguments["interaction_id"],
                    "feedback_type": arguments["feedback_type"],
                    "score": arguments["score"]
                }
                
            elif name == "store_multimodal_memory":
                memory_id = brain.store_multimodal_memory(
                    content=arguments["content"],
                    data=arguments["data"],
                    modality=arguments["modality"],
                    memory_type=arguments["memory_type"],
                    metadata=arguments.get("metadata", {})
                )
                result = {
                    "memory_id": memory_id,
                    "status": "stored",
                    "modality": arguments["modality"],
                    "memory_type": arguments["memory_type"]
                }
                
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def main():
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bolor-brain-mcp",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    if __name__ == "__main__":
        asyncio.run(main())
        
else:
    def main():
        print("MCP not available. Install with: pip install mcp")
        print("This module provides Bolor Brain MCP cognitive tools for MCP integration.")
        print("Author: Bolorerdene Bundgaa | https://bolor.me")
        
        # Demo the brain functionality
        print("\n🧠 Brain Demo:")
        
        # Store some memories
        id1 = brain.store_memory("Python is a programming language", "semantic")
        id2 = brain.store_memory("I helped a user debug code yesterday", "episodic")
        id3 = brain.store_memory("When debugging, check syntax first", "procedural")
        
        print(f"Stored {len(brain.memories)} memories")
        
        # Process with attention
        result = brain.process_with_attention("How do I debug Python code?")
        print(f"\nAttention processing result:")
        print(f"Response: {result['response']}")
        print(f"Attention Focus: {result['attention_focus']}")
        print(f"Context memories: {len(result['context_memories'])}")
        
        # Get statistics
        stats = brain.get_memory_statistics()
        print(f"\nBrain Statistics:")
        print(f"Total memories: {stats['total_memories']}")
        print(f"Memory types: {stats['memory_types']}")
        
    if __name__ == "__main__":
        main()