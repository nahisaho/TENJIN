"""Methodology entity - Represents research/teaching methodologies."""

from dataclasses import dataclass, field
from datetime import datetime

from ..value_objects.methodology_id import MethodologyId


@dataclass
class Methodology:
    """Represents a methodology associated with educational theories.

    Attributes:
        id: Unique identifier.
        name: Name of the methodology.
        name_ja: Japanese name.
        description: Detailed description.
        description_ja: Japanese description.
        steps: Implementation steps.
        related_theory_ids: IDs of related theories.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: MethodologyId
    name: str
    name_ja: str | None = None
    description: str = ""
    description_ja: str = ""
    steps: list[str] = field(default_factory=list)
    related_theory_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate methodology data."""
        if not self.name:
            raise ValueError("Methodology name cannot be empty")

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Compare by ID."""
        if not isinstance(other, Methodology):
            return NotImplemented
        return self.id == other.id

    def add_step(self, step: str) -> None:
        """Add an implementation step.

        Args:
            step: Step description to add.
        """
        if step and step not in self.steps:
            self.steps.append(step)
            self.updated_at = datetime.utcnow()

    def link_theory(self, theory_id: str) -> None:
        """Link this methodology to a theory.

        Args:
            theory_id: ID of theory to link.
        """
        if theory_id not in self.related_theory_ids:
            self.related_theory_ids.append(theory_id)
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all methodology data.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "name_ja": self.name_ja,
            "description": self.description,
            "description_ja": self.description_ja,
            "steps": self.steps,
            "related_theory_ids": self.related_theory_ids,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
