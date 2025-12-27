# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- **Theory Editor E2Eテスト**: Playwright による14件のE2Eテスト
- **InferenceService単体テスト**: 10件のテストケース

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

[Unreleased]: https://github.com/nahisaho/TENJIN/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/nahisaho/TENJIN/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/nahisaho/TENJIN/releases/tag/v0.1.0
