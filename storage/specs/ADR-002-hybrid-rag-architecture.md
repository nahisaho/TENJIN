# ADR-002: ハイブリッドRAGアーキテクチャ

**ID**: ADR-002
**Status**: Accepted
**Created**: 2025-12-26
**Decision Makers**: GitHub Copilot
**Related**: REQ-001, DESIGN-001, ADR-001

---

## Context

教育理論のGraphRAGシステムでは、以下の2種類のクエリを効率的に処理する必要がある：

1. **構造的クエリ**: 「構成主義に基づく理論は？」「ピアジェが影響を与えた理論家は？」
2. **意味的クエリ**: 「モチベーション向上に効果的な理論は？」「協調学習に関連する概念は？」

単一のデータベースでは両方のクエリを最適に処理できない。

---

## Decision

**Graph検索（Neo4j）+ Vector検索（ChromaDB）のハイブリッドRAG**を採用する。

```
Query ──▶ ┌─────────────────────────────────────┐
          │        Hybrid RAG Engine            │
          │                                     │
          │   ┌───────────┐   ┌───────────┐    │
          │   │   Neo4j   │   │ ChromaDB  │    │
          │   │  (Graph)  │   │ (Vector)  │    │
          │   └─────┬─────┘   └─────┬─────┘    │
          │         │               │          │
          │         └───────┬───────┘          │
          │                 ▼                  │
          │         Result Fusion              │
          │                 ▼                  │
          │         LLM Reranking              │
          └─────────────────┼───────────────────┘
                            ▼
                      Final Results
```

---

## Alternatives Considered

### 1. Graph-only（Neo4j + Full-text Index）

| Pros | Cons |
|------|------|
| シンプルな構成 | 意味的検索が弱い |
| 関係性クエリに強い | 類似度計算が限定的 |
| 運用コスト低 | |

### 2. Vector-only（ChromaDB / Pinecone）

| Pros | Cons |
|------|------|
| 意味的検索に強い | 関係性クエリが苦手 |
| スケーラブル | グラフトラバーサル不可 |
| | 構造的知識の表現が困難 |

### 3. Neo4j + Vector Index（Neo4j 5.x内蔵）

| Pros | Cons |
|------|------|
| 単一DB | ベクトル検索機能が限定的 |
| 統合クエリ | パフォーマンス懸念 |
| | 埋め込みモデル固定 |

### 4. ハイブリッドRAG（選択）

| Pros | Cons |
|------|------|
| 両方の強みを活用 | 複雑性増加 |
| 高精度な検索 | 2つのDB運用 |
| 柔軟なクエリ対応 | 結果融合ロジック必要 |
| 独立スケーリング | |

---

## Consequences

### Positive

1. **検索精度向上**: 構造的+意味的クエリの両方に対応
2. **柔軟性**: クエリタイプに応じた最適化
3. **拡張性**: 各DBを独立にスケール可能
4. **教育理論に最適**: 理論間関係（Graph）+ 概念類似性（Vector）

### Negative

1. **運用複雑性**: 2つのDBの同期・管理
2. **データ整合性**: 両DBのデータ一貫性維持
3. **結果融合**: マージロジックのチューニング必要

### Mitigations

1. 単一のDataLoaderでGraph/Vectorを同時更新
2. 定期的な整合性チェック
3. Reciprocal Rank Fusionで結果統合

---

## Implementation

### 1. ハイブリッド検索サービス

