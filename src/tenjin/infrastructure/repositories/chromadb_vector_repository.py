"""ChromaDB implementation of VectorRepository."""

from typing import Any, Sequence

from ...domain.repositories.vector_repository import VectorRepository
from ...domain.value_objects.search_query import SearchQuery
from ...domain.value_objects.search_result import SearchResult, SearchResults
from ..adapters.chromadb_adapter import ChromaDBAdapter
from ..adapters.esperanto_adapter import EmbeddingAdapter, EsperantoAdapter
from ..config.logging import get_logger

logger = get_logger(__name__)


class ChromaDBVectorRepository(VectorRepository):
    """ChromaDB implementation of VectorRepository.

    Provides vector search operations using ChromaDB for storage
    and esperanto for embeddings.
    """

    def __init__(
        self,
        chromadb_adapter: ChromaDBAdapter,
        embedding_adapter: EmbeddingAdapter,
        llm_adapter: EsperantoAdapter | None = None,
    ) -> None:
        """Initialize repository.

        Args:
            chromadb_adapter: ChromaDB adapter for storage.
            embedding_adapter: Esperanto embedding adapter.
            llm_adapter: Optional LLM adapter for reranking.
        """
        self._chromadb = chromadb_adapter
        self._embedding = embedding_adapter
        self._llm = llm_adapter

    async def semantic_search(
        self,
        query: SearchQuery,
    ) -> SearchResults:
        """Perform semantic search using embeddings."""
        # Generate query embedding
        query_embedding = await self._embedding.embed(query.query)

        # Build where filter
        where_filter: dict[str, Any] | None = None
        if query.categories:
            if len(query.categories) == 1:
                where_filter = {"category": query.categories[0].value}
            else:
                where_filter = {
                    "$or": [{"category": c.value} for c in query.categories]
                }

        # Execute search
        results = self._chromadb.query(
            query_embeddings=[query_embedding],
            n_results=query.limit,
            where=where_filter,
            include=["metadatas", "documents", "distances"],
        )

        # Convert to SearchResults
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                # Convert cosine distance to similarity score
                score = max(0.0, 1.0 - distance)

                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""

                search_results.append(
                    SearchResult(
                        id=doc_id,
                        entity_type=metadata.get("entity_type", "theory"),
                        name=metadata.get("name", ""),
                        score=score,
                        snippet=document[:300] if document else "",
                        metadata=metadata,
                    )
                )

        return SearchResults(
            results=tuple(search_results),
            total_count=len(search_results),
            query=query.query,
            search_type="semantic",
        )

    async def similar_to(
        self,
        entity_id: str,
        entity_type: str,
        limit: int = 10,
    ) -> Sequence[SearchResult]:
        """Find entities similar to a given entity."""
        # Get the entity's embedding
        existing = self._chromadb.get(ids=[entity_id], include=["embeddings"])

        if not existing["embeddings"] or not existing["embeddings"][0]:
            logger.warning(f"No embedding found for entity: {entity_id}")
            return []

        entity_embedding = existing["embeddings"][0]

        # Search for similar
        results = self._chromadb.query(
            query_embeddings=[entity_embedding],
            n_results=limit + 1,  # +1 to exclude self
            where={"entity_type": entity_type} if entity_type else None,
            include=["metadatas", "documents", "distances"],
        )

        # Convert results, excluding the query entity itself
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                if doc_id == entity_id:
                    continue

                distance = results["distances"][0][i] if results["distances"] else 0
                score = max(0.0, 1.0 - distance)
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""

                search_results.append(
                    SearchResult(
                        id=doc_id,
                        entity_type=metadata.get("entity_type", entity_type),
                        name=metadata.get("name", ""),
                        score=score,
                        snippet=document[:300] if document else "",
                        metadata=metadata,
                    )
                )

                if len(search_results) >= limit:
                    break

        return search_results

    async def add_embedding(
        self,
        entity_id: str,
        entity_type: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add or update embedding for an entity."""
        try:
            # Generate embedding
            embedding = await self._embedding.embed(text)

            # Prepare metadata
            full_metadata = metadata or {}
            full_metadata["entity_type"] = entity_type

            # Upsert to ChromaDB
            self._chromadb.upsert(
                ids=[entity_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[full_metadata],
            )

            logger.debug(f"Added embedding for {entity_type}: {entity_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add embedding: {e}")
            return False

    async def delete_embedding(self, entity_id: str) -> bool:
        """Delete embedding for an entity."""
        try:
            self._chromadb.delete(ids=[entity_id])
            logger.debug(f"Deleted embedding: {entity_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete embedding: {e}")
            return False

    async def get_embedding(self, entity_id: str) -> list[float] | None:
        """Get raw embedding vector for an entity."""
        try:
            results = self._chromadb.get(ids=[entity_id], include=["embeddings"])
            if results["embeddings"] and results["embeddings"][0]:
                return results["embeddings"][0]
            return None
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None

    async def batch_add_embeddings(
        self,
        items: Sequence[dict[str, Any]],
    ) -> int:
        """Add multiple embeddings in batch."""
        if not items:
            return 0

        try:
            # Extract texts for batch embedding
            texts = [item["text"] for item in items]
            embeddings = await self._embedding.embed_batch(texts)

            # Prepare data for upsert
            ids = [item["id"] for item in items]
            documents = texts
            metadatas = [
                {
                    "entity_type": item.get("type", "unknown"),
                    "name": item.get("name", ""),
                    **item.get("metadata", {}),
                }
                for item in items
            ]

            # Batch upsert
            self._chromadb.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

            logger.info(f"Batch added {len(items)} embeddings")
            return len(items)
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return 0

    async def hybrid_search(
        self,
        query: SearchQuery,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
    ) -> SearchResults:
        """Perform hybrid search combining keyword and semantic."""
        # Get semantic results
        semantic_results = await self.semantic_search(query.with_limit(query.limit * 2))

        # For hybrid, we adjust scores based on keyword matches
        hybrid_results = []
        query_terms = query.query.lower().split()

        for result in semantic_results.results:
            # Calculate keyword score based on term matches
            text_to_search = f"{result.name} {result.snippet}".lower()
            matches = sum(1 for term in query_terms if term in text_to_search)
            keyword_score = min(1.0, matches / max(len(query_terms), 1))

            # Combine scores
            hybrid_score = (
                semantic_weight * result.score + keyword_weight * keyword_score
            )

            hybrid_results.append(
                SearchResult(
                    id=result.id,
                    entity_type=result.entity_type,
                    name=result.name,
                    score=hybrid_score,
                    snippet=result.snippet,
                    metadata={
                        **result.metadata,
                        "semantic_score": result.score,
                        "keyword_score": keyword_score,
                    },
                )
            )

        # Sort by hybrid score and limit
        hybrid_results.sort(key=lambda x: x.score, reverse=True)
        hybrid_results = hybrid_results[: query.limit]

        return SearchResults(
            results=tuple(hybrid_results),
            total_count=semantic_results.total_count,
            query=query.query,
            search_type="hybrid",
        )

    async def rerank_results(
        self,
        query: str,
        results: Sequence[SearchResult],
        top_k: int = 10,
    ) -> Sequence[SearchResult]:
        """Rerank search results using LLM."""
        if not self._llm or not results:
            return list(results)[:top_k]

        # Prepare documents for reranking
        documents = [
            {
                "id": r.id,
                "content": f"{r.name}: {r.snippet}",
                "original_score": r.score,
            }
            for r in results
        ]

        # Use LLM to rerank
        reranked = await self._llm.rerank(query, documents, top_k)

        # Map back to SearchResults
        id_to_result = {r.id: r for r in results}
        reranked_results = []

        for i, doc in enumerate(reranked):
            original = id_to_result.get(doc["id"])
            if original:
                reranked_results.append(
                    SearchResult(
                        id=original.id,
                        entity_type=original.entity_type,
                        name=original.name,
                        score=1.0 - (i / len(reranked)),  # Position-based score
                        snippet=original.snippet,
                        metadata={
                            **original.metadata,
                            "rerank_position": i + 1,
                            "original_score": original.score,
                        },
                    )
                )

        return reranked_results

    async def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the vector collection."""
        stats = self._chromadb.get_statistics()

        # Get entity type breakdown
        all_docs = self._chromadb.get(include=["metadatas"])
        type_counts: dict[str, int] = {}

        if all_docs["metadatas"]:
            for metadata in all_docs["metadatas"]:
                entity_type = metadata.get("entity_type", "unknown")
                type_counts[entity_type] = type_counts.get(entity_type, 0) + 1

        return {
            **stats,
            "entity_type_counts": type_counts,
        }

    async def clear_collection(self) -> bool:
        """Clear all embeddings from the collection."""
        try:
            self._chromadb.reset()
            logger.warning("Vector collection cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
