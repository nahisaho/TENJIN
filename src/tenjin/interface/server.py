"""MCP Server - Main entry point for TENJIN educational theory GraphRAG."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

from ..infrastructure.config.settings import get_settings
from ..infrastructure.config.logging import get_logger, setup_logging
from ..infrastructure.adapters.neo4j_adapter import Neo4jAdapter
from ..infrastructure.adapters.chromadb_adapter import ChromaDBAdapter
from ..infrastructure.adapters.esperanto_adapter import EsperantoAdapter
from ..infrastructure.adapters.embedding_adapter import EmbeddingAdapter
from ..infrastructure.repositories.neo4j_theory_repository import Neo4jTheoryRepository
from ..infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
from ..infrastructure.repositories.chromadb_vector_repository import ChromaDBVectorRepository
from ..application.services import (
    TheoryService,
    SearchService,
    GraphService,
    AnalysisService,
    RecommendationService,
    CitationService,
    MethodologyService,
)

logger = get_logger(__name__)


class TenjinServer:
    """TENJIN MCP Server for educational theory GraphRAG."""

    def __init__(self) -> None:
        """Initialize TENJIN server."""
        self._settings = get_settings()
        self._server = Server("tenjin")
        self._initialized = False

        # Adapters
        self._neo4j: Neo4jAdapter | None = None
        self._chromadb: ChromaDBAdapter | None = None
        self._llm: EsperantoAdapter | None = None
        self._embedding: EmbeddingAdapter | None = None

        # Repositories
        self._theory_repo: Neo4jTheoryRepository | None = None
        self._graph_repo: Neo4jGraphRepository | None = None
        self._vector_repo: ChromaDBVectorRepository | None = None

        # Services
        self._theory_service: TheoryService | None = None
        self._search_service: SearchService | None = None
        self._graph_service: GraphService | None = None
        self._analysis_service: AnalysisService | None = None
        self._recommendation_service: RecommendationService | None = None
        self._citation_service: CitationService | None = None
        self._methodology_service: MethodologyService | None = None

    async def initialize(self) -> None:
        """Initialize all adapters, repositories, and services."""
        if self._initialized:
            return

        logger.info("Initializing TENJIN server...")

        # Initialize adapters
        self._neo4j = Neo4jAdapter(
            uri=self._settings.neo4j.uri,
            username=self._settings.neo4j.username,
            password=self._settings.neo4j.password,
            database=self._settings.neo4j.database,
        )
        await self._neo4j.connect()

        self._chromadb = ChromaDBAdapter(
            persist_directory=self._settings.chromadb.persist_directory,
            collection_name=self._settings.chromadb.collection_name,
        )
        await self._chromadb.initialize()

        self._llm = EsperantoAdapter(
            provider=self._settings.llm.provider,
            model=self._settings.llm.model,
            api_key=self._settings.llm.api_key,
        )

        self._embedding = EmbeddingAdapter(
            provider=self._settings.embedding.provider,
            model=self._settings.embedding.model,
            api_key=self._settings.embedding.api_key,
        )

        # Initialize repositories
        self._theory_repo = Neo4jTheoryRepository(self._neo4j)
        self._graph_repo = Neo4jGraphRepository(self._neo4j)
        self._vector_repo = ChromaDBVectorRepository(
            self._chromadb, self._embedding
        )

        # Initialize services
        self._theory_service = TheoryService(self._theory_repo)
        self._search_service = SearchService(
            self._vector_repo,
            self._theory_repo,
            self._llm,
        )
        self._graph_service = GraphService(self._graph_repo)
        self._analysis_service = AnalysisService(
            self._theory_repo,
            self._graph_repo,
            self._llm,
        )
        self._recommendation_service = RecommendationService(
            self._theory_repo,
            self._vector_repo,
            self._graph_repo,
            self._llm,
        )
        self._citation_service = CitationService(self._theory_repo)
        self._methodology_service = MethodologyService(
            self._theory_repo,
            self._vector_repo,
            self._llm,
        )

        self._initialized = True
        logger.info("TENJIN server initialized successfully")

    async def shutdown(self) -> None:
        """Shutdown all connections."""
        logger.info("Shutting down TENJIN server...")

        if self._neo4j:
            await self._neo4j.close()

        self._initialized = False
        logger.info("TENJIN server shutdown complete")

    @property
    def server(self) -> Server:
        """Get MCP server instance."""
        return self._server

    @property
    def theory_service(self) -> TheoryService:
        """Get theory service."""
        if not self._theory_service:
            raise RuntimeError("Server not initialized")
        return self._theory_service

    @property
    def search_service(self) -> SearchService:
        """Get search service."""
        if not self._search_service:
            raise RuntimeError("Server not initialized")
        return self._search_service

    @property
    def graph_service(self) -> GraphService:
        """Get graph service."""
        if not self._graph_service:
            raise RuntimeError("Server not initialized")
        return self._graph_service

    @property
    def analysis_service(self) -> AnalysisService:
        """Get analysis service."""
        if not self._analysis_service:
            raise RuntimeError("Server not initialized")
        return self._analysis_service

    @property
    def recommendation_service(self) -> RecommendationService:
        """Get recommendation service."""
        if not self._recommendation_service:
            raise RuntimeError("Server not initialized")
        return self._recommendation_service

    @property
    def citation_service(self) -> CitationService:
        """Get citation service."""
        if not self._citation_service:
            raise RuntimeError("Server not initialized")
        return self._citation_service

    @property
    def methodology_service(self) -> MethodologyService:
        """Get methodology service."""
        if not self._methodology_service:
            raise RuntimeError("Server not initialized")
        return self._methodology_service


# Global server instance
_tenjin_server: TenjinServer | None = None


def get_tenjin_server() -> TenjinServer:
    """Get global TENJIN server instance."""
    global _tenjin_server
    if _tenjin_server is None:
        _tenjin_server = TenjinServer()
    return _tenjin_server


@asynccontextmanager
async def server_lifespan() -> AsyncIterator[TenjinServer]:
    """Server lifespan context manager."""
    server = get_tenjin_server()
    try:
        await server.initialize()
        yield server
    finally:
        await server.shutdown()


async def main() -> None:
    """Main entry point."""
    setup_logging()
    logger.info("Starting TENJIN MCP Server...")

    async with server_lifespan() as tenjin:
        # Register tools, resources, and prompts
        from .tools import register_tools
        from .resources import register_resources
        from .prompts import register_prompts

        register_tools(tenjin.server, tenjin)
        register_resources(tenjin.server, tenjin)
        register_prompts(tenjin.server, tenjin)

        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await tenjin.server.run(
                read_stream,
                write_stream,
                tenjin.server.create_initialization_options(),
            )


def run() -> None:
    """Run the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
