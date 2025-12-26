"""Theory entity - Core domain entity for educational theories."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from ..value_objects.theory_id import TheoryId
from ..value_objects.category_type import CategoryType
from ..value_objects.priority_level import PriorityLevel

if TYPE_CHECKING:
    from .theorist import Theorist
    from .concept import Concept


@dataclass
class Theory:
    """Represents an educational theory in the knowledge graph.

    Attributes:
        id: Unique identifier for the theory.
        name: Name of the theory.
        name_ja: Japanese name of the theory.
        description: Brief description of the theory.
        description_ja: Japanese description of the theory.
        category: Category the theory belongs to.
        priority: Priority level (1-5, 1=highest).
        year_proposed: Year the theory was proposed.
        key_principles: List of key principles.
        applications: Practical applications of the theory.
        strengths: Strengths of the theory.
        limitations: Limitations or criticisms.
        keywords: Searchable keywords.
        theorists: Associated theorists.
        concepts: Related concepts.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: TheoryId
    name: str
    name_ja: str
    description: str
    description_ja: str
    category: CategoryType
    priority: PriorityLevel
    year_proposed: int | None = None
    key_principles: list[str] = field(default_factory=list)
    applications: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    theorists: list["Theorist"] = field(default_factory=list)
    concepts: list["Concept"] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate theory data after initialization."""
        if not self.name:
            raise ValueError("Theory name cannot be empty")
        if not self.description:
            raise ValueError("Theory description cannot be empty")

    def get_full_text(self) -> str:
        """Get full text representation for embedding.

        Returns:
            Combined text of all theory content.
        """
        parts = [
            self.name,
            self.name_ja,
            self.description,
            self.description_ja,
            *self.key_principles,
            *self.applications,
            *self.keywords,
        ]
        return " ".join(filter(None, parts))

    def add_theorist(self, theorist: "Theorist") -> None:
        """Add a theorist to this theory.

        Args:
            theorist: Theorist to associate.
        """
        if theorist not in self.theorists:
            self.theorists.append(theorist)
            self.updated_at = datetime.utcnow()

    def add_concept(self, concept: "Concept") -> None:
        """Add a concept to this theory.

        Args:
            concept: Concept to associate.
        """
        if concept not in self.concepts:
            self.concepts.append(concept)
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all theory data.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "name_ja": self.name_ja,
            "description": self.description,
            "description_ja": self.description_ja,
            "category": self.category.value,
            "priority": self.priority.value,
            "year_proposed": self.year_proposed,
            "key_principles": self.key_principles,
            "applications": self.applications,
            "strengths": self.strengths,
            "limitations": self.limitations,
            "keywords": self.keywords,
            "theorist_names": [t.name for t in self.theorists],
            "concept_names": [c.name for c in self.concepts],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
