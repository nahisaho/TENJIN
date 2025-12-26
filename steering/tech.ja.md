# Technology Stack

**Project**: TENJIN
**Last Updated**: 2025-12-26
**Status**: 確定

---

## Overview

TENJIN教育理論GraphRAG MCPサーバーのための技術スタック。参照実装（TENGIN-GraphRAG）を基盤としつつ、esperantoによるマルチLLM統合と高性能アーキテクチャを採用。

## 技術スタック概要

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| 言語 | Python | 3.11+ | メイン開発言語 |
| MCP Framework | FastMCP (mcp[cli]) | 1.5+ | MCPサーバー実装 |
| LLM統合 | esperanto | 2.12+ | マルチプロバイダーLLM連携 |
| Graph DB | Neo4j | 5.x | ナレッジグラフ格納 |
| Vector DB | ChromaDB | 0.5+ | ベクトル検索 |
| Data Validation | Pydantic | 2.0+ | スキーマ定義・バリデーション |
| Async Runtime | asyncio | - | 非同期処理 |
| Caching | Redis / メモリ | - | 階層型キャッシュ |
| Testing | pytest | 8.0+ | テストフレームワーク |
| Linting | ruff | 0.4+ | コード品質 |
| Type Checking | mypy | 1.0+ | 型チェック |
| Container | Docker Compose | latest | 開発・本番環境 |
| CI/CD | GitHub Actions | - | 自動テスト・デプロイ |

---

## 詳細

### プログラミング言語

**Python 3.11+**

```
理由:
- ML/AIエコシステムが最も充実
- esperanto、MCP SDKがPython対応
- Neo4j、ChromaDBクライアントが成熟
- 非同期処理（asyncio）のサポート
- 型ヒント（typing）の充実
```

主要ライブラリ:
- `esperanto` - マルチプロバイダーLLM統合
- `mcp[cli]` - MCP Server SDK
- `neo4j` - Neo4j Python Driver
- `chromadb` - Vector Database
- `pydantic` - Data Validation
- `httpx` - Async HTTP Client
- `structlog` - Structured Logging
- `tenacity` - リトライ処理

---

### MCP Server Framework

**FastMCP (mcp[cli]) 1.5+**

```
理由:
- Anthropic公式SDK
- STDIO/SSEトランスポートサポート
- Tools/Resources/Promptsの標準実装
- 非同期処理対応
- 型安全なスキーマ定義
```

機能:
- JSON-RPC 2.0プロトコル
- 自動スキーマ生成
- エラーハンドリング標準化
- ストリーミングサポート

---

### LLM統合

**esperanto 2.12+**

```
理由:
- 15以上のLLMプロバイダーを統一インターフェースで提供
- 軽量（直接HTTP通信、SDKなし）
- 非同期サポート
- タスク対応Embedding
- LangChain統合オプション
```

サポートプロバイダー:
| プロバイダー | LLM | Embedding | 主な用途 |
|-------------|-----|-----------|---------|
| OpenAI | ✅ | ✅ | 高品質推論 |
| Anthropic | ✅ | - | Claude連携 |
| Google GenAI | ✅ | ✅ | Gemini |
| Ollama | ✅ | ✅ | ローカル実行 |
| Azure OpenAI | ✅ | ✅ | エンタープライズ |
| Groq | ✅ | - | 高速推論 |
| Mistral | ✅ | ✅ | EU準拠 |
| OpenRouter | ✅ | - | モデルアクセス |
| Perplexity | ✅ | - | 検索統合 |

設定例:
```python
from esperanto.factory import AIFactory

# LLMインスタンス作成
llm = AIFactory.create_language(
    "openai",
    "gpt-4o",
    config={"temperature": 0.7}
)

# Embeddingインスタンス作成
embedder = AIFactory.create_embedding(
    "openai",
    "text-embedding-3-small"
)
```

---

### グラフデータベース

**Neo4j 5.x**

```
理由:
- 最も成熟したグラフDB
- Cypher言語による直感的なクエリ
- 高性能グラフトラバーサル
- 可視化ツール（Bloom/Browser）
- Community Edition無料
```

データソース:
- [References/Educational-theory-research.md](../References/Educational-theory-research.md)
- 200の教育理論、9カテゴリ、優先度1-5付き

