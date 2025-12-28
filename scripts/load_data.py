#!/usr/bin/env python3
"""Script to load educational theory data into databases.

Usage:
    python -m scripts.load_data [--data-dir PATH] [--clear]

Options:
    --data-dir PATH    Directory containing JSON data files
    --clear            Clear existing data before loading
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tenjin.infrastructure.config.settings import get_settings
from tenjin.infrastructure.adapters.neo4j_adapter import Neo4jAdapter
from tenjin.infrastructure.adapters.chromadb_adapter import ChromaDBAdapter
from tenjin.infrastructure.adapters.esperanto_adapter import EmbeddingAdapter
from tenjin.infrastructure.data.data_loader import DataLoader


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


async def clear_databases(neo4j: Neo4jAdapter, chromadb: ChromaDBAdapter) -> None:
    """Clear all data from databases.

    Args:
        neo4j: Neo4j adapter.
        chromadb: ChromaDB adapter.
    """
    logging.info("Clearing existing data...")

    # Clear Neo4j
    await neo4j.execute_write("MATCH (n) DETACH DELETE n", {})
    logging.info("Cleared Neo4j database")

    # Clear ChromaDB collection
    try:
        await chromadb.delete_collection("theories")
        logging.info("Cleared ChromaDB theories collection")
    except Exception:
        logging.info("No existing ChromaDB collection to clear")


async def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Load educational theory data into TENJIN databases"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Directory containing JSON data files",
        default=Path(__file__).parent.parent / "data" / "theories",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before loading",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("TENJIN Data Loader")
    logger.info(f"Data directory: {args.data_dir}")

    # Validate data directory
    if not args.data_dir.exists():
        logger.error(f"Data directory not found: {args.data_dir}")
        return 1

    # Load settings
    settings = get_settings()

    # Initialize adapters
    neo4j_adapter = Neo4jAdapter(
        uri=settings.neo4j.uri,
        user=settings.neo4j.user,
        password=settings.neo4j.password,
    )
    chromadb_adapter = ChromaDBAdapter(persist_dir=settings.chromadb.persist_dir)
    embedding_adapter = EmbeddingAdapter(
        provider=settings.embedding.provider,
        model=settings.embedding.model,
    )

    try:
        # Connect to Neo4j
        logger.info("Connecting to Neo4j...")
        await neo4j_adapter.connect()
        logger.info("Connected to Neo4j")

        # Clear databases if requested
        if args.clear:
            await clear_databases(neo4j_adapter, chromadb_adapter)

        # Create data loader
        loader = DataLoader(
            neo4j_adapter=neo4j_adapter,
            chromadb_adapter=chromadb_adapter,
            embedding_adapter=embedding_adapter,
            data_dir=args.data_dir,
        )

        # Load all data
        logger.info("Loading data...")
        counts = await loader.load_all()

        # Print summary
        logger.info("=" * 50)
        logger.info("Data Loading Complete!")
        logger.info("=" * 50)
        for item_type, count in counts.items():
            logger.info(f"  {item_type.capitalize()}: {count}")
        logger.info("=" * 50)

        return 0

    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)
        return 1

    finally:
        await neo4j_adapter.close()
        logger.info("Disconnected from Neo4j")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
