"""RelationshipType value object - Types of relationships between theories."""

from enum import Enum


class RelationshipType(str, Enum):
    """Types of relationships between educational theories."""

    # Influence relationships
    INFLUENCES = "influences"  # A influences B
    INFLUENCED_BY = "influenced_by"  # A was influenced by B
    BUILDS_UPON = "builds_upon"  # A builds upon B

    # Contrast relationships
    CONTRASTS_WITH = "contrasts_with"  # A contrasts with B
    CRITIQUES = "critiques"  # A critiques B
    EXTENDS = "extends"  # A extends B

    # Similarity relationships
    SIMILAR_TO = "similar_to"  # A is similar to B
    COMPLEMENTS = "complements"  # A complements B
    OVERLAPS_WITH = "overlaps_with"  # A overlaps with B

    # Hierarchical relationships
    SPECIALIZES = "specializes"  # A is a specialization of B
    GENERALIZES = "generalizes"  # A generalizes B
    PART_OF = "part_of"  # A is part of B

    # Application relationships
    APPLIES_TO = "applies_to"  # A applies to context B
    DERIVED_FROM = "derived_from"  # A is derived from B

    @property
    def inverse(self) -> "RelationshipType":
        """Get the inverse relationship type.

        Returns:
            Inverse RelationshipType.
        """
        inverses = {
            self.INFLUENCES: self.INFLUENCED_BY,
            self.INFLUENCED_BY: self.INFLUENCES,
            self.BUILDS_UPON: self.EXTENDS,
            self.EXTENDS: self.BUILDS_UPON,
            self.SPECIALIZES: self.GENERALIZES,
            self.GENERALIZES: self.SPECIALIZES,
            self.PART_OF: self.PART_OF,  # No direct inverse
            self.CRITIQUES: self.CRITIQUES,  # Symmetric
            self.CONTRASTS_WITH: self.CONTRASTS_WITH,  # Symmetric
            self.SIMILAR_TO: self.SIMILAR_TO,  # Symmetric
            self.COMPLEMENTS: self.COMPLEMENTS,  # Symmetric
            self.OVERLAPS_WITH: self.OVERLAPS_WITH,  # Symmetric
            self.APPLIES_TO: self.DERIVED_FROM,
            self.DERIVED_FROM: self.APPLIES_TO,
        }
        return inverses.get(self, self)

    @property
    def is_symmetric(self) -> bool:
        """Check if this relationship is symmetric.

        Returns:
            True if symmetric (A rel B implies B rel A).
        """
        return self in {
            self.CONTRASTS_WITH,
            self.SIMILAR_TO,
            self.COMPLEMENTS,
            self.OVERLAPS_WITH,
        }

    @property
    def display_name(self) -> str:
        """Get human-readable display name.

        Returns:
            Formatted display name.
        """
        return self.value.replace("_", " ").title()

    @property
    def description(self) -> str:
        """Get description of this relationship type.

        Returns:
            Description string.
        """
        descriptions = {
            self.INFLUENCES: "Directly influences or impacts",
            self.INFLUENCED_BY: "Was influenced or impacted by",
            self.BUILDS_UPON: "Builds upon or develops from",
            self.CONTRASTS_WITH: "Presents contrasting viewpoint",
            self.CRITIQUES: "Offers critique or challenges",
            self.EXTENDS: "Extends or expands upon",
            self.SIMILAR_TO: "Shares similar concepts or approaches",
            self.COMPLEMENTS: "Complements or works well with",
            self.OVERLAPS_WITH: "Has overlapping concepts",
            self.SPECIALIZES: "Is a specialization of",
            self.GENERALIZES: "Generalizes or abstracts from",
            self.PART_OF: "Is a component or part of",
            self.APPLIES_TO: "Applies to or is used in",
            self.DERIVED_FROM: "Was derived or developed from",
        }
        return descriptions.get(self, "Unknown relationship")
