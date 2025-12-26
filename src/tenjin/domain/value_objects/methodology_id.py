"""MethodologyId value object - Immutable identifier for methodologies."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MethodologyId:
    """Immutable unique identifier for a Methodology.

    Attributes:
        value: The UUID value.
    """

    value: UUID

    @classmethod
    def generate(cls) -> "MethodologyId":
        """Generate a new random MethodologyId.

        Returns:
            New MethodologyId instance.
        """
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> "MethodologyId":
        """Create MethodologyId from string.

        Args:
            id_string: UUID string.

        Returns:
            MethodologyId instance.

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
