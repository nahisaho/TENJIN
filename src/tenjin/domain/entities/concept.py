"""Concept entity - Represents key concepts from educational theories."""

from dataclasses import dataclass, field
from datetime import datetime

from ..value_objects.concept_id import ConceptId


@dataclass
class Concept:
    """Represents a key concept from educational theories.

    Attributes:
        id: Unique identifier.
        name: Name of the concept.
        name_ja: Japanese name.
        definition: Definition of the concept.
        definition_ja: Japanese definition.
        related_theory_ids: IDs of related theories.
        related_concept_ids: IDs of related concepts.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: ConceptId
    name: str
    name_ja: str | None = None
    definition: str = ""
    definition_ja: str = ""
    related_theory_ids: list[str] = field(default_factory=list)
    related_concept_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate concept data."""
        if not self.name:
            raise ValueError("Concept name cannot be empty")

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Compare by ID."""
        if not isinstance(other, Concept):
            return NotImplemented
        return self.id == other.id

    def link_theory(self, theory_id: str) -> None:
        """Link this concept to a theory.

        Args:
            theory_id: ID of theory to link.
        """
        if theory_id not in self.related_theory_ids:
            self.related_theory_ids.append(theory_id)
            self.updated_at = datetime.utcnow()

    def link_concept(self, concept_id: str) -> None:
        """Link this concept to another concept.

        Args:
            concept_id: ID of concept to link.
        """
        if concept_id != str(self.id) and concept_id not in self.related_concept_ids:
            self.related_concept_ids.append(concept_id)
            self.updated_at = datetime.utcnow()

    def get_full_text(self) -> str:
        """Get full text for embedding.

        Returns:
            Combined text of concept content.
        """
        parts = [self.name, self.name_ja, self.definition, self.definition_ja]
        return " ".join(filter(None, parts))

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all concept data.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "name_ja": self.name_ja,
            "definition": self.definition,
            "definition_ja": self.definition_ja,
            "related_theory_ids": self.related_theory_ids,
            "related_concept_ids": self.related_concept_ids,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
