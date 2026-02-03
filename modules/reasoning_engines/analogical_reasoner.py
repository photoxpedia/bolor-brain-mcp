"""Analogical reasoning engine for cross-domain pattern transfer.

This module provides analogical reasoning capabilities:
- Find structural similarities between domains
- Transfer solutions from source to target domain
- Learn new patterns through analogy
- Map relationships across different contexts
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum
import threading
import time
import uuid
import logging

from .knowledge_graph import KnowledgeGraph, Node, Edge
from .case_based_reasoner import CaseBasedReasoner, Case

logger = logging.getLogger(__name__)


class MappingType(Enum):
    """Types of analogical mappings."""
    ATTRIBUTE = "attribute"  # Object properties (color, size)
    RELATIONAL = "relational"  # Relationships (causes, contains)
    STRUCTURAL = "structural"  # Higher-order structure
    CAUSAL = "causal"  # Causal relationships


@dataclass
class Concept:
    """A concept in a domain.

    Attributes:
        id: Unique identifier
        name: Concept name
        domain: Domain this concept belongs to
        attributes: Key-value attributes
        relations: List of relations to other concepts
    """
    id: str
    name: str
    domain: str
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: list[dict] = field(default_factory=list)

    def __post_init__(self):
        """Validate concept fields."""
        if not self.id:
            raise ValueError("Concept id cannot be empty")
        if not self.name:
            raise ValueError("Concept name cannot be empty")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "attributes": self.attributes,
            "relations": self.relations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Concept":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            domain=data.get("domain", ""),
            attributes=data.get("attributes", {}),
            relations=data.get("relations", []),
        )


@dataclass
class AnalogicalMapping:
    """A mapping between source and target concepts.

    Attributes:
        id: Unique identifier
        source_concept: Source concept ID
        target_concept: Target concept ID
        mapping_type: Type of mapping
        similarity: Mapping strength (0-1)
        mapped_attributes: Attribute correspondences
        mapped_relations: Relation correspondences
    """
    id: str
    source_concept: str
    target_concept: str
    mapping_type: MappingType
    similarity: float = 0.0
    mapped_attributes: dict[str, str] = field(default_factory=dict)
    mapped_relations: list[dict] = field(default_factory=list)

    def __post_init__(self):
        """Validate mapping fields."""
        if not 0 <= self.similarity <= 1:
            raise ValueError(f"similarity must be 0-1, got {self.similarity}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_concept": self.source_concept,
            "target_concept": self.target_concept,
            "mapping_type": self.mapping_type.value,
            "similarity": self.similarity,
            "mapped_attributes": self.mapped_attributes,
            "mapped_relations": self.mapped_relations,
        }


@dataclass
class Analogy:
    """A complete analogy between two domains.

    Attributes:
        id: Unique identifier
        source_domain: Source domain name
        target_domain: Target domain name
        mappings: List of concept mappings
        overall_similarity: Overall analogy quality (0-1)
        inferences: Inferences derived from the analogy
        created_at: Timestamp
    """
    id: str
    source_domain: str
    target_domain: str
    mappings: list[AnalogicalMapping] = field(default_factory=list)
    overall_similarity: float = 0.0
    inferences: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: time.time())

    def __post_init__(self):
        """Validate analogy fields."""
        if not self.id:
            raise ValueError("Analogy id cannot be empty")
        if not 0 <= self.overall_similarity <= 1:
            raise ValueError(f"overall_similarity must be 0-1")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "mappings": [m.to_dict() for m in self.mappings],
            "overall_similarity": self.overall_similarity,
            "inferences": self.inferences,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Analogy":
        """Create from dictionary."""
        mappings = []
        for m in data.get("mappings", []):
            mappings.append(AnalogicalMapping(
                id=m["id"],
                source_concept=m["source_concept"],
                target_concept=m["target_concept"],
                mapping_type=MappingType(m["mapping_type"]),
                similarity=m.get("similarity", 0.0),
                mapped_attributes=m.get("mapped_attributes", {}),
                mapped_relations=m.get("mapped_relations", []),
            ))
        return cls(
            id=data["id"],
            source_domain=data["source_domain"],
            target_domain=data["target_domain"],
            mappings=mappings,
            overall_similarity=data.get("overall_similarity", 0.0),
            inferences=data.get("inferences", []),
            created_at=data.get("created_at", time.time()),
        )


class AnalogicalReasoner:
    """Analogical reasoning engine.

    Uses Structure-Mapping Theory (SMT) principles:
    - Systematicity: Prefer mappings that preserve relational structure
    - One-to-one: Each element maps to at most one element
    - Parallel connectivity: Arguments of relations should map consistently

    Example:
        >>> reasoner = AnalogicalReasoner()
        >>> reasoner.add_concept(Concept(id="sun", name="Sun", domain="solar_system"))
        >>> reasoner.add_concept(Concept(id="nucleus", name="Nucleus", domain="atom"))
        >>> analogy = reasoner.find_analogy("solar_system", "atom")
    """

    def __init__(self, knowledge_graph: KnowledgeGraph = None,
                 case_reasoner: CaseBasedReasoner = None,
                 genome=None):
        """Initialize the analogical reasoner.

        Args:
            knowledge_graph: KnowledgeGraph for domain knowledge
            case_reasoner: CaseBasedReasoner for storing learned analogies
            genome: Optional CognitiveGenome for configurable parameters
        """
        self.kg = knowledge_graph or KnowledgeGraph()
        self.case_reasoner = case_reasoner or CaseBasedReasoner()
        self.genome = genome
        self._lock = threading.RLock()

        # Concept storage by domain
        self.domains: dict[str, dict[str, Concept]] = {}
        self.analogies: dict[str, Analogy] = {}

        # Mapping parameters
        self._attribute_weight = 0.3
        self._relational_weight = 0.5
        self._structural_weight = 0.7
        self._min_similarity = 0.3

    # === Concept Management ===

    def add_concept(self, concept: Concept) -> None:
        """Add a concept to the reasoner.

        Args:
            concept: The concept to add
        """
        with self._lock:
            if concept.domain not in self.domains:
                self.domains[concept.domain] = {}
            self.domains[concept.domain][concept.id] = concept

            # Also add to knowledge graph
            self.kg.add_node(Node(
                id=f"{concept.domain}:{concept.id}",
                label=concept.name,
                properties={"domain": concept.domain, **concept.attributes}
            ))

            # Add relations to knowledge graph
            for rel in concept.relations:
                self.kg.add_edge(Edge(
                    source=f"{concept.domain}:{concept.id}",
                    target=f"{concept.domain}:{rel.get('target', '')}",
                    relation=rel.get("type", "related_to"),
                    properties=rel.get("properties", {})
                ))

    def get_concept(self, concept_id: str, domain: str) -> Optional[Concept]:
        """Get a concept by ID and domain."""
        return self.domains.get(domain, {}).get(concept_id)

    def get_domain_concepts(self, domain: str) -> list[Concept]:
        """Get all concepts in a domain."""
        return list(self.domains.get(domain, {}).values())

    # === Analogy Finding ===

    def find_analogy(self, source_domain: str, target_domain: str,
                    source_focus: str = None) -> Optional[Analogy]:
        """Find an analogy between two domains.

        Args:
            source_domain: The source (well-understood) domain
            target_domain: The target (to-understand) domain
            source_focus: Optional concept to focus the analogy on

        Returns:
            An Analogy if found, None otherwise
        """
        source_concepts = self.get_domain_concepts(source_domain)
        target_concepts = self.get_domain_concepts(target_domain)

        if not source_concepts or not target_concepts:
            return None

        # Filter by focus if specified
        if source_focus:
            source_concepts = [c for c in source_concepts if c.id == source_focus]
            if not source_concepts:
                return None

        # Find mappings using Structure-Mapping
        mappings = self._find_structural_mappings(source_concepts, target_concepts)

        if not mappings:
            return None

        # Calculate overall similarity
        overall = sum(m.similarity for m in mappings) / len(mappings)

        if overall < self._min_similarity:
            return None

        # Generate inferences
        inferences = self._generate_inferences(mappings, source_concepts, target_concepts)

        analogy = Analogy(
            id=str(uuid.uuid4())[:8],
            source_domain=source_domain,
            target_domain=target_domain,
            mappings=mappings,
            overall_similarity=overall,
            inferences=inferences,
        )

        with self._lock:
            self.analogies[analogy.id] = analogy

        logger.debug(f"Found analogy: {source_domain} -> {target_domain}, sim={overall:.2f}")
        return analogy

    def _find_structural_mappings(self, source: list[Concept],
                                  target: list[Concept]) -> list[AnalogicalMapping]:
        """Find structural mappings between concepts.

        Uses greedy best-first mapping with structural constraints.
        """
        mappings = []
        used_targets = set()

        # Sort source by number of relations (prefer more connected)
        source_sorted = sorted(source, key=lambda c: len(c.relations), reverse=True)

        for s_concept in source_sorted:
            best_target = None
            best_score = 0.0
            best_mapping = None

            for t_concept in target:
                if t_concept.id in used_targets:
                    continue

                # Calculate multi-level similarity
                attr_sim = self._attribute_similarity(s_concept, t_concept)
                rel_sim = self._relational_similarity(s_concept, t_concept)
                struct_sim = self._structural_similarity(s_concept, t_concept, mappings)

                # Weighted combination (favor relational and structural)
                score = (
                    self._attribute_weight * attr_sim +
                    self._relational_weight * rel_sim +
                    self._structural_weight * struct_sim
                ) / (self._attribute_weight + self._relational_weight + self._structural_weight)

                if score > best_score and score >= self._min_similarity:
                    best_score = score
                    best_target = t_concept
                    best_mapping = AnalogicalMapping(
                        id=str(uuid.uuid4())[:8],
                        source_concept=s_concept.id,
                        target_concept=t_concept.id,
                        mapping_type=self._determine_mapping_type(attr_sim, rel_sim, struct_sim),
                        similarity=score,
                        mapped_attributes=self._map_attributes(s_concept, t_concept),
                        mapped_relations=self._map_relations(s_concept, t_concept),
                    )

            if best_target and best_mapping:
                mappings.append(best_mapping)
                used_targets.add(best_target.id)

        return mappings

    def _attribute_similarity(self, source: Concept, target: Concept) -> float:
        """Calculate attribute-level similarity."""
        if not source.attributes or not target.attributes:
            return 0.0

        common_keys = set(source.attributes.keys()) & set(target.attributes.keys())
        if not common_keys:
            # Check for semantic similarity in attribute names
            s_keys = set(source.attributes.keys())
            t_keys = set(target.attributes.keys())
            # Simple check: count keys with common substrings
            matches = 0
            for sk in s_keys:
                for tk in t_keys:
                    if sk in tk or tk in sk:
                        matches += 1
            return matches / max(len(s_keys), len(t_keys), 1)

        # For common keys, check value similarity
        same_values = sum(
            1 for k in common_keys
            if source.attributes[k] == target.attributes[k]
        )
        return same_values / max(len(source.attributes), len(target.attributes))

    def _relational_similarity(self, source: Concept, target: Concept) -> float:
        """Calculate relational similarity (types of relationships)."""
        if not source.relations or not target.relations:
            return 0.0

        source_types = {r.get("type", "") for r in source.relations}
        target_types = {r.get("type", "") for r in target.relations}

        if not source_types or not target_types:
            return 0.0

        # Jaccard similarity of relation types
        intersection = source_types & target_types
        union = source_types | target_types

        return len(intersection) / len(union) if union else 0.0

    def _structural_similarity(self, source: Concept, target: Concept,
                              existing_mappings: list[AnalogicalMapping]) -> float:
        """Calculate structural similarity considering existing mappings.

        Checks if the relations of source/target map consistently with
        already established mappings (parallel connectivity).
        """
        if not existing_mappings:
            return 0.5  # Neutral when no existing mappings

        # Build mapping lookup
        s_to_t = {m.source_concept: m.target_concept for m in existing_mappings}

        consistent = 0
        total = 0

        for s_rel in source.relations:
            s_target = s_rel.get("target", "")
            if s_target in s_to_t:
                # Source relation target is already mapped
                expected_t_target = s_to_t[s_target]

                # Check if target concept has relation to expected target
                for t_rel in target.relations:
                    if t_rel.get("type") == s_rel.get("type"):
                        total += 1
                        if t_rel.get("target") == expected_t_target:
                            consistent += 1

        return consistent / total if total > 0 else 0.5

    def _determine_mapping_type(self, attr_sim: float, rel_sim: float,
                               struct_sim: float) -> MappingType:
        """Determine the dominant mapping type."""
        if struct_sim > max(attr_sim, rel_sim):
            return MappingType.STRUCTURAL
        elif rel_sim > attr_sim:
            return MappingType.RELATIONAL
        else:
            return MappingType.ATTRIBUTE

    def _map_attributes(self, source: Concept, target: Concept) -> dict[str, str]:
        """Create attribute correspondences."""
        mapped = {}
        for s_key in source.attributes:
            if s_key in target.attributes:
                mapped[s_key] = s_key
            else:
                # Try to find similar attribute name
                for t_key in target.attributes:
                    if s_key in t_key or t_key in s_key:
                        mapped[s_key] = t_key
                        break
        return mapped

    def _map_relations(self, source: Concept, target: Concept) -> list[dict]:
        """Create relation correspondences."""
        mapped = []
        source_rels = {r.get("type", ""): r for r in source.relations}
        target_rels = {r.get("type", ""): r for r in target.relations}

        for rel_type, s_rel in source_rels.items():
            if rel_type in target_rels:
                mapped.append({
                    "source_relation": rel_type,
                    "target_relation": rel_type,
                    "source_target": s_rel.get("target", ""),
                    "target_target": target_rels[rel_type].get("target", ""),
                })
        return mapped

    # === Inference Generation ===

    def _generate_inferences(self, mappings: list[AnalogicalMapping],
                            source_concepts: list[Concept],
                            target_concepts: list[Concept]) -> list[str]:
        """Generate inferences from the analogy.

        Transfers knowledge from source to target based on mappings.
        """
        inferences = []
        target_by_id = {c.id: c for c in target_concepts}
        source_by_id = {c.id: c for c in source_concepts}

        for mapping in mappings:
            source = source_by_id.get(mapping.source_concept)
            target = target_by_id.get(mapping.target_concept)

            if not source or not target:
                continue

            # Transfer unmapped attributes
            for attr, value in source.attributes.items():
                if attr not in mapping.mapped_attributes and attr not in target.attributes:
                    inferences.append(
                        f"{target.name} may have {attr} (by analogy with {source.name})"
                    )

            # Transfer unmapped relations
            mapped_rel_types = {m.get("source_relation") for m in mapping.mapped_relations}
            for rel in source.relations:
                rel_type = rel.get("type", "")
                if rel_type and rel_type not in mapped_rel_types:
                    inferences.append(
                        f"{target.name} may {rel_type} something (by analogy with {source.name})"
                    )

        return inferences

    # === Pattern Transfer ===

    def transfer_pattern(self, source_domain: str, pattern: dict,
                        target_domain: str) -> Optional[dict]:
        """Transfer a pattern from source to target domain.

        Args:
            source_domain: Domain the pattern comes from
            pattern: Pattern to transfer (dict with concepts, relations)
            target_domain: Domain to transfer to

        Returns:
            Transferred pattern or None if no mapping found
        """
        # First, find or create analogy
        analogy = self.find_analogy(source_domain, target_domain)
        if not analogy:
            return None

        # Build mapping lookup
        s_to_t = {m.source_concept: m.target_concept for m in analogy.mappings}

        # Transfer pattern
        transferred = {"concepts": [], "relations": []}

        for concept in pattern.get("concepts", []):
            if concept in s_to_t:
                transferred["concepts"].append(s_to_t[concept])

        for rel in pattern.get("relations", []):
            source_id = rel.get("source", "")
            target_id = rel.get("target", "")
            if source_id in s_to_t and target_id in s_to_t:
                transferred["relations"].append({
                    "source": s_to_t[source_id],
                    "target": s_to_t[target_id],
                    "type": rel.get("type", "related_to"),
                })

        return transferred if transferred["concepts"] else None

    def solve_by_analogy(self, problem_domain: str, problem: dict,
                        analogy_domain: str = None) -> Optional[dict]:
        """Solve a problem using analogical reasoning.

        Args:
            problem_domain: Domain of the problem
            problem: Problem description (concepts, goal)
            analogy_domain: Specific domain to use for analogy (auto-selects if None)

        Returns:
            Solution based on analogy or None
        """
        # Find best analogy domain if not specified
        if not analogy_domain:
            analogy_domain = self._find_best_analogy_domain(problem_domain, problem)

        if not analogy_domain:
            return None

        # Find analogy
        analogy = self.find_analogy(analogy_domain, problem_domain)
        if not analogy:
            return None

        # Look for solution patterns in source domain
        source_patterns = self._find_solution_patterns(analogy_domain, problem)

        if not source_patterns:
            return None

        # Transfer best pattern
        best_pattern = max(source_patterns, key=lambda p: p.get("relevance", 0))
        solution = self.transfer_pattern(analogy_domain, best_pattern, problem_domain)

        if solution:
            solution["analogy_used"] = analogy.id
            solution["source_domain"] = analogy_domain
            solution["confidence"] = analogy.overall_similarity

        return solution

    def _find_best_analogy_domain(self, problem_domain: str, problem: dict) -> Optional[str]:
        """Find the best domain for analogical problem solving."""
        best_domain = None
        best_score = 0.0

        for domain in self.domains:
            if domain == problem_domain:
                continue

            # Score based on structural similarity
            analogy = self.find_analogy(domain, problem_domain)
            if analogy and analogy.overall_similarity > best_score:
                best_score = analogy.overall_similarity
                best_domain = domain

        return best_domain

    def _find_solution_patterns(self, domain: str, problem: dict) -> list[dict]:
        """Find patterns in domain that might solve the problem."""
        patterns = []
        concepts = self.get_domain_concepts(domain)

        # Look for concepts with goal-related relations
        goal = problem.get("goal", "")
        for concept in concepts:
            for rel in concept.relations:
                if goal.lower() in str(rel).lower():
                    patterns.append({
                        "concepts": [concept.id],
                        "relations": [rel],
                        "relevance": 0.7,
                    })

        return patterns

    # === Learning ===

    def learn_analogy(self, analogy: Analogy, success: bool) -> None:
        """Learn from analogy usage.

        Args:
            analogy: The analogy that was used
            success: Whether it led to successful reasoning
        """
        # Store as case for future retrieval
        case = Case(
            id=f"analogy_{analogy.id}",
            problem={"source": analogy.source_domain, "target": analogy.target_domain},
            solution={
                "mappings": [m.to_dict() for m in analogy.mappings],
                "inferences": analogy.inferences,
            },
            outcome="success" if success else "failure",
        )
        self.case_reasoner.store_case(case)

        # Adjust similarity weights based on success
        with self._lock:
            if success:
                # Strengthen relational/structural bias
                self._relational_weight = min(0.9, self._relational_weight + 0.05)
                self._structural_weight = min(0.9, self._structural_weight + 0.05)
            else:
                # Increase attribute weight
                self._attribute_weight = min(0.9, self._attribute_weight + 0.05)

    # === Statistics ===

    def get_stats(self) -> dict:
        """Get reasoner statistics."""
        total_concepts = sum(len(d) for d in self.domains.values())
        return {
            "total_domains": len(self.domains),
            "total_concepts": total_concepts,
            "total_analogies": len(self.analogies),
            "domains": list(self.domains.keys()),
        }

    def get_analogy(self, analogy_id: str) -> Optional[Analogy]:
        """Get an analogy by ID."""
        return self.analogies.get(analogy_id)

    def to_dict(self) -> dict:
        """Serialize reasoner state."""
        return {
            "domains": {
                d: {cid: c.to_dict() for cid, c in concepts.items()}
                for d, concepts in self.domains.items()
            },
            "analogies": {aid: a.to_dict() for aid, a in self.analogies.items()},
            "stats": self.get_stats(),
        }

    def clear(self) -> None:
        """Clear all data."""
        with self._lock:
            self.domains.clear()
            self.analogies.clear()
