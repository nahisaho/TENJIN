# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2025-12-28

### Added
- **synthesize_theoriesツール**: 複数理論の統合分析・比較
  - 統合フレームワークの生成
  - 理論間のシナジーと緊張関係の分析
  - 比較マトリックス生成
- **batch_searchツール**: 複数クエリの一括検索
  - 並列実行による高効率な検索
  - 共通理論の抽出
- **Theory Editor WebSocket**: リアルタイム同期
  - `ws-sync-server.py`: Starlette WebSocket + HTTPサーバー
  - 接続状態インジケーターUI
  - 理論の作成/更新/削除のブロードキャスト
- **検索フィルター拡張**: 年代・エビデンスレベルでフィルタリング
  - `year_from`/`year_to`: 年範囲フィルター
  - `decade`: 10年単位フィルター（例: "1990s"）
  - `evidence_level`: エビデンスレベルフィルター
- **エクスポート機能**: 3つの新しいエクスポートツール
  - `export_theories_json`: JSONフォーマット出力
  - `export_theories_markdown`: Markdown文書生成
  - `export_theories_csv`: CSVフォーマット出力
- **Redisキャッシュ統合**: 検索結果・理論データのキャッシング
  - `RedisAdapter`: 非同期Redis操作（get/set/delete）
  - `CacheService`: アプリケーションレベルのキャッシュ管理
  - `get_cache_stats` MCPツール: キャッシュ統計取得
  - `invalidate_cache` MCPツール: パターン指定でのキャッシュ無効化
  - 環境変数: `CACHE_ENABLED`, `CACHE_REDIS_URL`, `CACHE_TTL_SECONDS`
- **SSEトランスポート対応**: リモートMCPサーバーとしての動作
  - `--mode sse` オプションでSSEモード起動
  - `--host`/`--port` オプションでバインド設定
  - `/sse` エンドポイントでSSE接続
  - `/messages/` エンドポイントでPOSTメッセージ
  - `/health` ヘルスチェックエンドポイント
- **Docker SSEサービス**: `tenjin-sse` サービス追加
  - `docker-compose --profile sse` で起動
  - ポート8080で公開
- **依存関係追加**: starlette, uvicorn, redis, websockets

### Fixed
- ユニットテストを現在の実装に合わせて修正（51件パス）

### Tests
- E2Eテスト: 10件パス
- ユニットテスト: 51件パス
- 合計: 61件パス

## [0.2.1] - 2025-12-28

### Added
- **多言語エンベディング**: bge-m3モデルへの移行（100+言語対応）
  - 日本語検索精度の大幅向上
  - エンベディング次元: 768 → 1024
- **ChromaDB HTTPクライアント対応**: Docker環境でのHTTP接続サポート
  - `CHROMADB_HOST`/`CHROMADB_PORT` 環境変数による設定
  - ローカル開発用 PersistentClient との自動切り替え

### Fixed
- esperanto LLMプロバイダクラスの直接使用（OllamaLanguageModel, OpenAILanguageModel）
- LLMメソッド名修正（`chat_async` → `achat_complete`）
- Settings `.env`ファイル読み込み修正
- Neo4j Cypher修正（`length()` → `size()`）
- VectorRepository API修正（`search` → `semantic_search`）
- SearchResult属性修正（`entity_id` → `id`, `relevance_score` → `score`）
- Docker Compose: Linux環境でのOllama接続（extra_hosts設定）
- Dockerfile: __pycache__クリーンアップ追加

### Tests
- 単体テストをAPI変更に合わせて更新（18件パス）
- E2Eテスト全件パス（10件）

## [0.2.0] - 2025-12-28

### Added
- **InferenceService**: 高度なLLM推論操作
  - `recommend_theories_for_learner()`: 学習者プロファイルに基づく理論推薦
  - `analyze_learning_design_gaps()`: 学習設計のギャップ分析
  - `infer_theory_relationships()`: 理論間の関係推論
  - `reason_about_application()`: エビデンスに基づく推論
- **MCP推論ツール**: 4つの新しいMCPツール
  - `recommend_theories_for_learner`: 学習者向け理論推薦
  - `analyze_learning_design_gaps`: 学習設計ギャップ分析
  - `infer_theory_relationships`: 理論関係推論
  - `reason_about_application`: 適用推論
- **Docker機能強化**:
  - マルチステージDockerfile（base, runtime, data-loader）
  - docker-compose.preload.yml: プリロード用構成
  - ChromaDBサービス統合
  - データローダーサービス（profileベース）
  - ヘルスチェック設定
- **ビルドスクリプト**:
  - `scripts/build-preloaded-image.sh`: プリロード済みイメージ作成
  - `scripts/init_data.sh`: データ初期化スクリプト
- **Theory Editor E2Eテスト**: Playwright による14件のE2Eテスト
- **InferenceService単体テスト**: 10件のテストケース
- **ドキュメント**: Docker デプロイメントガイド（docs/DOCKER.ja.md）

### Fixed
- esperanto API互換性修正（`PROVIDERS` → `provider_classes`）
- `SearchQuery` 引数名修正（`query_text` → `query`）
- 空シナリオでのバリデーション追加

## [0.1.0] - 2025-12-27

### Added
- **クリーンアーキテクチャ実装**: 4層構造（Interface/Application/Domain/Infrastructure）
- **175+ 教育理論**: 11カテゴリーの包括的なナレッジグラフ
- **ハイブリッド検索**: セマンティック + グラフ + キーワード検索
- **MCPサーバー**: 33+ Tools, 15 Resources, 15 Prompts
- **マルチLLMサポート**: esperantoによる15+ プロバイダー対応
- **Theory Editor**: Webベースの教育理論データエディター
  - 理論の追加・編集・削除
  - カテゴリー/タグフィルタリング
  - バージョン管理・差分表示
  - Neo4j同期サーバー

### Services
- `TheoryService`: 理論データの取得・管理
- `SearchService`: ハイブリッド検索
- `GraphService`: グラフトラバーサル
- `AnalysisService`: 理論分析
- `RecommendationService`: 理論推薦
- `CitationService`: 引用生成
- `MethodologyService`: 教授法支援

### Infrastructure
- Neo4j: グラフデータベース
- ChromaDB: ベクトルデータベース
- esperanto: マルチLLM統合

### Documentation
- README.md（日本語）
- README.en.md（英語）
- Qiita記事
- インストールガイド
- 使用ガイド

[Unreleased]: https://github.com/nahisaho/TENJIN/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/nahisaho/TENJIN/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/nahisaho/TENJIN/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/nahisaho/TENJIN/releases/tag/v0.1.0
