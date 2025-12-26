"""Evidence entity - Represents research evidence for theories."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..value_objects.evidence_id import EvidenceId


class EvidenceType(str, Enum):
    """Types of research evidence."""

    EMPIRICAL = "empirical"
    META_ANALYSIS = "meta_analysis"
    CASE_STUDY = "case_study"
    LONGITUDINAL = "longitudinal"
    EXPERIMENTAL = "experimental"
    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    MIXED_METHODS = "mixed_methods"


class EvidenceStrength(str, Enum):
    """Strength levels of evidence."""

    STRONG = "strong"
    MODERATE = "moderate"
    LIMITED = "limited"
    EMERGING = "emerging"
    CONTESTED = "contested"


@dataclass
class Evidence:
    """Represents research evidence supporting or critiquing a theory.

    Attributes:
        id: Unique identifier.
        title: Title of the evidence/study.
        evidence_type: Type of evidence.
        strength: Strength of the evidence.
        description: Description of findings.
        source: Source citation.
        year: Publication year.
        related_theory_ids: IDs of related theories.
        supports: Whether evidence supports (True) or critiques (False).
        created_at: Creation timestamp.
    """

    id: EvidenceId
    title: str
    evidence_type: EvidenceType
    strength: EvidenceStrength
    description: str = ""
    source: str = ""
    year: int | None = None
    related_theory_ids: list[str] = field(default_factory=list)
    supports: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate evidence data."""
        if not self.title:
            raise ValueError("Evidence title cannot be empty")

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Compare by ID."""
        if not isinstance(other, Evidence):
            return NotImplemented
        return self.id == other.id

    def link_theory(self, theory_id: str) -> None:
        """Link this evidence to a theory.

        Args:
            theory_id: ID of theory to link.
        """
        if theory_id not in self.related_theory_ids:
            self.related_theory_ids.append(theory_id)

    @property
    def citation(self) -> str:
        """Get formatted citation.

        Returns:
            Formatted citation string.
        """
        if self.source and self.year:
            return f"{self.source} ({self.year})"
        return self.source or "Unknown source"

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all evidence data.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "evidence_type": self.evidence_type.value,
            "strength": self.strength.value,
            "description": self.description,
            "source": self.source,
            "year": self.year,
            "citation": self.citation,
            "related_theory_ids": self.related_theory_ids,
            "supports": self.supports,
            "created_at": self.created_at.isoformat(),
        }
