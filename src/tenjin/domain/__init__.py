"""Domain layer - Core business logic and entities.

This layer contains:
- Entities: Core business objects (Theory, Theorist, Concept, etc.)
- Value Objects: Immutable domain concepts (IDs, types, queries)
- Repositories: Abstract interfaces for data access
"""

from .entities import (
    Theory,
    Theorist,
    Category,
    EDUCATIONAL_CATEGORIES,
    TheoryRelationship,
    Methodology,
    Evidence,
    EvidenceType,
    EvidenceStrength,
    Concept,
)
from .value_objects import (
    TheoryId,
    TheoristId,
    ConceptId,
    MethodologyId,
    EvidenceId,
    CategoryType,
    PriorityLevel,
    RelationshipType,
    SearchQuery,
    SearchResult,
    SearchResults,
)
from .repositories import (
    TheoryRepository,
    GraphRepository,
    VectorRepository,
)

__all__ = [
    # Entities
    "Theory",
    "Theorist",
    "Category",
    "EDUCATIONAL_CATEGORIES",
    "TheoryRelationship",
    "Methodology",
    "Evidence",
    "EvidenceType",
    "EvidenceStrength",
    "Concept",
    # Value Objects
    "TheoryId",
    "TheoristId",
    "ConceptId",
    "MethodologyId",
    "EvidenceId",
    "CategoryType",
    "PriorityLevel",
    "RelationshipType",
    "SearchQuery",
    "SearchResult",
    "SearchResults",
    # Repositories
    "TheoryRepository",
    "GraphRepository",
    "VectorRepository",
]
