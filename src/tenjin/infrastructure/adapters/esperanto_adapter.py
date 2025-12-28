"""Esperanto adapter for LLM and embedding operations."""

from typing import Any

from esperanto import LanguageModel, provider_classes
from esperanto.providers.embedding.ollama import OllamaEmbeddingModel
from esperanto.providers.embedding.openai import OpenAIEmbeddingModel

from ..config.logging import get_logger
from ..config.settings import get_settings

logger = get_logger(__name__)


class EsperantoAdapter:
    """Adapter for esperanto LLM operations.

    Provides unified interface for multiple LLM providers through esperanto.
    Supports automatic fallback to alternative providers on failure.
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        fallback_providers: list[str] | None = None,
    ) -> None:
        """Initialize esperanto adapter.

        Args:
            provider: Primary LLM provider name.
            model: Model name to use.
            temperature: Generation temperature.
            max_tokens: Maximum tokens for generation.
            fallback_providers: List of fallback provider names.
        """
        settings = get_settings()
        self._provider = provider or settings.llm.provider
        self._model = model or settings.llm.model
        self._temperature = temperature or settings.llm.temperature
        self._max_tokens = max_tokens or settings.llm.max_tokens
        self._fallback_providers = (
            fallback_providers or settings.llm.fallback_provider_list
        )
        self._llm: LanguageModel | None = None

    def _create_llm(self, provider: str | None = None) -> LanguageModel:
        """Create a language model instance.

        Args:
            provider: Provider to use (defaults to primary).

        Returns:
            Configured LanguageModel instance.
        """
        use_provider = provider or self._provider
        logger.debug(f"Creating LLM with provider: {use_provider}, model: {self._model}")

        return LanguageModel(
            provider=use_provider,
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )

    @property
    def llm(self) -> LanguageModel:
        """Get or create the language model.

        Returns:
            LanguageModel instance.
        """
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional generation parameters.

        Returns:
            Generated text.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Try primary provider
        providers_to_try = [self._provider] + self._fallback_providers

        for provider in providers_to_try:
            try:
                llm = self._create_llm(provider) if provider != self._provider else self.llm
                response = await llm.chat_async(messages, **kwargs)
                return response.content
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                if provider == providers_to_try[-1]:
                    raise RuntimeError(f"All LLM providers failed. Last error: {e}")

        return ""

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: str | None = None,
    ) -> str:
        """Generate text with additional context.

        Args:
            prompt: User prompt.
            context: Context to include.
            system_prompt: Optional system prompt.

        Returns:
            Generated text.
        """
        full_prompt = f"Context:\n{context}\n\nQuery: {prompt}"
        return await self.generate(full_prompt, system_prompt)

    async def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Rerank documents based on relevance to query.

        Args:
            query: Search query.
            documents: List of documents with 'content' field.
            top_k: Number of documents to return.

        Returns:
            Reranked documents with scores.
        """
        if not documents:
            return []

        # Create reranking prompt
        doc_list = "\n".join(
            f"{i+1}. {doc.get('content', doc.get('name', ''))[:200]}"
            for i, doc in enumerate(documents[:20])  # Limit to 20 for context
        )

        prompt = f"""Given the query: "{query}"

Rank the following documents by relevance (most relevant first).
Return only the numbers of the top {top_k} most relevant documents, separated by commas.

Documents:
{doc_list}

Ranking (numbers only, comma-separated):"""

        try:
            response = await self.generate(prompt)
            # Parse response to get rankings
            rankings = [
                int(x.strip()) - 1
                for x in response.split(",")
                if x.strip().isdigit()
            ]

            # Reorder documents based on rankings
            reranked = []
            for idx in rankings[:top_k]:
                if 0 <= idx < len(documents):
                    doc = documents[idx].copy()
                    doc["rerank_position"] = len(reranked) + 1
                    reranked.append(doc)

            return reranked
        except Exception as e:
            logger.warning(f"Reranking failed, returning original order: {e}")
            return documents[:top_k]

    def get_available_providers(self) -> list[str]:
        """Get list of available LLM providers.

        Returns:
            List of provider names.
        """
        # Extract provider names from class names (e.g., "OpenAILanguageModel" -> "openai")
        return [
            cls.replace("LanguageModel", "").lower()
            for cls in provider_classes
            if "LanguageModel" in cls
        ]

    def health_check(self) -> bool:
        """Check if LLM provider is accessible.

        Returns:
            True if healthy.
        """
        try:
            # Just verify we can create the model
            _ = self.llm
            return True
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False


class EmbeddingAdapter:
    """Adapter for esperanto embedding operations.

    Provides text embedding functionality through esperanto.
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize embedding adapter.

        Args:
            provider: Embedding provider name.
            model: Embedding model name.
        """
        settings = get_settings()
        self._provider = provider or settings.embedding.provider
        self._model = model or settings.embedding.model
        self._embedding_model: EmbeddingModel | None = None

    @property
    def embedding_model(self) -> OllamaEmbeddingModel | OpenAIEmbeddingModel:
        """Get or create the embedding model.

        Returns:
            EmbeddingModel instance.
        """
        if self._embedding_model is None:
            settings = get_settings()
            logger.debug(
                f"Creating embedding model: {self._provider}/{self._model}"
            )
            if self._provider == "ollama":
                self._embedding_model = OllamaEmbeddingModel(
                    model_name=self._model,
                    base_url=settings.embedding.base_url,
                )
            elif self._provider == "openai":
                self._embedding_model = OpenAIEmbeddingModel(
                    model_name=self._model,
                    api_key=settings.embedding.api_key,
                )
            else:
                # Default to Ollama
                self._embedding_model = OllamaEmbeddingModel(
                    model_name=self._model,
                    base_url=settings.embedding.base_url,
                )
        return self._embedding_model

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector.
        """
        result = await self.embedding_model.aembed([text])
        return result[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        if not texts:
            return []

        # Process in batches to avoid rate limits
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            result = await self.embedding_model.aembed(batch)
            all_embeddings.extend(result)

        return all_embeddings

    def embed_sync(self, text: str) -> list[float]:
        """Generate embedding synchronously.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector.
        """
        result = self.embedding_model.embed([text])
        return result[0]

    @property
    def dimension(self) -> int:
        """Get embedding dimension.

        Returns:
            Embedding dimension (default estimate).
        """
        # Common dimensions by model
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "voyage-large-2": 1024,
            "voyage-2": 1024,
        }
        return dimensions.get(self._model, 1536)

    def health_check(self) -> bool:
        """Check if embedding model is accessible.

        Returns:
            True if healthy.
        """
        try:
            _ = self.embed_sync("test")
            return True
        except Exception as e:
            logger.error(f"Embedding health check failed: {e}")
            return False
