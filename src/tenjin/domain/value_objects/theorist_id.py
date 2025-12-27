"""TheoristId value object - Immutable identifier for theorists."""

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class TheoristId:
    """Immutable unique identifier for a Theorist.

    Attributes:
        value: The string identifier value.
    """

    value: str

    @classmethod
    def generate(cls) -> "TheoristId":
        """Generate a new random TheoristId.

        Returns:
            New TheoristId instance.
        """
        return cls(value=str(uuid4()))

    @classmethod
    def from_string(cls, id_string: str) -> "TheoristId":
        """Create TheoristId from string.

        Args:
            id_string: ID string.

        Returns:
            TheoristId instance.
        """
        return cls(value=id_string)

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    def __hash__(self) -> int:
        """Return hash of value."""
        return hash(self.value)
