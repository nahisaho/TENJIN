"""CategoryType value object - Enumeration of educational theory categories."""

from enum import Enum


class CategoryType(str, Enum):
    """Educational theory category types.

    Based on the 9 categories from Educational-theory-research.md.
    """

    COGNITIVE_DEVELOPMENT = "cognitive_development"
    BEHAVIORAL = "behavioral"
    CONSTRUCTIVIST = "constructivist"
    SOCIAL_LEARNING = "social_learning"
    HUMANISTIC = "humanistic"
    MOTIVATION = "motivation"
    INSTRUCTIONAL_DESIGN = "instructional_design"
    ADULT_LEARNING = "adult_learning"
    TECHNOLOGY_ENHANCED = "technology_enhanced"

    @classmethod
    def from_string(cls, value: str) -> "CategoryType":
        """Create CategoryType from string, handling various formats.

        Args:
            value: Category string in any format.

        Returns:
            Matching CategoryType.

        Raises:
            ValueError: If no matching category found.
        """
        # Normalize input
        normalized = value.lower().replace("-", "_").replace(" ", "_")

        # Try exact match
        try:
            return cls(normalized)
        except ValueError:
            pass

        # Try partial match
        for category in cls:
            if normalized in category.value or category.value in normalized:
                return category

        raise ValueError(f"Unknown category type: {value}")

    @property
    def display_name(self) -> str:
        """Get human-readable display name.

        Returns:
            Formatted display name.
        """
        return self.value.replace("_", " ").title()

    @property
    def display_name_ja(self) -> str:
        """Get Japanese display name.

        Returns:
            Japanese display name.
        """
        names = {
            self.COGNITIVE_DEVELOPMENT: "認知発達理論",
            self.BEHAVIORAL: "行動主義理論",
            self.CONSTRUCTIVIST: "構成主義理論",
            self.SOCIAL_LEARNING: "社会的学習理論",
            self.HUMANISTIC: "人間主義理論",
            self.MOTIVATION: "動機づけ理論",
            self.INSTRUCTIONAL_DESIGN: "インストラクショナルデザイン",
            self.ADULT_LEARNING: "成人学習理論",
            self.TECHNOLOGY_ENHANCED: "テクノロジー活用学習",
        }
        return names.get(self, self.display_name)
