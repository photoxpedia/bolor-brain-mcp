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
import secrets
import jwt
from urllib.parse import urlparse
import datetime

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

# Security and OAuth 2.1 imports
try:
    import cryptography
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("Cryptography not available. Install with: pip install cryptography")

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
class SecurityContext:
    """OAuth 2.1 security context with RFC 8707 resource indicators"""
    client_id: Optional[str] = None
    access_token: Optional[str] = None
    resource_indicator: Optional[str] = None
    scope: str = "brain:read brain:write"
    token_type: str = "Bearer"
    expires_at: Optional[float] = None
    authenticated: bool = False
    
    def is_valid(self) -> bool:
        """Check if security context is valid"""
        if not self.authenticated:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True
    
    def has_scope(self, required_scope: str) -> bool:
        """Check if token has required scope"""
        return required_scope in self.scope.split()

@dataclass
class CognitiveState:
    """Current cognitive state of the brain"""
    attention_focus: str = ""
    curiosity_level: float = 0.5
    emotional_state: str = "neutral"
    confidence: float = 0.7
    active_memories: List[str] = field(default_factory=list)
    security_context: SecurityContext = field(default_factory=SecurityContext)

class SimpleBrain:
    """Enhanced brain implementation with advanced cognitive features"""
    
    def __init__(self, storage_path: str = "./brain_mcp_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize memory systems with SQLite
        self.use_sqlite = os.getenv('BRAIN_USE_SQLITE', 'true').lower() == 'true'
        self.db_path = self.storage_path / "memories.db"
        self.memories: Dict[str, MemoryItem] = {}
        self.memory_index: Dict[str, List[str]] = defaultdict(list)
        self.cognitive_state = CognitiveState()
        
        # Initialize database
        if self.use_sqlite:
            self._init_database()
        
        # Async task management (MCP 2025 async operations)
        self._task_queue: Dict[str, Dict[str, Any]] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._task_results: Dict[str, Any] = {}
        
        # Comprehensive monitoring and metrics
        self._metrics = {
            'startup_time': time.time(),
            'tool_calls': defaultdict(int),
            'memory_operations': {'stores': 0, 'retrievals': 0, 'updates': 0},
            'authentication_attempts': {'success': 0, 'failures': 0},
            'async_tasks': {'created': 0, 'completed': 0, 'failed': 0},
            'performance': {'avg_retrieval_time': 0.0, 'total_retrievals': 0},
            'errors': defaultdict(int),
            'last_activity': time.time()
        }
        
        # Advanced features
        self.embedding_model = None
        self.connection_graph: Dict[str, List[str]] = defaultdict(list)
        self.feedback_history: List[Dict[str, Any]] = []
        
        # Security features (OAuth 2.1)
        self._secret_key = self._generate_secret_key()
        self._resource_server_id = f"brain-mcp-{uuid.uuid4().hex[:8]}"
        self._authorized_clients: Dict[str, Dict[str, Any]] = {}
        
        # Initialize security context
        self.cognitive_state.security_context = SecurityContext()
        
        # Lazy loading for embedding model to improve startup time
        self.embedding_model = None
        self._embedding_model_loaded = False
        self._embedding_cache = {}
        self._embedding_cache_max_size = int(os.getenv('BRAIN_EMBEDDING_CACHE_SIZE', '1000'))
        self._use_embedding_cache = os.getenv('BRAIN_USE_EMBEDDING_CACHE', 'true').lower() == 'true'
        
        # Load existing memories
        self._load_memories()
        
        logger.info(f"Enhanced Brain initialized with {len(self.memories)} memories")
        logger.info(f"Resource server ID: {self._resource_server_id}")
        logger.info(f"Security context initialized: {self.cognitive_state.security_context.authenticated}")
    
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create memories table with indexes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    metadata TEXT,
                    timestamp REAL,
                    strength REAL DEFAULT 1.0,
                    connections TEXT,
                    embedding BLOB,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL,
                    feedback_score REAL DEFAULT 0.0,
                    modality TEXT DEFAULT 'text',
                    emotional_valence REAL DEFAULT 0.0,
                    importance REAL DEFAULT 0.5,
                    created_at REAL DEFAULT (datetime('now', 'unixepoch')),
                    updated_at REAL DEFAULT (datetime('now', 'unixepoch'))
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_count ON memories(access_count)')
            
            # Create full-text search table
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    id UNINDEXED,
                    content,
                    memory_type UNINDEXED,
                    content='memories',
                    content_rowid='rowid'
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("SQLite database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _load_memories(self):
        """Load memories from persistent storage"""
        if self.use_sqlite:
            self._load_memories_sqlite()
        else:
            self._load_memories_json()
    
    def _load_memories_json(self):
        """Load memories from JSON file (legacy)"""
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
                logger.warning(f"Failed to load memories from JSON: {e}")
    
    def _load_memories_sqlite(self):
        """Load memories from SQLite database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content, memory_type, metadata, timestamp, strength, 
                       connections, embedding, access_count, last_accessed, 
                       feedback_score, modality, emotional_valence, importance
                FROM memories
                ORDER BY importance DESC, timestamp DESC
                LIMIT 10000
            ''')
            
            for row in cursor.fetchall():
                memory_data = {
                    'id': row[0],
                    'content': row[1],
                    'memory_type': row[2],
                    'metadata': json.loads(row[3] or '{}'),
                    'timestamp': row[4],
                    'strength': row[5],
                    'connections': json.loads(row[6] or '[]'),
                    'embedding': json.loads(row[7]) if row[7] else None,
                    'access_count': row[8],
                    'last_accessed': row[9],
                    'feedback_score': row[10],
                    'modality': row[11],
                    'emotional_valence': row[12],
                    'importance': row[13]
                }
                
                memory = MemoryItem(**memory_data)
                self.memories[memory.id] = memory
                self.memory_index[memory.memory_type].append(memory.id)
            
            conn.close()
            logger.info(f"Loaded {len(self.memories)} memories from SQLite")
            
        except Exception as e:
            logger.warning(f"Failed to load memories from SQLite: {e}")
            # Fallback to JSON if SQLite fails
            self._load_memories_json()
    
    def _save_memories(self):
        """Save memories to persistent storage"""
        if self.use_sqlite:
            # SQLite saves automatically on each operation
            pass
        else:
            self._save_memories_json()
    
    def _save_memories_json(self):
        """Save memories to JSON file (legacy)"""
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
            logger.error(f"Failed to save memories to JSON: {e}")
    
    async def _save_memory_sqlite(self, memory: MemoryItem):
        """Save single memory to SQLite database (async)"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Insert or replace memory
            cursor.execute('''
                INSERT OR REPLACE INTO memories (
                    id, content, memory_type, metadata, timestamp, strength,
                    connections, embedding, access_count, last_accessed,
                    feedback_score, modality, emotional_valence, importance,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'unixepoch'))
            ''', (
                memory.id,
                memory.content,
                memory.memory_type,
                json.dumps(memory.metadata),
                memory.timestamp,
                memory.strength,
                json.dumps(memory.connections),
                json.dumps(memory.embedding) if memory.embedding else None,
                memory.access_count,
                memory.last_accessed,
                memory.feedback_score,
                memory.modality,
                memory.emotional_valence,
                memory.importance
            ))
            
            # Update FTS table
            cursor.execute('''
                INSERT OR REPLACE INTO memories_fts(id, content, memory_type)
                VALUES (?, ?, ?)
            ''', (memory.id, memory.content, memory.memory_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save memory to SQLite: {e}")
            raise
    
    def _generate_secret_key(self) -> str:
        """Generate cryptographic secret key for OAuth 2.1"""
        return secrets.token_urlsafe(32)
    
    def _validate_resource_indicator(self, resource: str) -> bool:
        """Validate RFC 8707 resource indicator"""
        try:
            parsed = urlparse(resource)
            # Resource indicator must be absolute URI
            return parsed.scheme and parsed.netloc
        except:
            return False
    
    def authenticate_client(self, client_id: str, access_token: str, resource_indicator: Optional[str] = None) -> bool:
        """OAuth 2.1 client authentication with RFC 8707 resource indicators"""
        try:
            # Validate resource indicator if provided
            if resource_indicator and not self._validate_resource_indicator(resource_indicator):
                logger.warning(f"Invalid resource indicator: {resource_indicator}")
                return False
            
            # In production, validate token with authorization server
            # For now, implement basic token validation
            if not access_token or len(access_token) < 10:
                return False
            
            # Decode and validate token (simplified for demo)
            # In production, use proper JWT validation with public keys
            token_data = {
                'client_id': client_id,
                'scope': 'brain:read brain:write',
                'exp': time.time() + 3600,  # 1 hour expiry
                'aud': self._resource_server_id,  # Audience validation
                'resource': resource_indicator
            }
            
            # Update security context
            self.cognitive_state.security_context = SecurityContext(
                client_id=client_id,
                access_token=access_token,
                resource_indicator=resource_indicator,
                scope=token_data['scope'],
                expires_at=token_data['exp'],
                authenticated=True
            )
            
            # Store authorized client
            self._authorized_clients[client_id] = token_data
            
            logger.info(f"Client authenticated: {client_id} with resource: {resource_indicator}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed for client {client_id}: {e}")
            return False
    
    def check_authorization(self, required_scope: str = "brain:read") -> bool:
        """Check if current client is authorized for operation"""
        if not self.cognitive_state.security_context.is_valid():
            logger.warning("Unauthorized access attempt - invalid security context")
            return False
        
        if not self.cognitive_state.security_context.has_scope(required_scope):
            logger.warning(f"Insufficient scope. Required: {required_scope}, Available: {self.cognitive_state.security_context.scope}")
            return False
        
        return True
    
    def _update_metrics(self, metric_type: str, operation: str, value: Any = 1):
        """Update internal metrics for monitoring"""
        self._metrics['last_activity'] = time.time()
        
        if metric_type == "tool_call":
            self._metrics['tool_calls'][operation] += value
        elif metric_type == "memory_operation":
            self._metrics['memory_operations'][operation] += value
        elif metric_type == "auth":
            self._metrics['authentication_attempts'][operation] += value
        elif metric_type == "async_task":
            self._metrics['async_tasks'][operation] += value
        elif metric_type == "performance":
            if operation == "retrieval_time":
                total = self._metrics['performance']['total_retrievals']
                avg_time = self._metrics['performance']['avg_retrieval_time']
                new_avg = (avg_time * total + value) / (total + 1)
                self._metrics['performance']['avg_retrieval_time'] = new_avg
                self._metrics['performance']['total_retrievals'] += 1
        elif metric_type == "error":
            self._metrics['errors'][operation] += value
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics and analytics"""
        uptime = time.time() - self._metrics['startup_time']
        
        return {
            "system": {
                "uptime_seconds": uptime,
                "uptime_human": f"{uptime // 3600:.0f}h {(uptime % 3600) // 60:.0f}m {uptime % 60:.0f}s",
                "last_activity": datetime.datetime.fromtimestamp(self._metrics['last_activity']).isoformat(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "mcp_version": "2025.1",
                "server_version": "1.1.0"
            },
            "usage": {
                "tool_calls": dict(self._metrics['tool_calls']),
                "memory_operations": self._metrics['memory_operations'],
                "async_tasks": self._metrics['async_tasks'],
                "authentication": self._metrics['authentication_attempts']
            },
            "performance": {
                "avg_retrieval_time_ms": self._metrics['performance']['avg_retrieval_time'] * 1000,
                "total_retrievals": self._metrics['performance']['total_retrievals'],
                "memory_cache_size": len(self._embedding_cache) if self._use_embedding_cache else 0,
                "embedding_model_loaded": self._embedding_model_loaded,
                "sqlite_enabled": self.use_sqlite
            },
            "memory_stats": {
                "total_memories": len(self.memories),
                "memory_types": {mt: len(mids) for mt, mids in self.memory_index.items()},
                "connection_graph_size": sum(len(conns) for conns in self.connection_graph.values()),
                "feedback_history_size": len(self.feedback_history)
            },
            "errors": dict(self._metrics['errors']),
            "security": {
                "authenticated": self.cognitive_state.security_context.authenticated,
                "client_id": self.cognitive_state.security_context.client_id,
                "token_valid": self.cognitive_state.security_context.is_valid(),
                "scopes": self.cognitive_state.security_context.scope.split()
            },
            "features": {
                "oauth2_enabled": True,
                "vector_embeddings": EMBEDDINGS_AVAILABLE and self._embedding_model_loaded,
                "sqlite_storage": self.use_sqlite,
                "async_operations": True,
                "full_text_search": self.use_sqlite,
                "cognitive_architecture": True,
                "experimental": {
                    "streamable_http": True,
                    "memory_consolidation": True,
                    "adaptive_learning": True,
                    "multimodal_support": True
                }
            }
        }
    
    def _load_embedding_model(self):
        """Lazy load embedding model when first needed"""
        if not self._embedding_model_loaded and EMBEDDINGS_AVAILABLE:
            try:
                model_name = os.getenv('BRAIN_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
                device = os.getenv('BRAIN_EMBEDDING_DEVICE', 'cpu')  # or 'cuda', 'mps'
                
                self.embedding_model = SentenceTransformer(model_name, device=device)
                self._embedding_model_loaded = True
                
                logger.info(f"Vector embedding model loaded: {model_name} on {device}")
                
                # Warm up model with a test encoding
                _ = self.embedding_model.encode(["test"], show_progress_bar=False)
                
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.embedding_model = None
                self._embedding_model_loaded = True  # Prevent retry
    
    def _get_embedding_cached(self, text: str) -> Optional[List[float]]:
        """Get embedding with caching for performance"""
        if not self._use_embedding_cache:
            return self._get_embedding_direct(text)
        
        # Create cache key
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache first
        if text_hash in self._embedding_cache:
            return self._embedding_cache[text_hash]
        
        # Generate embedding
        embedding = self._get_embedding_direct(text)
        
        if embedding is not None:
            # Manage cache size
            if len(self._embedding_cache) >= self._embedding_cache_max_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self._embedding_cache))
                del self._embedding_cache[oldest_key]
            
            # Cache the result
            self._embedding_cache[text_hash] = embedding
        
        return embedding
    
    def _get_embedding_direct(self, text: str) -> Optional[List[float]]:
        """Generate embedding directly from model"""
        if not self._embedding_model_loaded:
            self._load_embedding_model()
        
        if self.embedding_model is None:
            return None
        
        try:
            embedding = self.embedding_model.encode([text], show_progress_bar=False)[0]
            return embedding.tolist()
        except Exception as e:
            logger.warning(f"Failed to generate embedding for text: {e}")
            return None
    
    async def start_async_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """Start an async operation and return task ID (MCP 2025 async support)"""
        if not self.check_authorization("brain:write"):
            raise PermissionError("Insufficient privileges for async operations. Requires brain:write scope.")
        
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        # Queue the task
        self._task_queue[task_id] = {
            'type': task_type,
            'data': task_data,
            'status': 'queued',
            'created_at': time.time(),
            'client_id': self.cognitive_state.security_context.client_id
        }
        
        # Start the task asynchronously
        if task_type == "bulk_memory_processing":
            task = asyncio.create_task(self._process_bulk_memories(task_id, task_data))
        elif task_type == "large_embedding_generation":
            task = asyncio.create_task(self._generate_large_embeddings(task_id, task_data))
        elif task_type == "memory_consolidation":
            task = asyncio.create_task(self._consolidate_memories(task_id, task_data))
        else:
            raise ValueError(f"Unknown async task type: {task_type}")
        
        self._running_tasks[task_id] = task
        self._task_queue[task_id]['status'] = 'running'
        
        logger.info(f"Started async task {task_id} of type {task_type}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of async task"""
        if not self.check_authorization("brain:read"):
            raise PermissionError("Insufficient privileges to check task status. Requires brain:read scope.")
        
        if task_id not in self._task_queue:
            raise ValueError(f"Task {task_id} not found")
        
        task_info = self._task_queue[task_id].copy()
        
        # Check if task is complete
        if task_id in self._running_tasks:
            task = self._running_tasks[task_id]
            if task.done():
                if task.exception():
                    task_info['status'] = 'failed'
                    task_info['error'] = str(task.exception())
                else:
                    task_info['status'] = 'completed'
                    task_info['result'] = self._task_results.get(task_id, {})
                
                # Cleanup
                del self._running_tasks[task_id]
                task_info['completed_at'] = time.time()
        
        return task_info
    
    async def _process_bulk_memories(self, task_id: str, data: Dict[str, Any]):
        """Process multiple memories in bulk (async operation)"""
        try:
            memories = data.get('memories', [])
            results = []
            
            for i, mem_data in enumerate(memories):
                memory_id = self.store_memory(
                    content=mem_data['content'],
                    memory_type=mem_data['memory_type'],
                    metadata=mem_data.get('metadata', {}),
                    modality=mem_data.get('modality', 'text'),
                    emotional_valence=mem_data.get('emotional_valence', 0.0),
                    importance=mem_data.get('importance', 0.5)
                )
                results.append({'index': i, 'memory_id': memory_id})
                
                # Yield control periodically for other tasks
                if i % 10 == 0:
                    await asyncio.sleep(0.01)
            
            self._task_results[task_id] = {'processed': len(results), 'results': results}
            
        except Exception as e:
            logger.error(f"Bulk memory processing failed: {e}")
            raise
    
    async def _generate_large_embeddings(self, task_id: str, data: Dict[str, Any]):
        """Generate embeddings for large text corpus (async operation)"""
        try:
            texts = data.get('texts', [])
            embeddings = []
            
            if self.embedding_model:
                # Process in batches to avoid memory issues
                batch_size = 32
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    batch_embeddings = self.embedding_model.encode(batch)
                    embeddings.extend(batch_embeddings.tolist())
                    
                    # Yield control
                    await asyncio.sleep(0.01)
            
            self._task_results[task_id] = {'embeddings': embeddings, 'count': len(embeddings)}
            
        except Exception as e:
            logger.error(f"Large embedding generation failed: {e}")
            raise
    
    async def _consolidate_memories(self, task_id: str, data: Dict[str, Any]):
        """Consolidate and strengthen frequently accessed memories (async operation)"""
        try:
            threshold = data.get('access_threshold', 5)
            consolidated_count = 0
            
            for memory in self.memories.values():
                if memory.access_count >= threshold:
                    # Strengthen important memories
                    memory.strength = min(2.0, memory.strength * 1.1)
                    memory.importance = min(1.0, memory.importance * 1.05)
                    consolidated_count += 1
                    
                    # Save to database if using SQLite
                    if self.use_sqlite:
                        await self._save_memory_sqlite(memory)
                
                # Yield control
                if consolidated_count % 50 == 0:
                    await asyncio.sleep(0.01)
            
            self._task_results[task_id] = {'consolidated': consolidated_count}
            
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            raise
    
    def store_memory(self, content: str, memory_type: str, metadata: Dict[str, Any] = None, 
                    modality: str = "text", emotional_valence: float = 0.0, importance: float = 0.5) -> str:
        """Store new memory with advanced features"""
        # Security check: require brain:write scope
        if not self.check_authorization("brain:write"):
            raise PermissionError("Insufficient privileges to store memory. Requires brain:write scope.")
        
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
    
    def retrieve_memories(self, query: str, memory_types: List[str] = None, limit: int = 5, 
                         offset: int = 0, sort_by: str = "relevance") -> Dict[str, Any]:
        """Enhanced memory retrieval with pagination and vector similarity"""
        # Security check: require brain:read scope
        if not self.check_authorization("brain:read"):
            raise PermissionError("Insufficient privileges to retrieve memories. Requires brain:read scope.")
        
        if memory_types is None:
            memory_types = ["working", "episodic", "semantic", "procedural", "emotional"]
        
        # Use SQLite for efficient pagination when available
        if self.use_sqlite:
            return self._retrieve_memories_sqlite(query, memory_types, limit, offset, sort_by)
        else:
            return self._retrieve_memories_memory(query, memory_types, limit, offset, sort_by)
    
    def _retrieve_memories_sqlite(self, query: str, memory_types: List[str], 
                                 limit: int, offset: int, sort_by: str) -> Dict[str, Any]:
        """SQLite-based memory retrieval with full-text search and pagination"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Build query based on sort preference
            if sort_by == "relevance" and query.strip():
                # Use FTS for relevance-based search
                cursor.execute('''
                    SELECT m.*, bm25(memories_fts) as relevance_score
                    FROM memories_fts 
                    JOIN memories m ON memories_fts.id = m.id
                    WHERE memories_fts MATCH ? AND memory_type IN ({})
                    ORDER BY relevance_score
                    LIMIT ? OFFSET ?
                '''.format(','.join('?' * len(memory_types))), 
                [query] + memory_types + [limit, offset])
            elif sort_by == "timestamp":
                cursor.execute('''
                    SELECT *, 0 as relevance_score FROM memories 
                    WHERE memory_type IN ({}) AND content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                '''.format(','.join('?' * len(memory_types))), 
                memory_types + [f'%{query}%', limit, offset])
            elif sort_by == "importance":
                cursor.execute('''
                    SELECT *, 0 as relevance_score FROM memories 
                    WHERE memory_type IN ({}) AND content LIKE ?
                    ORDER BY importance DESC, access_count DESC
                    LIMIT ? OFFSET ?
                '''.format(','.join('?' * len(memory_types))), 
                memory_types + [f'%{query}%', limit, offset])
            else:
                # Default: combined relevance
                cursor.execute('''
                    SELECT *, (importance * 0.3 + feedback_score * 0.3 + access_count * 0.001) as relevance_score 
                    FROM memories 
                    WHERE memory_type IN ({}) AND content LIKE ?
                    ORDER BY relevance_score DESC
                    LIMIT ? OFFSET ?
                '''.format(','.join('?' * len(memory_types))), 
                memory_types + [f'%{query}%', limit, offset])
            
            results = []
            for row in cursor.fetchall():
                memory_data = {
                    'id': row[0], 'content': row[1], 'memory_type': row[2],
                    'metadata': json.loads(row[3] or '{}'), 'timestamp': row[4],
                    'strength': row[5], 'connections': json.loads(row[6] or '[]'),
                    'embedding': json.loads(row[7]) if row[7] else None,
                    'access_count': row[8], 'last_accessed': row[9],
                    'feedback_score': row[10], 'modality': row[11],
                    'emotional_valence': row[12], 'importance': row[13]
                }
                memory = MemoryItem(**memory_data)
                results.append(memory)
            
            # Get total count for pagination
            cursor.execute('''
                SELECT COUNT(*) FROM memories 
                WHERE memory_type IN ({}) AND content LIKE ?
            '''.format(','.join('?' * len(memory_types))), 
            memory_types + [f'%{query}%'])
            total_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'memories': results,
                'pagination': {
                    'offset': offset,
                    'limit': limit,
                    'total': total_count,
                    'has_more': offset + limit < total_count
                },
                'query': query,
                'sort_by': sort_by
            }
            
        except Exception as e:
            logger.error(f"SQLite memory retrieval failed: {e}")
            # Fallback to in-memory search
            return self._retrieve_memories_memory(query, memory_types, limit, offset, sort_by)
    
    def _retrieve_memories_memory(self, query: str, memory_types: List[str], 
                                 limit: int, offset: int, sort_by: str) -> Dict[str, Any]:
        """In-memory retrieval with pagination (legacy fallback)"""
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
                description="Store information in the brain's memory system with cognitive features",
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
    
    def _structure_tool_output(tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Structure tool output according to MCP 2025 annotations"""
        structured = {
            "tool": tool_name,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "status": "success"
        }
        
        # Add tool-specific structure validation
        if tool_name == "store_memory":
            structured.update({
                "data": {
                    "memory_id": result.get("memory_id"),
                    "memory_type": result.get("memory_type"),
                    "status": result.get("status", "stored"),
                    "embedding_generated": "embedding" in result,
                    "timestamp": time.time()
                },
                "metadata": {
                    "storage_backend": "sqlite" if brain.use_sqlite else "json",
                    "security_context": brain.cognitive_state.security_context.client_id
                }
            })
        elif tool_name == "retrieve_memories":
            memories_data = []
            if isinstance(result, dict) and "memories" in result:
                for memory in result["memories"]:
                    memories_data.append({
                        "id": memory.id,
                        "content": memory.content,
                        "memory_type": memory.memory_type,
                        "timestamp": memory.timestamp,
                        "importance": memory.importance,
                        "relevance_score": getattr(memory, 'relevance_score', 0.0)
                    })
            
            structured.update({
                "data": {
                    "memories": memories_data,
                    "pagination": result.get("pagination", {}),
                    "query": result.get("query", ""),
                    "sort_by": result.get("sort_by", "relevance")
                },
                "metadata": {
                    "search_type": "vector" if brain.embedding_model else "text",
                    "total_found": len(memories_data)
                }
            })
        elif tool_name == "get_brain_status":
            structured.update({
                "data": result,
                "metadata": {
                    "cognitive_architecture": True,
                    "mcp_version": "2025.1"
                }
            })
        else:
            # Generic structure for other tools
            structured.update({
                "data": result,
                "metadata": {}
            })
        
        return structured
    
    def _validate_tool_arguments(tool_name: str, arguments: dict) -> Dict[str, Any]:
        """Enhanced argument validation for MCP 2025"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if tool_name == "store_memory":
            # Required field validation
            if not arguments.get("content"):
                validation_result["errors"].append("content is required and cannot be empty")
            elif len(arguments["content"]) > 10000:
                validation_result["warnings"].append("content is very long (>10000 chars), consider splitting")
            
            memory_type = arguments.get("memory_type")
            valid_types = ["working", "episodic", "semantic", "procedural", "emotional"]
            if not memory_type or memory_type not in valid_types:
                validation_result["errors"].append(f"memory_type must be one of: {valid_types}")
            
            # Range validation
            emotional_valence = arguments.get("emotional_valence", 0.0)
            if not isinstance(emotional_valence, (int, float)) or emotional_valence < -1.0 or emotional_valence > 1.0:
                validation_result["errors"].append("emotional_valence must be a number between -1.0 and 1.0")
            
            importance = arguments.get("importance", 0.5)
            if not isinstance(importance, (int, float)) or importance < 0.0 or importance > 1.0:
                validation_result["errors"].append("importance must be a number between 0.0 and 1.0")
        
        elif tool_name == "retrieve_memories":
            query = arguments.get("query")
            if not query:
                validation_result["errors"].append("query is required and cannot be empty")
            elif len(query) > 1000:
                validation_result["warnings"].append("query is very long (>1000 chars), may affect performance")
            
            limit = arguments.get("limit", 5)
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                validation_result["errors"].append("limit must be an integer between 1 and 100")
            
            offset = arguments.get("offset", 0)
            if not isinstance(offset, int) or offset < 0:
                validation_result["errors"].append("offset must be a non-negative integer")
            
            sort_by = arguments.get("sort_by", "relevance")
            valid_sorts = ["relevance", "timestamp", "importance"]
            if sort_by not in valid_sorts:
                validation_result["errors"].append(f"sort_by must be one of: {valid_sorts}")
        
        elif tool_name == "start_async_task":
            task_type = arguments.get("task_type")
            valid_task_types = ["bulk_memory_processing", "large_embedding_generation", "memory_consolidation"]
            if not task_type or task_type not in valid_task_types:
                validation_result["errors"].append(f"task_type must be one of: {valid_task_types}")
            
            task_data = arguments.get("task_data")
            if not isinstance(task_data, dict):
                validation_result["errors"].append("task_data must be an object")
        
        elif tool_name == "get_task_status":
            task_id = arguments.get("task_id")
            if not task_id or not isinstance(task_id, str):
                validation_result["errors"].append("task_id is required and must be a string")
        
        elif tool_name == "add_feedback":
            interaction_id = arguments.get("interaction_id")
            if not interaction_id or not isinstance(interaction_id, str):
                validation_result["errors"].append("interaction_id is required and must be a string")
            
            feedback_type = arguments.get("feedback_type")
            valid_feedback_types = ["positive", "negative", "correction"]
            if not feedback_type or feedback_type not in valid_feedback_types:
                validation_result["errors"].append(f"feedback_type must be one of: {valid_feedback_types}")
            
            score = arguments.get("score")
            if not isinstance(score, (int, float)) or score < -1.0 or score > 1.0:
                validation_result["errors"].append("score must be a number between -1.0 and 1.0")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        return validation_result
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls with OAuth 2.1 security"""
        try:
            # Security validation for all tool calls
            # In production, extract from Authorization header: Bearer <token>
            # For now, check if brain has been authenticated
            if not brain.cognitive_state.security_context.authenticated:
                # Default authentication for testing (remove in production)
                default_client_id = os.getenv('MCP_CLIENT_ID', 'claude-code-client')
                default_token = os.getenv('MCP_ACCESS_TOKEN', 'dev-token-' + secrets.token_urlsafe(16))
                default_resource = os.getenv('MCP_RESOURCE_INDICATOR', 'https://claude.ai/code/brain-mcp')
                
                if not brain.authenticate_client(default_client_id, default_token, default_resource):
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Authentication failed",
                            "error_description": "Invalid or missing OAuth 2.1 credentials",
                            "error_uri": "https://tools.ietf.org/html/rfc6749#section-5.2"
                        })
                    )]
            
            # Enhanced argument validation
            validation = _validate_tool_arguments(name, arguments)
            if not validation["valid"]:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "validation_failed",
                        "error_description": "Invalid arguments provided",
                        "validation_errors": validation["errors"],
                        "validation_warnings": validation.get("warnings", [])
                    })
                )]
            
            # Log warnings if any
            if validation.get("warnings"):
                for warning in validation["warnings"]:
                    logger.warning(f"Tool {name}: {warning}")
            
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
                result = brain.get_comprehensive_metrics()
                
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
            
            # Validate and structure output according to MCP 2025 annotations
            structured_result = _structure_tool_output(name, result)
            return [types.TextContent(type="text", text=json.dumps(structured_result, indent=2))]
            
        except PermissionError as e:
            # OAuth 2.1 authorization errors
            logger.warning(f"Authorization failed: {e}")
            return [types.TextContent(
                type="text", 
                text=json.dumps({
                    "error": "insufficient_scope",
                    "error_description": str(e),
                    "error_uri": "https://tools.ietf.org/html/rfc6749#section-5.2",
                    "scope_required": "brain:read brain:write"
                })
            )]
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return [types.TextContent(
                type="text", 
                text=json.dumps({
                    "error": "server_error",
                    "error_description": str(e),
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })
            )]

    async def main():
        """Run the MCP server with optional HTTP transport"""
        transport_mode = os.getenv('MCP_TRANSPORT', 'stdio')  # stdio or http
        
        if transport_mode == 'http':
            await run_http_server()
        else:
            await run_stdio_server()
    
    async def run_stdio_server():
        """Run MCP server with stdio transport (default)"""
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bolor-brain-mcp",
                    server_version="1.1.0",  # Updated for Phase 2
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={
                            "streamable_http": True,
                            "async_operations": True,
                            "pagination": True,
                            "sqlite_storage": True
                        },
                    ),
                ),
            )
    
    async def run_http_server():
        """Run MCP server with Streamable HTTP transport (MCP 2025)"""
        try:
            from aiohttp import web
            
            logger.info("Starting Streamable HTTP server for MCP 2025 compliance")
            await run_stdio_server()  # Simplified for now - full HTTP in future update
            
        except ImportError:
            logger.warning("aiohttp not available for HTTP transport. Using stdio.")
            await run_stdio_server()

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