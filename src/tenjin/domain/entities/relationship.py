"""TheoryRelationship entity - Represents relationships between theories."""

from dataclasses import dataclass, field
from datetime import datetime

from ..value_objects.relationship_type import RelationshipType


@dataclass
class TheoryRelationship:
    """Represents a relationship between two theories.

    Attributes:
        source_id: ID of the source theory.
        target_id: ID of the target theory.
        relationship_type: Type of relationship.
        description: Description of the relationship.
        strength: Relationship strength (0.0-1.0).
        bidirectional: Whether relationship goes both ways.
        created_at: Creation timestamp.
    """

    source_id: str
    target_id: str
    relationship_type: RelationshipType
    description: str = ""
    strength: float = 0.5
    bidirectional: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate relationship data."""
        if self.source_id == self.target_id:
            raise ValueError("Source and target cannot be the same")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("Strength must be between 0.0 and 1.0")

    def __hash__(self) -> int:
        """Hash based on source, target, and type."""
        return hash((self.source_id, self.target_id, self.relationship_type))

    def __eq__(self, other: object) -> bool:
        """Compare relationships."""
        if not isinstance(other, TheoryRelationship):
            return NotImplemented
        return (
            self.source_id == other.source_id
            and self.target_id == other.target_id
            and self.relationship_type == other.relationship_type
        )

    @property
    def relationship_key(self) -> str:
        """Get unique key for this relationship.

        Returns:
            Formatted relationship key.
        """
        return f"{self.source_id}-{self.relationship_type.value}-{self.target_id}"

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all relationship data.
        """
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "description": self.description,
            "strength": self.strength,
            "bidirectional": self.bidirectional,
            "created_at": self.created_at.isoformat(),
        }
