# タスク分解書: TENJIN 教育理論GraphRAG MCPサーバー

**ID**: TASKS-001
**Feature**: TENJIN Education Theory GraphRAG MCP Server
**Version**: 1.0
**Created**: 2025-12-26
**Updated**: 2025-12-26
**Status**: Draft
**Related**: REQ-001, DESIGN-001, ADR-001~003
**Author**: GitHub Copilot

---

## 1. タスク概要

### 1.1 フェーズ構成

| フェーズ | 説明 | 推定工数 | 依存関係 |
|---------|------|---------|---------|
| Phase 1 | プロジェクト基盤構築 | 2日 | なし |
| Phase 2 | Domain Layer実装 | 2日 | Phase 1 |
| Phase 3 | Infrastructure Layer実装 | 3日 | Phase 2 |
| Phase 4 | Application Layer実装 | 3日 | Phase 3 |
| Phase 5 | Interface Layer (MCP) 実装 | 3日 | Phase 4 |
| Phase 6 | データ準備・ローディング | 2日 | Phase 3 |
| Phase 7 | テスト・統合 | 2日 | Phase 5, 6 |
| Phase 8 | ドキュメント・デプロイ | 1日 | Phase 7 |
| **合計** | | **18日** | |

### 1.2 優先度定義

| 優先度 | 説明 |
|--------|------|
| P0 | 必須（MVP） |
| P1 | 重要（初期リリース） |
| P2 | 推奨（改善） |

---

## 2. Phase 1: プロジェクト基盤構築

### TASK-1.1: プロジェクト初期化 [P0]

**説明**: pyproject.toml、ディレクトリ構造、開発環境のセットアップ

**成果物**:
- `pyproject.toml` - 依存関係定義
- `src/tenjin/__init__.py` - パッケージ初期化
- `.env.example` - 環境変数テンプレート
- `README.md` - プロジェクト説明

**サブタスク**:
```
□ TASK-1.1.1: pyproject.toml作成
  - Python 3.11+
  - 依存関係: mcp[cli], esperanto, neo4j, chromadb, pydantic, etc.
  - 開発依存: pytest, ruff, mypy
  
□ TASK-1.1.2: ディレクトリ構造作成
  - src/tenjin/interface/tools/
  - src/tenjin/interface/resources/
  - src/tenjin/interface/prompts/
  - src/tenjin/application/services/
  - src/tenjin/domain/entities/
  - src/tenjin/domain/repositories/
  - src/tenjin/domain/value_objects/
  - src/tenjin/infrastructure/adapters/
  - src/tenjin/infrastructure/repositories/
  - src/tenjin/infrastructure/config/
  
□ TASK-1.1.3: .env.example作成
  - NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
  - CHROMA_PERSIST_DIR
  - LLM_PROVIDER, LLM_MODEL
  - OPENAI_API_KEY, ANTHROPIC_API_KEY
  
□ TASK-1.1.4: README.md更新
```

**検証基準**:
- `uv sync` が成功
- `uv run python -c "import tenjin"` が成功

---

### TASK-1.2: Docker環境構築 [P0]

**説明**: 開発用Docker Compose環境

**成果物**:
- `docker-compose.yml`
- `Dockerfile`

**サブタスク**:
```
□ TASK-1.2.1: docker-compose.yml作成
  - Neo4j 5.x サービス
  - ChromaDB サービス（オプション）
  - Redis サービス（オプション）
  
□ TASK-1.2.2: Dockerfile作成
  - Python 3.11ベース
  - uvによる依存インストール
```

