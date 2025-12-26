"""TheoristId value object - Immutable identifier for theorists."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TheoristId:
    """Immutable unique identifier for a Theorist.

    Attributes:
        value: The UUID value.
    """

    value: UUID

    @classmethod
    def generate(cls) -> "TheoristId":
        """Generate a new random TheoristId.

        Returns:
            New TheoristId instance.
        """
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> "TheoristId":
        """Create TheoristId from string.

        Args:
            id_string: UUID string.

        Returns:
            TheoristId instance.

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
