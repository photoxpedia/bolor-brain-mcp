"""
Bolor Brain Cognitive Genome System
====================================

Provides evolvable parameters that control ALL cognitive behavior.
Instead of hardcoded magic numbers, all parameters come from this genome.

Evolution triggers:
- Stagnation: When stuck, use larger mutations (0.15 magnitude)
- Breakthrough: When succeeding, use smaller refinements (0.05 magnitude)

Gene Categories:
- ATTENTION: What draws focus
- DRIVES: Motivational baselines and sensitivities
- REASONING: Strategy weights and thresholds
- ACTION: When and how to act
- LEARNING: Memory and pattern acquisition
- SIMULATION: World model parameters
- CREATIVITY: Novel solution generation
- SOCIAL: Interpersonal interaction
"""

import json
import logging
import random
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class GeneCategory(Enum):
    """Categories of cognitive genes."""
    ATTENTION = "attention"
    DRIVES = "drives"
    REASONING = "reasoning"
    ACTION = "action"
    LEARNING = "learning"
    SIMULATION = "simulation"
    CREATIVITY = "creativity"
    SOCIAL = "social"


@dataclass
class Gene:
    """
    A single evolvable gene with bounded value and fitness tracking.

    Attributes:
        name: Unique identifier for this gene
        value: Current value (within min_value to max_value)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        category: Which category this gene belongs to
        description: Human-readable description of what this gene controls
        fitness: How well this gene's current value is performing (0-1)
    """
    name: str
    value: float
    min_value: float
    max_value: float
    category: GeneCategory
    description: str
    fitness: float = 0.5

    def mutate(self, magnitude: float = 0.1) -> float:
        """
        Mutate the gene value within bounds.

        Args:
            magnitude: How much to mutate (0-1, scaled by gene range)

        Returns:
            The new value after mutation
        """
        gene_range = self.max_value - self.min_value
        max_change = gene_range * magnitude

        # Random change between -max_change and +max_change
        change = random.uniform(-max_change, max_change)

        new_value = self.value + change

        # Clamp to bounds
        self.value = max(self.min_value, min(self.max_value, new_value))

        return self.value

    def to_dict(self) -> Dict[str, Any]:
        """Convert gene to dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "category": self.category.value,
            "description": self.description,
            "fitness": self.fitness
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Gene":
        """Create gene from dictionary."""
        return cls(
            name=data["name"],
            value=data["value"],
            min_value=data["min_value"],
            max_value=data["max_value"],
            category=GeneCategory(data["category"]),
            description=data["description"],
            fitness=data.get("fitness", 0.5)
        )


# =============================================================================
# DEFAULT GENES (60+ genes across 8 categories)
# =============================================================================

DEFAULT_GENES: List[Dict[str, Any]] = [
    # =========================================================================
    # ATTENTION GENES (6 genes)
    # =========================================================================
    {
        "name": "incomplete_pattern_weight",
        "value": 0.7,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "How much incomplete patterns attract attention"
    },
    {
        "name": "knowledge_gap_weight",
        "value": 0.6,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "How much knowledge gaps attract attention"
    },
    {
        "name": "exploration_rate",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "Tendency to explore vs exploit known patterns"
    },
    {
        "name": "focus_duration",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "How long attention stays on a single topic"
    },
    {
        "name": "novelty_attention_boost",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "Extra attention given to novel stimuli"
    },
    {
        "name": "urgency_attention_weight",
        "value": 0.8,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "How much urgent matters capture attention"
    },
    {
        "name": "distraction_resistance",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "Resistance to switching attention away from current focus"
    },
    {
        "name": "parallel_attention_capacity",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "attention",
        "description": "Ability to attend to multiple things simultaneously"
    },

    # =========================================================================
    # DRIVES GENES (11 genes)
    # =========================================================================
    {
        "name": "curiosity_baseline",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "Baseline curiosity level"
    },
    {
        "name": "curiosity_sensitivity",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "How easily curiosity is triggered"
    },
    {
        "name": "competence_baseline",
        "value": 0.35,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "Baseline competence drive"
    },
    {
        "name": "competence_sensitivity",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "How easily competence drive responds"
    },
    {
        "name": "novelty_baseline",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "Baseline novelty seeking"
    },
    {
        "name": "novelty_sensitivity",
        "value": 0.6,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "How easily novelty drive responds"
    },
    {
        "name": "connection_baseline",
        "value": 0.25,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "Baseline social connection drive"
    },
    {
        "name": "stability_baseline",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "Baseline stability/predictability drive"
    },
    {
        "name": "drive_decay_rate",
        "value": 0.01,
        "min_value": 0.001,
        "max_value": 0.1,
        "category": "drives",
        "description": "How fast drives increase when unsatisfied"
    },
    {
        "name": "drive_satisfaction_boost",
        "value": 0.2,
        "min_value": 0.05,
        "max_value": 0.5,
        "category": "drives",
        "description": "Boost when a drive is satisfied"
    },
    {
        "name": "drive_frustration_penalty",
        "value": 0.15,
        "min_value": 0.0,
        "max_value": 0.5,
        "category": "drives",
        "description": "Penalty when a drive is frustrated"
    },
    {
        "name": "connection_sensitivity",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "How easily connection drive responds"
    },
    {
        "name": "stability_sensitivity",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "drives",
        "description": "How easily stability drive responds"
    },

    # =========================================================================
    # REASONING GENES (11 genes)
    # =========================================================================
    {
        "name": "analytical_weight",
        "value": 0.6,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Weight for analytical reasoning strategy"
    },
    {
        "name": "creative_weight",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Weight for creative reasoning strategy"
    },
    {
        "name": "critical_weight",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Weight for critical reasoning strategy"
    },
    {
        "name": "systems_weight",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Weight for systems thinking strategy"
    },
    {
        "name": "intuitive_weight",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Weight for intuitive reasoning strategy"
    },
    {
        "name": "ethical_weight",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Weight for ethical reasoning strategy"
    },
    {
        "name": "max_reasoning_steps",
        "value": 10.0,
        "min_value": 1.0,
        "max_value": 50.0,
        "category": "reasoning",
        "description": "Maximum steps in reasoning chain"
    },
    {
        "name": "min_confidence_threshold",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Minimum confidence to accept a conclusion"
    },
    {
        "name": "case_similarity_threshold",
        "value": 0.7,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "Similarity threshold for case-based reasoning"
    },
    {
        "name": "hypothesis_generation_breadth",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "How many hypotheses to generate"
    },
    {
        "name": "analogy_abstraction_depth",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "reasoning",
        "description": "How abstract analogies can be"
    },

    # =========================================================================
    # ACTION GENES (8 genes)
    # =========================================================================
    {
        "name": "investigate_threshold",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "Threshold to start investigation"
    },
    {
        "name": "explore_threshold",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "Threshold to start exploration"
    },
    {
        "name": "urgency_threshold",
        "value": 0.7,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "When urgency triggers immediate action"
    },
    {
        "name": "prefer_investigation",
        "value": 0.6,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "Preference for investigation over action"
    },
    {
        "name": "action_confidence_required",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "Confidence needed before taking action"
    },
    {
        "name": "risk_tolerance",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "Willingness to take risky actions"
    },
    {
        "name": "persistence_threshold",
        "value": 0.6,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "How long to persist before giving up"
    },
    {
        "name": "action_speed",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "action",
        "description": "Speed vs deliberation tradeoff"
    },

    # =========================================================================
    # LEARNING GENES (14 genes)
    # =========================================================================
    {
        "name": "memory_strength_initial",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Initial strength of new memories"
    },
    {
        "name": "memory_decay_rate",
        "value": 0.01,
        "min_value": 0.001,
        "max_value": 0.1,
        "category": "learning",
        "description": "How fast memories decay"
    },
    {
        "name": "association_strength_increment",
        "value": 0.1,
        "min_value": 0.01,
        "max_value": 0.5,
        "category": "learning",
        "description": "How much associations strengthen per use"
    },
    {
        "name": "trust_new_rules",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Trust given to newly learned rules"
    },
    {
        "name": "confirmation_threshold",
        "value": 0.7,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Confirmations needed to promote pattern"
    },
    {
        "name": "initial_pattern_confidence",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Starting confidence for new patterns"
    },
    {
        "name": "curriculum_pattern_confidence",
        "value": 0.8,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Confidence for curriculum-learned patterns"
    },
    {
        "name": "min_pattern_success_rate",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Minimum success rate before pattern is demoted"
    },
    {
        "name": "prune_after_uses",
        "value": 10.0,
        "min_value": 1.0,
        "max_value": 100.0,
        "category": "learning",
        "description": "Uses before evaluating pattern for pruning"
    },
    {
        "name": "promotion_threshold",
        "value": 0.8,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Success rate to promote pattern to proven"
    },
    {
        "name": "min_observations_for_causation",
        "value": 3.0,
        "min_value": 1.0,
        "max_value": 20.0,
        "category": "learning",
        "description": "Observations needed to infer causation"
    },
    {
        "name": "base_learned_confidence",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Initial confidence for learned causations"
    },
    {
        "name": "reinforcement_rate",
        "value": 0.1,
        "min_value": 0.01,
        "max_value": 0.5,
        "category": "learning",
        "description": "How much confirmation strengthens belief"
    },
    {
        "name": "min_causation_strength",
        "value": 0.2,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "learning",
        "description": "Below this, causation is removed"
    },

    # =========================================================================
    # SIMULATION GENES (8 genes)
    # =========================================================================
    {
        "name": "default_increase_magnitude",
        "value": 0.1,
        "min_value": 0.01,
        "max_value": 0.5,
        "category": "simulation",
        "description": "Default magnitude for increases in simulation"
    },
    {
        "name": "default_decrease_magnitude",
        "value": 0.1,
        "min_value": 0.01,
        "max_value": 0.5,
        "category": "simulation",
        "description": "Default magnitude for decreases in simulation"
    },
    {
        "name": "equilibrium_threshold",
        "value": 0.001,
        "min_value": 0.0001,
        "max_value": 0.1,
        "category": "simulation",
        "description": "Change below which system is at equilibrium"
    },
    {
        "name": "unknown_link_penalty",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "simulation",
        "description": "Penalty for unknown causal links"
    },
    {
        "name": "simulation_max_steps",
        "value": 100.0,
        "min_value": 10.0,
        "max_value": 1000.0,
        "category": "simulation",
        "description": "Maximum steps in a simulation"
    },
    {
        "name": "counterfactual_depth",
        "value": 3.0,
        "min_value": 1.0,
        "max_value": 10.0,
        "category": "simulation",
        "description": "Depth of counterfactual reasoning"
    },
    {
        "name": "temporal_discount",
        "value": 0.9,
        "min_value": 0.5,
        "max_value": 1.0,
        "category": "simulation",
        "description": "Discount factor for future outcomes"
    },
    {
        "name": "simulation_precision",
        "value": 0.5,
        "min_value": 0.1,
        "max_value": 1.0,
        "category": "simulation",
        "description": "Precision vs speed tradeoff in simulation"
    },

    # =========================================================================
    # CREATIVITY GENES (8 genes)
    # =========================================================================
    {
        "name": "novelty_generation_rate",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "creativity",
        "description": "Rate of generating novel ideas"
    },
    {
        "name": "combination_breadth",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "creativity",
        "description": "How broadly to combine concepts"
    },
    {
        "name": "abstraction_tendency",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "creativity",
        "description": "Tendency to abstract vs concretize"
    },
    {
        "name": "constraint_relaxation_rate",
        "value": 0.3,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "creativity",
        "description": "How easily constraints are relaxed"
    },
    {
        "name": "divergent_exploration_depth",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "creativity",
        "description": "Depth of divergent exploration"
    },
    {
        "name": "blending_threshold",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "creativity",
        "description": "Threshold for concept blending"
    },
    {
        "name": "random_injection_rate",
        "value": 0.1,
        "min_value": 0.0,
        "max_value": 0.5,
        "category": "creativity",
        "description": "Rate of random element injection"
    },
    {
        "name": "analogy_distance_preference",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "creativity",
        "description": "Preference for near vs far analogies"
    },

    # =========================================================================
    # SOCIAL GENES (6 genes)
    # =========================================================================
    {
        "name": "empathy_weight",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "social",
        "description": "Weight given to empathetic considerations"
    },
    {
        "name": "cooperation_tendency",
        "value": 0.6,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "social",
        "description": "Tendency to cooperate vs compete"
    },
    {
        "name": "trust_initial",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "social",
        "description": "Initial trust for new entities"
    },
    {
        "name": "trust_update_rate",
        "value": 0.1,
        "min_value": 0.01,
        "max_value": 0.5,
        "category": "social",
        "description": "How quickly trust is updated"
    },
    {
        "name": "reciprocity_expectation",
        "value": 0.5,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "social",
        "description": "Expectation of reciprocal behavior"
    },
    {
        "name": "social_conformity",
        "value": 0.4,
        "min_value": 0.0,
        "max_value": 1.0,
        "category": "social",
        "description": "Tendency to conform to social norms"
    },
]


class CognitiveGenome:
    """
    Container for all cognitive genes with evolution capabilities.

    The genome controls ALL cognitive parameters through learnable genes
    instead of hardcoded magic numbers. Evolution allows the system to
    adapt to its environment over time.
    """

    VERSION = "1.0.0"

    # Evolution magnitudes for different triggers
    STAGNATION_MAGNITUDE = 0.15
    BREAKTHROUGH_MAGNITUDE = 0.05

    # Fitness threshold for preservation
    FIT_GENE_THRESHOLD = 0.7

    def __init__(self, genes: Optional[Dict[str, Gene]] = None):
        """
        Initialize the cognitive genome.

        Args:
            genes: Optional dict of Gene objects. If None, uses DEFAULT_GENES.
        """
        self._lock = threading.RLock()
        if genes is not None:
            self.genes = genes
        else:
            self.genes = self._create_default_genes()

    def _create_default_genes(self) -> Dict[str, Gene]:
        """Create genes from DEFAULT_GENES list."""
        genes = {}
        for gene_def in DEFAULT_GENES:
            gene = Gene(
                name=gene_def["name"],
                value=gene_def["value"],
                min_value=gene_def["min_value"],
                max_value=gene_def["max_value"],
                category=GeneCategory(gene_def["category"]),
                description=gene_def["description"],
                fitness=0.5
            )
            genes[gene.name] = gene
        return genes

    def get(self, name: str, default: Optional[float] = None) -> Optional[float]:
        """
        Get a gene's current value.

        Args:
            name: Gene name
            default: Value to return if gene doesn't exist

        Returns:
            Gene value or default
        """
        gene = self.genes.get(name)
        if gene is None:
            return default
        return gene.value

    def get_gene(self, name: str) -> Optional[Gene]:
        """
        Get the Gene object itself.

        Args:
            name: Gene name

        Returns:
            Gene object or None
        """
        return self.genes.get(name)

    def set(self, name: str, value: float) -> None:
        """
        Set a gene's value (clamped to bounds).

        Args:
            name: Gene name
            value: New value

        Raises:
            KeyError: If gene doesn't exist
        """
        with self._lock:
            gene = self.genes.get(name)
            if gene is None:
                raise KeyError(f"Gene '{name}' does not exist")

            # Clamp to bounds
            gene.value = max(gene.min_value, min(gene.max_value, value))

    def mutate(self, name: str, magnitude: float = 0.1) -> float:
        """
        Mutate a specific gene.

        Args:
            name: Gene name
            magnitude: Mutation magnitude (0-1)

        Returns:
            New gene value

        Raises:
            KeyError: If gene doesn't exist
        """
        with self._lock:
            gene = self.genes.get(name)
            if gene is None:
                raise KeyError(f"Gene '{name}' does not exist")

            return gene.mutate(magnitude)

    def get_category(self, category: GeneCategory) -> List[Gene]:
        """
        Get all genes in a category.

        Args:
            category: GeneCategory to filter by

        Returns:
            List of Gene objects in that category
        """
        return [gene for gene in self.genes.values() if gene.category == category]

    def evolve(
        self,
        trigger: str = "stagnation",
        mutation_rate: float = 0.1,
        preserve_fit: bool = True
    ) -> Dict[str, Any]:
        """
        Evolve the genome based on trigger type.

        Args:
            trigger: "stagnation" (bigger mutations) or "breakthrough" (smaller)
            mutation_rate: Fraction of genes to mutate (0-1)
            preserve_fit: If True, don't mutate genes with fitness > 0.7

        Returns:
            Report of mutations made

        Raises:
            ValueError: If mutation_rate is not between 0 and 1
        """
        # Input validation
        if not 0.0 <= mutation_rate <= 1.0:
            raise ValueError(f"mutation_rate must be between 0 and 1, got {mutation_rate}")

        with self._lock:
            # Determine mutation magnitude based on trigger
            if trigger == "stagnation":
                magnitude = self.STAGNATION_MAGNITUDE
            elif trigger == "breakthrough":
                magnitude = self.BREAKTHROUGH_MAGNITUDE
            else:
                magnitude = 0.1

            mutations = []
            genes_mutated = 0

            # Get genes eligible for mutation
            eligible_genes = list(self.genes.values())
            if preserve_fit:
                eligible_genes = [g for g in eligible_genes if g.fitness <= self.FIT_GENE_THRESHOLD]

            # Edge case: no eligible genes
            if not eligible_genes:
                logger.warning("No eligible genes for evolution (all genes fit)")
                return {
                    "trigger": trigger,
                    "magnitude": magnitude,
                    "mutation_rate": mutation_rate,
                    "preserve_fit": preserve_fit,
                    "genes_mutated": 0,
                    "mutations": []
                }

            # Randomly select genes to mutate based on mutation_rate
            num_to_mutate = max(1, int(len(eligible_genes) * mutation_rate))
            genes_to_mutate = random.sample(eligible_genes, min(num_to_mutate, len(eligible_genes)))

            for gene in genes_to_mutate:
                old_value = gene.value
                new_value = gene.mutate(magnitude)

                if abs(new_value - old_value) > 0.0001:
                    mutations.append({
                        "gene": gene.name,
                        "old_value": old_value,
                        "new_value": new_value,
                        "category": gene.category.value
                    })
                    genes_mutated += 1

            logger.info(f"Evolved genome: trigger={trigger}, mutations={genes_mutated}")

            return {
                "trigger": trigger,
                "magnitude": magnitude,
                "mutation_rate": mutation_rate,
                "preserve_fit": preserve_fit,
                "genes_mutated": genes_mutated,
                "mutations": mutations
            }

    def update_fitness(self, name: str, outcome: float, learning_rate: float = 0.1) -> float:
        """
        Update a gene's fitness based on outcome.

        Args:
            name: Gene name
            outcome: Outcome value (-1 to 1, positive = good)
            learning_rate: How much to adjust fitness

        Returns:
            New fitness value

        Raises:
            KeyError: If gene doesn't exist
            ValueError: If outcome or learning_rate is invalid
        """
        # Input validation
        if not -1.0 <= outcome <= 1.0:
            raise ValueError(f"outcome must be between -1 and 1, got {outcome}")
        if learning_rate <= 0:
            raise ValueError(f"learning_rate must be positive, got {learning_rate}")

        with self._lock:
            gene = self.genes.get(name)
            if gene is None:
                raise KeyError(f"Gene '{name}' does not exist")

            # Adjust fitness based on outcome
            adjustment = outcome * learning_rate
            gene.fitness = max(0.0, min(1.0, gene.fitness + adjustment))

            return gene.fitness

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert genome to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "version": self.VERSION,
            "genes": {name: gene.to_dict() for name, gene in self.genes.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CognitiveGenome":
        """
        Create genome from dictionary.

        Args:
            data: Dictionary from to_dict()

        Returns:
            CognitiveGenome instance
        """
        genes = {}
        for name, gene_data in data.get("genes", {}).items():
            genes[name] = Gene.from_dict(gene_data)

        return cls(genes=genes)

    def save(self, path: Union[str, Path]) -> None:
        """
        Save genome to JSON file.

        Args:
            path: File path to save to
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

        logger.info(f"Saved genome to {path}")

    @classmethod
    def load(cls, path: Union[str, Path]) -> "CognitiveGenome":
        """
        Load genome from JSON file.

        Args:
            path: File path to load from

        Returns:
            CognitiveGenome instance (default if file doesn't exist)

        Raises:
            PermissionError: If permission is denied to read the file
        """
        path = Path(path)

        if not path.exists():
            logger.info(f"Genome file {path} not found, using defaults")
            return cls()

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            genome = cls.from_dict(data)
            logger.info(f"Loaded genome from {path}")
            return genome

        except json.JSONDecodeError as e:
            logger.error(f"Corrupted genome file at {path}: {e}. Using defaults.")
            return cls()
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid genome structure in {path}: {e}. Using defaults.")
            return cls()
        except PermissionError as e:
            logger.error(f"Permission denied reading {path}: {e}")
            raise
        except FileNotFoundError:
            logger.info(f"No genome file at {path}, using defaults")
            return cls()
        except Exception as e:
            logger.error(f"Unexpected error loading genome: {e}", exc_info=True)
            raise

    def __len__(self) -> int:
        """Return number of genes."""
        return len(self.genes)

    def __repr__(self) -> str:
        """String representation."""
        return f"CognitiveGenome(genes={len(self.genes)}, version={self.VERSION})"