スキーマ:
```cypher
// ノードタイプ
(:Theory), (:Theorist), (:Concept), (:Principle)
(:Evidence), (:Method), (:Context), (:Paradigm)
(:Category)

// 関係タイプ
-[:BASED_ON]->
-[:EXTENDS]->
-[:CONTRADICTS]->
-[:COMPLEMENTS]->
-[:PROPOSED_BY]->
-[:HAS_CONCEPT]->
-[:HAS_PRINCIPLE]->
-[:SUPPORTS]->
-[:APPLIES_TO]->
-[:BELONGS_TO]->
-[:BELONGS_TO_CATEGORY]->
```

開発環境:
- Docker Compose（ローカル）
- Neo4j AuraDB Free（クラウド開発）

本番環境:
- Neo4j AuraDB Professional
- セルフホスト（Docker/Kubernetes）

---

### ベクトルデータベース

**ChromaDB 0.5+**

```
理由:
- 軽量でPython native
- ローカル実行可能
- 永続化サポート
- メタデータフィルタリング
- 複数コレクション対応
```

コレクション設計:
- `theories` - 理論埋め込み
- `concepts` - 概念埋め込み
- `evidence` - エビデンス埋め込み
- `methods` - 教授法埋め込み

---

### キャッシュ戦略

**階層型キャッシュ**

```
L1: メモリキャッシュ（TTL: 5分）
  - 頻繁にアクセスされる検索結果
  - LLMレスポンス

L2: Redis（TTL: 1時間）
  - グラフクエリ結果
  - Embedding結果

L3: ファイルキャッシュ（TTL: 24時間）
  - 静的データ（理論メタデータ）
```

実装:
```python
from functools import lru_cache
from diskcache import Cache

# L1: メモリキャッシュ
@lru_cache(maxsize=1000)
def get_theory_cache(theory_id: str): ...

# L2: ディスクキャッシュ
disk_cache = Cache("./cache")
```

---

### 非同期処理

**asyncio + httpx**

```
理由:
- I/Oバウンドタスク（LLM API、DB）の効率化
- MCP Serverの非同期要件対応
- 並列クエリ実行
```

パターン:
```python
import asyncio
from httpx import AsyncClient

async def parallel_search(queries: list[str]) -> list[Result]:
    async with AsyncClient() as client:
        tasks = [search_single(client, q) for q in queries]
        return await asyncio.gather(*tasks)
```

---

### テスト戦略

**pytest 8.0+ + pytest-asyncio**

```
テストレベル:
- Unit Tests: ドメインロジック、サービス層
- Integration Tests: DB統合、API統合
- E2E Tests: MCPプロトコル検証

カバレッジ目標: 90%+
```

ツール:
- `pytest` - テストフレームワーク
- `pytest-asyncio` - 非同期テスト
- `pytest-cov` - カバレッジ
- `testcontainers` - DB統合テスト
- `httpx` - APIテスト

---

### 開発ツール

**コード品質**

| ツール | 用途 |
|--------|------|
| ruff | Linter + Formatter |
| mypy | 型チェック |
| pre-commit | コミット前検証 |
| black | コードフォーマット（ruffで代替可） |

**設定例** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4"]

[tool.mypy]
python_version = "3.11"
strict = true
```

---

### コンテナ化

**Docker Compose**

```yaml
services:
  tenjin-server:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - neo4j
      - chromadb
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - CHROMADB_HOST=chromadb

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
```

---

### CI/CD

**GitHub Actions**

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:5-community
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest --cov

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv run ruff check
      - run: uv run mypy src/
```

---

## アーキテクチャ決定記録 (ADR)

| ADR | 決定 | 理由 |
|-----|------|------|
| ADR-001 | esperanto採用 | マルチプロバイダー対応、軽量 |
| ADR-002 | Neo4j採用 | グラフDB成熟度、Cypher |
| ADR-003 | FastMCP採用 | 公式SDK、安定性 |
| ADR-004 | ChromaDB採用 | Python native、軽量 |
| ADR-005 | 階層型キャッシュ | パフォーマンス最適化 |

---

## 依存関係

```toml
# pyproject.toml
[project]
requires-python = ">=3.11"
dependencies = [
    "esperanto>=2.12",
    "mcp[cli]>=1.5",
    "neo4j>=5.0",
    "chromadb>=0.5",
    "pydantic>=2.0",
    "httpx>=0.27",
    "structlog>=24.0",
    "tenacity>=8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "ruff>=0.4",
    "mypy>=1.0",
    "testcontainers>=4.0",
]
```

---

## References

- [esperanto Documentation](https://github.com/lfnovo/esperanto)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [参照実装: TENGIN-GraphRAG](../References/TENGIN-GraphRAG/)

---

*Run `musubi steering` to update this document after technology decisions change.*
