"""Category entity - Represents educational theory categories."""

from dataclasses import dataclass, field
from datetime import datetime

from ..value_objects.category_type import CategoryType


@dataclass
class Category:
    """Represents a category of educational theories.

    Attributes:
        type: Category type enum value.
        name: Display name of the category.
        name_ja: Japanese name.
        description: Category description.
        description_ja: Japanese description.
        theory_count: Number of theories in this category.
        created_at: Creation timestamp.
    """

    type: CategoryType
    name: str
    name_ja: str
    description: str = ""
    description_ja: str = ""
    theory_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __hash__(self) -> int:
        """Hash based on type."""
        return hash(self.type)

    def __eq__(self, other: object) -> bool:
        """Compare by type."""
        if not isinstance(other, Category):
            return NotImplemented
        return self.type == other.type

    def increment_count(self) -> None:
        """Increment theory count."""
        self.theory_count += 1

    def decrement_count(self) -> None:
        """Decrement theory count (minimum 0)."""
        self.theory_count = max(0, self.theory_count - 1)

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all category data.
        """
        return {
            "type": self.type.value,
            "name": self.name,
            "name_ja": self.name_ja,
            "description": self.description,
            "description_ja": self.description_ja,
            "theory_count": self.theory_count,
            "created_at": self.created_at.isoformat(),
        }


# Pre-defined categories based on Educational-theory-research.md
EDUCATIONAL_CATEGORIES: dict[CategoryType, Category] = {
    CategoryType.COGNITIVE_DEVELOPMENT: Category(
        type=CategoryType.COGNITIVE_DEVELOPMENT,
        name="Cognitive Development",
        name_ja="認知発達理論",
        description="Theories focusing on how thinking and understanding develop",
        description_ja="思考と理解の発達に焦点を当てた理論",
    ),
    CategoryType.BEHAVIORAL: Category(
        type=CategoryType.BEHAVIORAL,
        name="Behavioral Theories",
        name_ja="行動主義理論",
        description="Theories based on observable behavior and conditioning",
        description_ja="観察可能な行動と条件付けに基づく理論",
    ),
    CategoryType.CONSTRUCTIVIST: Category(
        type=CategoryType.CONSTRUCTIVIST,
        name="Constructivist Theories",
        name_ja="構成主義理論",
        description="Theories emphasizing learner-constructed knowledge",
        description_ja="学習者が知識を構築することを強調する理論",
    ),
    CategoryType.SOCIAL_LEARNING: Category(
        type=CategoryType.SOCIAL_LEARNING,
        name="Social Learning",
        name_ja="社会的学習理論",
        description="Theories focusing on learning through social interaction",
        description_ja="社会的相互作用を通じた学習に焦点を当てた理論",
    ),
    CategoryType.HUMANISTIC: Category(
        type=CategoryType.HUMANISTIC,
        name="Humanistic Theories",
        name_ja="人間主義理論",
        description="Theories emphasizing personal growth and self-actualization",
        description_ja="個人の成長と自己実現を強調する理論",
    ),
    CategoryType.MOTIVATION: Category(
        type=CategoryType.MOTIVATION,
        name="Motivation Theories",
        name_ja="動機づけ理論",
        description="Theories explaining what drives learning behavior",
        description_ja="学習行動を駆り立てるものを説明する理論",
    ),
    CategoryType.INSTRUCTIONAL_DESIGN: Category(
        type=CategoryType.INSTRUCTIONAL_DESIGN,
        name="Instructional Design",
        name_ja="インストラクショナルデザイン",
        description="Theories for designing effective instruction",
        description_ja="効果的な指導を設計するための理論",
    ),
    CategoryType.ADULT_LEARNING: Category(
        type=CategoryType.ADULT_LEARNING,
        name="Adult Learning",
        name_ja="成人学習理論",
        description="Theories specific to adult education",
        description_ja="成人教育に特化した理論",
    ),
    CategoryType.TECHNOLOGY_ENHANCED: Category(
        type=CategoryType.TECHNOLOGY_ENHANCED,
        name="Technology-Enhanced Learning",
        name_ja="テクノロジー活用学習",
        description="Theories for technology-mediated learning",
        description_ja="テクノロジーを介した学習のための理論",
    ),
}
