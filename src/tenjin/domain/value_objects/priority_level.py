"""PriorityLevel value object - Theory priority levels."""

from enum import IntEnum


class PriorityLevel(IntEnum):
    """Priority levels for educational theories.

    1 = Highest priority (foundational theories)
    5 = Lowest priority (specialized/emerging theories)
    """

    CRITICAL = 1  # Foundational, must-know theories
    HIGH = 2  # Important, widely-used theories
    MEDIUM = 3  # Valuable, contextually important
    LOW = 4  # Specialized or historical interest
    OPTIONAL = 5  # Emerging or niche theories

    @classmethod
    def from_int(cls, value: int) -> "PriorityLevel":
        """Create PriorityLevel from integer.

        Args:
            value: Priority value (1-5).

        Returns:
            Matching PriorityLevel.

        Raises:
            ValueError: If value out of range.
        """
        if value < 1:
            return cls.CRITICAL
        if value > 5:
            return cls.OPTIONAL
        return cls(value)

    @property
    def description(self) -> str:
        """Get description of this priority level.

        Returns:
            Description string.
        """
        descriptions = {
            self.CRITICAL: "Foundational theories essential for understanding education",
            self.HIGH: "Important theories widely used in practice",
            self.MEDIUM: "Valuable theories with specific applications",
            self.LOW: "Specialized theories for specific contexts",
            self.OPTIONAL: "Emerging or niche theories",
        }
        return descriptions.get(self, "Unknown priority")

    @property
    def description_ja(self) -> str:
        """Get Japanese description.

        Returns:
            Japanese description string.
        """
        descriptions = {
            self.CRITICAL: "教育理解に不可欠な基礎理論",
            self.HIGH: "実践で広く使用される重要理論",
            self.MEDIUM: "特定の応用に価値ある理論",
            self.LOW: "特定のコンテキスト向けの専門理論",
            self.OPTIONAL: "新興またはニッチな理論",
        }
        return descriptions.get(self, "不明")
