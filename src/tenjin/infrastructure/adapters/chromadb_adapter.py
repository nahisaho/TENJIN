"""ChromaDB adapter for vector database operations."""

from typing import Any, Sequence

import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config.logging import get_logger
from ..config.settings import get_settings

logger = get_logger(__name__)


class ChromaDBAdapter:
    """Adapter for ChromaDB vector database operations.

    Provides interface for embedding storage and semantic search.
    """

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        """Initialize ChromaDB adapter.

        Args:
            persist_dir: Directory for persistent storage.
            collection_name: Name of the collection to use.
        """
        settings = get_settings()
        self._persist_dir = persist_dir or settings.chromadb.persist_dir
        self._collection_name = collection_name or settings.chromadb.collection_name
        self._client: chromadb.ClientAPI | None = None
        self._collection: chromadb.Collection | None = None

    def connect(self) -> None:
        """Initialize ChromaDB client and collection."""
        if self._client is None:
            logger.info(f"Initializing ChromaDB at {self._persist_dir}")
            self._client = chromadb.PersistentClient(
                path=self._persist_dir,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                f"ChromaDB collection '{self._collection_name}' initialized "
                f"with {self._collection.count()} documents"
            )

    def close(self) -> None:
        """Close ChromaDB connection (persists automatically)."""
        logger.info("ChromaDB connection closed")
        self._client = None
        self._collection = None

    @property
    def collection(self) -> chromadb.Collection:
        """Get the active collection.

        Returns:
            ChromaDB collection.

        Raises:
            RuntimeError: If not connected.
        """
        if self._collection is None:
            self.connect()
        return self._collection  # type: ignore

    def add(
        self,
        ids: Sequence[str],
        embeddings: Sequence[list[float]] | None = None,
        documents: Sequence[str] | None = None,
        metadatas: Sequence[dict[str, Any]] | None = None,
    ) -> None:
        """Add documents to the collection.

        Args:
            ids: Document IDs.
            embeddings: Pre-computed embeddings (optional).
            documents: Document texts (for auto-embedding).
            metadatas: Document metadata.
        """
        kwargs: dict[str, Any] = {"ids": list(ids)}

        if embeddings is not None:
            kwargs["embeddings"] = list(embeddings)
        if documents is not None:
            kwargs["documents"] = list(documents)
        if metadatas is not None:
            kwargs["metadatas"] = list(metadatas)

        self.collection.add(**kwargs)
        logger.debug(f"Added {len(ids)} documents to ChromaDB")

    def upsert(
        self,
        ids: Sequence[str],
        embeddings: Sequence[list[float]] | None = None,
        documents: Sequence[str] | None = None,
        metadatas: Sequence[dict[str, Any]] | None = None,
    ) -> None:
        """Upsert documents to the collection.

        Args:
            ids: Document IDs.
            embeddings: Pre-computed embeddings (optional).
            documents: Document texts.
            metadatas: Document metadata.
        """
        kwargs: dict[str, Any] = {"ids": list(ids)}

        if embeddings is not None:
            kwargs["embeddings"] = list(embeddings)
        if documents is not None:
            kwargs["documents"] = list(documents)
        if metadatas is not None:
            kwargs["metadatas"] = list(metadatas)

        self.collection.upsert(**kwargs)
        logger.debug(f"Upserted {len(ids)} documents to ChromaDB")

    def query(
        self,
        query_embeddings: Sequence[list[float]] | None = None,
        query_texts: Sequence[str] | None = None,
        n_results: int = 10,
        where: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> dict[str, Any]:
        """Query the collection.

        Args:
            query_embeddings: Embeddings to query with.
            query_texts: Texts to query with (auto-embedded).
            n_results: Number of results to return.
            where: Filter conditions.
            include: Fields to include in results.

        Returns:
            Query results dictionary.
        """
        kwargs: dict[str, Any] = {"n_results": n_results}

        if query_embeddings is not None:
            kwargs["query_embeddings"] = list(query_embeddings)
        elif query_texts is not None:
            kwargs["query_texts"] = list(query_texts)

        if where is not None:
            kwargs["where"] = where
        if include is not None:
            kwargs["include"] = include
        else:
            kwargs["include"] = ["metadatas", "documents", "distances"]

        return self.collection.query(**kwargs)

    def get(
        self,
        ids: Sequence[str] | None = None,
        where: dict[str, Any] | None = None,
        limit: int | None = None,
        include: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get documents from the collection.

        Args:
            ids: Specific document IDs to retrieve.
            where: Filter conditions.
            limit: Maximum number of results.
            include: Fields to include.

        Returns:
            Retrieved documents.
        """
        kwargs: dict[str, Any] = {}

        if ids is not None:
            kwargs["ids"] = list(ids)
        if where is not None:
            kwargs["where"] = where
        if limit is not None:
            kwargs["limit"] = limit
        if include is not None:
            kwargs["include"] = include
        else:
            kwargs["include"] = ["metadatas", "documents", "embeddings"]

        return self.collection.get(**kwargs)

    def delete(
        self,
        ids: Sequence[str] | None = None,
        where: dict[str, Any] | None = None,
    ) -> None:
        """Delete documents from the collection.

        Args:
            ids: Document IDs to delete.
            where: Filter conditions for deletion.
        """
        kwargs: dict[str, Any] = {}

        if ids is not None:
            kwargs["ids"] = list(ids)
        if where is not None:
            kwargs["where"] = where

        self.collection.delete(**kwargs)
        logger.debug(f"Deleted documents from ChromaDB")

    def count(self) -> int:
        """Get the number of documents in the collection.

        Returns:
            Document count.
        """
        return self.collection.count()

    def reset(self) -> None:
        """Reset the collection (delete all documents)."""
        logger.warning(f"Resetting ChromaDB collection '{self._collection_name}'")
        if self._client:
            self._client.delete_collection(self._collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    def health_check(self) -> bool:
        """Check if ChromaDB is healthy.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            _ = self.collection.count()
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get collection statistics.

        Returns:
            Dictionary with collection stats.
        """
        return {
            "collection_name": self._collection_name,
            "document_count": self.count(),
            "persist_directory": self._persist_dir,
        }
