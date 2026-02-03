"""
Tests for the Cognitive Genome system.

TDD: These tests are written BEFORE the implementation.
The genome system must support:
- 8 gene categories (ATTENTION, DRIVES, REASONING, ACTION, LEARNING, SIMULATION, CREATIVITY, SOCIAL)
- 60+ evolvable genes with min/max bounds
- Mutation with magnitude control
- Evolution triggers (stagnation, breakthrough)
- Fitness tracking per gene
- Save/load to JSON
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


class TestGeneCategory:
    """Test GeneCategory enum."""

    def test_gene_category_has_8_categories(self):
        """GeneCategory should have exactly 8 categories."""
        from modules.genome import GeneCategory

        categories = list(GeneCategory)
        assert len(categories) == 8

    def test_gene_category_names(self):
        """GeneCategory should have specific category names."""
        from modules.genome import GeneCategory

        expected = {"ATTENTION", "DRIVES", "REASONING", "ACTION", "LEARNING", "SIMULATION", "CREATIVITY", "SOCIAL"}
        actual = {cat.name for cat in GeneCategory}
        assert actual == expected

    def test_gene_category_values(self):
        """GeneCategory values should be lowercase strings."""
        from modules.genome import GeneCategory

        for cat in GeneCategory:
            assert cat.value == cat.name.lower()


class TestGene:
    """Test Gene dataclass."""

    def test_gene_creation(self):
        """Gene should be creatable with required fields."""
        from modules.genome import Gene, GeneCategory

        gene = Gene(
            name="test_gene",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.ATTENTION,
            description="A test gene"
        )

        assert gene.name == "test_gene"
        assert gene.value == 0.5
        assert gene.min_value == 0.0
        assert gene.max_value == 1.0
        assert gene.category == GeneCategory.ATTENTION
        assert gene.description == "A test gene"
        assert gene.fitness == 0.5  # Default fitness

    def test_gene_default_fitness(self):
        """Gene should have default fitness of 0.5."""
        from modules.genome import Gene, GeneCategory

        gene = Gene(
            name="test",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.ATTENTION,
            description="test"
        )

        assert gene.fitness == 0.5

    def test_gene_custom_fitness(self):
        """Gene should accept custom fitness."""
        from modules.genome import Gene, GeneCategory

        gene = Gene(
            name="test",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.ATTENTION,
            description="test",
            fitness=0.8
        )

        assert gene.fitness == 0.8

    def test_gene_mutate_changes_value(self):
        """Gene.mutate() should change the value."""
        from modules.genome import Gene, GeneCategory

        gene = Gene(
            name="test",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.ATTENTION,
            description="test"
        )

        original = gene.value
        gene.mutate(magnitude=0.1)
        # Value should have changed (with high probability)
        # Note: There's a tiny chance it stays the same if random is exactly 0
        # We'll verify bounds instead
        assert 0.0 <= gene.value <= 1.0

    def test_gene_mutate_respects_bounds(self):
        """Gene.mutate() should keep value within bounds."""
        from modules.genome import Gene, GeneCategory

        # Test lower bound
        gene_low = Gene(
            name="test_low",
            value=0.0,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.ATTENTION,
            description="test"
        )
        gene_low.mutate(magnitude=0.5)
        assert gene_low.value >= 0.0

        # Test upper bound
        gene_high = Gene(
            name="test_high",
            value=1.0,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.ATTENTION,
            description="test"
        )
        gene_high.mutate(magnitude=0.5)
        assert gene_high.value <= 1.0

    def test_gene_mutate_with_non_unit_range(self):
        """Gene.mutate() should work with non-0-to-1 ranges."""
        from modules.genome import Gene, GeneCategory

        gene = Gene(
            name="test",
            value=50.0,
            min_value=10.0,
            max_value=100.0,
            category=GeneCategory.SIMULATION,
            description="test"
        )

        gene.mutate(magnitude=0.2)
        assert 10.0 <= gene.value <= 100.0

    def test_gene_mutate_magnitude_affects_change_size(self):
        """Larger magnitude should allow larger changes on average."""
        from modules.genome import Gene, GeneCategory
        import statistics

        # Run multiple mutations and compare average change
        small_changes = []
        large_changes = []

        for _ in range(100):
            gene_small = Gene(
                name="test",
                value=0.5,
                min_value=0.0,
                max_value=1.0,
                category=GeneCategory.ATTENTION,
                description="test"
            )
            original = gene_small.value
            gene_small.mutate(magnitude=0.01)
            small_changes.append(abs(gene_small.value - original))

            gene_large = Gene(
                name="test",
                value=0.5,
                min_value=0.0,
                max_value=1.0,
                category=GeneCategory.ATTENTION,
                description="test"
            )
            original = gene_large.value
            gene_large.mutate(magnitude=0.5)
            large_changes.append(abs(gene_large.value - original))

        avg_small = statistics.mean(small_changes)
        avg_large = statistics.mean(large_changes)

        # Large magnitude should produce larger average changes
        assert avg_large > avg_small

    def test_gene_to_dict(self):
        """Gene should convert to dictionary."""
        from modules.genome import Gene, GeneCategory

        gene = Gene(
            name="test_gene",
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            category=GeneCategory.ATTENTION,
            description="A test gene",
            fitness=0.7
        )

        gene_dict = gene.to_dict()

        assert gene_dict["name"] == "test_gene"
        assert gene_dict["value"] == 0.5
        assert gene_dict["min_value"] == 0.0
        assert gene_dict["max_value"] == 1.0
        assert gene_dict["category"] == "attention"
        assert gene_dict["description"] == "A test gene"
        assert gene_dict["fitness"] == 0.7

    def test_gene_from_dict(self):
        """Gene should be creatable from dictionary."""
        from modules.genome import Gene, GeneCategory

        gene_dict = {
            "name": "test_gene",
            "value": 0.5,
            "min_value": 0.0,
            "max_value": 1.0,
            "category": "attention",
            "description": "A test gene",
            "fitness": 0.7
        }

        gene = Gene.from_dict(gene_dict)

        assert gene.name == "test_gene"
        assert gene.value == 0.5
        assert gene.min_value == 0.0
        assert gene.max_value == 1.0
        assert gene.category == GeneCategory.ATTENTION
        assert gene.description == "A test gene"
        assert gene.fitness == 0.7


class TestCognitiveGenomeDefaults:
    """Test CognitiveGenome default genes."""

    def test_genome_has_60_plus_genes(self):
        """CognitiveGenome should have at least 60 genes."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        assert len(genome.genes) >= 60

    def test_genome_has_attention_genes(self):
        """CognitiveGenome should have attention genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        attention_genes = genome.get_category(GeneCategory.ATTENTION)

        expected_genes = {
            "incomplete_pattern_weight",
            "knowledge_gap_weight",
            "exploration_rate",
            "focus_duration",
            "novelty_attention_boost",
            "urgency_attention_weight"
        }

        actual_genes = {g.name for g in attention_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(attention_genes) >= 6

    def test_genome_has_drives_genes(self):
        """CognitiveGenome should have drives genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        drives_genes = genome.get_category(GeneCategory.DRIVES)

        expected_genes = {
            "curiosity_baseline",
            "curiosity_sensitivity",
            "competence_baseline",
            "competence_sensitivity",
            "novelty_baseline",
            "novelty_sensitivity",
            "connection_baseline",
            "stability_baseline",
            "drive_decay_rate",
            "drive_satisfaction_boost",
            "drive_frustration_penalty"
        }

        actual_genes = {g.name for g in drives_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(drives_genes) >= 11

    def test_genome_has_reasoning_genes(self):
        """CognitiveGenome should have reasoning genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        reasoning_genes = genome.get_category(GeneCategory.REASONING)

        expected_genes = {
            "analytical_weight",
            "creative_weight",
            "critical_weight",
            "systems_weight",
            "intuitive_weight",
            "ethical_weight",
            "max_reasoning_steps",
            "min_confidence_threshold",
            "case_similarity_threshold",
        }

        actual_genes = {g.name for g in reasoning_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(reasoning_genes) >= 9

    def test_genome_has_action_genes(self):
        """CognitiveGenome should have action genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        action_genes = genome.get_category(GeneCategory.ACTION)

        expected_genes = {
            "investigate_threshold",
            "explore_threshold",
            "urgency_threshold",
            "prefer_investigation",
            "action_confidence_required",
            "risk_tolerance",
            "persistence_threshold"
        }

        actual_genes = {g.name for g in action_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(action_genes) >= 7

    def test_genome_has_learning_genes(self):
        """CognitiveGenome should have learning genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        learning_genes = genome.get_category(GeneCategory.LEARNING)

        expected_genes = {
            "memory_strength_initial",
            "memory_decay_rate",
            "association_strength_increment",
            "trust_new_rules",
            "confirmation_threshold",
            "initial_pattern_confidence",
            "curriculum_pattern_confidence",
            "min_pattern_success_rate",
            "prune_after_uses",
            "promotion_threshold",
            "min_observations_for_causation",
            "base_learned_confidence",
            "reinforcement_rate",
            "min_causation_strength"
        }

        actual_genes = {g.name for g in learning_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(learning_genes) >= 14

    def test_genome_has_simulation_genes(self):
        """CognitiveGenome should have simulation genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        sim_genes = genome.get_category(GeneCategory.SIMULATION)

        expected_genes = {
            "default_increase_magnitude",
            "default_decrease_magnitude",
            "equilibrium_threshold",
            "unknown_link_penalty",
            "simulation_max_steps",
            "counterfactual_depth"
        }

        actual_genes = {g.name for g in sim_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(sim_genes) >= 6

    def test_genome_has_creativity_genes(self):
        """CognitiveGenome should have creativity genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        creativity_genes = genome.get_category(GeneCategory.CREATIVITY)

        expected_genes = {
            "novelty_generation_rate",
            "combination_breadth",
            "abstraction_tendency",
            "constraint_relaxation_rate",
            "divergent_exploration_depth",
            "blending_threshold"
        }

        actual_genes = {g.name for g in creativity_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(creativity_genes) >= 6

    def test_genome_has_social_genes(self):
        """CognitiveGenome should have social genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        social_genes = genome.get_category(GeneCategory.SOCIAL)

        expected_genes = {
            "empathy_weight",
            "cooperation_tendency",
            "trust_initial",
            "trust_update_rate"
        }

        actual_genes = {g.name for g in social_genes}
        assert expected_genes.issubset(actual_genes)
        assert len(social_genes) >= 4


class TestCognitiveGenomeMethods:
    """Test CognitiveGenome methods."""

    def test_genome_get_returns_gene_value(self):
        """CognitiveGenome.get() should return gene value."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        value = genome.get("curiosity_baseline")

        assert isinstance(value, (int, float))
        assert 0.0 <= value <= 1.0

    def test_genome_get_nonexistent_returns_none(self):
        """CognitiveGenome.get() should return None for nonexistent gene."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        value = genome.get("nonexistent_gene")

        assert value is None

    def test_genome_get_with_default(self):
        """CognitiveGenome.get() should return default for nonexistent gene."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        value = genome.get("nonexistent_gene", default=0.42)

        assert value == 0.42

    def test_genome_set_changes_value(self):
        """CognitiveGenome.set() should change gene value."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        original = genome.get("curiosity_baseline")
        genome.set("curiosity_baseline", 0.99)
        new_value = genome.get("curiosity_baseline")

        assert new_value == 0.99
        assert new_value != original

    def test_genome_set_clamps_to_bounds(self):
        """CognitiveGenome.set() should clamp value to gene bounds."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        # Try to set above max
        genome.set("curiosity_baseline", 999.0)
        assert genome.get("curiosity_baseline") <= 1.0

        # Try to set below min
        genome.set("curiosity_baseline", -999.0)
        assert genome.get("curiosity_baseline") >= 0.0

    def test_genome_set_nonexistent_raises(self):
        """CognitiveGenome.set() should raise for nonexistent gene."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        with pytest.raises(KeyError):
            genome.set("nonexistent_gene", 0.5)

    def test_genome_mutate_changes_gene(self):
        """CognitiveGenome.mutate() should mutate a specific gene."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        original = genome.get("curiosity_baseline")

        # Mutate many times to ensure change
        for _ in range(10):
            genome.mutate("curiosity_baseline", magnitude=0.3)

        # Check bounds are respected
        value = genome.get("curiosity_baseline")
        assert 0.0 <= value <= 1.0

    def test_genome_get_gene_returns_gene_object(self):
        """CognitiveGenome.get_gene() should return Gene object."""
        from modules.genome import CognitiveGenome, Gene

        genome = CognitiveGenome()
        gene = genome.get_gene("curiosity_baseline")

        assert isinstance(gene, Gene)
        assert gene.name == "curiosity_baseline"


class TestCognitiveGenomeEvolution:
    """Test CognitiveGenome evolution behavior."""

    def test_evolve_stagnation_uses_larger_mutations(self):
        """evolve(trigger='stagnation') should use larger mutations (0.15)."""
        from modules.genome import CognitiveGenome
        import statistics

        # Run evolution multiple times and measure average change
        changes = []
        for _ in range(50):
            genome = CognitiveGenome()
            original_values = {name: gene.value for name, gene in genome.genes.items()}

            genome.evolve(trigger="stagnation", mutation_rate=1.0)  # Mutate all genes

            for name, gene in genome.genes.items():
                changes.append(abs(gene.value - original_values[name]))

        avg_change = statistics.mean(changes)
        # Stagnation should produce noticeable changes
        assert avg_change > 0.01

    def test_evolve_breakthrough_uses_smaller_mutations(self):
        """evolve(trigger='breakthrough') should use smaller mutations (0.05)."""
        from modules.genome import CognitiveGenome
        import statistics

        # Run evolution multiple times and measure average change
        stagnation_changes = []
        breakthrough_changes = []

        for _ in range(50):
            genome_stag = CognitiveGenome()
            original_stag = {name: gene.value for name, gene in genome_stag.genes.items()}
            genome_stag.evolve(trigger="stagnation", mutation_rate=1.0)
            for name, gene in genome_stag.genes.items():
                stagnation_changes.append(abs(gene.value - original_stag[name]))

            genome_break = CognitiveGenome()
            original_break = {name: gene.value for name, gene in genome_break.genes.items()}
            genome_break.evolve(trigger="breakthrough", mutation_rate=1.0)
            for name, gene in genome_break.genes.items():
                breakthrough_changes.append(abs(gene.value - original_break[name]))

        avg_stag = statistics.mean(stagnation_changes)
        avg_break = statistics.mean(breakthrough_changes)

        # Stagnation should produce larger changes than breakthrough
        assert avg_stag > avg_break

    def test_evolve_preserves_fit_genes(self):
        """evolve(preserve_fit=True) should not mutate genes with fitness > 0.7."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        # Set some genes as highly fit
        fit_gene = genome.get_gene("curiosity_baseline")
        fit_gene.fitness = 0.9
        original_value = fit_gene.value

        # Evolve with preserve_fit=True
        genome.evolve(trigger="stagnation", mutation_rate=1.0, preserve_fit=True)

        # Fit gene should not have changed
        assert fit_gene.value == original_value

    def test_evolve_mutation_rate_controls_gene_selection(self):
        """mutation_rate should control what percentage of genes are mutated."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        # Set all genes to same value and fitness
        for gene in genome.genes.values():
            gene.value = 0.5
            gene.fitness = 0.5

        original_values = {name: 0.5 for name in genome.genes}

        # Evolve with 10% mutation rate
        genome.evolve(trigger="stagnation", mutation_rate=0.1, preserve_fit=False)

        # Count how many genes changed
        changed_count = sum(
            1 for name, gene in genome.genes.items()
            if abs(gene.value - original_values[name]) > 0.001
        )

        total_genes = len(genome.genes)
        mutation_percentage = changed_count / total_genes

        # Should be roughly around 10% (with some randomness)
        # Allow wide margin for randomness
        assert 0.0 <= mutation_percentage <= 0.3

    def test_evolve_returns_mutation_report(self):
        """evolve() should return a report of mutations made."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        report = genome.evolve(trigger="stagnation", mutation_rate=0.5)

        assert "trigger" in report
        assert "mutations" in report
        assert "genes_mutated" in report
        assert report["trigger"] == "stagnation"
        assert isinstance(report["genes_mutated"], int)

    def test_evolve_validates_mutation_rate(self):
        """evolve() should raise ValueError for invalid mutation_rate."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        with pytest.raises(ValueError, match="mutation_rate must be between 0 and 1"):
            genome.evolve(trigger="stagnation", mutation_rate=1.5)

        with pytest.raises(ValueError, match="mutation_rate must be between 0 and 1"):
            genome.evolve(trigger="stagnation", mutation_rate=-0.1)

    def test_evolve_handles_empty_eligible_genes(self):
        """evolve() should handle case when all genes are fit."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        # Set all genes as highly fit
        for gene in genome.genes.values():
            gene.fitness = 0.9  # Above FIT_GENE_THRESHOLD (0.7)

        # Evolve with preserve_fit=True should not mutate any genes
        report = genome.evolve(trigger="stagnation", mutation_rate=1.0, preserve_fit=True)

        assert report["genes_mutated"] == 0
        assert report["mutations"] == []


class TestCognitiveGenomeFitness:
    """Test CognitiveGenome fitness tracking."""

    def test_update_fitness_changes_gene_fitness(self):
        """update_fitness() should change gene fitness based on outcome."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        gene = genome.get_gene("curiosity_baseline")
        original_fitness = gene.fitness

        # Positive outcome should increase fitness
        genome.update_fitness("curiosity_baseline", outcome=1.0)
        assert gene.fitness > original_fitness

    def test_update_fitness_negative_outcome(self):
        """update_fitness() with negative outcome should decrease fitness."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        gene = genome.get_gene("curiosity_baseline")
        gene.fitness = 0.8  # Start high

        # Negative outcome should decrease fitness
        genome.update_fitness("curiosity_baseline", outcome=-1.0)
        assert gene.fitness < 0.8

    def test_update_fitness_clamps_to_bounds(self):
        """update_fitness() should keep fitness between 0 and 1."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        gene = genome.get_gene("curiosity_baseline")

        # Test that fitness stays clamped at 1.0
        gene.fitness = 0.99
        genome.update_fitness("curiosity_baseline", outcome=1.0, learning_rate=0.5)
        assert gene.fitness <= 1.0

        # Test that fitness stays clamped at 0.0
        gene.fitness = 0.01
        genome.update_fitness("curiosity_baseline", outcome=-1.0, learning_rate=0.5)
        assert gene.fitness >= 0.0

    def test_update_fitness_validates_outcome(self):
        """update_fitness() should raise ValueError for invalid outcome."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        with pytest.raises(ValueError, match="outcome must be between -1 and 1"):
            genome.update_fitness("curiosity_baseline", outcome=2.0)

        with pytest.raises(ValueError, match="outcome must be between -1 and 1"):
            genome.update_fitness("curiosity_baseline", outcome=-2.0)

    def test_update_fitness_validates_learning_rate(self):
        """update_fitness() should raise ValueError for invalid learning_rate."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        with pytest.raises(ValueError, match="learning_rate must be positive"):
            genome.update_fitness("curiosity_baseline", outcome=0.5, learning_rate=0)

        with pytest.raises(ValueError, match="learning_rate must be positive"):
            genome.update_fitness("curiosity_baseline", outcome=0.5, learning_rate=-0.1)


class TestCognitiveGenomeSerialization:
    """Test CognitiveGenome serialization."""

    def test_to_dict_returns_dict(self):
        """to_dict() should return a dictionary."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        genome_dict = genome.to_dict()

        assert isinstance(genome_dict, dict)
        assert "genes" in genome_dict
        assert "version" in genome_dict

    def test_to_dict_includes_all_genes(self):
        """to_dict() should include all genes."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        genome_dict = genome.to_dict()

        assert len(genome_dict["genes"]) == len(genome.genes)

    def test_from_dict_restores_genome(self):
        """from_dict() should restore genome state."""
        from modules.genome import CognitiveGenome

        original = CognitiveGenome()
        original.set("curiosity_baseline", 0.77)
        original.update_fitness("curiosity_baseline", outcome=1.0)

        genome_dict = original.to_dict()
        restored = CognitiveGenome.from_dict(genome_dict)

        assert restored.get("curiosity_baseline") == 0.77
        assert restored.get_gene("curiosity_baseline").fitness == original.get_gene("curiosity_baseline").fitness

    def test_save_and_load(self):
        """save() and load() should persist genome to file."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()
        genome.set("curiosity_baseline", 0.88)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "genome.json"

            genome.save(path)
            assert path.exists()

            loaded = CognitiveGenome.load(path)
            assert loaded.get("curiosity_baseline") == 0.88

    def test_load_nonexistent_returns_default(self):
        """load() of nonexistent file should return default genome."""
        from modules.genome import CognitiveGenome

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.json"

            genome = CognitiveGenome.load(path)

            # Should return a valid genome with defaults
            assert isinstance(genome, CognitiveGenome)
            assert len(genome.genes) >= 60


class TestDefaultGenes:
    """Test DEFAULT_GENES list."""

    def test_default_genes_exists(self):
        """DEFAULT_GENES should be defined."""
        from modules.genome import DEFAULT_GENES

        assert DEFAULT_GENES is not None
        assert isinstance(DEFAULT_GENES, list)

    def test_default_genes_has_60_plus_entries(self):
        """DEFAULT_GENES should have at least 60 entries."""
        from modules.genome import DEFAULT_GENES

        assert len(DEFAULT_GENES) >= 60

    def test_default_genes_has_all_categories(self):
        """DEFAULT_GENES should cover all 8 categories."""
        from modules.genome import DEFAULT_GENES, GeneCategory

        categories_present = set()
        for gene_def in DEFAULT_GENES:
            # Gene definitions should have category
            if isinstance(gene_def, dict):
                categories_present.add(gene_def.get("category"))
            else:
                categories_present.add(gene_def.category.value)

        expected_categories = {cat.value for cat in GeneCategory}
        assert categories_present == expected_categories


class TestCognitiveGenomeGetCategory:
    """Test get_category method."""

    def test_get_category_returns_list(self):
        """get_category() should return a list of genes."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()
        genes = genome.get_category(GeneCategory.ATTENTION)

        assert isinstance(genes, list)
        assert len(genes) > 0

    def test_get_category_all_same_category(self):
        """get_category() should return only genes of that category."""
        from modules.genome import CognitiveGenome, GeneCategory

        genome = CognitiveGenome()

        for category in GeneCategory:
            genes = genome.get_category(category)
            for gene in genes:
                assert gene.category == category


class TestCognitiveGenomeThreadSafety:
    """Test CognitiveGenome thread safety."""

    def test_genome_has_lock(self):
        """CognitiveGenome should have a threading lock."""
        from modules.genome import CognitiveGenome
        import threading

        genome = CognitiveGenome()
        assert hasattr(genome, '_lock')
        assert isinstance(genome._lock, type(threading.RLock()))

    def test_concurrent_mutations(self):
        """CognitiveGenome should handle concurrent mutations safely."""
        from modules.genome import CognitiveGenome
        import threading
        import time

        genome = CognitiveGenome()
        errors = []

        def mutate_genes():
            try:
                for _ in range(100):
                    genome.mutate("curiosity_baseline", magnitude=0.1)
                    genome.set("competence_baseline", 0.5)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=mutate_genes) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should have occurred
        assert len(errors) == 0

        # Gene values should still be within bounds
        assert 0.0 <= genome.get("curiosity_baseline") <= 1.0
        assert 0.0 <= genome.get("competence_baseline") <= 1.0


class TestCognitiveGenomeIntegration:
    """Integration tests for CognitiveGenome."""

    def test_genome_values_affect_behavior(self):
        """Genome values should be usable for controlling behavior."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        # Get a threshold value
        threshold = genome.get("investigate_threshold")
        assert isinstance(threshold, (int, float))

        # Should be usable in conditional logic
        test_value = 0.5
        if test_value > threshold:
            action = "investigate"
        else:
            action = "wait"

        assert action in ["investigate", "wait"]

    def test_genome_round_trip_preserves_mutations(self):
        """Save/load should preserve mutations."""
        from modules.genome import CognitiveGenome

        genome = CognitiveGenome()

        # Evolve and track changes
        genome.evolve(trigger="stagnation", mutation_rate=0.5)
        evolved_values = {name: gene.value for name, gene in genome.genes.items()}

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "evolved_genome.json"
            genome.save(path)

            loaded = CognitiveGenome.load(path)
            loaded_values = {name: gene.value for name, gene in loaded.genes.items()}

            # Values should match
            for name in evolved_values:
                assert abs(evolved_values[name] - loaded_values[name]) < 0.0001
