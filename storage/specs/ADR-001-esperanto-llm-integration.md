# ADR-001: esperantoによるマルチLLM統合

**ID**: ADR-001
**Status**: Accepted
**Created**: 2025-12-26
**Decision Makers**: GitHub Copilot
**Related**: REQ-001, DESIGN-001

---

## Context

TENJINシステムでは、教育理論の分析・推論・生成機能にLLMを活用する必要がある。参照実装（TENGIN-GraphRAG）では限定的なLLM連携（埋め込みのみ）だったが、TENJINでは本格的なLLM推論機能を提供する。

### 要件

1. マルチプロバイダー対応（OpenAI、Anthropic、Google、Ollama等）
2. プロバイダー切り替えの容易性
3. フォールバック機能
4. ストリーミングサポート
5. 非同期処理対応
6. 統一されたAPI

---

## Decision

**esperanto** ライブラリを採用する。

```python
from esperanto import LanguageModelRouter, EmbeddingModelRouter

# LLM Router
llm = LanguageModelRouter(
    provider="openai",
    model="gpt-4o-mini",
    fallback_providers=["anthropic", "ollama"]
)

# Embedding Router
embedding = EmbeddingModelRouter(
    provider="openai",
    model="text-embedding-3-small"
)
```

---

## Alternatives Considered

### 1. 直接SDK利用（OpenAI SDK等）

| Pros | Cons |
|------|------|
| シンプル | プロバイダーごとに異なるAPI |
| 最新機能即座に利用 | 切り替え時のコード変更大 |
| | ベンダーロックイン |

### 2. LangChain

| Pros | Cons |
|------|------|
| 豊富な機能 | 重量級（学習コスト高） |
| 広いコミュニティ | オーバーヘッド |
| | 本プロジェクトには過剰 |

### 3. LiteLLM

| Pros | Cons |
|------|------|
| 軽量 | esperantoより機能限定 |
| 多プロバイダー対応 | コミュニティ小さめ |

### 4. esperanto（選択）

| Pros | Cons |
|------|------|
| 15+プロバイダー対応 | 比較的新しいライブラリ |
| 統一API | ドキュメント限定 |
| フォールバック機能 | |
| 軽量かつ十分な機能 | |
| ストリーミング対応 | |

---

## Consequences

### Positive

1. **プロバイダー柔軟性**: 環境変数でプロバイダー切り替え可能
2. **コスト最適化**: 用途に応じてモデル選択
3. **可用性向上**: フォールバックで障害対応
4. **開発効率**: 統一APIで学習コスト低減

### Negative

1. **依存リスク**: esperantoのメンテナンス状況に依存
2. **最新機能遅延**: プロバイダー固有機能は遅れて対応

### Mitigations

1. esperanto Adapterを抽象化し、必要時に差し替え可能に
2. 重要な機能は直接SDK呼び出しも可能な設計に

---

## Implementation

### 1. esperanto Adapter

```python
# src/tenjin/infrastructure/adapters/esperanto_adapter.py

from typing import AsyncIterator
from esperanto import LanguageModelRouter, EmbeddingModelRouter
from pydantic import BaseModel

class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    fallback_providers: list[str] = ["anthropic", "ollama"]
    temperature: float = 0.7
    max_tokens: int = 4096

class EsperantoAdapter:
    def __init__(self, config: LLMConfig):
        self.llm = LanguageModelRouter(
            provider=config.provider,
            model=config.model,
            fallback_providers=config.fallback_providers
        )
        self.embedding = EmbeddingModelRouter(
            provider="openai",
            model="text-embedding-3-small"
        )
    
    async def chat(
        self,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None
    ) -> str:
        """Chat completion"""
        response = await self.llm.achat(
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens
        )
        return response.content
    
    async def stream_chat(
        self,
        messages: list[dict]
    ) -> AsyncIterator[str]:
        """Streaming chat completion"""
        async for chunk in self.llm.astream_chat(messages=messages):
            yield chunk.content
    
    async def embed(self, text: str) -> list[float]:
        """Generate embedding"""
        response = await self.embedding.aembed(text)
        return response.embedding
    
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding"""
        return [await self.embed(t) for t in texts]
```

### 2. 環境変数設定

```bash
# .env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_FALLBACK_PROVIDERS=anthropic,ollama
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### 3. サービス層での利用

```python
# src/tenjin/application/services/reasoning_service.py

class ReasoningService:
    def __init__(self, llm_adapter: EsperantoAdapter, theory_repo: TheoryRepository):
        self.llm = llm_adapter
        self.theory_repo = theory_repo
    
    async def analyze_theory(self, theory_id: str) -> TheoryAnalysis:
        """理論を分析"""
        theory = await self.theory_repo.get_by_id(theory_id)
        
        messages = [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": f"次の教育理論を分析してください:\n\n{theory.to_prompt()}"}
        ]
        
        analysis = await self.llm.chat(messages)
        return TheoryAnalysis.parse(analysis)
```

---

## References

- [esperanto GitHub](https://github.com/lfnovo/esperanto)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [REQ-001 Requirements](./REQ-001-tenjin-education-graphrag.md)
