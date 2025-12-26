"""Neo4j database adapter for graph operations."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Sequence

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from ..config.logging import get_logger
from ..config.settings import get_settings

logger = get_logger(__name__)


class Neo4jAdapter:
    """Adapter for Neo4j graph database operations.

    Provides async interface for Neo4j operations with connection pooling
    and automatic retry logic.
    """

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize Neo4j adapter.

        Args:
            uri: Neo4j connection URI.
            user: Database username.
            password: Database password.
        """
        settings = get_settings()
        self._uri = uri or settings.neo4j.uri
        self._user = user or settings.neo4j.user
        self._password = password or settings.neo4j.password
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        if self._driver is None:
            logger.info(f"Connecting to Neo4j at {self._uri}")
            self._driver = AsyncGraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
            )
            # Verify connectivity
            await self._driver.verify_connectivity()
            logger.info("Neo4j connection established")

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            logger.info("Closing Neo4j connection")
            await self._driver.close()
            self._driver = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Get a database session.

        Yields:
            AsyncSession for database operations.
        """
        if self._driver is None:
            await self.connect()

        async with self._driver.session() as session:  # type: ignore
            yield session

    async def execute_read(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> Sequence[dict[str, Any]]:
        """Execute a read query with retry logic.

        Args:
            query: Cypher query string.
            parameters: Query parameters.
            max_retries: Maximum retry attempts.

        Returns:
            List of result records as dictionaries.
        """
        parameters = parameters or {}

        for attempt in range(max_retries):
            try:
                async with self.session() as session:
                    result = await session.run(query, parameters)
                    records = await result.data()
                    return records
            except (ServiceUnavailable, SessionExpired) as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(
                        f"Neo4j query failed (attempt {attempt + 1}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Neo4j query failed after {max_retries} attempts")
                    raise

        return []

    async def execute_write(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a write query.

        Args:
            query: Cypher query string.
            parameters: Query parameters.

        Returns:
            Result summary as dictionary.
        """
        parameters = parameters or {}

        async with self.session() as session:
            result = await session.run(query, parameters)
            summary = await result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "nodes_deleted": summary.counters.nodes_deleted,
                "relationships_created": summary.counters.relationships_created,
                "relationships_deleted": summary.counters.relationships_deleted,
                "properties_set": summary.counters.properties_set,
            }

    async def execute_batch(
        self,
        queries: Sequence[tuple[str, dict[str, Any]]],
    ) -> Sequence[dict[str, Any]]:
        """Execute multiple queries in a transaction.

        Args:
            queries: List of (query, parameters) tuples.

        Returns:
            List of result summaries.
        """
        results = []

        async with self.session() as session:
            async with session.begin_transaction() as tx:
                for query, params in queries:
                    result = await tx.run(query, params)
                    summary = await result.consume()
                    results.append(
                        {
                            "nodes_created": summary.counters.nodes_created,
                            "relationships_created": summary.counters.relationships_created,
                        }
                    )
                await tx.commit()

        return results

    async def health_check(self) -> bool:
        """Check if Neo4j is healthy.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            result = await self.execute_read("RETURN 1 as n")
            return len(result) > 0 and result[0].get("n") == 1
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

    async def create_indexes(self) -> None:
        """Create necessary indexes for the knowledge graph."""
        indexes = [
            "CREATE INDEX theory_id IF NOT EXISTS FOR (t:Theory) ON (t.id)",
            "CREATE INDEX theory_name IF NOT EXISTS FOR (t:Theory) ON (t.name)",
            "CREATE INDEX theory_category IF NOT EXISTS FOR (t:Theory) ON (t.category)",
            "CREATE INDEX theorist_id IF NOT EXISTS FOR (t:Theorist) ON (t.id)",
            "CREATE INDEX theorist_name IF NOT EXISTS FOR (t:Theorist) ON (t.name)",
            "CREATE INDEX concept_id IF NOT EXISTS FOR (c:Concept) ON (c.id)",
            "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)",
            "CREATE INDEX category_type IF NOT EXISTS FOR (c:Category) ON (c.type)",
            "CREATE FULLTEXT INDEX theory_fulltext IF NOT EXISTS FOR (t:Theory) ON EACH [t.name, t.name_ja, t.description, t.description_ja]",
        ]

        for index_query in indexes:
            try:
                await self.execute_write(index_query)
                logger.debug(f"Created index: {index_query[:50]}...")
            except Exception as e:
                # Index may already exist
                logger.debug(f"Index creation note: {e}")

        logger.info("Neo4j indexes created/verified")

    async def clear_database(self) -> None:
        """Clear all data from the database. Use with caution!"""
        logger.warning("Clearing all Neo4j data")
        await self.execute_write("MATCH (n) DETACH DELETE n")

    async def get_statistics(self) -> dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with node and relationship counts.
        """
        query = """
        MATCH (n)
        WITH labels(n) as labels, count(*) as count
        UNWIND labels as label
        RETURN label, sum(count) as count
        ORDER BY count DESC
        """
        node_counts = await self.execute_read(query)

        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(*) as count
        ORDER BY count DESC
        """
        rel_counts = await self.execute_read(rel_query)

        return {
            "nodes": {r["label"]: r["count"] for r in node_counts},
            "relationships": {r["type"]: r["count"] for r in rel_counts},
        }