```python
# src/tenjin/application/services/search_service.py

from typing import Optional
from dataclasses import dataclass

@dataclass
class SearchResult:
    id: str
    name: str
    score: float
    source: str  # "graph" | "vector" | "hybrid"
    metadata: dict

class HybridSearchService:
    def __init__(
        self,
        graph_repo: GraphRepository,
        vector_repo: VectorRepository,
        llm_adapter: EsperantoAdapter
    ):
        self.graph = graph_repo
        self.vector = vector_repo
        self.llm = llm_adapter
    
    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        graph_weight: float = 0.5,
        vector_weight: float = 0.5,
        rerank: bool = True
    ) -> list[SearchResult]:
        """ハイブリッド検索"""
        
        # 1. 並列で両方の検索を実行
        graph_results, vector_results = await asyncio.gather(
            self._graph_search(query, limit * 2),
            self._vector_search(query, limit * 2)
        )
        
        # 2. Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion(
            graph_results, 
            vector_results,
            graph_weight,
            vector_weight
        )
        
        # 3. LLMリランキング（オプション）
        if rerank:
            fused = await self._llm_rerank(query, fused[:limit * 2])
        
        return fused[:limit]
    
    async def _graph_search(self, query: str, limit: int) -> list[SearchResult]:
        """Cypherベースのグラフ検索"""
        cypher = """
        CALL db.index.fulltext.queryNodes('theory_index', $query)
        YIELD node, score
        RETURN node.id AS id, node.name_ja AS name, score
        ORDER BY score DESC
        LIMIT $limit
        """
        results = await self.graph.execute(cypher, {"query": query, "limit": limit})
        return [SearchResult(r["id"], r["name"], r["score"], "graph", {}) for r in results]
    
    async def _vector_search(self, query: str, limit: int) -> list[SearchResult]:
        """ベクトル類似度検索"""
        embedding = await self.llm.embed(query)
        results = await self.vector.similarity_search(embedding, limit)
        return [SearchResult(r.id, r.name, r.score, "vector", r.metadata) for r in results]
    
    def _reciprocal_rank_fusion(
        self,
        graph_results: list[SearchResult],
        vector_results: list[SearchResult],
        graph_weight: float,
        vector_weight: float,
        k: int = 60
    ) -> list[SearchResult]:
        """RRFで結果を融合"""
        scores = {}
        
        for rank, r in enumerate(graph_results):
            scores[r.id] = scores.get(r.id, 0) + graph_weight / (k + rank + 1)
        
        for rank, r in enumerate(vector_results):
            scores[r.id] = scores.get(r.id, 0) + vector_weight / (k + rank + 1)
        
        # IDからSearchResultを再構築
        all_results = {r.id: r for r in graph_results + vector_results}
        fused = [
            SearchResult(id=id, name=all_results[id].name, score=score, source="hybrid", metadata={})
            for id, score in sorted(scores.items(), key=lambda x: -x[1])
        ]
        return fused
    
    async def _llm_rerank(
        self,
        query: str,
        results: list[SearchResult]
    ) -> list[SearchResult]:
        """LLMによるリランキング"""
        if not results:
            return results
        
        candidates = "\n".join([f"{i+1}. {r.name}" for i, r in enumerate(results)])
        
        messages = [
            {"role": "system", "content": "あなたは教育理論の専門家です。"},
            {"role": "user", "content": f"""
クエリ: {query}

以下の教育理論を、クエリへの関連性が高い順に並べ替えてください。
番号のみをカンマ区切りで出力してください。

{candidates}
"""}
        ]
        
        response = await self.llm.chat(messages, temperature=0)
        
        try:
            order = [int(x.strip()) - 1 for x in response.split(",")]
            reranked = [results[i] for i in order if 0 <= i < len(results)]
            # リランクされなかったものを末尾に
            remaining = [r for r in results if r not in reranked]
            return reranked + remaining
        except:
            return results  # パース失敗時は元の順序
```

### 2. データ同期

```python
# src/tenjin/infrastructure/data_loader.py

class TheoryDataLoader:
    def __init__(
        self,
        neo4j: Neo4jAdapter,
        chromadb: ChromaDBAdapter,
        llm: EsperantoAdapter
    ):
        self.neo4j = neo4j
        self.chromadb = chromadb
        self.llm = llm
    
    async def load_theory(self, theory: Theory) -> None:
        """理論を両DBに同時にロード"""
        # 1. Neo4jにノード作成
        await self.neo4j.create_node("Theory", theory.to_dict())
        
        # 2. ChromaDBにベクトル作成
        text = f"{theory.name_ja} {theory.name_en} {theory.description}"
        embedding = await self.llm.embed(text)
        await self.chromadb.add(
            id=theory.id,
            embedding=embedding,
            metadata={"name": theory.name_ja, "category": theory.category}
        )
```

---

## References

- [Reciprocal Rank Fusion (RRF)](https://www.elastic.co/blog/reciprocal-rank-fusion-rrf)
- [Neo4j Full-Text Search](https://neo4j.com/docs/cypher-manual/current/indexes-for-full-text-search/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [GraphRAG Paper](https://arxiv.org/abs/2404.16130)
