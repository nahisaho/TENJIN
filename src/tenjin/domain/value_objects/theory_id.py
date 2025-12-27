"""TheoryId value object - Immutable identifier for theories."""

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class TheoryId:
    """Immutable unique identifier for a Theory.

    Attributes:
        value: The string identifier value.
    """

    value: str

    @classmethod
    def generate(cls) -> "TheoryId":
        """Generate a new random TheoryId.

        Returns:
            New TheoryId instance.
        """
        return cls(value=str(uuid4()))

    @classmethod
    def from_string(cls, id_string: str) -> "TheoryId":
        """Create TheoryId from string.

        Args:
            id_string: ID string.

        Returns:
            TheoryId instance.
        """
        return cls(value=id_string)

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    def __hash__(self) -> int:
        """Return hash of value."""
        return hash(self.value)
