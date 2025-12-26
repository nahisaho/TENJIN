"""SearchResult value object - Encapsulates search result data."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SearchResult:
    """Immutable search result.

    Attributes:
        id: Entity ID.
        entity_type: Type of entity (theory, concept, etc.).
        name: Entity name.
        score: Relevance score (0.0-1.0).
        snippet: Text snippet showing match.
        metadata: Additional metadata.
    """

    id: str
    entity_type: str
    name: str
    score: float
    snippet: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate search result."""
        if not 0.0 <= self.score <= 1.0:
            # Clamp score to valid range
            object.__setattr__(self, "score", max(0.0, min(1.0, self.score)))

    @property
    def is_high_relevance(self) -> bool:
        """Check if result is highly relevant.

        Returns:
            True if score >= 0.8.
        """
        return self.score >= 0.8

    @property
    def is_medium_relevance(self) -> bool:
        """Check if result is medium relevance.

        Returns:
            True if 0.5 <= score < 0.8.
        """
        return 0.5 <= self.score < 0.8

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "name": self.name,
            "score": self.score,
            "snippet": self.snippet,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class SearchResults:
    """Collection of search results with metadata.

    Attributes:
        results: List of search results.
        total_count: Total matching results (before pagination).
        query: Original query string.
        search_type: Type of search performed.
    """

    results: tuple[SearchResult, ...]
    total_count: int
    query: str
    search_type: str

    @property
    def count(self) -> int:
        """Get number of results in this page.

        Returns:
            Number of results.
        """
        return len(self.results)

    @property
    def has_more(self) -> bool:
        """Check if there are more results.

        Returns:
            True if total_count > count.
        """
        return self.total_count > self.count

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "results": [r.to_dict() for r in self.results],
            "count": self.count,
            "total_count": self.total_count,
            "query": self.query,
            "search_type": self.search_type,
            "has_more": self.has_more,
        }
