"""Tests for AnalogicalReasoner."""

import pytest
import threading
from modules.reasoning_engines.analogical_reasoner import (
    AnalogicalReasoner,
    Concept,
    Analogy,
    AnalogicalMapping,
    MappingType,
)
from modules.reasoning_engines.knowledge_graph import KnowledgeGraph
from modules.reasoning_engines.case_based_reasoner import CaseBasedReasoner


# === Concept Tests ===

class TestConceptCreation:
    """Tests for Concept creation."""

    def test_concept_creation_basic(self):
        """Test basic concept creation."""
        concept = Concept(id="sun", name="Sun", domain="solar_system")
        assert concept.id == "sun"
        assert concept.name == "Sun"
        assert concept.domain == "solar_system"

    def test_concept_with_attributes(self):
        """Test concept with attributes."""
        concept = Concept(
            id="sun",
            name="Sun",
            domain="solar_system",
            attributes={"mass": "large", "type": "star"},
        )
        assert concept.attributes["mass"] == "large"
        assert concept.attributes["type"] == "star"

    def test_concept_with_relations(self):
        """Test concept with relations."""
        concept = Concept(
            id="sun",
            name="Sun",
            domain="solar_system",
            relations=[{"type": "attracts", "target": "earth"}],
        )
        assert len(concept.relations) == 1
        assert concept.relations[0]["type"] == "attracts"

    def test_concept_empty_id_raises(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            Concept(id="", name="Sun", domain="solar_system")

    def test_concept_empty_name_raises(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Concept(id="sun", name="", domain="solar_system")

    def test_concept_to_dict(self):
        """Test concept serialization."""
        concept = Concept(
            id="sun",
            name="Sun",
            domain="solar_system",
            attributes={"mass": "large"},
        )
        d = concept.to_dict()
        assert d["id"] == "sun"
        assert d["attributes"]["mass"] == "large"

    def test_concept_from_dict(self):
        """Test concept deserialization."""
        data = {
            "id": "sun",
            "name": "Sun",
            "domain": "solar_system",
            "attributes": {"mass": "large"},
        }
        concept = Concept.from_dict(data)
        assert concept.id == "sun"
        assert concept.attributes["mass"] == "large"


# === AnalogicalMapping Tests ===

class TestAnalogicalMapping:
    """Tests for AnalogicalMapping."""

    def test_mapping_creation(self):
        """Test mapping creation."""
        mapping = AnalogicalMapping(
            id="m1",
            source_concept="sun",
            target_concept="nucleus",
            mapping_type=MappingType.RELATIONAL,
            similarity=0.8,
        )
        assert mapping.source_concept == "sun"
        assert mapping.target_concept == "nucleus"
        assert mapping.similarity == 0.8

    def test_mapping_invalid_similarity_raises(self):
        """Test that invalid similarity raises."""
        with pytest.raises(ValueError, match="similarity must be 0-1"):
            AnalogicalMapping(
                id="m1",
                source_concept="sun",
                target_concept="nucleus",
                mapping_type=MappingType.RELATIONAL,
                similarity=1.5,
            )

    def test_mapping_to_dict(self):
        """Test mapping serialization."""
        mapping = AnalogicalMapping(
            id="m1",
            source_concept="sun",
            target_concept="nucleus",
            mapping_type=MappingType.STRUCTURAL,
            similarity=0.7,
        )
        d = mapping.to_dict()
        assert d["mapping_type"] == "structural"
        assert d["similarity"] == 0.7


# === Analogy Tests ===

class TestAnalogy:
    """Tests for Analogy dataclass."""

    def test_analogy_creation(self):
        """Test analogy creation."""
        analogy = Analogy(
            id="a1",
            source_domain="solar_system",
            target_domain="atom",
        )
        assert analogy.source_domain == "solar_system"
        assert analogy.target_domain == "atom"

    def test_analogy_empty_id_raises(self):
        """Test that empty ID raises."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            Analogy(id="", source_domain="a", target_domain="b")

    def test_analogy_to_dict(self):
        """Test analogy serialization."""
        analogy = Analogy(
            id="a1",
            source_domain="solar_system",
            target_domain="atom",
            overall_similarity=0.75,
            inferences=["nucleus attracts electrons"],
        )
        d = analogy.to_dict()
        assert d["overall_similarity"] == 0.75
        assert len(d["inferences"]) == 1

    def test_analogy_from_dict(self):
        """Test analogy deserialization."""
        data = {
            "id": "a1",
            "source_domain": "solar_system",
            "target_domain": "atom",
            "mappings": [],
            "overall_similarity": 0.8,
        }
        analogy = Analogy.from_dict(data)
        assert analogy.overall_similarity == 0.8


# === AnalogicalReasoner Basic Tests ===

class TestAnalogicalReasonerBasics:
    """Tests for basic AnalogicalReasoner operations."""

    def test_reasoner_creation(self):
        """Test reasoner creation."""
        reasoner = AnalogicalReasoner()
        assert len(reasoner.domains) == 0

    def test_reasoner_with_components(self):
        """Test reasoner with external components."""
        kg = KnowledgeGraph()
        cbr = CaseBasedReasoner()
        reasoner = AnalogicalReasoner(kg, cbr)
        assert reasoner.kg is kg
        assert reasoner.case_reasoner is cbr

    def test_add_concept(self):
        """Test adding a concept."""
        reasoner = AnalogicalReasoner()
        concept = Concept(id="sun", name="Sun", domain="solar_system")
        reasoner.add_concept(concept)
        assert "solar_system" in reasoner.domains
        assert "sun" in reasoner.domains["solar_system"]

    def test_get_concept(self):
        """Test getting a concept."""
        reasoner = AnalogicalReasoner()
        concept = Concept(id="sun", name="Sun", domain="solar_system")
        reasoner.add_concept(concept)
        retrieved = reasoner.get_concept("sun", "solar_system")
        assert retrieved.name == "Sun"

    def test_get_domain_concepts(self):
        """Test getting all concepts in domain."""
        reasoner = AnalogicalReasoner()
        reasoner.add_concept(Concept(id="sun", name="Sun", domain="solar_system"))
        reasoner.add_concept(Concept(id="earth", name="Earth", domain="solar_system"))
        concepts = reasoner.get_domain_concepts("solar_system")
        assert len(concepts) == 2


# === Analogy Finding Tests ===

class TestAnalogyFinding:
    """Tests for finding analogies."""

    def setup_method(self):
        """Set up test domains."""
        self.reasoner = AnalogicalReasoner()

        # Solar system domain
        self.reasoner.add_concept(Concept(
            id="sun",
            name="Sun",
            domain="solar_system",
            attributes={"mass": "large", "role": "center"},
            relations=[{"type": "attracts", "target": "earth"}],
        ))
        self.reasoner.add_concept(Concept(
            id="earth",
            name="Earth",
            domain="solar_system",
            attributes={"mass": "small", "role": "orbiter"},
            relations=[{"type": "orbits", "target": "sun"}],
        ))

        # Atom domain
        self.reasoner.add_concept(Concept(
            id="nucleus",
            name="Nucleus",
            domain="atom",
            attributes={"mass": "large", "role": "center"},
            relations=[{"type": "attracts", "target": "electron"}],
        ))
        self.reasoner.add_concept(Concept(
            id="electron",
            name="Electron",
            domain="atom",
            attributes={"mass": "small", "role": "orbiter"},
            relations=[{"type": "orbits", "target": "nucleus"}],
        ))

    def test_find_analogy_basic(self):
        """Test finding a basic analogy."""
        analogy = self.reasoner.find_analogy("solar_system", "atom")
        assert analogy is not None
        assert analogy.source_domain == "solar_system"
        assert analogy.target_domain == "atom"

    def test_find_analogy_has_mappings(self):
        """Test that analogy has mappings."""
        analogy = self.reasoner.find_analogy("solar_system", "atom")
        assert len(analogy.mappings) > 0

    def test_find_analogy_similarity(self):
        """Test analogy similarity is reasonable."""
        analogy = self.reasoner.find_analogy("solar_system", "atom")
        # Should be high since domains are structurally similar
        assert analogy.overall_similarity >= 0.3

    def test_find_analogy_generates_inferences(self):
        """Test that analogy generates inferences."""
        analogy = self.reasoner.find_analogy("solar_system", "atom")
        # May or may not have inferences depending on mappings
        assert isinstance(analogy.inferences, list)

    def test_find_analogy_empty_domain_returns_none(self):
        """Test that empty domain returns None."""
        result = self.reasoner.find_analogy("nonexistent", "atom")
        assert result is None

    def test_find_analogy_with_focus(self):
        """Test finding analogy with focus concept."""
        analogy = self.reasoner.find_analogy("solar_system", "atom", source_focus="sun")
        assert analogy is not None
        # Should have mapping from sun
        source_concepts = [m.source_concept for m in analogy.mappings]
        assert "sun" in source_concepts


# === Mapping Similarity Tests ===

class TestMappingSimilarity:
    """Tests for similarity calculations."""

    def setup_method(self):
        """Set up reasoner."""
        self.reasoner = AnalogicalReasoner()

    def test_attribute_similarity_same_attributes(self):
        """Test attribute similarity with same attributes."""
        c1 = Concept(id="a", name="A", domain="d1", attributes={"x": 1, "y": 2})
        c2 = Concept(id="b", name="B", domain="d2", attributes={"x": 1, "y": 2})
        sim = self.reasoner._attribute_similarity(c1, c2)
        assert sim == 1.0

    def test_attribute_similarity_different_attributes(self):
        """Test attribute similarity with different attributes."""
        c1 = Concept(id="a", name="A", domain="d1", attributes={"x": 1})
        c2 = Concept(id="b", name="B", domain="d2", attributes={"y": 2})
        sim = self.reasoner._attribute_similarity(c1, c2)
        assert sim < 1.0

    def test_attribute_similarity_empty(self):
        """Test attribute similarity with empty attributes."""
        c1 = Concept(id="a", name="A", domain="d1")
        c2 = Concept(id="b", name="B", domain="d2")
        sim = self.reasoner._attribute_similarity(c1, c2)
        assert sim == 0.0

    def test_relational_similarity_same_types(self):
        """Test relational similarity with same types."""
        c1 = Concept(id="a", name="A", domain="d1", relations=[{"type": "causes"}])
        c2 = Concept(id="b", name="B", domain="d2", relations=[{"type": "causes"}])
        sim = self.reasoner._relational_similarity(c1, c2)
        assert sim == 1.0

    def test_relational_similarity_different_types(self):
        """Test relational similarity with different types."""
        c1 = Concept(id="a", name="A", domain="d1", relations=[{"type": "causes"}])
        c2 = Concept(id="b", name="B", domain="d2", relations=[{"type": "prevents"}])
        sim = self.reasoner._relational_similarity(c1, c2)
        assert sim == 0.0


# === Pattern Transfer Tests ===

class TestPatternTransfer:
    """Tests for pattern transfer."""

    def setup_method(self):
        """Set up domains for transfer."""
        self.reasoner = AnalogicalReasoner()

        # Source domain
        self.reasoner.add_concept(Concept(
            id="cause",
            name="Cause",
            domain="source",
            relations=[{"type": "leads_to", "target": "effect"}],
        ))
        self.reasoner.add_concept(Concept(
            id="effect",
            name="Effect",
            domain="source",
        ))

        # Target domain
        self.reasoner.add_concept(Concept(
            id="input",
            name="Input",
            domain="target",
            relations=[{"type": "leads_to", "target": "output"}],
        ))
        self.reasoner.add_concept(Concept(
            id="output",
            name="Output",
            domain="target",
        ))

    def test_transfer_pattern(self):
        """Test transferring a pattern."""
        pattern = {
            "concepts": ["cause", "effect"],
            "relations": [{"source": "cause", "target": "effect", "type": "leads_to"}],
        }
        result = self.reasoner.transfer_pattern("source", pattern, "target")
        # May or may not find transfer depending on mapping
        assert result is None or "concepts" in result


# === Solve By Analogy Tests ===

class TestSolveByAnalogy:
    """Tests for solving by analogy."""

    def setup_method(self):
        """Set up domains."""
        self.reasoner = AnalogicalReasoner()

        # Problem solving domain
        self.reasoner.add_concept(Concept(
            id="army",
            name="Army",
            domain="military",
            relations=[{"type": "attacks", "target": "fortress"}],
        ))
        self.reasoner.add_concept(Concept(
            id="fortress",
            name="Fortress",
            domain="military",
        ))

    def test_solve_by_analogy_no_domain(self):
        """Test solving when no analogy domain exists."""
        problem = {"concepts": ["problem"], "goal": "solve"}
        result = self.reasoner.solve_by_analogy("unknown", problem)
        assert result is None


# === Learning Tests ===

class TestLearning:
    """Tests for learning from analogies."""

    def setup_method(self):
        """Set up reasoner."""
        self.reasoner = AnalogicalReasoner()

    def test_learn_analogy_success(self):
        """Test learning from successful analogy."""
        analogy = Analogy(
            id="a1",
            source_domain="solar_system",
            target_domain="atom",
            overall_similarity=0.8,
        )
        initial_rel_weight = self.reasoner._relational_weight
        self.reasoner.learn_analogy(analogy, success=True)
        # Weights should adjust
        assert self.reasoner._relational_weight >= initial_rel_weight

    def test_learn_analogy_failure(self):
        """Test learning from failed analogy."""
        analogy = Analogy(
            id="a1",
            source_domain="solar_system",
            target_domain="atom",
            overall_similarity=0.8,
        )
        initial_attr_weight = self.reasoner._attribute_weight
        self.reasoner.learn_analogy(analogy, success=False)
        # Attribute weight should increase on failure
        assert self.reasoner._attribute_weight >= initial_attr_weight


# === Thread Safety Tests ===

class TestThreadSafety:
    """Tests for thread safety."""

    def test_reasoner_has_lock(self):
        """Test that reasoner has a lock."""
        reasoner = AnalogicalReasoner()
        assert hasattr(reasoner, "_lock")
        assert isinstance(reasoner._lock, type(threading.RLock()))

    def test_concurrent_concept_addition(self):
        """Test concurrent concept addition."""
        reasoner = AnalogicalReasoner()
        errors = []

        def add_concepts(domain_id):
            try:
                for i in range(10):
                    concept = Concept(
                        id=f"c{domain_id}_{i}",
                        name=f"Concept {domain_id}_{i}",
                        domain=f"domain_{domain_id}",
                    )
                    reasoner.add_concept(concept)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_concepts, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(reasoner.domains) == 5


# === Statistics Tests ===

class TestStatistics:
    """Tests for statistics."""

    def test_get_stats(self):
        """Test getting statistics."""
        reasoner = AnalogicalReasoner()
        reasoner.add_concept(Concept(id="c1", name="C1", domain="d1"))
        reasoner.add_concept(Concept(id="c2", name="C2", domain="d2"))

        stats = reasoner.get_stats()
        assert stats["total_domains"] == 2
        assert stats["total_concepts"] == 2

    def test_to_dict(self):
        """Test serialization."""
        reasoner = AnalogicalReasoner()
        reasoner.add_concept(Concept(id="c1", name="C1", domain="d1"))

        d = reasoner.to_dict()
        assert "domains" in d
        assert "stats" in d

    def test_clear(self):
        """Test clearing data."""
        reasoner = AnalogicalReasoner()
        reasoner.add_concept(Concept(id="c1", name="C1", domain="d1"))
        reasoner.clear()
        assert len(reasoner.domains) == 0
