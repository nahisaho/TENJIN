"""SearchQuery value object - Encapsulates search parameters."""

from dataclasses import dataclass, field
from typing import Literal

from .category_type import CategoryType
from .priority_level import PriorityLevel


@dataclass(frozen=True)
class SearchQuery:
    """Immutable search query parameters.

    Attributes:
        query: Search query text.
        search_type: Type of search (semantic, keyword, hybrid).
        categories: Filter by categories.
        priority_min: Minimum priority level.
        priority_max: Maximum priority level.
        limit: Maximum number of results.
        offset: Result offset for pagination.
        include_related: Include related theories.
        language: Preferred language (en, ja, both).
    """

    query: str
    search_type: Literal["semantic", "keyword", "hybrid"] = "hybrid"
    categories: tuple[CategoryType, ...] = field(default_factory=tuple)
    priority_min: PriorityLevel = PriorityLevel.OPTIONAL
    priority_max: PriorityLevel = PriorityLevel.CRITICAL
    limit: int = 10
    offset: int = 0
    include_related: bool = True
    language: Literal["en", "ja", "both"] = "both"

    def __post_init__(self) -> None:
        """Validate search query."""
        if not self.query.strip():
            raise ValueError("Search query cannot be empty")
        if self.limit < 1:
            raise ValueError("Limit must be at least 1")
        if self.limit > 100:
            object.__setattr__(self, "limit", 100)
        if self.offset < 0:
            raise ValueError("Offset cannot be negative")

    def with_limit(self, limit: int) -> "SearchQuery":
        """Create new query with different limit.

        Args:
            limit: New limit value.

        Returns:
            New SearchQuery with updated limit.
        """
        return SearchQuery(
            query=self.query,
            search_type=self.search_type,
            categories=self.categories,
            priority_min=self.priority_min,
            priority_max=self.priority_max,
            limit=limit,
            offset=self.offset,
            include_related=self.include_related,
            language=self.language,
        )

    def with_offset(self, offset: int) -> "SearchQuery":
        """Create new query with different offset.

        Args:
            offset: New offset value.

        Returns:
            New SearchQuery with updated offset.
        """
        return SearchQuery(
            query=self.query,
            search_type=self.search_type,
            categories=self.categories,
            priority_min=self.priority_min,
            priority_max=self.priority_max,
            limit=self.limit,
            offset=offset,
            include_related=self.include_related,
            language=self.language,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "query": self.query,
            "search_type": self.search_type,
            "categories": [c.value for c in self.categories],
            "priority_min": self.priority_min.value,
            "priority_max": self.priority_max.value,
            "limit": self.limit,
            "offset": self.offset,
            "include_related": self.include_related,
            "language": self.language,
        }
