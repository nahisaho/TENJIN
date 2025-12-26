"""ConceptId value object - Immutable identifier for concepts."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ConceptId:
    """Immutable unique identifier for a Concept.

    Attributes:
        value: The UUID value.
    """

    value: UUID

    @classmethod
    def generate(cls) -> "ConceptId":
        """Generate a new random ConceptId.

        Returns:
            New ConceptId instance.
        """
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> "ConceptId":
        """Create ConceptId from string.

        Args:
            id_string: UUID string.

        Returns:
            ConceptId instance.

        Raises:
            ValueError: If string is not a valid UUID.
        """
        return cls(value=UUID(id_string))

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.value)

    def __hash__(self) -> int:
        """Return hash of value."""
        return hash(self.value)
