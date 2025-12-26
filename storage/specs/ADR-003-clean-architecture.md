# ADR-003: Clean Architecture + MCPサーバーパターン

**ID**: ADR-003
**Status**: Accepted
**Created**: 2025-12-26
**Decision Makers**: GitHub Copilot
**Related**: REQ-001, DESIGN-001

---

## Context

TENJINは以下の特性を持つシステムである：

1. **MCPサーバー**: 外部AIアプリケーションからの呼び出し
2. **複数のデータソース**: Neo4j（Graph）、ChromaDB（Vector）、LLM
3. **ビジネスロジック**: 推論、推薦、生成の複雑なロジック
4. **将来の拡張**: 新しいLLMプロバイダー、DB、機能の追加

これらを満たすアーキテクチャが必要。

---

## Decision

**Clean Architecture（4層）+ MCPサーバーパターン**を採用する。

```
┌─────────────────────────────────────────────────────────────────┐
│                    Interface Layer (MCP)                         │
│                 Tools / Resources / Prompts                      │
├─────────────────────────────────────────────────────────────────┤
│                    Application Layer                             │
│                        Services                                  │
├─────────────────────────────────────────────────────────────────┤
│                     Domain Layer                                 │
│              Entities / Repositories / Value Objects             │
├─────────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                            │
│           Adapters (Neo4j, ChromaDB, esperanto, Cache)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Alternatives Considered

### 1. 単純な3層アーキテクチャ

```
Controller → Service → Repository
```

| Pros | Cons |
|------|------|
| シンプル | ドメインロジックが散在 |
| 学習コスト低 | テスト困難 |
| | DB依存が浸透 |

### 2. Hexagonal Architecture（Ports & Adapters）

| Pros | Cons |
|------|------|
| 外部依存の分離 | Clean Architectureとほぼ同等 |
| テスト容易 | 用語の混乱（Port/Adapter） |

### 3. Clean Architecture（選択）

| Pros | Cons |
|------|------|
| 依存性の方向が明確 | 初期コード量多い |
| ドメイン中心 | レイヤー間のマッピング |
| テスト容易 | 学習コスト |
| 変更容易性 | |

---

## Consequences

### Positive

1. **依存性逆転**: Infrastructure → Domain ではなく Domain ← Infrastructure
2. **テスト容易性**: 各層を独立してテスト可能
3. **柔軟性**: Neo4j→別DB、esperanto→別LLMの差し替え容易
4. **MCP対応**: Interface層でMCPプリミティブを明確に定義

### Negative

1. **コード量**: レイヤー間の変換コード
2. **初期コスト**: ディレクトリ構造の設計
3. **オーバーエンジニアリングリスク**: 小規模なら過剰

### Mitigations

1. Pydanticでエンティティ/DTOの自動変換
2. テンプレートによる構造統一
3. 必要な部分から段階的に適用

---

## Implementation

### 1. レイヤー定義

#### Domain Layer（最内層）

```python
# src/tenjin/domain/entities/theory.py

from pydantic import BaseModel
from typing import Optional

class Theory(BaseModel):
    """教育理論エンティティ"""
    id: str
    name_ja: str
    name_en: str
    theorist: str
    priority: int  # 1-5
    category: str
    description: str
    era: Optional[str] = None
    region: Optional[str] = None
    
    def to_prompt(self) -> str:
        """LLMプロンプト用テキスト"""
        return f"""
理論名: {self.name_ja} ({self.name_en})
提唱者: {self.theorist}
カテゴリ: {self.category}
優先度: {self.priority}/5
説明: {self.description}
"""

# src/tenjin/domain/repositories/theory_repository.py

from abc import ABC, abstractmethod
from typing import Optional

class TheoryRepository(ABC):
    """理論リポジトリインターフェース"""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Theory]:
        pass
    
    @abstractmethod
    async def get_all(self) -> list[Theory]:
        pass
    
    @abstractmethod
    async def get_by_category(self, category: str) -> list[Theory]:
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[Theory]:
        pass
```

#### Application Layer

```python
# src/tenjin/application/services/search_service.py

from tenjin.domain.repositories import TheoryRepository, VectorRepository
from tenjin.domain.entities import Theory

class SearchService:
    """検索サービス"""
    
    def __init__(
        self,
        theory_repo: TheoryRepository,
        vector_repo: VectorRepository
    ):
        self.theory_repo = theory_repo
        self.vector_repo = vector_repo
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None
    ) -> list[Theory]:
        """セマンティック検索"""
        results = await self.vector_repo.similarity_search(query, limit * 2)
        
        theories = []
        for r in results:
            theory = await self.theory_repo.get_by_id(r.id)
            if theory and (not category or theory.category == category):
                theories.append(theory)
        
        return theories[:limit]
```

#### Infrastructure Layer

```python
# src/tenjin/infrastructure/repositories/neo4j_theory_repository.py

from tenjin.domain.repositories import TheoryRepository
from tenjin.domain.entities import Theory
from tenjin.infrastructure.adapters import Neo4jAdapter

