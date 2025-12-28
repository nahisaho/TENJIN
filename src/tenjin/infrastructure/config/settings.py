"""Application configuration settings using Pydantic."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Neo4jSettings(BaseSettings):
    """Neo4j database settings."""

    model_config = SettingsConfigDict(env_prefix="NEO4J_")

    uri: str = Field(default="bolt://localhost:7687", description="Neo4j connection URI")
    user: str = Field(default="neo4j", description="Neo4j username")
    password: str = Field(default="password", description="Neo4j password")


class ChromaDBSettings(BaseSettings):
    """ChromaDB vector database settings."""

    model_config = SettingsConfigDict(env_prefix="CHROMA_")

    persist_dir: str = Field(default="./data/chromadb", description="ChromaDB persistence directory")
    collection_name: str = Field(default="tenjin_theories", description="Default collection name")


class LLMSettings(BaseSettings):
    """LLM provider settings for esperanto."""

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider: str = Field(default="openai", description="Primary LLM provider")
    model: str = Field(default="gpt-4o-mini", description="LLM model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: int = Field(default=4096, gt=0, description="Maximum tokens")
    fallback_providers: str = Field(
        default="anthropic,ollama",
        description="Comma-separated fallback providers",
    )

    @property
    def fallback_provider_list(self) -> list[str]:
        """Get fallback providers as list."""
        return [p.strip() for p in self.fallback_providers.split(",") if p.strip()]


class EmbeddingSettings(BaseSettings):
    """Embedding model settings."""

    model_config = SettingsConfigDict(
        env_prefix="EMBEDDING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider: str = Field(default="ollama", description="Embedding provider")
    model: str = Field(default="nomic-embed-text", description="Embedding model name")
    base_url: str = Field(default="http://localhost:11434", description="Embedding service base URL")
    api_key: str | None = Field(default=None, description="API key for embedding service")


class CacheSettings(BaseSettings):
    """Cache settings."""

    model_config = SettingsConfigDict(env_prefix="CACHE_")

    enabled: bool = Field(default=True, description="Enable caching")
    ttl_seconds: int = Field(default=3600, gt=0, description="Cache TTL in seconds")
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    debug: bool = Field(default=False, description="Debug mode")

    # API Keys (optional, esperanto will use env vars)
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    google_api_key: str | None = Field(default=None, description="Google API key")

    # Sub-settings
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    chromadb: ChromaDBSettings = Field(default_factory=ChromaDBSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
