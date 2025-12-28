"""MCP Server - Main entry point for TENJIN educational theory GraphRAG."""

import argparse
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
import uvicorn

from ..infrastructure.config.settings import get_settings
from ..infrastructure.config.logging import get_logger, setup_logging
from ..infrastructure.adapters.neo4j_adapter import Neo4jAdapter
from ..infrastructure.adapters.chromadb_adapter import ChromaDBAdapter
from ..infrastructure.adapters.esperanto_adapter import EsperantoAdapter
from ..infrastructure.adapters.esperanto_adapter import EmbeddingAdapter
from ..infrastructure.adapters.redis_adapter import RedisAdapter
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
    InferenceService,
    CacheService,
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
        self._redis: RedisAdapter | None = None

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
        self._inference_service: InferenceService | None = None
        self._cache_service: CacheService | None = None

    async def initialize(self) -> None:
        """Initialize all adapters, repositories, and services."""
        if self._initialized:
            return

        logger.info("Initializing TENJIN server...")

        # Initialize adapters
        self._neo4j = Neo4jAdapter(
            uri=self._settings.neo4j.uri,
            user=self._settings.neo4j.user,
            password=self._settings.neo4j.password,
        )
        await self._neo4j.connect()

        self._chromadb = ChromaDBAdapter(
            persist_dir=self._settings.chromadb.persist_dir,
            collection_name=self._settings.chromadb.collection_name,
        )
        self._chromadb.connect()

        self._llm = EsperantoAdapter(
            provider=self._settings.llm.provider,
            model=self._settings.llm.model,
        )

        self._embedding = EmbeddingAdapter(
            provider=self._settings.embedding.provider,
            model=self._settings.embedding.model,
        )

        # Initialize Redis adapter (optional - for caching)
        if self._settings.cache.enabled:
            try:
                self._redis = RedisAdapter(
                    url=self._settings.cache.redis_url,
                    default_ttl=self._settings.cache.ttl_seconds,
                )
                await self._redis.connect()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}. Continuing without cache.")
                self._redis = None

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
        self._inference_service = InferenceService(
            self._theory_repo,
            self._vector_repo,
            self._graph_repo,
            self._llm,
        )

        # Initialize cache service
        if self._redis:
            self._cache_service = CacheService(self._redis)
            logger.info("Cache service initialized")

        self._initialized = True
        logger.info("TENJIN server initialized successfully")

    async def shutdown(self) -> None:
        """Shutdown all connections."""
        logger.info("Shutting down TENJIN server...")

        if self._redis:
            await self._redis.close()

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

    @property
    def inference_service(self) -> InferenceService:
        """Get inference service."""
        if not self._inference_service:
            raise RuntimeError("Server not initialized")
        return self._inference_service

    @property
    def cache_service(self) -> CacheService | None:
        """Get cache service (may be None if Redis is not available)."""
        return self._cache_service

    @property
    def redis_adapter(self) -> RedisAdapter | None:
        """Get Redis adapter (may be None if not available)."""
        return self._redis

    def get_inference_service(self) -> InferenceService:
        """Get inference service (method form for tools)."""
        return self.inference_service


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
    """Main entry point (STDIO mode)."""
    setup_logging()
    logger.info("Starting TENJIN MCP Server (STDIO mode)...")

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


async def main_sse(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Main entry point (SSE mode for remote access)."""
    setup_logging()
    logger.info(f"Starting TENJIN MCP Server (SSE mode on {host}:{port})...")

    # Create SSE transport
    sse_transport = SseServerTransport("/messages/")

    async with server_lifespan() as tenjin:
        # Register tools, resources, and prompts
        from .tools import register_tools
        from .resources import register_resources
        from .prompts import register_prompts

        register_tools(tenjin.server, tenjin)
        register_resources(tenjin.server, tenjin)
        register_prompts(tenjin.server, tenjin)

        # SSE connection handler
        async def handle_sse(request: Request) -> Response:
            """Handle SSE connection."""
            logger.info(f"SSE connection from {request.client}")
            async with sse_transport.connect_sse(
                request.scope,
                request.receive,
                request._send,  # type: ignore
            ) as (read_stream, write_stream):
                await tenjin.server.run(
                    read_stream,
                    write_stream,
                    tenjin.server.create_initialization_options(),
                )
            return Response()

        # POST message handler
        async def handle_messages(request: Request) -> Response:
            """Handle POST messages."""
            await sse_transport.handle_post_message(
                request.scope,
                request.receive,
                request._send,  # type: ignore
            )
            return Response()

        # Health check endpoint
        async def health_check(request: Request) -> Response:
            """Health check endpoint."""
            return Response(
                content='{"status": "healthy", "service": "tenjin-mcp"}',
                media_type="application/json",
            )

        # Create Starlette app
        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/messages/", endpoint=handle_messages, methods=["POST"]),
                Route("/health", endpoint=health_check),
            ],
        )

        # Run with uvicorn
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


def run() -> None:
    """Run the server (with CLI argument parsing)."""
    parser = argparse.ArgumentParser(
        description="TENJIN - Educational Theory GraphRAG MCP Server"
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode: stdio (default) or sse",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for SSE mode (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for SSE mode (default: 8080)",
    )
    args = parser.parse_args()

    if args.mode == "sse":
        asyncio.run(main_sse(host=args.host, port=args.port))
    else:
        asyncio.run(main())


if __name__ == "__main__":
    run()
