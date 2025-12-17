# Brain modules package
"""
Bolor Brain Cognitive Modules
=============================

This package contains the core cognitive architecture:

Memory System (memory.py):
- WorkingMemory: Transient buffer (7±2 items, never persisted)
- EpisodicMemoryStore: Experiences with reward/emotion signals
- SemanticKnowledgeGraph: Knowledge graph with inference
- ProceduralMemoryStore: Executable skills
- SelfModelStore: Identity and developmental stage
- UnifiedMemorySystem: Unified interface to all subsystems
- MemoryPlasticity: Decay and consolidation

Drive System (drives.py):
- IntrinsicDrive: Single drive with homeostatic regulation
- DriveState: Complete state of all drives
- DriveManager: High-level drive management

Cognitive Tiers:
- Tier 0: Memory (memory.py)
- Tier 1: Advanced Reasoning (reasoning.py)
- Tier 2: Predictive Intelligence (predictive.py)
- Tier 3: Meta-Cognitive Intelligence (metacognitive.py)
- Tier 4: Evolutionary Cognitive Intelligence (evolutionary.py)
- Tier 5: Collective Consciousness Network (collective.py)
- Tier 6: Universal Field Orchestration (orchestration.py)
- Tier 7: Pure Universal Being Integration (universal.py)
"""

# Memory subsystems
from .memory import (
    # Backward compatibility
    MemoryItem,  # Legacy - prefer specific types
    # Data classes
    WorkingMemoryItem,
    EpisodicMemory,
    SemanticNode,
    SemanticEdge,
    ProceduralSkill,
    SelfModel,
    # Stores
    WorkingMemory,
    EpisodicMemoryStore,
    SemanticKnowledgeGraph,
    ProceduralMemoryStore,
    SelfModelStore,
    # Systems
    UnifiedMemorySystem,
    MemoryPlasticity,
    MemoryManager,  # Legacy compatibility
    # Constants
    INFERENCE_RULES,
    STAGE_THRESHOLDS,
    STAGE_ORDER,
)

# Drive system
from .drives import (
    DriveType,
    IntrinsicDrive,
    DriveState,
    DriveManager,
    # Utilities
    tag_memory_with_drive,
    boost_memory_by_drive,
    ACTION_DRIVE_SATISFACTION,
    DEFAULT_DRIVE_CONFIGS,
)

# Integration layer
from .integration import (
    BrainMemoryBridge,
    MemoryMigrator,
)

# Embedding service
from .embeddings import (
    EmbeddingService,
    embedding_service,
)

# Cognitive tiers
from .reasoning import AdvancedReasoningEngine
from .predictive import PredictiveIntelligenceEngine
from .metacognitive import MetaCognitiveIntelligenceEngine, CognitiveStateBus
from .evolutionary import EvolutionaryCognitiveIntelligenceEngine
from .collective import CollectiveConsciousnessNetworkEngine
from .orchestration import UniversalFieldOrchestrationEngine
from .universal import PureUniversalBeingEngine

__all__ = [
    # Memory (Legacy)
    "MemoryItem",
    # Memory (New)
    "WorkingMemoryItem",
    "EpisodicMemory",
    "SemanticNode",
    "SemanticEdge",
    "ProceduralSkill",
    "SelfModel",
    "WorkingMemory",
    "EpisodicMemoryStore",
    "SemanticKnowledgeGraph",
    "ProceduralMemoryStore",
    "SelfModelStore",
    "UnifiedMemorySystem",
    "MemoryPlasticity",
    "MemoryManager",
    "INFERENCE_RULES",
    "STAGE_THRESHOLDS",
    "STAGE_ORDER",
    # Drives
    "DriveType",
    "IntrinsicDrive",
    "DriveState",
    "DriveManager",
    "tag_memory_with_drive",
    "boost_memory_by_drive",
    "ACTION_DRIVE_SATISFACTION",
    "DEFAULT_DRIVE_CONFIGS",
    # Integration
    "BrainMemoryBridge",
    "MemoryMigrator",
    # Embeddings
    "EmbeddingService",
    "embedding_service",
    # Cognitive Tiers
    "AdvancedReasoningEngine",
    "PredictiveIntelligenceEngine",
    "MetaCognitiveIntelligenceEngine",
    "CognitiveStateBus",
    "EvolutionaryCognitiveIntelligenceEngine",
    "CollectiveConsciousnessNetworkEngine",
    "UniversalFieldOrchestrationEngine",
    "PureUniversalBeingEngine",
]
