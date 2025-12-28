"""Theorist entity - Represents educational theory founders/contributors."""

from dataclasses import dataclass, field
from datetime import datetime

from ..value_objects.theorist_id import TheoristId


@dataclass
class Theorist:
    """Represents a theorist (founder/contributor) of educational theories.

    Attributes:
        id: Unique identifier.
        name: Full name of the theorist.
        name_ja: Japanese name.
        birth_year: Year of birth.
        death_year: Year of death (None if alive).
        nationality: Country of origin.
        primary_field: Primary field of study/work.
        biography: Brief biography.
        contributions: Key contributions to education.
        key_works: Key published works.
        related_theory_ids: Related theory IDs.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    id: TheoristId
    name: str
    name_ja: str | None = None
    birth_year: int | None = None
    death_year: int | None = None
    nationality: str | None = None
    primary_field: str | None = None
    biography: str | None = None
    contributions: list[str] = field(default_factory=list)
    key_works: list[str] = field(default_factory=list)
    related_theory_ids: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate theorist data."""
        if not self.name:
            raise ValueError("Theorist name cannot be empty")

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Compare by ID."""
        if not isinstance(other, Theorist):
            return NotImplemented
        return self.id == other.id

    @property
    def lifespan(self) -> str:
        """Get formatted lifespan string.

        Returns:
            Formatted lifespan (e.g., "1896-1980").
        """
        if self.birth_year and self.death_year:
            return f"{self.birth_year}-{self.death_year}"
        if self.birth_year:
            return f"{self.birth_year}-present"
        return "Unknown"

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all theorist data.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "name_ja": self.name_ja,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "lifespan": self.lifespan,
            "nationality": self.nationality,
            "biography": self.biography,
            "contributions": self.contributions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
