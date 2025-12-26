"""EvidenceId value object - Immutable identifier for evidence."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EvidenceId:
    """Immutable unique identifier for Evidence.

    Attributes:
        value: The UUID value.
    """

    value: UUID

    @classmethod
    def generate(cls) -> "EvidenceId":
        """Generate a new random EvidenceId.

        Returns:
            New EvidenceId instance.
        """
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> "EvidenceId":
        """Create EvidenceId from string.

        Args:
            id_string: UUID string.

        Returns:
            EvidenceId instance.

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
