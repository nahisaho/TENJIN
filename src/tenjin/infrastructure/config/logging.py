"""Logging configuration for TENJIN."""

import logging
import sys
from typing import Literal

from .settings import get_settings


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None = None,
) -> logging.Logger:
    """Configure and return the root logger.

    Args:
        level: Optional override for log level. Uses settings if not provided.

    Returns:
        Configured root logger.
    """
    settings = get_settings()
    log_level = level or settings.log_level

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure stream handler (stderr for MCP compatibility)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger("tenjin")
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Set third-party loggers to WARNING to reduce noise
    for logger_name in ["neo4j", "chromadb", "httpx", "httpcore"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Args:
        name: Logger name, typically __name__.

    Returns:
        Logger instance.
    """
    return logging.getLogger(f"tenjin.{name}")
