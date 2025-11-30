"""
Brain Memory System Module
Core memory operations and storage management
"""
import sqlite3
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import uuid
import time
import json
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class MemoryItem:
    """A single memory item with cognitive metadata"""
    memory_id: str
    content: str
    memory_type: str  # working, episodic, semantic, procedural, emotional
    timestamp: float
    importance: float = 0.5
    emotional_valence: float = 0.0
    retrieval_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    modality: str = "text"  # text, image, audio, structured

class MemoryManager:
    """Manages all memory operations for the brain"""
    
    def __init__(self, storage_path: Path, use_sqlite: bool = True):
        self.storage_path = storage_path
        self.use_sqlite = use_sqlite
        self.db_path = storage_path / "memories.db"
        self.memories: Dict[str, MemoryItem] = {}
        
        if use_sqlite:
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create memories table with FTS5 for full-text search
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                importance REAL DEFAULT 0.5,
                emotional_valence REAL DEFAULT 0.0,
                retrieval_count INTEGER DEFAULT 0,
                last_accessed REAL DEFAULT 0,
                metadata TEXT DEFAULT '{}',
                modality TEXT DEFAULT 'text'
            )
            """)
            
            # Create FTS5 virtual table for content search
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts 
            USING fts5(memory_id, content, memory_type, modality)
            """)
            
            conn.commit()
            conn.close()
            logger.info("Memory database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory database: {e}")
    
    def store_memory(self, content: str, memory_type: str, 
                    importance: float = 0.5, emotional_valence: float = 0.0,
                    metadata: Dict[str, Any] = None, modality: str = "text") -> str:
        """Store a new memory"""
        memory_id = str(uuid.uuid4())
        memory = MemoryItem(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=time.time(),
            importance=importance,
            emotional_valence=emotional_valence,
            metadata=metadata or {},
            modality=modality
        )
        
        self.memories[memory_id] = memory
        
        if self.use_sqlite:
            self._store_to_sqlite(memory)
        
        return memory_id
    
    def _store_to_sqlite(self, memory: MemoryItem):
        """Store memory to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store in main table
            cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (memory_id, content, memory_type, timestamp, importance, 
             emotional_valence, retrieval_count, last_accessed, metadata, modality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.memory_id, memory.content, memory.memory_type,
                memory.timestamp, memory.importance, memory.emotional_valence,
                memory.retrieval_count, memory.last_accessed,
                json.dumps(memory.metadata), memory.modality
            ))
            
            # Store in FTS table for search
            cursor.execute("""
            INSERT OR REPLACE INTO memories_fts
            (memory_id, content, memory_type, modality)
            VALUES (?, ?, ?, ?)
            """, (memory.memory_id, memory.content, memory.memory_type, memory.modality))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store memory to SQLite: {e}")
    
    def retrieve_memories(self, query: str = "", memory_type: str = "", 
                         limit: int = 10, min_importance: float = 0.0) -> List[MemoryItem]:
        """Retrieve memories based on query and filters"""
        if self.use_sqlite:
            return self._retrieve_from_sqlite(query, memory_type, limit, min_importance)
        else:
            return self._retrieve_from_memory(query, memory_type, limit, min_importance)
    
    def _retrieve_from_sqlite(self, query: str, memory_type: str, 
                             limit: int, min_importance: float) -> List[MemoryItem]:
        """Retrieve memories from SQLite with FTS5 search"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if query:
                # Use FTS5 for content search
                sql = """
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.memory_id = fts.memory_id
                WHERE fts MATCH ?
                AND m.importance >= ?
                """
                params = [query, min_importance]
                
                if memory_type:
                    sql += " AND m.memory_type = ?"
                    params.append(memory_type)
                
                sql += " ORDER BY m.importance DESC, m.timestamp DESC LIMIT ?"
                params.append(limit)
            else:
                # Simple filter query
                sql = "SELECT * FROM memories WHERE importance >= ?"
                params = [min_importance]
                
                if memory_type:
                    sql += " AND memory_type = ?"
                    params.append(memory_type)
                
                sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
                params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memory = MemoryItem(
                    memory_id=row[0], content=row[1], memory_type=row[2],
                    timestamp=row[3], importance=row[4], emotional_valence=row[5],
                    retrieval_count=row[6], last_accessed=row[7],
                    metadata=json.loads(row[8]), modality=row[9]
                )
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories from SQLite: {e}")
            return []
    
    def _retrieve_from_memory(self, query: str, memory_type: str, 
                             limit: int, min_importance: float) -> List[MemoryItem]:
        """Retrieve memories from in-memory storage"""
        filtered_memories = []
        
        for memory in self.memories.values():
            if memory.importance < min_importance:
                continue
            if memory_type and memory.memory_type != memory_type:
                continue
            if query and query.lower() not in memory.content.lower():
                continue
            
            filtered_memories.append(memory)
        
        # Sort by importance and timestamp
        filtered_memories.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        return filtered_memories[:limit]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM memories")
                total_memories = cursor.fetchone()[0]
                
                cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
                type_counts = dict(cursor.fetchall())
                
                cursor.execute("SELECT AVG(importance) FROM memories")
                avg_importance = cursor.fetchone()[0] or 0.0
                
                conn.close()
                
                return {
                    "total_memories": total_memories,
                    "type_breakdown": type_counts,
                    "average_importance": avg_importance,
                    "storage_type": "sqlite"
                }
            except Exception as e:
                logger.error(f"Failed to get SQLite memory stats: {e}")
        
        # Fallback to in-memory stats
        type_counts = {}
        total_importance = 0
        
        for memory in self.memories.values():
            type_counts[memory.memory_type] = type_counts.get(memory.memory_type, 0) + 1
            total_importance += memory.importance
        
        return {
            "total_memories": len(self.memories),
            "type_breakdown": type_counts,
            "average_importance": total_importance / len(self.memories) if self.memories else 0.0,
            "storage_type": "memory"
        }