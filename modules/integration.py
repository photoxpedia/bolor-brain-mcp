"""
Brain Memory Integration Layer
==============================
Bridges the legacy SimpleBrain memory system with the new UnifiedMemorySystem.
Handles migration and provides unified access.
"""

import sqlite3
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from .memory import (
    UnifiedMemorySystem,
    EpisodicMemory,
    SemanticNode,
    ProceduralSkill,
    WorkingMemory,
)
from .drives import DriveManager, DriveType, tag_memory_with_drive

logger = logging.getLogger(__name__)


class MemoryMigrator:
    """
    Migrates existing memories from the old flat schema to the new differentiated system.
    """

    def __init__(self, old_db_path: Path, unified_system: UnifiedMemorySystem):
        self.old_db_path = old_db_path
        self.unified = unified_system
        self._migration_stats = {
            "total_found": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0
        }

    def migrate(self, mark_as_foundation: bool = True) -> Dict[str, Any]:
        """
        Migrate all existing memories to the new episodic format.
        First 100 memories are marked as foundation memories.

        Returns migration statistics.
        """
        if not self.old_db_path.exists():
            logger.info("No existing database to migrate")
            return {"status": "no_migration_needed", "stats": self._migration_stats}

        try:
            conn = sqlite3.connect(str(self.old_db_path))
            cursor = conn.cursor()

            # Check if old memories table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='memories'
            """)
            if not cursor.fetchone():
                conn.close()
                return {"status": "no_old_memories_table", "stats": self._migration_stats}

            # Check if already migrated (look for migration marker)
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='episodic_memories'
            """)
            if cursor.fetchone():
                # Check if episodic_memories has data
                cursor.execute("SELECT COUNT(*) FROM episodic_memories")
                if cursor.fetchone()[0] > 0:
                    logger.info("Migration already completed")
                    conn.close()
                    return {"status": "already_migrated", "stats": self._migration_stats}

            # Get all old memories
            cursor.execute("""
                SELECT id, content, memory_type, metadata, timestamp, strength,
                       emotional_valence, importance, access_count, modality
                FROM memories
                ORDER BY timestamp ASC
            """)

            rows = cursor.fetchall()
            self._migration_stats["total_found"] = len(rows)
            conn.close()

            logger.info(f"Found {len(rows)} memories to migrate")

            # Migrate each memory
            for idx, row in enumerate(rows):
                try:
                    memory_id, content, memory_type, metadata_json, timestamp, strength, \
                        emotional_valence, importance, access_count, modality = row

                    metadata = json.loads(metadata_json or '{}')

                    # Determine which drive this memory might satisfy
                    drive = tag_memory_with_drive(
                        self.unified.self_model._model.drive_state if hasattr(self.unified.self_model, '_model') else {},
                        content,
                        memory_type
                    )

                    # Mark first 100 as foundation - they get protection
                    is_foundation = idx < 100 if mark_as_foundation else False

                    # Store in new episodic format
                    episode_id = self.unified.episodic.store(
                        situation=content,
                        action=metadata.get("action", ""),
                        outcome=metadata.get("outcome", ""),
                        reward=metadata.get("reward", 0.0),
                        emotional_valence=emotional_valence or 0.0,
                        emotional_intensity=abs(emotional_valence or 0.0),
                        drive_satisfied=drive,
                        metadata={
                            "legacy_id": memory_id,
                            "legacy_type": memory_type,
                            "importance": importance,
                            "modality": modality,
                            "migrated_at": time.time(),
                            **metadata
                        }
                    )

                    # If it was semantic type, also add to knowledge graph
                    if memory_type == "semantic":
                        self.unified.semantic.add_node(
                            label=content[:100],  # First 100 chars as label
                            node_type="concept",
                            properties={"full_content": content, **metadata},
                            source_episodes=[episode_id],
                            confidence=importance or 0.5
                        )

                    self._migration_stats["migrated"] += 1

                except Exception as e:
                    logger.warning(f"Failed to migrate memory {memory_id}: {e}")
                    self._migration_stats["errors"] += 1

            # Update self-model experience count
            self.unified.self_model.update(
                experience_count=self._migration_stats["migrated"]
            )

            logger.info(f"Migration complete: {self._migration_stats}")

            return {
                "status": "migration_complete",
                "stats": self._migration_stats
            }

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return {
                "status": "migration_failed",
                "error": str(e),
                "stats": self._migration_stats
            }


