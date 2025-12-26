"""TheoryId value object - Immutable identifier for theories."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TheoryId:
    """Immutable unique identifier for a Theory.

    Attributes:
        value: The UUID value.
    """

    value: UUID

    @classmethod
    def generate(cls) -> "TheoryId":
        """Generate a new random TheoryId.

        Returns:
            New TheoryId instance.
        """
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_string: str) -> "TheoryId":
        """Create TheoryId from string.

        Args:
            id_string: UUID string.

        Returns:
            TheoryId instance.

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
