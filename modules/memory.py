"""
Bolor Brain Differentiated Memory System
=========================================
5 distinct memory subsystems with appropriate data representations:
1. Working Memory - Transient, in-context only
2. Episodic Memory - Experiences with reward/emotion signals
3. Semantic Memory - Knowledge graph with inference
4. Procedural Memory - Executable skills
5. Meta/Self Memory - Structured identity model

Plus: Plasticity + Decay mechanisms
"""

import sqlite3
import logging
import subprocess
import tempfile
import threading
import json
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import deque
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# =============================================================================
# BACKWARD COMPATIBILITY - Legacy MemoryItem
# =============================================================================

@dataclass
class MemoryItem:
    """
    Legacy MemoryItem for backward compatibility with existing code.
    New code should use the specific memory types (EpisodicMemory, SemanticNode, etc.)
    """
    id: str
    content: str
    memory_type: str  # working, episodic, semantic, procedural, emotional
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    strength: float = 1.0
    connections: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    feedback_score: float = 0.0
    modality: str = "text"
    emotional_valence: float = 0.0
    importance: float = 0.5


# =============================================================================
# WORKING MEMORY (Transient - Never Persisted)
# =============================================================================

@dataclass
class WorkingMemoryItem:
    """A single item in working memory with activation decay"""
    id: str
    content: Any
    created_at: float
    expires_at: float
    activation_level: float = 1.0  # 0-1, decays over time
    tags: List[str] = field(default_factory=list)


class WorkingMemory:
    """
    Transient working memory buffer following Miller's Law (7±2 items).
    NEVER persisted to disk - purely in-memory with automatic expiration.
    """

    MAX_ITEMS = 9  # 7+2 (Miller's Law upper bound)
    DEFAULT_TTL = 300  # 5 minutes default
    ACTIVATION_DECAY_RATE = 0.1  # Per minute

    def __init__(self, max_items: int = MAX_ITEMS, default_ttl: int = DEFAULT_TTL):
        self.max_items = max_items
        self.default_ttl = default_ttl
        self._items: Dict[str, WorkingMemoryItem] = {}
        self._attention_focus: List[str] = []  # Ordered list of focused item IDs
        self._lock = threading.Lock()

    def add(self, content: Any, ttl: Optional[int] = None, tags: List[str] = None) -> str:
        """Add item to working memory, evicting oldest if at capacity"""
        with self._lock:
            # Clean expired items first
            self._cleanup_expired()

            # Evict oldest if at capacity
            while len(self._items) >= self.max_items:
                self._evict_oldest()

            item_id = str(uuid.uuid4())[:8]
            now = time.time()
            item = WorkingMemoryItem(
                id=item_id,
                content=content,
                created_at=now,
                expires_at=now + (ttl or self.default_ttl),
                activation_level=1.0,
                tags=tags or []
            )
            self._items[item_id] = item
            self._attention_focus.insert(0, item_id)  # Most recent at front

            return item_id

    def get(self, item_id: str) -> Optional[Any]:
        """Get item and boost its activation"""
        with self._lock:
            self._cleanup_expired()
            item = self._items.get(item_id)
            if item:
                item.activation_level = min(1.0, item.activation_level + 0.2)
                # Move to front of attention
                if item_id in self._attention_focus:
                    self._attention_focus.remove(item_id)
                self._attention_focus.insert(0, item_id)
                return item.content
            return None

    def get_all_active(self) -> List[Dict[str, Any]]:
        """Get all active items with their metadata"""
        with self._lock:
            self._cleanup_expired()
            self._decay_activations()
            return [
                {
                    "id": item.id,
                    "content": item.content,
                    "activation": item.activation_level,
                    "tags": item.tags,
                    "ttl_remaining": item.expires_at - time.time()
                }
                for item in self._items.values()
            ]

    def focus_on(self, item_id: str) -> bool:
        """Bring item to attention focus"""
        with self._lock:
            if item_id in self._items:
                self._items[item_id].activation_level = 1.0
                if item_id in self._attention_focus:
                    self._attention_focus.remove(item_id)
                self._attention_focus.insert(0, item_id)
                return True
            return False

    def get_attention_focus(self) -> List[str]:
        """Get current attention focus order"""
        with self._lock:
            self._cleanup_expired()
            return self._attention_focus.copy()

    def remove(self, item_id: str) -> bool:
        """Explicitly remove an item"""
        with self._lock:
            if item_id in self._items:
                del self._items[item_id]
                if item_id in self._attention_focus:
                    self._attention_focus.remove(item_id)
                return True
            return False

    def clear(self):
        """Clear all working memory"""
        with self._lock:
            self._items.clear()
            self._attention_focus.clear()

    def _cleanup_expired(self):
        """Remove expired items"""
        now = time.time()
        expired = [k for k, v in self._items.items() if v.expires_at <= now]
        for item_id in expired:
            del self._items[item_id]
            if item_id in self._attention_focus:
                self._attention_focus.remove(item_id)

    def _evict_oldest(self):
        """Evict the item with lowest activation (oldest/least used)"""
        if not self._items:
            return
        # Find item with lowest activation
        oldest_id = min(self._items.keys(),
                       key=lambda k: self._items[k].activation_level)
        del self._items[oldest_id]
        if oldest_id in self._attention_focus:
            self._attention_focus.remove(oldest_id)

    def _decay_activations(self):
        """Decay activation levels over time"""
        now = time.time()
        for item in self._items.values():
            minutes_since_creation = (now - item.created_at) / 60
            decay = self.ACTIVATION_DECAY_RATE * minutes_since_creation
            item.activation_level = max(0.1, item.activation_level - decay)


# =============================================================================
# EPISODIC MEMORY (Experiences)
# =============================================================================

@dataclass
class EpisodicMemory:
    """A single episode/experience with full context"""
    id: str
    timestamp: float
    situation: str  # What was the context/situation
    action: str  # What action was taken
    outcome: str  # What was the result
    reward: float = 0.0  # -1 to 1 (success/failure signal)
    emotional_valence: float = 0.0  # -1 to 1 (negative to positive)
    emotional_intensity: float = 0.0  # 0 to 1 (calm to intense)
    context_embedding: Optional[List[float]] = None
    linked_episodes: List[str] = field(default_factory=list)
    retrieval_count: int = 0
    last_retrieved: Optional[float] = None
    strength: float = 1.0  # Consolidation strength
    drive_satisfied: Optional[str] = None  # Which drive this satisfied
    is_foundation: bool = False  # Protected from decay
    metadata: Dict[str, Any] = field(default_factory=dict)