**検証基準**:
- `docker-compose up -d` が成功
- Neo4j Browser (http://localhost:7474) アクセス可能

---

### TASK-1.3: 設定管理 [P0]

**説明**: Pydantic Settingsによる設定管理

**成果物**:
- `src/tenjin/infrastructure/config/settings.py`
- `src/tenjin/infrastructure/config/logging.py`

**サブタスク**:
```
□ TASK-1.3.1: Settings クラス作成
  - Neo4j設定
  - ChromaDB設定
  - LLM設定（esperanto）
  - キャッシュ設定
  
□ TASK-1.3.2: ログ設定
  - structlog設定
  - JSON形式ログ
```

**検証基準**:
- 環境変数から設定読み込み成功
- ログ出力フォーマット確認

---

## 3. Phase 2: Domain Layer実装

### TASK-2.1: Entities実装 [P0]

**説明**: ドメインエンティティの定義

**成果物**:
- `src/tenjin/domain/entities/theory.py`
- `src/tenjin/domain/entities/theorist.py`
- `src/tenjin/domain/entities/concept.py`
- `src/tenjin/domain/entities/principle.py`
- `src/tenjin/domain/entities/evidence.py`
- `src/tenjin/domain/entities/method.py`
- `src/tenjin/domain/entities/context.py`
- `src/tenjin/domain/entities/category.py`
- `src/tenjin/domain/entities/paradigm.py`

**サブタスク**:
```
□ TASK-2.1.1: Theory エンティティ
  class Theory(BaseModel):
      id: str
      name_ja: str
      name_en: str
      theorist: str
      priority: int  # 1-5
      category: str
      description: str
      era: Optional[str]
      region: Optional[str]

□ TASK-2.1.2: Theorist エンティティ
□ TASK-2.1.3: Concept エンティティ
□ TASK-2.1.4: Principle エンティティ
□ TASK-2.1.5: Evidence エンティティ
□ TASK-2.1.6: Method エンティティ
□ TASK-2.1.7: Context エンティティ
□ TASK-2.1.8: Category エンティティ
□ TASK-2.1.9: Paradigm エンティティ
□ TASK-2.1.10: __init__.py でエクスポート
```

**検証基準**:
- 各エンティティのPydanticバリデーション成功
- `mypy` 型チェック成功

---

### TASK-2.2: Value Objects実装 [P0]

**説明**: 値オブジェクトの定義

**成果物**:
- `src/tenjin/domain/value_objects/theory_category.py`
- `src/tenjin/domain/value_objects/evidence_level.py`
- `src/tenjin/domain/value_objects/citation_format.py`
- `src/tenjin/domain/value_objects/priority.py`

**サブタスク**:
```
□ TASK-2.2.1: TheoryCategory Enum
  - LEARNING_THEORY = "学習理論"
  - INSTRUCTIONAL_THEORY = "教授法・指導法理論"
  - DEVELOPMENTAL_THEORY = "発達理論"
  - MOTIVATION_THEORY = "動機づけ理論"
  - ASSESSMENT_THEORY = "評価理論"
  - SOCIAL_LEARNING_THEORY = "社会的学習理論"
  - ASIAN_THEORY = "東洋・アジア教育理論"
  - TECHNOLOGY_THEORY = "テクノロジー活用理論"
  - MODERN_THEORY = "現代教育理論"
  - ALTERNATIVE_THEORY = "批判的・オルタナティブ・特別支援教育"

□ TASK-2.2.2: EvidenceLevel Enum
□ TASK-2.2.3: CitationFormat Enum (APA, MLA, Chicago)
□ TASK-2.2.4: Priority Enum (1-5)
```

**検証基準**:
- Enumの値アクセス成功

---

### TASK-2.3: Repository Interfaces実装 [P0]

**説明**: リポジトリインターフェース（抽象クラス）の定義

**成果物**:
- `src/tenjin/domain/repositories/theory_repository.py`
- `src/tenjin/domain/repositories/concept_repository.py`
- `src/tenjin/domain/repositories/graph_repository.py`
- `src/tenjin/domain/repositories/vector_repository.py`

**サブタスク**:
```
□ TASK-2.3.1: TheoryRepository ABC
  - get_by_id(id) -> Optional[Theory]
  - get_all() -> list[Theory]
  - get_by_category(category) -> list[Theory]
  - search(query, limit) -> list[Theory]
  
□ TASK-2.3.2: ConceptRepository ABC
□ TASK-2.3.3: GraphRepository ABC
  - traverse(start_id, depth) -> Graph
  - find_path(from_id, to_id) -> list[Node]
  - get_related(id, relation_type) -> list[Node]
  
□ TASK-2.3.4: VectorRepository ABC
  - similarity_search(query, limit) -> list[SearchResult]
  - add(id, embedding, metadata)
```

**検証基準**:
- ABCの定義が正しい
- 型ヒントが完全

---

## 4. Phase 3: Infrastructure Layer実装

### TASK-3.1: Neo4j Adapter実装 [P0]

**説明**: Neo4jデータベースとの接続アダプター

**成果物**:
- `src/tenjin/infrastructure/adapters/neo4j_adapter.py`

**サブタスク**:
```
□ TASK-3.1.1: Neo4jAdapter クラス
  - from_env() クラスメソッド
  - execute(cypher, params) -> list[dict]
  - execute_single(cypher, params) -> Optional[dict]
  - create_node(label, properties)
  - create_relationship(from_id, to_id, type, properties)
  
□ TASK-3.1.2: 接続プール管理
□ TASK-3.1.3: エラーハンドリング
□ TASK-3.1.4: 非同期対応 (async)
```

**検証基準**:
- Neo4j接続成功
- CRUDオペレーション動作

---

### TASK-3.2: ChromaDB Adapter実装 [P0]

**説明**: ChromaDBベクトルデータベースとの接続アダプター

**成果物**:
- `src/tenjin/infrastructure/adapters/chromadb_adapter.py`

**サブタスク**:
```
□ TASK-3.2.1: ChromaDBAdapter クラス
  - from_env() クラスメソッド
  - add(id, embedding, metadata)
  - add_batch(items)
  - similarity_search(embedding, limit) -> list[SearchResult]
  - delete(id)
  
□ TASK-3.2.2: コレクション管理
□ TASK-3.2.3: メタデータフィルタリング
```

**検証基準**:
- ベクトル追加・検索成功

---

### TASK-3.3: esperanto Adapter実装 [P0]

**説明**: esperantoによるLLM統合アダプター

**成果物**:
- `src/tenjin/infrastructure/adapters/esperanto_adapter.py`

**サブタスク**:
```
□ TASK-3.3.1: EsperantoAdapter クラス
  - from_env() クラスメソッド
  - chat(messages, temperature, max_tokens) -> str
  - stream_chat(messages) -> AsyncIterator[str]
  - embed(text) -> list[float]
  - embed_batch(texts) -> list[list[float]]
  
□ TASK-3.3.2: プロバイダーフォールバック
□ TASK-3.3.3: リトライロジック (tenacity)
□ TASK-3.3.4: レート制限対応
```

**検証基準**:
- OpenAI API呼び出し成功
- フォールバック動作確認

---

### TASK-3.4: Repository実装 [P0]

**説明**: リポジトリインターフェースの具体実装

**成果物**:
- `src/tenjin/infrastructure/repositories/neo4j_theory_repository.py`
- `src/tenjin/infrastructure/repositories/neo4j_graph_repository.py`
- `src/tenjin/infrastructure/repositories/chromadb_vector_repository.py`

**サブタスク**:
```
□ TASK-3.4.1: Neo4jTheoryRepository
□ TASK-3.4.2: Neo4jGraphRepository
□ TASK-3.4.3: ChromaDBVectorRepository
```

**検証基準**:
- インターフェースを完全に実装
- 統合テスト成功

---

### TASK-3.5: Cache Adapter実装 [P1]

**説明**: 階層型キャッシュアダプター

**成果物**:
- `src/tenjin/infrastructure/adapters/cache_adapter.py`

**サブタスク**:
```
□ TASK-3.5.1: インメモリキャッシュ（L1）
□ TASK-3.5.2: Redis接続（L2、オプション）
□ TASK-3.5.3: TTL管理
□ TASK-3.5.4: キャッシュキー生成
```

**検証基準**:
- キャッシュヒット/ミス動作

---

## 5. Phase 4: Application Layer実装

### TASK-4.1: Search Service実装 [P0]

**説明**: 検索機能サービス

**成果物**:
- `src/tenjin/application/services/search_service.py`

**サブタスク**:
```
□ TASK-4.1.1: semantic_search() - セマンティック検索
□ TASK-4.1.2: hybrid_search() - ハイブリッドRAG
□ TASK-4.1.3: full_text_search() - 全文検索
□ TASK-4.1.4: filter_by_category() - カテゴリフィルタ
□ TASK-4.1.5: _reciprocal_rank_fusion() - RRF
□ TASK-4.1.6: _llm_rerank() - LLMリランキング
```

**検証基準**:
- 各検索メソッドが正しい結果を返す

---

### TASK-4.2: Reasoning Service実装 [P0]

**説明**: LLM推論機能サービス

**成果物**:
- `src/tenjin/application/services/reasoning_service.py`

**サブタスク**:
```
□ TASK-4.2.1: analyze_theory() - 理論分析
□ TASK-4.2.2: synthesize_theories() - 理論統合
□ TASK-4.2.3: infer_applications() - 適用推論
□ TASK-4.2.4: evaluate_evidence() - エビデンス評価
□ TASK-4.2.5: explain_relationship() - 関係説明
□ TASK-4.2.6: critique_theory() - 批判的分析
```

**検証基準**:
- LLM応答が適切なフォーマット

---

### TASK-4.3: Recommend Service実装 [P0]

**説明**: 推薦機能サービス

**成果物**:
- `src/tenjin/application/services/recommend_service.py`

**サブタスク**:
```
□ TASK-4.3.1: recommend_for_context() - 文脈ベース推薦
□ TASK-4.3.2: recommend_for_learner() - 学習者ベース推薦
□ TASK-4.3.3: recommend_for_curriculum() - カリキュラム推薦
□ TASK-4.3.4: recommend_integration() - 統合推薦
□ TASK-4.3.5: recommend_complementary() - 補完理論推薦
```

**検証基準**:
- 推薦結果にスコア付き

---

### TASK-4.4: Generation Service実装 [P0]

**説明**: コンテンツ生成サービス

**成果物**:
- `src/tenjin/application/services/generation_service.py`

**サブタスク**:
```
□ TASK-4.4.1: generate_lesson_plan() - 授業計画生成
□ TASK-4.4.2: generate_assessment() - 評価生成
□ TASK-4.4.3: generate_learning_path() - 学習パス生成
□ TASK-4.4.4: generate_activity() - 学習活動生成
□ TASK-4.4.5: generate_rubric() - ルーブリック生成
□ TASK-4.4.6: generate_explanation() - 説明生成
```

**検証基準**:
- 生成コンテンツの構造が正しい

---

### TASK-4.5: Graph Service実装 [P0]

**説明**: グラフ操作サービス

**成果物**:
- `src/tenjin/application/services/graph_service.py`

**サブタスク**:
```
□ TASK-4.5.1: traverse() - グラフトラバーサル
□ TASK-4.5.2: find_path() - パス検索
□ TASK-4.5.3: get_subgraph() - サブグラフ抽出
□ TASK-4.5.4: get_related() - 関連ノード取得
```

**検証基準**:
- グラフ構造が正しく返される

---

### TASK-4.6: Citation Service実装 [P1]

**説明**: 引用生成サービス

**成果物**:
- `src/tenjin/application/services/citation_service.py`

**サブタスク**:
```
□ TASK-4.6.1: cite_theory() - 理論引用生成
□ TASK-4.6.2: format_citation() - フォーマット変換 (APA/MLA/Chicago)
□ TASK-4.6.3: generate_bibliography() - 参考文献リスト
```

---

### TASK-4.7: Compare Service実装 [P1]

**説明**: 比較分析サービス

**成果物**:
- `src/tenjin/application/services/compare_service.py`

**サブタスク**:
```
□ TASK-4.7.1: compare_theories() - 理論比較
□ TASK-4.7.2: compare_paradigms() - パラダイム比較
□ TASK-4.7.3: compare_methods() - 教授法比較
□ TASK-4.7.4: trace_evolution() - 発展追跡
□ TASK-4.7.5: analyze_strengths() - 強み分析
```

---

## 6. Phase 5: Interface Layer (MCP) 実装

### TASK-5.1: MCP Server基盤 [P0]

**説明**: FastMCPサーバーの基盤実装

**成果物**:
- `src/tenjin/server.py`

**サブタスク**:
```
□ TASK-5.1.1: FastMCPインスタンス作成
□ TASK-5.1.2: 依存性注入セットアップ
□ TASK-5.1.3: エラーハンドリング
□ TASK-5.1.4: ヘルスチェック
```

**検証基準**:
- `uv run tenjin` でサーバー起動
- MCP Inspector接続成功

---

### TASK-5.2: Search Tools実装 [P0]

**説明**: 検索系MCPツール（8個）

**成果物**:
- `src/tenjin/interface/tools/search_tools.py`

**サブタスク**:
```
□ TASK-5.2.1: search_theories
□ TASK-5.2.2: search_concepts
□ TASK-5.2.3: search_theorists
□ TASK-5.2.4: search_evidence
□ TASK-5.2.5: search_methods
□ TASK-5.2.6: hybrid_search
□ TASK-5.2.7: full_text_search
□ TASK-5.2.8: filter_by_category
```

**検証基準**:
- 各ツールがMCP Inspectorで呼び出し可能

---

### TASK-5.3: Reasoning Tools実装 [P0]

**説明**: 推論系MCPツール（6個）

**成果物**:
- `src/tenjin/interface/tools/reasoning_tools.py`

**サブタスク**:
```
□ TASK-5.3.1: analyze_theory
□ TASK-5.3.2: synthesize_theories
□ TASK-5.3.3: infer_applications
□ TASK-5.3.4: evaluate_evidence
□ TASK-5.3.5: explain_relationship
□ TASK-5.3.6: critique_theory
```

---

### TASK-5.4: Recommend Tools実装 [P0]

**説明**: 推薦系MCPツール（5個）

**成果物**:
- `src/tenjin/interface/tools/recommend_tools.py`

**サブタスク**:
```
□ TASK-5.4.1: recommend_for_context
□ TASK-5.4.2: recommend_for_learner
□ TASK-5.4.3: recommend_for_curriculum
□ TASK-5.4.4: recommend_integration
□ TASK-5.4.5: recommend_complementary
```

---

### TASK-5.5: Generate Tools実装 [P0]

**説明**: 生成系MCPツール（6個）

**成果物**:
- `src/tenjin/interface/tools/generate_tools.py`

**サブタスク**:
```
□ TASK-5.5.1: generate_lesson_plan
□ TASK-5.5.2: generate_assessment
□ TASK-5.5.3: generate_learning_path
□ TASK-5.5.4: generate_activity
□ TASK-5.5.5: generate_rubric
□ TASK-5.5.6: generate_explanation
```

---

### TASK-5.6: Compare Tools実装 [P1]

**説明**: 比較系MCPツール（5個）

**成果物**:
- `src/tenjin/interface/tools/compare_tools.py`

**サブタスク**:
```
□ TASK-5.6.1: compare_theories
□ TASK-5.6.2: compare_paradigms
□ TASK-5.6.3: compare_methods
□ TASK-5.6.4: trace_evolution
□ TASK-5.6.5: analyze_strengths
```

---

### TASK-5.7: System Tools実装 [P0]

**説明**: システム系MCPツール（3個）

**成果物**:
- `src/tenjin/interface/tools/system_tools.py`

**サブタスク**:
```
□ TASK-5.7.1: get_graph_stats
□ TASK-5.7.2: health_check
□ TASK-5.7.3: get_schema
```

---

### TASK-5.8: Resources実装 [P0]

**説明**: MCPリソース（15個）

**成果物**:
- `src/tenjin/interface/resources/theory_resources.py`
- `src/tenjin/interface/resources/concept_resources.py`
- `src/tenjin/interface/resources/theorist_resources.py`
- `src/tenjin/interface/resources/evidence_resources.py`
- `src/tenjin/interface/resources/method_resources.py`
- `src/tenjin/interface/resources/graph_resources.py`

**サブタスク**:
```
□ TASK-5.8.1: theory://list, theory://{id}, theory://{category}/list
□ TASK-5.8.2: concept://list, concept://{id}, concept://{theory_id}
□ TASK-5.8.3: theorist://list, theorist://{id}, theorist://{era}
□ TASK-5.8.4: evidence://{theory_id}
□ TASK-5.8.5: method://list, method://{id}
□ TASK-5.8.6: context://list
□ TASK-5.8.7: graph://schema, graph://stats
```

---

### TASK-5.9: Prompts実装 [P1]

**説明**: MCPプロンプトテンプレート（15個）

**成果物**:
- `src/tenjin/interface/prompts/lesson_prompts.py`
- `src/tenjin/interface/prompts/assessment_prompts.py`
- `src/tenjin/interface/prompts/analysis_prompts.py`
- `src/tenjin/interface/prompts/integration_prompts.py`

**サブタスク**:
```
□ TASK-5.9.1: design_lesson
□ TASK-5.9.2: create_assessment
□ TASK-5.9.3: explain_theory
□ TASK-5.9.4: curriculum_plan
□ TASK-5.9.5: theory_debate
□ TASK-5.9.6: case_study
□ TASK-5.9.7: learner_analysis
□ TASK-5.9.8: theory_application
□ TASK-5.9.9: research_summary
□ TASK-5.9.10: compare_approaches
□ TASK-5.9.11: troubleshoot_learning
□ TASK-5.9.12: design_activity
□ TASK-5.9.13: feedback_guide
□ TASK-5.9.14: theory_integration
□ TASK-5.9.15: assessment_rubric
```

---

## 7. Phase 6: データ準備・ローディング

### TASK-6.1: データ変換 [P0]

**説明**: Educational-theory-research.mdからJSONデータへの変換

**成果物**:
- `data/theories/*.json` (10ファイル、200理論)
- `data/theorists/theorists.json`
- `data/relationships/theory_relationships.json`

**サブタスク**:
```
□ TASK-6.1.1: learning_theories.json (38理論)
□ TASK-6.1.2: instructional_theories.json (32理論)
□ TASK-6.1.3: developmental_theories.json (18理論)
□ TASK-6.1.4: motivation_theories.json (16理論)
□ TASK-6.1.5: assessment_theories.json (12理論)
□ TASK-6.1.6: social_learning_theories.json (18理論)
□ TASK-6.1.7: asian_theories.json (28理論)
□ TASK-6.1.8: technology_theories.json (22理論)
□ TASK-6.1.9: modern_theories.json (16理論)
□ TASK-6.1.10: alternative_theories.json (26理論)
□ TASK-6.1.11: theorists.json
□ TASK-6.1.12: theory_relationships.json
```

**検証基準**:
- 各JSONファイルがスキーマに準拠

---

### TASK-6.2: データローダー実装 [P0]

**説明**: JSONデータをNeo4j/ChromaDBにロードするスクリプト

**成果物**:
- `src/tenjin/infrastructure/data_loader.py`
- `scripts/load_data.py`

**サブタスク**:
```
□ TASK-6.2.1: TheoryDataLoader クラス
□ TASK-6.2.2: Neo4jへのノード・関係作成
□ TASK-6.2.3: ChromaDBへのベクトル作成
□ TASK-6.2.4: 全文検索インデックス作成
□ TASK-6.2.5: データ検証
```

**検証基準**:
- 200理論がNeo4jにロード
- ベクトルがChromaDBにロード

---

### TASK-6.3: グラフスキーマ設定 [P0]

**説明**: Neo4jグラフスキーマの設定

**成果物**:
- `scripts/setup_schema.cypher`

**サブタスク**:
```
□ TASK-6.3.1: 制約作成（一意性）
□ TASK-6.3.2: インデックス作成
□ TASK-6.3.3: 全文検索インデックス作成
```

---

## 8. Phase 7: テスト・統合

### TASK-7.1: ユニットテスト [P0]

**説明**: 各層のユニットテスト

**成果物**:
- `tests/unit/domain/`
- `tests/unit/application/`
- `tests/unit/infrastructure/`

**サブタスク**:
```
□ TASK-7.1.1: Entityテスト
□ TASK-7.1.2: Value Objectテスト
□ TASK-7.1.3: Serviceテスト（モック使用）
□ TASK-7.1.4: Adapterテスト（モック使用）
```

**検証基準**:
- カバレッジ80%以上

---

### TASK-7.2: 統合テスト [P0]

**説明**: コンポーネント間の統合テスト

**成果物**:
- `tests/integration/`

**サブタスク**:
```
□ TASK-7.2.1: Neo4j統合テスト
□ TASK-7.2.2: ChromaDB統合テスト
□ TASK-7.2.3: esperanto統合テスト
□ TASK-7.2.4: Service統合テスト
```

**検証基準**:
- Docker環境でテスト成功

---

### TASK-7.3: E2Eテスト [P0]

**説明**: MCPサーバーのE2Eテスト

**成果物**:
- `tests/e2e/test_mcp_server.py`

**サブタスク**:
```
□ TASK-7.3.1: ツール呼び出しテスト
□ TASK-7.3.2: リソース読み取りテスト
□ TASK-7.3.3: プロンプト取得テスト
□ TASK-7.3.4: エラーハンドリングテスト
```

**検証基準**:
- MCP Inspector で全機能動作確認

---

## 9. Phase 8: ドキュメント・デプロイ

### TASK-8.1: ドキュメント作成 [P1]

**説明**: 利用者向けドキュメント

**成果物**:
- `docs/USAGE_GUIDE.md`
- `docs/API_REFERENCE.md`
- `docs/MCP_INTEGRATION.md`
- `docs/EDUCATION_THEORIES.md`

**サブタスク**:
```
□ TASK-8.1.1: 使い方ガイド
□ TASK-8.1.2: APIリファレンス（全ツール）
□ TASK-8.1.3: MCP統合ガイド
□ TASK-8.1.4: 教育理論一覧
```

---

### TASK-8.2: CI/CD設定 [P1]

**説明**: GitHub Actionsによる自動テスト・ビルド

**成果物**:
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`

**サブタスク**:
```
□ TASK-8.2.1: テスト自動実行
□ TASK-8.2.2: Lint/Type Check
□ TASK-8.2.3: Docker Imageビルド
```

---

### TASK-8.3: MCP設定ファイル [P0]

**説明**: Claude Desktop等での利用設定

**成果物**:
- `mcp-config.json.example`
- インストールスクリプト

**サブタスク**:
```
□ TASK-8.3.1: claude_desktop_config.json 例
□ TASK-8.3.2: VS Code設定例
□ TASK-8.3.3: README.mdにセットアップ手順
```

---

## 10. 依存関係グラフ

```
Phase 1 (基盤)
    │
    ▼
Phase 2 (Domain) ──────────────────┐
    │                              │
    ▼                              │
Phase 3 (Infrastructure) ◀─────────┤
    │                              │
    ├──────────────────────────────┤
    │                              │
    ▼                              ▼
Phase 4 (Application)         Phase 6 (Data)
    │                              │
    ▼                              │
Phase 5 (MCP Interface) ◀──────────┘
    │
    ▼
Phase 7 (Test)
    │
    ▼
Phase 8 (Deploy)
```

---

## 11. チェックリスト

### MVP（Phase 1-5, 6-7の一部）

- [ ] プロジェクト基盤
- [ ] Domain Layer
- [ ] Neo4j Adapter
- [ ] ChromaDB Adapter
- [ ] esperanto Adapter
- [ ] Search Service
- [ ] Reasoning Service
- [ ] MCP Server基盤
- [ ] Search Tools (8)
- [ ] Reasoning Tools (6)
- [ ] System Tools (3)
- [ ] 基本データロード (50理論)
- [ ] E2Eテスト

### フルリリース

- [ ] 全Services
- [ ] 全Tools (33)
- [ ] 全Resources (15)
- [ ] 全Prompts (15)
- [ ] 全データ (200理論)
- [ ] ドキュメント
- [ ] CI/CD

---

## 変更履歴

| バージョン | 日付 | 変更者 | 変更内容 |
|-----------|------|--------|---------|
| 1.0 | 2025-12-26 | GitHub Copilot | 初版作成 |