class Neo4jTheoryRepository(TheoryRepository):
    """Neo4j実装のTheoryRepository"""
    
    def __init__(self, neo4j: Neo4jAdapter):
        self.neo4j = neo4j
    
    async def get_by_id(self, id: str) -> Optional[Theory]:
        cypher = """
        MATCH (t:Theory {id: $id})
        RETURN t
        """
        result = await self.neo4j.execute_single(cypher, {"id": id})
        return Theory(**result) if result else None
    
    async def get_all(self) -> list[Theory]:
        cypher = "MATCH (t:Theory) RETURN t"
        results = await self.neo4j.execute(cypher)
        return [Theory(**r) for r in results]
    
    async def get_by_category(self, category: str) -> list[Theory]:
        cypher = """
        MATCH (t:Theory)-[:BELONGS_TO_CATEGORY]->(c:Category {name: $category})
        RETURN t
        """
        results = await self.neo4j.execute(cypher, {"category": category})
        return [Theory(**r) for r in results]
    
    async def search(self, query: str, limit: int = 10) -> list[Theory]:
        cypher = """
        CALL db.index.fulltext.queryNodes('theory_fulltext', $query)
        YIELD node, score
        RETURN node AS t
        ORDER BY score DESC
        LIMIT $limit
        """
        results = await self.neo4j.execute(cypher, {"query": query, "limit": limit})
        return [Theory(**r["t"]) for r in results]
```

#### Interface Layer（MCP）

```python
# src/tenjin/interface/tools/search_tools.py

from mcp.server.fastmcp import FastMCP
from tenjin.application.services import SearchService

def register_search_tools(mcp: FastMCP, search_service: SearchService):
    """検索ツールを登録"""
    
    @mcp.tool()
    async def search_theories(
        query: str,
        limit: int = 10,
        category: str | None = None
    ) -> list[dict]:
        """
        教育理論をセマンティック検索します。
        
        Args:
            query: 検索クエリ
            limit: 結果数上限（デフォルト: 10）
            category: フィルタするカテゴリ（オプション）
        
        Returns:
            マッチした教育理論のリスト
        """
        theories = await search_service.semantic_search(query, limit, category)
        return [t.model_dump() for t in theories]
```

### 2. 依存性注入

```python
# src/tenjin/server.py

from mcp.server.fastmcp import FastMCP
from tenjin.infrastructure.adapters import Neo4jAdapter, ChromaDBAdapter, EsperantoAdapter
from tenjin.infrastructure.repositories import Neo4jTheoryRepository, ChromaDBVectorRepository
from tenjin.application.services import SearchService, ReasoningService
from tenjin.interface.tools import register_search_tools, register_reasoning_tools

def create_server() -> FastMCP:
    """MCPサーバーを作成"""
    
    # Infrastructure
    neo4j = Neo4jAdapter.from_env()
    chromadb = ChromaDBAdapter.from_env()
    llm = EsperantoAdapter.from_env()
    
    # Repositories
    theory_repo = Neo4jTheoryRepository(neo4j)
    vector_repo = ChromaDBVectorRepository(chromadb, llm)
    
    # Services
    search_service = SearchService(theory_repo, vector_repo)
    reasoning_service = ReasoningService(llm, theory_repo)
    
    # MCP Server
    mcp = FastMCP("tenjin")
    
    # Register tools
    register_search_tools(mcp, search_service)
    register_reasoning_tools(mcp, reasoning_service)
    
    return mcp

if __name__ == "__main__":
    mcp = create_server()
    mcp.run()
```

### 3. ディレクトリ構造

```
src/tenjin/
├── server.py                  # Entry point
├── interface/                 # Interface Layer (MCP)
│   ├── tools/
│   ├── resources/
│   └── prompts/
├── application/               # Application Layer
│   └── services/
├── domain/                    # Domain Layer
│   ├── entities/
│   ├── repositories/          # Interfaces
│   └── value_objects/
└── infrastructure/            # Infrastructure Layer
    ├── adapters/
    ├── repositories/          # Implementations
    └── config/
```

---

## Testing Strategy

```python
# tests/unit/application/test_search_service.py

import pytest
from unittest.mock import AsyncMock
from tenjin.application.services import SearchService
from tenjin.domain.entities import Theory

@pytest.fixture
def mock_theory_repo():
    repo = AsyncMock()
    repo.get_by_id.return_value = Theory(
        id="T001",
        name_ja="構成主義",
        name_en="Constructivism",
        theorist="Jean Piaget",
        priority=5,
        category="学習理論",
        description="学習者が能動的に知識を構築"
    )
    return repo

@pytest.fixture
def mock_vector_repo():
    repo = AsyncMock()
    repo.similarity_search.return_value = [
        AsyncMock(id="T001", score=0.95)
    ]
    return repo

@pytest.mark.asyncio
async def test_semantic_search(mock_theory_repo, mock_vector_repo):
    service = SearchService(mock_theory_repo, mock_vector_repo)
    results = await service.semantic_search("知識構築", limit=5)
    
    assert len(results) == 1
    assert results[0].name_ja == "構成主義"
```

---

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