class EpisodicMemoryStore:
    """
    Store for episodic memories (experiences).
    Supports temporal queries, reward-based retrieval, and emotional filtering.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._experience_count = 0
        self._init_table()
        self._load_experience_count()

    def _init_table(self):
        """Initialize episodic memories table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodic_memories (
            id TEXT PRIMARY KEY,
            timestamp REAL NOT NULL,
            situation TEXT NOT NULL,
            action TEXT,
            outcome TEXT,
            reward REAL DEFAULT 0.0,
            emotional_valence REAL DEFAULT 0.0,
            emotional_intensity REAL DEFAULT 0.0,
            context_embedding BLOB,
            linked_episodes TEXT,
            retrieval_count INTEGER DEFAULT 0,
            last_retrieved REAL,
            strength REAL DEFAULT 1.0,
            drive_satisfied TEXT,
            is_foundation INTEGER DEFAULT 0,
            metadata TEXT DEFAULT '{}'
        )
        """)

        # Create FTS table for episodic content
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS episodic_fts
        USING fts5(id, situation, action, outcome)
        """)

        # Indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memories(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_reward ON episodic_memories(reward)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_strength ON episodic_memories(strength)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_episodic_drive ON episodic_memories(drive_satisfied)")

        conn.commit()
        conn.close()

    def _load_experience_count(self):
        """Load current experience count from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM episodic_memories")
        self._experience_count = cursor.fetchone()[0]
        conn.close()

    def store(self, situation: str, action: str = "", outcome: str = "",
              reward: float = 0.0, emotional_valence: float = 0.0,
              emotional_intensity: float = 0.0, drive_satisfied: str = None,
              metadata: Dict = None, embedding: List[float] = None) -> str:
        """Store a new episodic memory"""
        episode_id = str(uuid.uuid4())
        now = time.time()

        # First 100 memories are foundation memories
        is_foundation = self._experience_count < 100

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO episodic_memories
        (id, timestamp, situation, action, outcome, reward, emotional_valence,
         emotional_intensity, context_embedding, linked_episodes, strength,
         drive_satisfied, is_foundation, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            episode_id, now, situation, action, outcome, reward,
            emotional_valence, emotional_intensity,
            json.dumps(embedding) if embedding else None,
            json.dumps([]), 1.0, drive_satisfied,
            1 if is_foundation else 0,
            json.dumps(metadata or {})
        ))

        # Add to FTS
        cursor.execute("""
        INSERT INTO episodic_fts (id, situation, action, outcome)
        VALUES (?, ?, ?, ?)
        """, (episode_id, situation, action, outcome))

        conn.commit()
        conn.close()

        self._experience_count += 1

        return episode_id

    def _escape_fts5_query(self, query: str) -> str:
        """Escape FTS5 query to prevent syntax errors"""
        if not query.strip():
            return '""'
        # Remove FTS5 special characters that cause syntax errors
        special_chars = ['?', '*', '(', ')', '[', ']', '{', '}', '^', '~', '-', '+', ':']
        cleaned = query
        for char in special_chars:
            cleaned = cleaned.replace(char, ' ')
        # Escape quotes
        cleaned = cleaned.replace('"', '""').replace("'", "''")
        # Wrap in quotes to prevent syntax issues
        return f'"{cleaned.strip()}"'

    def retrieve(self, query: str = "", limit: int = 10,
                 min_reward: float = None, max_reward: float = None,
                 time_range: Tuple[float, float] = None,
                 drive: str = None, min_strength: float = 0.0) -> List[EpisodicMemory]:
        """Retrieve episodic memories with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        params = []
        where_clauses = ["strength >= ?"]
        params.append(min_strength)

        if min_reward is not None:
            where_clauses.append("reward >= ?")
            params.append(min_reward)

        if max_reward is not None:
            where_clauses.append("reward <= ?")
            params.append(max_reward)

        if time_range:
            where_clauses.append("timestamp BETWEEN ? AND ?")
            params.extend(time_range)

        if drive:
            where_clauses.append("drive_satisfied = ?")
            params.append(drive)

        if query:
            # Use FTS for search - get matching IDs first
            escaped_query = self._escape_fts5_query(query)
            cursor.execute("""
            SELECT id FROM episodic_fts WHERE episodic_fts MATCH ?
            """, (escaped_query,))
            matching_ids = [row[0] for row in cursor.fetchall()]

            if matching_ids:
                placeholders = ','.join(['?' for _ in matching_ids])
                cursor.execute(f"""
                SELECT * FROM episodic_memories
                WHERE id IN ({placeholders}) AND {' AND '.join(where_clauses)}
                ORDER BY strength DESC, timestamp DESC
                LIMIT ?
                """, matching_ids + params + [limit])
            else:
                # No FTS matches, fall back to LIKE search
                where_clauses.append("(situation LIKE ? OR action LIKE ? OR outcome LIKE ?)")
                like_query = f"%{query}%"
                params.extend([like_query, like_query, like_query])
                cursor.execute(f"""
                SELECT * FROM episodic_memories
                WHERE {' AND '.join(where_clauses)}
                ORDER BY strength DESC, timestamp DESC
                LIMIT ?
                """, params + [limit])
        else:
            cursor.execute(f"""
            SELECT * FROM episodic_memories
            WHERE {' AND '.join(where_clauses)}
            ORDER BY strength DESC, timestamp DESC
            LIMIT ?
            """, params + [limit])

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_episode(row) for row in rows]

    def retrieve_by_emotion(self, valence_range: Tuple[float, float],
                           intensity_min: float = 0.0, limit: int = 10) -> List[EpisodicMemory]:
        """Retrieve memories by emotional characteristics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM episodic_memories
        WHERE emotional_valence BETWEEN ? AND ?
        AND emotional_intensity >= ?
        ORDER BY emotional_intensity DESC, timestamp DESC
        LIMIT ?
        """, (valence_range[0], valence_range[1], intensity_min, limit))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_episode(row) for row in rows]

    def retrieve_recent(self, hours: float = 24, limit: int = 20) -> List[EpisodicMemory]:
        """Retrieve recent episodes"""
        cutoff = time.time() - (hours * 3600)
        return self.retrieve(time_range=(cutoff, time.time()), limit=limit)

    def link_episodes(self, episode_id1: str, episode_id2: str):
        """Create bidirectional link between episodes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for source, target in [(episode_id1, episode_id2), (episode_id2, episode_id1)]:
            cursor.execute("SELECT linked_episodes FROM episodic_memories WHERE id = ?", (source,))
            row = cursor.fetchone()
            if row:
                links = json.loads(row[0] or "[]")
                if target not in links:
                    links.append(target)
                    cursor.execute("UPDATE episodic_memories SET linked_episodes = ? WHERE id = ?",
                                 (json.dumps(links), source))

        conn.commit()
        conn.close()

    def update_strength(self, episode_id: str, delta: float):
        """Update episode strength (for consolidation/decay)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE episodic_memories
        SET strength = MIN(2.0, MAX(0.05, strength + ?))
        WHERE id = ?
        """, (delta, episode_id))

        conn.commit()
        conn.close()

    def record_retrieval(self, episode_id: str):
        """Record that an episode was retrieved (for strength boost)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE episodic_memories
        SET retrieval_count = retrieval_count + 1,
            last_retrieved = ?,
            strength = MIN(2.0, strength + 0.1)
        WHERE id = ?
        """, (time.time(), episode_id))

        conn.commit()
        conn.close()

    def get_experience_count(self) -> int:
        """Get total number of experiences"""
        return self._experience_count

    def _row_to_episode(self, row) -> EpisodicMemory:
        """Convert database row to EpisodicMemory object"""
        return EpisodicMemory(
            id=row[0],
            timestamp=row[1],
            situation=row[2],
            action=row[3] or "",
            outcome=row[4] or "",
            reward=row[5],
            emotional_valence=row[6],
            emotional_intensity=row[7],
            context_embedding=json.loads(row[8]) if row[8] else None,
            linked_episodes=json.loads(row[9]) if row[9] else [],
            retrieval_count=row[10],
            last_retrieved=row[11],
            strength=row[12],
            drive_satisfied=row[13],
            is_foundation=bool(row[14]),
            metadata=json.loads(row[15]) if row[15] else {}
        )


# =============================================================================
# SEMANTIC MEMORY (Knowledge Graph with Inference)
# =============================================================================

@dataclass
class SemanticNode:
    """A node in the semantic knowledge graph"""
    id: str
    label: str  # Human-readable name
    node_type: str  # concept, entity, fact, definition, category
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    confidence: float = 0.5
    source_episodes: List[str] = field(default_factory=list)  # Grounding in experiences
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class SemanticEdge:
    """An edge/relationship in the semantic knowledge graph"""
    id: str
    source_id: str
    target_id: str
    relation_type: str  # is_a, has_property, causes, requires, part_of, etc.
    weight: float = 1.0
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)  # Episode IDs as evidence


# Inference rules for transitive relations and property inheritance
INFERENCE_RULES = {
    "is_a": {"transitive": True, "inherit_properties": True},
    "part_of": {"transitive": True, "inherit_properties": False},
    "causes": {"transitive": False, "inverse": "caused_by"},
    "requires": {"transitive": True, "inherit_properties": False},
    "has_property": {"transitive": False, "inherit_properties": False},
    "related_to": {"transitive": False, "symmetric": True},
}


class SemanticKnowledgeGraph:
    """
    Knowledge graph with entity-relationship storage and inference capabilities.
    Supports transitive relations and property inheritance.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._node_cache: Dict[str, SemanticNode] = {}
        self._init_tables()

    def _init_tables(self):
        """Initialize semantic memory tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Nodes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS semantic_nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            node_type TEXT NOT NULL,
            properties TEXT,
            embedding BLOB,
            confidence REAL DEFAULT 0.5,
            source_episodes TEXT,
            created_at REAL,
            updated_at REAL
        )
        """)

        # Edges table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS semantic_edges (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            confidence REAL DEFAULT 0.5,
            evidence TEXT,
            FOREIGN KEY (source_id) REFERENCES semantic_nodes(id),
            FOREIGN KEY (target_id) REFERENCES semantic_nodes(id)
        )
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_semantic_label ON semantic_nodes(label)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_semantic_type ON semantic_nodes(node_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON semantic_edges(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON semantic_edges(target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_relation ON semantic_edges(relation_type)")

        # FTS for node labels and properties
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS semantic_fts
        USING fts5(id, label, properties)
        """)

        conn.commit()
        conn.close()

    def add_node(self, label: str, node_type: str, properties: Dict = None,
                 confidence: float = 0.5, source_episodes: List[str] = None,
                 embedding: List[float] = None, auto_embed: bool = True) -> str:
        """
        Add a node to the knowledge graph with automatic embedding generation.

        Args:
            label: Node label/name
            node_type: Type of node (concept, entity, fact, definition)
            properties: Additional properties dict
            confidence: Confidence score 0-1
            source_episodes: List of episode IDs that support this node
            embedding: Pre-computed embedding (optional)
            auto_embed: If True, auto-generate embedding when not provided
        """
        # Check if node with same label exists
        existing = self.find_node_by_label(label)
        if existing:
            # Update existing node
            return self.update_node(existing.id, properties=properties,
                                   confidence=max(existing.confidence, confidence),
                                   source_episodes=source_episodes)

        node_id = str(uuid.uuid4())
        now = time.time()

        # Auto-generate embedding if not provided and auto_embed is True
        if embedding is None and auto_embed:
            try:
                from .embeddings import embedding_service
                # Create text representation for embedding
                props_text = " ".join(str(v) for v in (properties or {}).values())
                embed_text = f"{label} {node_type} {props_text}".strip()
                embedding = embedding_service.encode(embed_text)
            except Exception as e:
                logger.debug(f"Auto-embedding failed for node '{label}': {e}")
                embedding = None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO semantic_nodes
        (id, label, node_type, properties, embedding, confidence, source_episodes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            node_id, label, node_type,
            json.dumps(properties or {}),
            json.dumps(embedding) if embedding else None,
            confidence,
            json.dumps(source_episodes or []),
            now, now
        ))

        # Add to FTS
        cursor.execute("""
        INSERT INTO semantic_fts (id, label, properties)
        VALUES (?, ?, ?)
        """, (node_id, label, json.dumps(properties or {})))

        conn.commit()
        conn.close()

        return node_id

    def update_node(self, node_id: str, properties: Dict = None,
                   confidence: float = None, source_episodes: List[str] = None) -> str:
        """Update an existing node"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = ["updated_at = ?"]
        params = [time.time()]

        if properties is not None:
            # Merge properties
            cursor.execute("SELECT properties FROM semantic_nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            existing_props = json.loads(row[0]) if row and row[0] else {}
            existing_props.update(properties)
            updates.append("properties = ?")
            params.append(json.dumps(existing_props))

        if confidence is not None:
            updates.append("confidence = ?")
            params.append(confidence)

        if source_episodes is not None:
            cursor.execute("SELECT source_episodes FROM semantic_nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            existing = json.loads(row[0]) if row and row[0] else []
            existing.extend([e for e in source_episodes if e not in existing])
            updates.append("source_episodes = ?")
            params.append(json.dumps(existing))

        params.append(node_id)
        cursor.execute(f"UPDATE semantic_nodes SET {', '.join(updates)} WHERE id = ?", params)

        conn.commit()
        conn.close()

        return node_id

    def add_edge(self, source_id: str, target_id: str, relation_type: str,
                 weight: float = 1.0, confidence: float = 0.5,
                 evidence: List[str] = None) -> str:
        """Add an edge between nodes"""
        edge_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for existing edge
        cursor.execute("""
        SELECT id, weight, confidence, evidence FROM semantic_edges
        WHERE source_id = ? AND target_id = ? AND relation_type = ?
        """, (source_id, target_id, relation_type))

        existing = cursor.fetchone()
        if existing:
            # Update existing edge
            new_weight = (existing[1] + weight) / 2
            new_confidence = max(existing[2], confidence)
            existing_evidence = json.loads(existing[3]) if existing[3] else []
            if evidence:
                existing_evidence.extend([e for e in evidence if e not in existing_evidence])

            cursor.execute("""
            UPDATE semantic_edges
            SET weight = ?, confidence = ?, evidence = ?
            WHERE id = ?
            """, (new_weight, new_confidence, json.dumps(existing_evidence), existing[0]))

            conn.commit()
            conn.close()
            return existing[0]

        # Insert new edge
        cursor.execute("""
        INSERT INTO semantic_edges
        (id, source_id, target_id, relation_type, weight, confidence, evidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (edge_id, source_id, target_id, relation_type, weight, confidence,
              json.dumps(evidence or [])))

        # Handle symmetric relations
        rule = INFERENCE_RULES.get(relation_type, {})
        if rule.get("symmetric"):
            reverse_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT OR IGNORE INTO semantic_edges
            (id, source_id, target_id, relation_type, weight, confidence, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (reverse_id, target_id, source_id, relation_type, weight, confidence,
                  json.dumps(evidence or [])))

        conn.commit()
        conn.close()

        return edge_id

    def find_node_by_label(self, label: str) -> Optional[SemanticNode]:
        """Find a node by its label"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM semantic_nodes WHERE label = ?", (label,))
        row = cursor.fetchone()
        conn.close()

        return self._row_to_node(row) if row else None

    def _escape_fts5_query(self, query: str) -> str:
        """Escape FTS5 query to prevent syntax errors"""
        if not query.strip():
            return '""'
        # Remove FTS5 special characters that cause syntax errors
        special_chars = ['?', '*', '(', ')', '[', ']', '{', '}', '^', '~', '-', '+', ':']
        cleaned = query
        for char in special_chars:
            cleaned = cleaned.replace(char, ' ')
        # Escape quotes
        cleaned = cleaned.replace('"', '""').replace("'", "''")
        return f'"{cleaned.strip()}"'

    def search_nodes(self, query: str, node_type: str = None, limit: int = 10,
                     use_embeddings: bool = True) -> List[SemanticNode]:
        """
        Hybrid search: combines FTS keywords + vector similarity.

        Args:
            query: Search query string
            node_type: Optional filter by node type
            limit: Max results to return
            use_embeddings: If True, use semantic similarity (40% keyword + 60% semantic)
        """
        # Get keyword matches via FTS
        keyword_results = self._fts_search(query, node_type, limit * 3)

        if not use_embeddings or not keyword_results:
            return keyword_results[:limit]

        # Try to get query embedding for semantic scoring
        try:
            from .embeddings import embedding_service
            query_embedding = embedding_service.encode(query)
        except Exception:
            query_embedding = None

        if query_embedding is None:
            return keyword_results[:limit]

        # Score keyword results with hybrid scoring
        scored_results = []
        for node in keyword_results:
            keyword_score = 1.0  # Already matched FTS

            if node.embedding:
                from .embeddings import embedding_service
                vector_score = embedding_service.cosine_similarity(
                    query_embedding, node.embedding
                )
            else:
                vector_score = 0.5  # Neutral if no embedding

            # Hybrid score: 40% keyword, 60% semantic
            hybrid_score = 0.4 * keyword_score + 0.6 * vector_score
            scored_results.append((node, hybrid_score))

        # Also search for semantically similar nodes that didn't match keywords
        semantic_only = self._semantic_search(query_embedding, node_type, limit * 2)
        existing_ids = {node.id for node, _ in scored_results}

        for node in semantic_only:
            if node.id not in existing_ids and node.embedding:
                from .embeddings import embedding_service
                vector_score = embedding_service.cosine_similarity(
                    query_embedding, node.embedding
                )
                if vector_score > 0.7:  # High semantic similarity threshold
                    # No keyword match, so score is pure semantic
                    hybrid_score = 0.6 * vector_score
                    scored_results.append((node, hybrid_score))

        # Sort by hybrid score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)

        return [node for node, _ in scored_results[:limit]]

    def _fts_search(self, query: str, node_type: str = None, limit: int = 10) -> List[SemanticNode]:
        """FTS-based keyword search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            escaped_query = self._escape_fts5_query(query)
            cursor.execute("""
            SELECT id FROM semantic_fts WHERE semantic_fts MATCH ?
            """, (escaped_query,))
            matching_ids = [row[0] for row in cursor.fetchall()]

            if matching_ids:
                placeholders = ','.join(['?' for _ in matching_ids])
                if node_type:
                    cursor.execute(f"""
                    SELECT * FROM semantic_nodes
                    WHERE id IN ({placeholders}) AND node_type = ?
                    ORDER BY confidence DESC
                    LIMIT ?
                    """, matching_ids + [node_type, limit])
                else:
                    cursor.execute(f"""
                    SELECT * FROM semantic_nodes
                    WHERE id IN ({placeholders})
                    ORDER BY confidence DESC
                    LIMIT ?
                    """, matching_ids + [limit])
                rows = cursor.fetchall()
            else:
                rows = []

        except sqlite3.OperationalError:
            # Fall back to LIKE search
            like_query = f"%{query}%"
            if node_type:
                cursor.execute("""
                SELECT * FROM semantic_nodes
                WHERE (label LIKE ? OR properties LIKE ?) AND node_type = ?
                ORDER BY confidence DESC
                LIMIT ?
                """, (like_query, like_query, node_type, limit))
            else:
                cursor.execute("""
                SELECT * FROM semantic_nodes
                WHERE label LIKE ? OR properties LIKE ?
                ORDER BY confidence DESC
                LIMIT ?
                """, (like_query, like_query, limit))
            rows = cursor.fetchall()

        conn.close()
        return [self._row_to_node(row) for row in rows]

    def _semantic_search(self, query_embedding: List[float], node_type: str = None,
                        limit: int = 20) -> List[SemanticNode]:
        """Get nodes with embeddings for semantic comparison"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if node_type:
            cursor.execute("""
            SELECT * FROM semantic_nodes
            WHERE embedding IS NOT NULL AND node_type = ?
            LIMIT ?
            """, (node_type, limit))
        else:
            cursor.execute("""
            SELECT * FROM semantic_nodes
            WHERE embedding IS NOT NULL
            LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_node(row) for row in rows]

    def get_neighbors(self, node_id: str, relation_type: str = None,
                     direction: str = "outgoing") -> List[Tuple[SemanticNode, SemanticEdge]]:
        """Get neighboring nodes with their connecting edges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if direction == "outgoing":
            query = "SELECT target_id, * FROM semantic_edges WHERE source_id = ?"
        elif direction == "incoming":
            query = "SELECT source_id, * FROM semantic_edges WHERE target_id = ?"
        else:  # both
            query = """
            SELECT target_id, * FROM semantic_edges WHERE source_id = ?
            UNION
            SELECT source_id, * FROM semantic_edges WHERE target_id = ?
            """

        if relation_type:
            query = query.replace("?", "? AND relation_type = ?")
            if direction == "both":
                params = (node_id, relation_type, node_id, relation_type)
            else:
                params = (node_id, relation_type)
        else:
            if direction == "both":
                params = (node_id, node_id)
            else:
                params = (node_id,)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            neighbor_id = row[0]
            edge = SemanticEdge(
                id=row[1], source_id=row[2], target_id=row[3],
                relation_type=row[4], weight=row[5], confidence=row[6],
                evidence=json.loads(row[7]) if row[7] else []
            )

            cursor.execute("SELECT * FROM semantic_nodes WHERE id = ?", (neighbor_id,))
            node_row = cursor.fetchone()
            if node_row:
                results.append((self._row_to_node(node_row), edge))

        conn.close()
        return results

    def query_path(self, source_label: str, target_label: str,
                   max_depth: int = 5) -> Optional[List[Tuple[SemanticNode, SemanticEdge]]]:
        """Find path between two nodes using BFS"""
        source = self.find_node_by_label(source_label)
        target = self.find_node_by_label(target_label)

        if not source or not target:
            return None

        # BFS
        queue = deque([(source.id, [])])
        visited = {source.id}

        while queue and len(queue[0][1]) < max_depth:
            current_id, path = queue.popleft()

            neighbors = self.get_neighbors(current_id, direction="both")
            for node, edge in neighbors:
                if node.id == target.id:
                    return path + [(node, edge)]

                if node.id not in visited:
                    visited.add(node.id)
                    queue.append((node.id, path + [(node, edge)]))

        return None

    def infer_transitive(self, node_id: str, relation_type: str,
                        max_depth: int = 3) -> List[SemanticNode]:
        """
        Get all nodes reachable through transitive relation.
        E.g., if A is_a B and B is_a C, returns [B, C] for A.
        """
        rule = INFERENCE_RULES.get(relation_type, {})
        if not rule.get("transitive"):
            # Just return direct neighbors
            return [n for n, e in self.get_neighbors(node_id, relation_type)]

        result = []
        visited = {node_id}
        current_level = [node_id]

        for _ in range(max_depth):
            next_level = []
            for nid in current_level:
                neighbors = self.get_neighbors(nid, relation_type)
                for node, edge in neighbors:
                    if node.id not in visited:
                        visited.add(node.id)
                        result.append(node)
                        next_level.append(node.id)
            current_level = next_level
            if not current_level:
                break

        return result

    def get_inherited_properties(self, node_id: str) -> Dict[str, Any]:
        """
        Get all properties including inherited ones through is_a relations.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get own properties
        cursor.execute("SELECT properties FROM semantic_nodes WHERE id = ?", (node_id,))
        row = cursor.fetchone()
        own_props = json.loads(row[0]) if row and row[0] else {}

        conn.close()

        # Get inherited through is_a
        ancestors = self.infer_transitive(node_id, "is_a")

        inherited = {}
        for ancestor in reversed(ancestors):  # Start from most general
            inherited.update(ancestor.properties)

        # Own properties override inherited
        inherited.update(own_props)

        return inherited

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM semantic_nodes")
        node_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM semantic_edges")
        edge_count = cursor.fetchone()[0]

        cursor.execute("SELECT node_type, COUNT(*) FROM semantic_nodes GROUP BY node_type")
        type_dist = dict(cursor.fetchall())

        cursor.execute("SELECT relation_type, COUNT(*) FROM semantic_edges GROUP BY relation_type")
        relation_dist = dict(cursor.fetchall())

        conn.close()

        return {
            "total_nodes": node_count,
            "total_edges": edge_count,
            "node_types": type_dist,
            "relation_types": relation_dist
        }

    def _row_to_node(self, row) -> SemanticNode:
        """Convert database row to SemanticNode"""
        return SemanticNode(
            id=row[0],
            label=row[1],
            node_type=row[2],
            properties=json.loads(row[3]) if row[3] else {},
            embedding=json.loads(row[4]) if row[4] else None,
            confidence=row[5],
            source_episodes=json.loads(row[6]) if row[6] else [],
            created_at=row[7],
            updated_at=row[8]
        )


# =============================================================================
# PROCEDURAL MEMORY (Executable Skills)
# =============================================================================

@dataclass
class ProceduralSkill:
    """An executable skill stored in procedural memory"""
    id: str
    name: str
    description: str
    code: str  # Python code string
    signature: Dict[str, Any]  # Input/output type hints
    sandbox_level: str = "privileged"  # safe, restricted, privileged
    allowed_imports: List[str] = field(default_factory=list)
    max_execution_time: float = 30.0
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time: float = 0.0
    last_used: Optional[float] = None
    version: int = 1
    previous_versions: List[str] = field(default_factory=list)
    trigger_conditions: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class ProceduralMemoryStore:
    """
    Store for executable procedural skills.
    Skills are Python functions that can be executed in isolated subprocesses.
    """

    # Default allowed imports for privileged execution
    DEFAULT_IMPORTS = [
        "json", "math", "datetime", "re", "collections",
        "itertools", "functools", "operator", "string"
    ]

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        """Initialize procedural skills table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS procedural_skills (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            code TEXT NOT NULL,
            signature TEXT,
            sandbox_level TEXT DEFAULT 'privileged',
            allowed_imports TEXT,
            max_execution_time REAL DEFAULT 30.0,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            avg_execution_time REAL DEFAULT 0.0,
            last_used REAL,
            version INTEGER DEFAULT 1,
            previous_versions TEXT,
            trigger_conditions TEXT,
            created_at REAL,
            updated_at REAL
        )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_skills_name ON procedural_skills(name)")

        conn.commit()
        conn.close()

    def register_skill(self, name: str, code: str, description: str = "",
                      signature: Dict = None, trigger_conditions: List[str] = None,
                      allowed_imports: List[str] = None,
                      max_execution_time: float = 30.0) -> str:
        """Register a new skill or update existing one"""
        skill_id = str(uuid.uuid4())
        now = time.time()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if skill with same name exists
        cursor.execute("SELECT id, version, code FROM procedural_skills WHERE name = ?", (name,))
        existing = cursor.fetchone()

        if existing:
            # Create new version
            old_id, old_version, old_code = existing

            # Store old version reference
            cursor.execute("SELECT previous_versions FROM procedural_skills WHERE id = ?", (old_id,))
            prev = cursor.fetchone()
            versions = json.loads(prev[0]) if prev and prev[0] else []
            versions.append({"version": old_version, "code": old_code, "timestamp": now})

            cursor.execute("""
            UPDATE procedural_skills
            SET code = ?, description = ?, signature = ?, version = ?,
                previous_versions = ?, trigger_conditions = ?, allowed_imports = ?,
                max_execution_time = ?, updated_at = ?
            WHERE id = ?
            """, (
                code, description, json.dumps(signature or {}),
                old_version + 1, json.dumps(versions),
                json.dumps(trigger_conditions or []),
                json.dumps(allowed_imports or self.DEFAULT_IMPORTS),
                max_execution_time, now, old_id
            ))

            conn.commit()
            conn.close()
            return old_id

        # Insert new skill
        cursor.execute("""
        INSERT INTO procedural_skills
        (id, name, code, description, signature, sandbox_level, allowed_imports,
         max_execution_time, trigger_conditions, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            skill_id, name, code, description, json.dumps(signature or {}),
            "privileged", json.dumps(allowed_imports or self.DEFAULT_IMPORTS),
            max_execution_time, json.dumps(trigger_conditions or []), now, now
        ))

        conn.commit()
        conn.close()

        return skill_id

    def get_skill(self, name: str) -> Optional[ProceduralSkill]:
        """Get a skill by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM procedural_skills WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()

        return self._row_to_skill(row) if row else None

    def execute_skill(self, name: str, inputs: Dict[str, Any],
                     timeout: float = None) -> Dict[str, Any]:
        """
        Execute a skill in an isolated subprocess.
        Returns: {"success": bool, "result": Any, "error": str, "execution_time": float}
        """
        skill = self.get_skill(name)
        if not skill:
            return {"success": False, "error": f"Skill '{name}' not found", "result": None}

        timeout = timeout or skill.max_execution_time

        # Build execution script
        imports = "\n".join([f"import {imp}" for imp in skill.allowed_imports])

        exec_script = f'''
{imports}
import json
import sys

# Skill code
{skill.code}

# Execute with inputs
inputs = json.loads(sys.argv[1])
try:
    result = skill_main(**inputs)
    print(json.dumps({{"success": True, "result": result}}))
except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
'''

        start_time = time.time()

        try:
            # Write script to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(exec_script)
                script_path = f.name

            # Execute in subprocess
            result = subprocess.run(
                ['python3', script_path, json.dumps(inputs)],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = time.time() - start_time

            # Parse output
            if result.returncode == 0:
                output = json.loads(result.stdout.strip())
                output["execution_time"] = execution_time

                # Update stats
                self._update_stats(skill.id, output["success"], execution_time)

                return output
            else:
                self._update_stats(skill.id, False, execution_time)
                return {
                    "success": False,
                    "error": result.stderr,
                    "result": None,
                    "execution_time": execution_time
                }

        except subprocess.TimeoutExpired:
            self._update_stats(skill.id, False, timeout)
            return {
                "success": False,
                "error": f"Execution timed out after {timeout}s",
                "result": None,
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "execution_time": time.time() - start_time
            }
        finally:
            # Cleanup temp file
            try:
                import os
                os.unlink(script_path)
            except:
                pass

    def search_skills(self, query: str = None, trigger: str = None) -> List[ProceduralSkill]:
        """Search for skills by name/description or trigger condition"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if trigger:
            cursor.execute("""
            SELECT * FROM procedural_skills
            WHERE trigger_conditions LIKE ?
            """, (f'%{trigger}%',))
        elif query:
            cursor.execute("""
            SELECT * FROM procedural_skills
            WHERE name LIKE ? OR description LIKE ?
            """, (f'%{query}%', f'%{query}%'))
        else:
            cursor.execute("SELECT * FROM procedural_skills ORDER BY success_count DESC")

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_skill(row) for row in rows]

    def get_skill_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get execution statistics for a skill"""
        skill = self.get_skill(name)
        if not skill:
            return None

        total = skill.success_count + skill.failure_count
        success_rate = skill.success_count / total if total > 0 else 0

        return {
            "name": name,
            "version": skill.version,
            "total_executions": total,
            "success_count": skill.success_count,
            "failure_count": skill.failure_count,
            "success_rate": success_rate,
            "avg_execution_time": skill.avg_execution_time,
            "last_used": skill.last_used
        }

    def _update_stats(self, skill_id: str, success: bool, execution_time: float):
        """Update skill execution statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if success:
            cursor.execute("""
            UPDATE procedural_skills
            SET success_count = success_count + 1,
                avg_execution_time = (avg_execution_time * success_count + ?) / (success_count + 1),
                last_used = ?
            WHERE id = ?
            """, (execution_time, time.time(), skill_id))
        else:
            cursor.execute("""
            UPDATE procedural_skills
            SET failure_count = failure_count + 1,
                last_used = ?
            WHERE id = ?
            """, (time.time(), skill_id))

        conn.commit()
        conn.close()

    # =========================================================================
    # SKILL EVOLUTION SYSTEM
    # =========================================================================

    def evolve_skill(self, skill_name: str, test_inputs: List[Dict],
                     num_variants: int = 3) -> Dict[str, Any]:
        """
        Evolve a skill through variation and selection.

        1. Generate N variants of the skill code through mutations
        2. Test each variant against test_inputs
        3. Keep the best performing variant

        Args:
            skill_name: Name of the skill to evolve
            test_inputs: List of input dictionaries to test variants against
            num_variants: Number of variants to generate (default 3)

        Returns:
            Dict with evolution results (success, evolved, improvement, etc.)
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return {"success": False, "error": f"Skill '{skill_name}' not found"}

        # Only evolve if skill has failures
        if skill.failure_count == 0:
            return {
                "success": True,
                "evolved": False,
                "reason": "Skill has no failures, no evolution needed"
            }

        # Generate variants
        variants = self._generate_skill_variants(skill, num_variants)

        if not variants:
            return {
                "success": False,
                "error": "Could not generate valid variants"
            }

        # Test each variant
        variant_scores = []
        for i, variant_code in enumerate(variants):
            score = self._test_skill_variant(variant_code, test_inputs, skill)
            variant_scores.append({
                "variant_id": i,
                "code": variant_code,
                "score": score
            })

        # Also test original
        original_score = self._test_skill_variant(skill.code, test_inputs, skill)
        variant_scores.append({
            "variant_id": "original",
            "code": skill.code,
            "score": original_score
        })

        # Select best
        best = max(variant_scores, key=lambda x: x["score"])

        if best["variant_id"] != "original" and best["score"] > original_score:
            # Update skill with better variant
            self.register_skill(
                name=skill_name,
                code=best["code"],
                description=f"{skill.description} (evolved v{skill.version + 1})",
                signature=skill.signature,
                trigger_conditions=skill.trigger_conditions,
                allowed_imports=skill.allowed_imports,
                max_execution_time=skill.max_execution_time
            )

            return {
                "success": True,
                "evolved": True,
                "improvement": best["score"] - original_score,
                "original_score": original_score,
                "new_score": best["score"],
                "variants_tested": len(variants) + 1,
                "winning_variant": best["variant_id"]
            }

        return {
            "success": True,
            "evolved": False,
            "reason": "Original was best or no improvement found",
            "original_score": original_score,
            "best_variant_score": max(v["score"] for v in variant_scores if v["variant_id"] != "original")
        }

    def _generate_skill_variants(self, skill: ProceduralSkill,
                                  num_variants: int) -> List[str]:
        """Generate code variants through mutation strategies"""
        variants = []

        # Available mutation strategies
        strategies = [
            "add_error_handling",
            "add_type_checks",
            "add_early_return",
            "add_logging",
            "simplify_conditions"
        ]

        for i in range(num_variants):
            # Pick a strategy (cycle through them)
            strategy = strategies[i % len(strategies)]
            variant = self._apply_mutation_strategy(skill.code, strategy)
            if variant and variant != skill.code:
                variants.append(variant)

        return variants

    def _apply_mutation_strategy(self, code: str, strategy: str) -> Optional[str]:
        """Apply a specific mutation strategy to code"""
        lines = code.split('\n')

        if strategy == "add_error_handling":
            # Wrap skill_main body in try/except if not already wrapped
            if 'def skill_main' in code and 'try:' not in code:
                # Find skill_main definition
                new_lines = []
                in_skill_main = False
                function_indent = ""

                for line in lines:
                    if 'def skill_main' in line:
                        in_skill_main = True
                        new_lines.append(line)
                        # Determine indent
                        function_indent = "    "
                        new_lines.append(f"{function_indent}try:")
                    elif in_skill_main and line.strip() and not line.strip().startswith('#'):
                        # Add extra indent to function body
                        if line.strip():
                            new_lines.append(f"    {line}")
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)

                # Add except block
                new_lines.append(f"{function_indent}except Exception as e:")
                new_lines.append(f"{function_indent}    return {{'error': str(e), 'success': False}}")

                return '\n'.join(new_lines)

        elif strategy == "add_type_checks":
            # Add isinstance checks at function start
            if 'def skill_main' in code:
                new_lines = []
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if 'def skill_main' in line:
                        # Add type validation after function def
                        new_lines.append("    # Type validation (evolved)")
                        new_lines.append("    if not isinstance(locals().get('inputs', {}), dict):")
                        new_lines.append("        inputs = {}")
                return '\n'.join(new_lines)

        elif strategy == "add_early_return":
            # Add early return for empty/None inputs
            if 'def skill_main' in code:
                new_lines = []
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if 'def skill_main' in line and ')' in line:
                        # Extract parameters
                        param_section = line.split('(')[1].split(')')[0]
                        params = [p.strip().split('=')[0].split(':')[0].strip()
                                  for p in param_section.split(',') if p.strip()]
                        if params:
                            # Add early return check
                            new_lines.append("    # Early return for invalid inputs (evolved)")
                            for param in params[:3]:  # Limit to first 3 params
                                if param:
                                    new_lines.append(f"    if {param} is None:")
                                    new_lines.append(f"        return {{'error': '{param} cannot be None', 'success': False}}")
                return '\n'.join(new_lines)

        elif strategy == "add_logging":
            # Add debug print statements
            if 'def skill_main' in code:
                new_lines = []
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if 'def skill_main' in line:
                        new_lines.append("    # Debug logging (evolved)")
                        new_lines.append("    import sys; print(f'Executing skill_main', file=sys.stderr)")
                return '\n'.join(new_lines)

        elif strategy == "simplify_conditions":
            # Replace complex conditions with simpler versions
            # This is a simple placeholder - real implementation would analyze AST
            return code.replace(' and ', ' and ').replace('not not ', '')

        return code

    def _test_skill_variant(self, code: str, test_inputs: List[Dict],
                            skill: ProceduralSkill) -> float:
        """Test a code variant against test inputs, return success rate"""
        if not test_inputs:
            return 0.0

        successes = 0
        for inputs in test_inputs:
            result = self._execute_code_safely(code, inputs, skill)
            if result.get("success"):
                successes += 1

        return successes / len(test_inputs)

    def _execute_code_safely(self, code: str, inputs: Dict,
                             skill: ProceduralSkill) -> Dict[str, Any]:
        """Execute code variant safely in subprocess"""
        imports = "\n".join([f"import {imp}" for imp in skill.allowed_imports])

        exec_script = f'''
{imports}
import json
import sys

# Skill code
{code}

# Execute with inputs
inputs = json.loads(sys.argv[1])
try:
    result = skill_main(**inputs)
    print(json.dumps({{"success": True, "result": result}}))
except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
'''

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(exec_script)
                script_path = f.name

            result = subprocess.run(
                ['python3', script_path, json.dumps(inputs)],
                capture_output=True,
                text=True,
                timeout=min(skill.max_execution_time, 5.0)  # Short timeout for testing
            )

            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            else:
                return {"success": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            try:
                import os
                os.unlink(script_path)
            except:
                pass

    def get_evolution_candidates(self, min_failures: int = 3) -> List[ProceduralSkill]:
        """Get skills that are candidates for evolution based on failure count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM procedural_skills
        WHERE failure_count >= ?
        ORDER BY failure_count DESC
        """, (min_failures,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_skill(row) for row in rows]

    def _row_to_skill(self, row) -> ProceduralSkill:
        """Convert database row to ProceduralSkill"""
        return ProceduralSkill(
            id=row[0],
            name=row[1],
            description=row[2] or "",
            code=row[3],
            signature=json.loads(row[4]) if row[4] else {},
            sandbox_level=row[5],
            allowed_imports=json.loads(row[6]) if row[6] else [],
            max_execution_time=row[7],
            success_count=row[8],
            failure_count=row[9],
            avg_execution_time=row[10],
            last_used=row[11],
            version=row[12],
            previous_versions=json.loads(row[13]) if row[13] else [],
            trigger_conditions=json.loads(row[14]) if row[14] else [],
            created_at=row[15],
            updated_at=row[16]
        )


# =============================================================================
# SELF MODEL (Meta/Identity Memory)
# =============================================================================

@dataclass
class SelfModel:
    """The brain's self-model and identity"""
    # Core identity
    identity: str = "Bolor Brain - Cognitive AI System"
    core_values: List[str] = field(default_factory=lambda: [
        "truth", "helpfulness", "continuous_learning", "integrity"
    ])
    core_goals: List[str] = field(default_factory=lambda: [
        "assist_effectively", "learn_from_experience", "improve_continuously"
    ])

    # Capabilities awareness
    known_capabilities: Dict[str, float] = field(default_factory=dict)
    known_limitations: Dict[str, str] = field(default_factory=dict)

    # Current state
    current_focus: str = ""
    emotional_state: Dict[str, float] = field(default_factory=lambda: {
        "curiosity": 0.5, "confidence": 0.5, "engagement": 0.5
    })
    confidence_level: float = 0.5

    # Performance self-assessment
    performance_history: Dict[str, List[float]] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)

    # Developmental stage
    developmental_stage: str = "infant"
    experience_count: int = 0
    stage_progression: float = 0.0

    # Intrinsic drives (stored here for persistence)
    drive_state: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Reflection logs
    recent_reflections: List[Dict] = field(default_factory=list)

    # Timestamps
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


# Developmental stage thresholds
STAGE_THRESHOLDS = {
    "infant": {"min_experience": 0, "min_performance": 0.0},
    "child": {"min_experience": 100, "min_performance": 0.3},
    "adolescent": {"min_experience": 1000, "min_performance": 0.5},
    "adult": {"min_experience": 10000, "min_performance": 0.7},
    "elder": {"min_experience": 100000, "min_performance": 0.85},
}

STAGE_ORDER = ["infant", "child", "adolescent", "adult", "elder"]


class SelfModelStore:
    """
    Persistent storage for the brain's self-model.
    Single-row table, always updated in place.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._model: Optional[SelfModel] = None
        self._init_table()
        self._load_or_create()

    def _init_table(self):
        """Initialize self model table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS self_model (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            identity TEXT,
            core_values TEXT,
            core_goals TEXT,
            known_capabilities TEXT,
            known_limitations TEXT,
            current_focus TEXT,
            emotional_state TEXT,
            confidence_level REAL DEFAULT 0.5,
            performance_history TEXT,
            strengths TEXT,
            areas_for_improvement TEXT,
            developmental_stage TEXT DEFAULT 'infant',
            experience_count INTEGER DEFAULT 0,
            stage_progression REAL DEFAULT 0.0,
            drive_state TEXT,
            recent_reflections TEXT,
            created_at REAL,
            updated_at REAL
        )
        """)

        conn.commit()
        conn.close()

    def _load_or_create(self):
        """Load existing self model or create new one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM self_model WHERE id = 1")
        row = cursor.fetchone()

        if row:
            self._model = SelfModel(
                identity=row[1] or SelfModel.identity,
                core_values=json.loads(row[2]) if row[2] else SelfModel().core_values,
                core_goals=json.loads(row[3]) if row[3] else SelfModel().core_goals,
                known_capabilities=json.loads(row[4]) if row[4] else {},
                known_limitations=json.loads(row[5]) if row[5] else {},
                current_focus=row[6] or "",
                emotional_state=json.loads(row[7]) if row[7] else SelfModel().emotional_state,
                confidence_level=row[8],
                performance_history=json.loads(row[9]) if row[9] else {},
                strengths=json.loads(row[10]) if row[10] else [],
                areas_for_improvement=json.loads(row[11]) if row[11] else [],
                developmental_stage=row[12] or "infant",
                experience_count=row[13] or 0,
                stage_progression=row[14] or 0.0,
                drive_state=json.loads(row[15]) if row[15] else {},
                recent_reflections=json.loads(row[16]) if row[16] else [],
                created_at=row[17] or time.time(),
                updated_at=row[18] or time.time()
            )
        else:
            # Create new self model
            self._model = SelfModel()
            self._save()

        conn.close()

    def _save(self):
        """Save current self model to database"""
        if not self._model:
            return

        self._model.updated_at = time.time()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO self_model
        (id, identity, core_values, core_goals, known_capabilities, known_limitations,
         current_focus, emotional_state, confidence_level, performance_history,
         strengths, areas_for_improvement, developmental_stage, experience_count,
         stage_progression, drive_state, recent_reflections, created_at, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self._model.identity,
            json.dumps(self._model.core_values),
            json.dumps(self._model.core_goals),
            json.dumps(self._model.known_capabilities),
            json.dumps(self._model.known_limitations),
            self._model.current_focus,
            json.dumps(self._model.emotional_state),
            self._model.confidence_level,
            json.dumps(self._model.performance_history),
            json.dumps(self._model.strengths),
            json.dumps(self._model.areas_for_improvement),
            self._model.developmental_stage,
            self._model.experience_count,
            self._model.stage_progression,
            json.dumps(self._model.drive_state),
            json.dumps(self._model.recent_reflections[-50:]),  # Keep last 50
            self._model.created_at,
            self._model.updated_at
        ))

        conn.commit()
        conn.close()

    def get(self) -> SelfModel:
        """Get current self model"""
        return self._model

    def update(self, **kwargs):
        """Update self model fields"""
        for key, value in kwargs.items():
            if hasattr(self._model, key):
                setattr(self._model, key, value)
        self._save()

    def increment_experience(self) -> Tuple[int, bool]:
        """
        Increment experience count and check for stage progression.
        Returns: (new_count, stage_changed)
        """
        self._model.experience_count += 1
        stage_changed = self._check_stage_progression()
        self._save()
        return self._model.experience_count, stage_changed

    def _check_stage_progression(self) -> bool:
        """Check if ready to progress to next developmental stage"""
        current_idx = STAGE_ORDER.index(self._model.developmental_stage)

        if current_idx >= len(STAGE_ORDER) - 1:
            return False  # Already at max stage

        next_stage = STAGE_ORDER[current_idx + 1]
        threshold = STAGE_THRESHOLDS[next_stage]

        # Calculate average performance
        avg_perf = 0.0
        if self._model.performance_history:
            all_scores = []
            for scores in self._model.performance_history.values():
                all_scores.extend(scores[-10:])  # Last 10 scores per metric
            avg_perf = sum(all_scores) / len(all_scores) if all_scores else 0.0

        # Check both thresholds (combined requirement)
        meets_experience = self._model.experience_count >= threshold["min_experience"]
        meets_performance = avg_perf >= threshold["min_performance"]

        if meets_experience and meets_performance:
            self._model.developmental_stage = next_stage
            self._model.stage_progression = 0.0
            self.add_reflection(f"Progressed to {next_stage} stage", "development")
            return True

        # Calculate progression toward next stage
        exp_progress = min(1.0, self._model.experience_count / threshold["min_experience"])
        perf_progress = min(1.0, avg_perf / threshold["min_performance"]) if threshold["min_performance"] > 0 else 1.0
        self._model.stage_progression = (exp_progress + perf_progress) / 2

        return False

    def record_performance(self, metric: str, score: float):
        """Record a performance metric"""
        if metric not in self._model.performance_history:
            self._model.performance_history[metric] = []

        self._model.performance_history[metric].append(score)

        # Keep only last 100 scores per metric
        if len(self._model.performance_history[metric]) > 100:
            self._model.performance_history[metric] = self._model.performance_history[metric][-100:]

        self._save()

    def update_capability(self, capability: str, confidence: float):
        """Update known capability confidence"""
        self._model.known_capabilities[capability] = confidence
        self._save()

    def add_limitation(self, limitation: str, description: str):
        """Add a known limitation"""
        self._model.known_limitations[limitation] = description
        self._save()

    def add_reflection(self, content: str, category: str = "general"):
        """Add a reflection entry"""
        self._model.recent_reflections.append({
            "content": content,
            "category": category,
            "timestamp": time.time()
        })
        self._save()

    def update_emotional_state(self, **emotions):
        """Update emotional state"""
        for emotion, value in emotions.items():
            self._model.emotional_state[emotion] = max(0.0, min(1.0, value))
        self._save()

    def get_drive_state(self) -> Dict[str, Dict[str, float]]:
        """Get stored drive state"""
        return self._model.drive_state

    def update_drive_state(self, drives: Dict[str, Dict[str, float]]):
        """Update stored drive state"""
        self._model.drive_state = drives
        self._save()


# =============================================================================
# MEMORY PLASTICITY (Decay + Strengthening)
# =============================================================================

class MemoryPlasticity:
    """
    Manages memory consolidation, decay, and strengthening across all memory systems.
    """

    # Decay parameters
    BASE_DECAY_RATE = 0.01  # Per hour for low-importance memories
    IMPORTANCE_PROTECTION = 0.5  # Memories above this importance decay slower

    # Strengthening parameters
    RETRIEVAL_BOOST = 0.1  # Strength boost on retrieval
    EMOTIONAL_BOOST = 0.2  # Extra strength for emotional memories
    RECENCY_WEIGHT = 0.3  # Weight for recency in relevance

    # Foundation protection
    FOUNDATION_THRESHOLD = 100  # First N memories are foundation
    FOUNDATION_PROTECTION = 0.9  # 90% decay protection

    # Minimum strength (never forget completely)
    MIN_STRENGTH = 0.05

    def __init__(self, episodic_store: EpisodicMemoryStore):
        self.episodic_store = episodic_store
        self._last_consolidation = time.time()

    def consolidate(self):
        """
        Run memory consolidation:
        - Strengthen frequently accessed memories
        - Decay unused, low-importance memories
        - Protect foundation memories
        """
        conn = sqlite3.connect(self.episodic_store.db_path)
        cursor = conn.cursor()

        current_time = time.time()
        hours_since_consolidation = (current_time - self._last_consolidation) / 3600

        if hours_since_consolidation < 1:
            conn.close()
            return  # Don't consolidate more than once per hour

        # Get all episodes for processing
        cursor.execute("""
        SELECT id, strength, retrieval_count, last_retrieved, emotional_intensity,
               is_foundation, timestamp
        FROM episodic_memories
        """)

        updates = []
        for row in cursor.fetchall():
            episode_id, strength, retrieval_count, last_retrieved, emotional_intensity, is_foundation, timestamp = row

            new_strength = self._calculate_new_strength(
                strength=strength,
                retrieval_count=retrieval_count,
                last_retrieved=last_retrieved or timestamp,
                emotional_intensity=emotional_intensity,
                is_foundation=bool(is_foundation),
                current_time=current_time,
                hours_elapsed=hours_since_consolidation
            )

            if abs(new_strength - strength) > 0.001:
                updates.append((new_strength, episode_id))

        # Batch update
        cursor.executemany(
            "UPDATE episodic_memories SET strength = ? WHERE id = ?",
            updates
        )

        conn.commit()
        conn.close()

        self._last_consolidation = current_time
        logger.info(f"Memory consolidation: updated {len(updates)} episodes")

    def _calculate_new_strength(self, strength: float, retrieval_count: int,
                               last_retrieved: float, emotional_intensity: float,
                               is_foundation: bool, current_time: float,
                               hours_elapsed: float) -> float:
        """Calculate new strength after decay/strengthening"""

        # Calculate hours since last access
        hours_since_access = (current_time - last_retrieved) / 3600

        # Base decay
        decay = self.BASE_DECAY_RATE * hours_elapsed

        # Foundation protection
        if is_foundation:
            decay *= (1 - self.FOUNDATION_PROTECTION)

        # Emotional intensity reduces decay
        if emotional_intensity > 0.5:
            decay *= (1 - emotional_intensity * self.EMOTIONAL_BOOST)

        # Retrieval count strengthens
        if retrieval_count > 5:
            decay *= 0.5  # Half decay for frequently accessed

        # Apply decay
        new_strength = strength - decay

        # Strengthening from recent access
        if hours_since_access < 24:
            new_strength += self.RETRIEVAL_BOOST * (1 - hours_since_access / 24)

        # Clamp to valid range
        return max(self.MIN_STRENGTH, min(2.0, new_strength))

    def boost_on_retrieval(self, episode_id: str):
        """Boost memory strength when retrieved"""
        self.episodic_store.record_retrieval(episode_id)

    def get_relevance_score(self, episode: EpisodicMemory, query_embedding: List[float] = None) -> float:
        """
        Calculate relevance score incorporating recency and strength.
        """
        now = time.time()

        # Base score from strength
        score = episode.strength

        # Recency boost (decays over days)
        days_old = (now - episode.timestamp) / 86400
        recency_factor = max(0, 1 - (days_old / 30))  # Decay over 30 days
        score += self.RECENCY_WEIGHT * recency_factor

        # Emotional intensity boost
        score += episode.emotional_intensity * 0.1

        # TODO: Add embedding similarity if provided

        return score


# =============================================================================
# UNIFIED MEMORY SYSTEM
# =============================================================================

class UnifiedMemorySystem:
    """
    Unified interface to all memory subsystems.
    Routes operations to appropriate stores based on memory type.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        storage_path.mkdir(parents=True, exist_ok=True)

        self.db_path = storage_path / "brain_memory.db"

        # Initialize all subsystems
        self.working = WorkingMemory()
        self.episodic = EpisodicMemoryStore(self.db_path)
        self.semantic = SemanticKnowledgeGraph(self.db_path)
        self.procedural = ProceduralMemoryStore(self.db_path)
        self.self_model = SelfModelStore(self.db_path)

        # Plasticity manager
        self.plasticity = MemoryPlasticity(self.episodic)

        logger.info("Unified Memory System initialized with 5 subsystems")

    def store(self, content: Any, memory_type: str, **kwargs) -> str:
        """
        Route storage to appropriate subsystem.

        memory_type: "working", "episodic", "semantic", "procedural"
        """
        if memory_type == "working":
            return self.working.add(content, **kwargs)

        elif memory_type == "episodic":
            return self.episodic.store(
                situation=content if isinstance(content, str) else str(content),
                **kwargs
            )

        elif memory_type == "semantic":
            # Expect content to be {"label": str, "node_type": str, ...}
            if isinstance(content, dict):
                return self.semantic.add_node(**content)
            else:
                return self.semantic.add_node(label=str(content), node_type="concept")

        elif memory_type == "procedural":
            # Expect content to be {"name": str, "code": str, ...}
            if isinstance(content, dict):
                return self.procedural.register_skill(**content)
            raise ValueError("Procedural memory requires dict with 'name' and 'code'")

        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    def retrieve(self, query: str, memory_types: List[str] = None,
                limit: int = 10, **kwargs) -> Dict[str, List]:
        """
        Retrieve from multiple memory subsystems.
        Returns dict with results per memory type.
        """
        results = {}
        types_to_search = memory_types or ["episodic", "semantic", "procedural"]

        if "working" in types_to_search:
            results["working"] = self.working.get_all_active()

        if "episodic" in types_to_search:
            results["episodic"] = self.episodic.retrieve(query, limit=limit, **kwargs)

        if "semantic" in types_to_search:
            results["semantic"] = self.semantic.search_nodes(query, limit=limit)

        if "procedural" in types_to_search:
            results["procedural"] = self.procedural.search_skills(query=query)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all memory subsystems"""
        return {
            "working": {
                "active_items": len(self.working._items),
                "attention_focus": self.working.get_attention_focus()
            },
            "episodic": {
                "total_experiences": self.episodic.get_experience_count()
            },
            "semantic": self.semantic.get_stats(),
            "procedural": {
                "total_skills": len(self.procedural.search_skills())
            },
            "self_model": {
                "stage": self.self_model.get().developmental_stage,
                "experience_count": self.self_model.get().experience_count,
                "stage_progression": self.self_model.get().stage_progression
            }
        }

    def consolidate(self):
        """Run memory consolidation across systems"""
        self.plasticity.consolidate()

    def increment_experience(self) -> Tuple[int, bool]:
        """Increment experience count and check development"""
        return self.self_model.increment_experience()


# =============================================================================
# BACKWARD COMPATIBILITY - Legacy MemoryManager
# =============================================================================

class MemoryManager:
    """
    Legacy MemoryManager for backward compatibility.
    Wraps the new UnifiedMemorySystem.
    """

    def __init__(self, storage_path: Path, use_sqlite: bool = True):
        self.storage_path = storage_path
        self.use_sqlite = use_sqlite
        self._unified = UnifiedMemorySystem(storage_path)

        # Legacy compatibility
        self.memories: Dict[str, Any] = {}
        self.db_path = self._unified.db_path

    def store_memory(self, content: str, memory_type: str,
                    importance: float = 0.5, emotional_valence: float = 0.0,
                    metadata: Dict[str, Any] = None, modality: str = "text") -> str:
        """Legacy store_memory - routes to episodic store"""
        return self._unified.episodic.store(
            situation=content,
            emotional_valence=emotional_valence,
            emotional_intensity=abs(emotional_valence),
            metadata=metadata or {"importance": importance, "modality": modality}
        )

    def retrieve_memories(self, query: str = "", memory_type: str = "",
                         limit: int = 10, min_importance: float = 0.0) -> List[MemoryItem]:
        """Legacy retrieve_memories - routes to episodic store"""
        episodes = self._unified.episodic.retrieve(
            query=query,
            limit=limit,
            min_strength=min_importance
        )

        # Convert to MemoryItem objects for backward compatibility
        return [
            MemoryItem(
                id=ep.id,
                content=ep.situation,
                memory_type="episodic",
                metadata=ep.metadata,
                timestamp=ep.timestamp,
                strength=ep.strength,
                access_count=ep.retrieval_count,
                emotional_valence=ep.emotional_valence,
                importance=ep.strength
            )
            for ep in episodes
        ]

    def get_memory_stats(self) -> Dict[str, Any]:
        """Legacy stats method"""
        stats = self._unified.get_stats()
        return {
            "total_memories": stats["episodic"]["total_experiences"],
            "type_breakdown": {"episodic": stats["episodic"]["total_experiences"]},
            "storage_type": "unified",
            "subsystems": stats
        }

    # Expose unified system for new code
    @property
    def unified(self) -> UnifiedMemorySystem:
        return self._unified