class BrainMemoryBridge:
    """
    Bridges the old SimpleBrain memory interface with the new UnifiedMemorySystem.
    Provides backward compatibility while enabling new features.
    """

    # Evolution configuration
    EVOLUTION_FAILURE_THRESHOLD = 3  # Failures before evolution is considered
    EVOLUTION_TEST_CASES_REQUIRED = 3  # Test cases needed to trigger evolution

    def __init__(self, storage_path: Path, auto_migrate: bool = True):
        self.storage_path = storage_path
        storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize new unified system
        self.unified = UnifiedMemorySystem(storage_path)

        # Initialize drive manager connected to self-model
        self.drives = DriveManager(self.unified.self_model)

        # Failed test cases for skill evolution
        self._failed_test_cases: Dict[str, List[Dict]] = {}

        # Check for legacy database and migrate
        legacy_db = storage_path / "memories.db"
        if auto_migrate and legacy_db.exists():
            migrator = MemoryMigrator(legacy_db, self.unified)
            migration_result = migrator.migrate()
            logger.info(f"Migration result: {migration_result['status']}")

        logger.info("BrainMemoryBridge initialized")

    # =========================================================================
    # LEGACY API (backward compatible)
    # =========================================================================

    def store_memory(self, content: str, memory_type: str,
                    metadata: Dict = None, modality: str = "text",
                    emotional_valence: float = 0.0,
                    importance: float = 0.5) -> str:
        """Legacy store_memory - routes to appropriate subsystem"""

        # Tag with drive
        drive = tag_memory_with_drive(
            self.drives.get_state(),
            content,
            memory_type
        )

        # Record action for drive satisfaction
        self.drives.record_action("learn" if "learn" in content.lower() else "store")

        # Route based on type
        if memory_type == "working":
            return self.unified.working.add(content, tags=[modality])

        elif memory_type == "procedural":
            # Check if it looks like code
            if "def " in content or "function" in content:
                return self.unified.procedural.register_skill(
                    name=f"skill_{int(time.time())}",
                    code=content,
                    description=metadata.get("description", "") if metadata else ""
                )

        elif memory_type == "semantic":
            return self.unified.semantic.add_node(
                label=content[:100],
                node_type="concept",
                properties={"full_content": content, **(metadata or {})}
            )

        # Default: episodic
        return self.unified.episodic.store(
            situation=content,
            emotional_valence=emotional_valence,
            emotional_intensity=abs(emotional_valence),
            drive_satisfied=drive,
            metadata={"importance": importance, "modality": modality, **(metadata or {})}
        )

    def retrieve_memories(self, query: str, memory_types: List[str] = None,
                         limit: int = 10) -> List[Dict]:
        """Legacy retrieve_memories - searches all subsystems"""

        # Update drives (time-based decay/increase)
        self.drives.get_state().update_all()

        results = []
        types_to_search = memory_types or ["episodic", "semantic", "procedural"]

        # Search episodic
        if "episodic" in types_to_search or not memory_types:
            episodes = self.unified.episodic.retrieve(query, limit=limit)
            for ep in episodes:
                # Record retrieval for plasticity
                self.unified.episodic.record_retrieval(ep.id)
                results.append({
                    "id": ep.id,
                    "content": ep.situation,
                    "memory_type": "episodic",
                    "timestamp": ep.timestamp,
                    "strength": ep.strength,
                    "metadata": ep.metadata,
                    "emotional_valence": ep.emotional_valence,
                    "reward": ep.reward
                })

        # Search semantic
        if "semantic" in types_to_search:
            nodes = self.unified.semantic.search_nodes(query, limit=limit)
            for node in nodes:
                results.append({
                    "id": node.id,
                    "content": node.properties.get("full_content", node.label),
                    "memory_type": "semantic",
                    "timestamp": node.created_at,
                    "strength": node.confidence,
                    "metadata": node.properties
                })

        # Search procedural
        if "procedural" in types_to_search:
            skills = self.unified.procedural.search_skills(query=query)
            for skill in skills[:limit]:
                results.append({
                    "id": skill.id,
                    "content": skill.description or skill.name,
                    "memory_type": "procedural",
                    "timestamp": skill.created_at,
                    "strength": skill.success_count / max(1, skill.success_count + skill.failure_count),
                    "metadata": {"code": skill.code, "signature": skill.signature}
                })

        # Sort by strength/relevance
        results.sort(key=lambda x: x.get("strength", 0), reverse=True)

        return results[:limit]

    # =========================================================================
    # NEW API (differentiated memory access)
    # =========================================================================

    # --- Working Memory ---
    def add_to_working_memory(self, content: Any, ttl: int = None,
                             tags: List[str] = None) -> str:
        """Add item to transient working memory"""
        return self.unified.working.add(content, ttl=ttl, tags=tags)

    def get_working_memory(self) -> List[Dict]:
        """Get all active working memory items"""
        return self.unified.working.get_all_active()

    def clear_working_memory(self):
        """Clear working memory"""
        self.unified.working.clear()

    # --- Episodic Memory ---
    def store_episode(self, situation: str, action: str = "",
                     outcome: str = "", reward: float = 0.0,
                     emotional_valence: float = 0.0,
                     emotional_intensity: float = 0.0) -> str:
        """Store an episodic memory (experience)"""
        drive = tag_memory_with_drive(
            self.drives.get_state(),
            f"{situation} {action} {outcome}",
            "episodic"
        )

        episode_id = self.unified.episodic.store(
            situation=situation,
            action=action,
            outcome=outcome,
            reward=reward,
            emotional_valence=emotional_valence,
            emotional_intensity=emotional_intensity,
            drive_satisfied=drive
        )

        # Record outcome for drives
        self.drives.record_outcome(outcome, reward)

        # Increment experience and check development
        self.unified.increment_experience()

        return episode_id

    def retrieve_episodes(self, query: str = "", limit: int = 10,
                         min_reward: float = None, time_hours: float = None) -> List[EpisodicMemory]:
        """Retrieve episodic memories"""
        time_range = None
        if time_hours:
            now = time.time()
            time_range = (now - time_hours * 3600, now)

        return self.unified.episodic.retrieve(
            query=query,
            limit=limit,
            min_reward=min_reward,
            time_range=time_range
        )

    def get_recent_episodes(self, hours: float = 24) -> List[EpisodicMemory]:
        """Get recent episodic memories"""
        return self.unified.episodic.retrieve_recent(hours=hours)

    # --- Semantic Memory (Knowledge Graph) ---
    def add_concept(self, label: str, node_type: str = "concept",
                   properties: Dict = None, source_episode: str = None) -> str:
        """Add a concept to the knowledge graph"""
        return self.unified.semantic.add_node(
            label=label,
            node_type=node_type,
            properties=properties,
            source_episodes=[source_episode] if source_episode else None
        )

    def add_relationship(self, source_label: str, target_label: str,
                        relation_type: str, evidence_episode: str = None) -> Optional[str]:
        """Add a relationship between concepts"""
        source = self.unified.semantic.find_node_by_label(source_label)
        target = self.unified.semantic.find_node_by_label(target_label)

        if not source or not target:
            return None

        return self.unified.semantic.add_edge(
            source_id=source.id,
            target_id=target.id,
            relation_type=relation_type,
            evidence=[evidence_episode] if evidence_episode else None
        )

    def query_knowledge(self, query: str, node_type: str = None) -> List[SemanticNode]:
        """Search the knowledge graph"""
        return self.unified.semantic.search_nodes(query, node_type=node_type)

    def get_concept_relations(self, label: str) -> List[Tuple[SemanticNode, Any]]:
        """Get all relations for a concept"""
        node = self.unified.semantic.find_node_by_label(label)
        if not node:
            return []
        return self.unified.semantic.get_neighbors(node.id, direction="both")

    def infer_relations(self, label: str, relation_type: str) -> List[SemanticNode]:
        """Get inferred transitive relations"""
        node = self.unified.semantic.find_node_by_label(label)
        if not node:
            return []
        return self.unified.semantic.infer_transitive(node.id, relation_type)

    # --- Procedural Memory (Skills) ---
    def register_skill(self, name: str, code: str, description: str = "",
                      trigger_conditions: List[str] = None) -> str:
        """Register an executable skill"""
        self.drives.record_action("practice")
        return self.unified.procedural.register_skill(
            name=name,
            code=code,
            description=description,
            trigger_conditions=trigger_conditions
        )

    def execute_skill(self, name: str, inputs: Dict) -> Dict[str, Any]:
        """
        Execute a skill with auto-evolution on repeated failures.

        When a skill fails repeatedly:
        1. Failed inputs are stored as test cases
        2. After threshold failures with enough test cases, evolution is triggered
        3. Evolution generates code variants and selects the best one
        """
        result = self.unified.procedural.execute_skill(name, inputs)

        # Record for drives
        if result.get("success"):
            self.drives.record_action("succeed")
        else:
            self.drives.record_action("fail_and_learn")

            # Check if skill should evolve
            skill = self.unified.procedural.get_skill(name)
            if skill and skill.failure_count >= self.EVOLUTION_FAILURE_THRESHOLD:
                # Store failed input for evolution testing
                self._store_failed_test_case(name, inputs)

                # Trigger evolution if enough test cases
                test_cases = self._get_failed_test_cases(name)
                if len(test_cases) >= self.EVOLUTION_TEST_CASES_REQUIRED:
                    evolution_result = self.unified.procedural.evolve_skill(
                        name, test_cases, num_variants=3
                    )

                    if evolution_result.get("evolved"):
                        improvement = evolution_result.get("improvement", 0)
                        logger.info(
                            f"Skill '{name}' evolved with {improvement:.2%} improvement "
                            f"(v{skill.version} -> v{skill.version + 1})"
                        )

                        # Clear test cases after successful evolution
                        self._clear_failed_test_cases(name)

                        # Record evolution for drives (satisfies competence)
                        self.drives.record_action("evolve")

                        # Add evolution result to response
                        result["evolution"] = evolution_result

        return result

    def _store_failed_test_case(self, skill_name: str, inputs: Dict):
        """Store failed inputs as test cases for skill evolution"""
        if skill_name not in self._failed_test_cases:
            self._failed_test_cases[skill_name] = []

        # Avoid duplicates (simple check on string representation)
        inputs_str = json.dumps(inputs, sort_keys=True)
        existing = [json.dumps(tc, sort_keys=True) for tc in self._failed_test_cases[skill_name]]

        if inputs_str not in existing:
            self._failed_test_cases[skill_name].append(inputs)

            # Limit to last 10 test cases per skill
            if len(self._failed_test_cases[skill_name]) > 10:
                self._failed_test_cases[skill_name] = self._failed_test_cases[skill_name][-10:]

    def _get_failed_test_cases(self, skill_name: str) -> List[Dict]:
        """Get stored failed test cases for a skill"""
        return self._failed_test_cases.get(skill_name, [])

    def _clear_failed_test_cases(self, skill_name: str):
        """Clear failed test cases after successful evolution"""
        if skill_name in self._failed_test_cases:
            del self._failed_test_cases[skill_name]

    def evolve_skill_manually(self, skill_name: str, test_inputs: List[Dict] = None,
                              num_variants: int = 3) -> Dict[str, Any]:
        """
        Manually trigger skill evolution.

        Args:
            skill_name: Name of the skill to evolve
            test_inputs: Test inputs to use (if None, uses stored failed cases)
            num_variants: Number of variants to generate

        Returns:
            Evolution result dict
        """
        # Use provided inputs or stored failed cases
        if test_inputs is None:
            test_inputs = self._get_failed_test_cases(skill_name)

        if not test_inputs:
            return {
                "success": False,
                "error": f"No test inputs provided and no failed test cases stored for '{skill_name}'"
            }

        result = self.unified.procedural.evolve_skill(skill_name, test_inputs, num_variants)

        if result.get("evolved"):
            self._clear_failed_test_cases(skill_name)
            self.drives.record_action("evolve")

        return result

    def get_evolution_candidates(self, min_failures: int = 3) -> List[Dict[str, Any]]:
        """Get skills that are candidates for evolution"""
        skills = self.unified.procedural.get_evolution_candidates(min_failures)
        return [
            {
                "name": s.name,
                "failure_count": s.failure_count,
                "success_count": s.success_count,
                "version": s.version,
                "stored_test_cases": len(self._get_failed_test_cases(s.name))
            }
            for s in skills
        ]

    def get_skill(self, name: str) -> Optional[ProceduralSkill]:
        """Get a skill by name"""
        return self.unified.procedural.get_skill(name)

    def search_skills(self, query: str = None, trigger: str = None) -> List[ProceduralSkill]:
        """Search for skills"""
        return self.unified.procedural.search_skills(query=query, trigger=trigger)

    # --- Self Model ---
    def get_self_model(self) -> Dict[str, Any]:
        """Get the brain's self model"""
        model = self.unified.self_model.get()
        return {
            "identity": model.identity,
            "core_values": model.core_values,
            "core_goals": model.core_goals,
            "developmental_stage": model.developmental_stage,
            "experience_count": model.experience_count,
            "stage_progression": model.stage_progression,
            "emotional_state": model.emotional_state,
            "confidence_level": model.confidence_level,
            "strengths": model.strengths,
            "areas_for_improvement": model.areas_for_improvement
        }

    def update_self_model(self, **kwargs):
        """Update self model attributes"""
        self.unified.self_model.update(**kwargs)

    def record_performance(self, metric: str, score: float):
        """Record a performance metric for development tracking"""
        self.unified.self_model.record_performance(metric, score)

    def add_reflection(self, content: str, category: str = "general"):
        """Add a reflection to the self model"""
        self.unified.self_model.add_reflection(content, category)

    # --- Drives ---
    def get_drive_state(self) -> Dict[str, Dict[str, float]]:
        """Get current state of all drives"""
        return self.drives.get_state().get_all_drives()

    def get_dominant_drive(self) -> Tuple[str, float]:
        """Get the most urgent drive"""
        drive_type, urgency = self.drives.get_state().get_dominant_drive()
        return drive_type.value if drive_type else None, urgency

    def get_motivation_context(self) -> Dict[str, Any]:
        """Get full motivation context for decision making"""
        return self.drives.get_motivation_context()

    def record_drive_action(self, action: str) -> Dict[str, float]:
        """Record an action for drive satisfaction"""
        return self.drives.record_action(action)

    # --- Consolidation ---
    def consolidate_memories(self):
        """Run memory consolidation (decay/strengthen)"""
        self.unified.consolidate()

    # --- Stats ---
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        stats = self.unified.get_stats()
        stats["drives"] = self.drives.get_state().get_all_drives()
        stats["motivation"] = self.drives.get_motivation_context()
        return stats
