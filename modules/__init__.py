# Brain modules package
"""
Bolor Brain Cognitive Modules
=============================

This package contains the core cognitive architecture:

Configuration (config.py):
- Config: Central configuration dataclass
- get_config/set_config: Global config access
- validate_python_version: Version checking
- VALID_PROVIDERS: Supported LLM providers

LLM Bridge (llm_bridge.py):
- LLMBridge: Optional LLM integration with fallback
- LLMResponse: Structured response from LLM operations
- LLMBridgeError: Error type for bridge operations

Cognitive Genome (genome.py):
- CognitiveGenome: Evolvable parameters for all cognitive behavior
- Gene: Single evolvable parameter with fitness tracking
- GeneCategory: Categories of genes (attention, drives, etc.)
- DEFAULT_GENES: 60+ default gene definitions

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

Reasoning Engines (reasoning_engines/):
- SymbolicReasoner: Forward/backward chaining with rules and facts
- KnowledgeGraph: Graph-based knowledge with traversal and inference
- CaseBasedReasoner: Experience-based reasoning with 4R cycle
- HypothesisEngine: Hypothesis generation and testing
- AnalogicalReasoner: Cross-domain pattern transfer
- HybridReasoner: Orchestrates all reasoning approaches
"""

# Configuration
from .config import (
    Config,
    get_config,
    set_config,
    validate_python_version,
    VALID_PROVIDERS,
    VALID_LLM_USE_CASES,
)

# LLM Bridge
from .llm_bridge import (
    LLMBridge,
    LLMResponse,
    LLMBridgeError,
)

# Cognitive Genome
from .genome import (
    CognitiveGenome,
    Gene,
    GeneCategory,
    DEFAULT_GENES,
)

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

# Reasoning Engines (Phase 2)
from .reasoning_engines import (
    # Symbolic Reasoner
    SymbolicReasoner,
    Fact,
    FactType,
    Rule,
    ReasoningResult,
    # Knowledge Graph
    KnowledgeGraph,
    Node,
    Edge,
    PathResult,
    # Case-Based Reasoner
    CaseBasedReasoner,
    Case,
    CaseMatch,
    CaseReasoningResult,
    # Hypothesis Engine
    HypothesisEngine,
    Hypothesis,
    HypothesisTest,
    # Analogical Reasoner
    AnalogicalReasoner,
    Concept,
    Analogy,
    AnalogicalMapping,
    MappingType,
    # Hybrid Reasoner
    HybridReasoner,
    HybridReasoningResult,
    ReasoningApproach,
    ProblemType,
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
    # Configuration
    "Config",
    "get_config",
    "set_config",
    "validate_python_version",
    "VALID_PROVIDERS",
    "VALID_LLM_USE_CASES",
    # LLM Bridge
    "LLMBridge",
    "LLMResponse",
    "LLMBridgeError",
    # Cognitive Genome
    "CognitiveGenome",
    "Gene",
    "GeneCategory",
    "DEFAULT_GENES",
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
    # Reasoning Engines (Phase 2)
    "SymbolicReasoner",
    "Fact",
    "FactType",
    "Rule",
    "ReasoningResult",
    "KnowledgeGraph",
    "Node",
    "Edge",
    "PathResult",
    "CaseBasedReasoner",
    "Case",
    "CaseMatch",
    "CaseReasoningResult",
    "HypothesisEngine",
    "Hypothesis",
    "HypothesisTest",
    "AnalogicalReasoner",
    "Concept",
    "Analogy",
    "AnalogicalMapping",
    "MappingType",
    "HybridReasoner",
    "HybridReasoningResult",
    "ReasoningApproach",
    "ProblemType",
]
