# TENJIN - 教育理論GraphRAG MCPサーバー

<div align="center">

![TENJIN Logo](docs/images/logo.png)

**教育理論の知識をGraphRAGで提供するModel Context Protocol (MCP) サーバー**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.5+-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.en.md) | 日本語

</div>

## 概要

TENJINは、200以上の教育理論をGraph + Vector RAG（Retrieval-Augmented Generation）技術で提供するMCPサーバーです。AIアシスタントが教育理論の知識を活用して、教育者、研究者、学習者をサポートします。

### 主な機能

- 🎓 **200+ 教育理論**: 学習理論、発達理論、教授法など9カテゴリーの包括的なデータベース
- 🔍 **ハイブリッド検索**: グラフ構造検索 + ベクトル類似検索 + LLMリランキング
- 🌐 **マルチLLMサポート**: [esperanto](https://github.com/lfnovo/esperanto)による15+ LLMプロバイダー対応
- 📚 **33+ MCPツール**: 理論検索、分析、比較、推薦、引用生成など
- 🇯🇵 **日本語対応**: 日本語・英語バイリンガルサポート
- 🏗️ **クリーンアーキテクチャ**: 保守性・テスト容易性の高い4層構造

## クイックスタート

### 前提条件

- Python 3.11以上
- Docker & Docker Compose（データベース用）
- API Key（OpenAI, Anthropic, または他のLLMプロバイダー）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-org/tenjin.git
cd tenjin

# 依存関係をインストール
pip install -e .

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してAPI Keyを設定
```

### データベース起動

```bash
# Neo4j + Redis を起動
docker-compose up -d

# データベースが起動するまで待機
sleep 30
```

### データロード

```bash
# 教育理論データをロード
python -m scripts.load_data --clear
```

### MCPサーバー起動

```bash
# MCPサーバーを起動
python -m tenjin
```

### Claude Desktopとの連携

`claude_desktop_config.json`に以下を追加:

```json
{
  "mcpServers": {
    "tenjin": {
      "command": "python",
      "args": ["-m", "tenjin"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Layer (MCP)                     │
│  ┌─────────┐ ┌───────────┐ ┌─────────┐ ┌─────────────────┐ │
│  │  Tools  │ │ Resources │ │ Prompts │ │ TenjinServer    │ │
│  │ (33+)   │ │ (15)      │ │ (15)    │ │                 │ │
│  └────┬────┘ └─────┬─────┘ └────┬────┘ └────────┬────────┘ │
└───────┼────────────┼────────────┼───────────────┼──────────┘
        │            │            │               │
┌───────┼────────────┼────────────┼───────────────┼──────────┐
│       ▼            ▼            ▼               ▼           │
│                   Application Layer                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│
│  │TheoryService │ │SearchService │ │AnalysisService       ││
│  │GraphService  │ │Recommendation│ │CitationService       ││
│  │              │ │Service       │ │MethodologyService    ││
│  └──────┬───────┘ └──────┬───────┘ └───────────┬──────────┘│
└─────────┼────────────────┼─────────────────────┼───────────┘
          │                │                     │
┌─────────┼────────────────┼─────────────────────┼───────────┐
│         ▼                ▼                     ▼            │
│                    Domain Layer                             │
│  ┌────────────────┐ ┌──────────────┐ ┌───────────────────┐ │
│  │    Entities    │ │ Value Objects│ │Repository         │ │
│  │Theory,Theorist │ │TheoryId,     │ │Interfaces         │ │
│  │Category,etc.   │ │CategoryType  │ │                   │ │
│  └────────────────┘ └──────────────┘ └───────────────────┘ │
└────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────┐
│                             ▼                               │
│                  Infrastructure Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐ │
│  │ Neo4jAdapter│ │ChromaDB     │ │EsperantoAdapter       │ │
│  │ (Graph DB)  │ │Adapter      │ │(Multi-LLM)            │ │
│  │             │ │(Vector DB)  │ │                       │ │
│  └─────────────┘ └─────────────┘ └───────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## MCPツール一覧

### 理論ツール (6)
| ツール | 説明 |
|--------|------|
| `get_theory` | IDで理論を取得 |
| `list_theories` | 全理論を一覧表示 |
| `get_theories_by_category` | カテゴリー別に理論を取得 |
| `get_theories_by_priority` | 優先度別に理論を取得 |
| `get_theory_details` | 理論の詳細情報を取得 |
| `get_theory_statistics` | 理論統計を取得 |

### 検索ツール (5)
| ツール | 説明 |
|--------|------|
| `search_theories` | キーワードで理論を検索 |
| `semantic_search` | 意味的類似性で検索 |
| `hybrid_search` | グラフ+ベクトルハイブリッド検索 |
| `find_similar_theories` | 類似理論を発見 |
| `advanced_search` | フィルター付き高度検索 |

### グラフツール (7)
| ツール | 説明 |
|--------|------|
| `get_related_theories` | 関連理論を取得 |
| `find_theory_path` | 理論間のパスを発見 |
| `get_theory_network` | 理論ネットワークを取得 |
| `get_theory_clusters` | 理論クラスターを取得 |
| `get_influential_theories` | 影響力の高い理論を取得 |
| `get_theory_lineage` | 理論の系譜を取得 |
| `visualize_relationships` | 関係性を可視化 |

### 分析ツール (4)
| ツール | 説明 |
|--------|------|
| `compare_theories` | 理論を比較 |
| `analyze_theory` | 理論を深く分析 |
| `synthesize_theories` | 複数理論を統合 |
| `get_theory_applications` | 応用例を取得 |

### 推薦ツール (5)
| ツール | 説明 |
|--------|------|
| `recommend_theories` | コンテキストに基づく推薦 |
| `recommend_similar` | 類似理論を推薦 |
| `recommend_for_learner` | 学習者プロファイルに基づく推薦 |
| `create_learning_path` | 学習パスを作成 |
| `recommend_for_context` | 教育コンテキストに基づく推薦 |

### 引用ツール (4)
| ツール | 説明 |
|--------|------|
| `generate_citation` | 引用を生成（APA/MLA/Chicago/Harvard） |
| `generate_bibliography` | 参考文献リストを生成 |
| `export_citations` | 引用をエクスポート（BibTeX/RIS） |
| `preview_citation` | 引用のプレビュー |

### 方法論ツール (6)
| ツール | 説明 |
|--------|------|
| `get_methodology` | 方法論を取得 |
| `list_methodologies` | 全方法論を一覧表示 |
| `search_methodologies` | 方法論を検索 |
| `recommend_methodology` | 方法論を推薦 |
| `get_implementation_guide` | 実装ガイドを取得 |
| `get_methodology_evidence` | エビデンスを取得 |

## MCPリソース (15)

- `theories://all` - 全理論
- `theories://category/{category}` - カテゴリー別理論
- `theories://priority/{level}` - 優先度別理論
- `theory://{theory_id}` - 個別理論
- `theorists://all` - 全理論家
- `theorist://{theorist_id}` - 個別理論家
- `categories://all` - 全カテゴリー
- `relationships://all` - 全関係性
- `relationships://type/{type}` - タイプ別関係性
- `graph://full` - 完全グラフ
- `graph://theory/{theory_id}` - 理論別グラフ
- `statistics://theories` - 理論統計
- `statistics://categories` - カテゴリー統計
- `methodologies://all` - 全方法論
- `methodology://{methodology_id}` - 個別方法論

## MCPプロンプト (15)

- `lesson_plan` - 授業計画作成
- `theory_analysis` - 理論分析
- `theory_comparison` - 理論比較
- `research_proposal` - 研究提案
- `assessment_design` - 評価設計
- `student_guidance` - 学生指導
- `curriculum_design` - カリキュラム設計
- `professional_development` - 専門性開発
- `learning_path` - 学習パス
- `theory_application` - 理論応用
- `evidence_synthesis` - エビデンス統合
- `methodology_guide` - 方法論ガイド
- `japanese_context` - 日本の教育コンテキスト
- `technology_integration` - テクノロジー統合
- `collaborative_learning` - 協働学習

## 教育理論カテゴリー

| カテゴリー | 説明 | 理論数 |
|-----------|------|--------|
| 学習理論 | 行動主義、認知主義、構成主義など | 38 |
| 発達理論 | 認知発達、社会情動的発達など | 18 |
| 教授法 | PBL、反転学習、ソクラテス式など | 32 |
| カリキュラム | 逆向き設計、スパイラルカリキュラムなど | 10 |
| 動機づけ | 自己決定理論、成長マインドセットなど | 16 |
| 評価 | 形成的評価、ルーブリック評価など | 12 |
| 社会的学習 | 協同学習、実践共同体など | 18 |
| 東洋・アジア | 授業研究、儒教教育思想など | 28 |
| テクノロジー | コネクティビズム、TPACKなど | 22 |
| 現代教育 | 21世紀型スキル、SEL、UDLなど | 16 |
| 批判的・代替 | 批判的教育学、インクルーシブ教育など | 26 |

## 設定

### 環境変数

```bash
# データベース
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
CHROMADB_PATH=./data/chromadb

# LLM (esperanto)
LLM_PROVIDER=openai  # openai, anthropic, google, ollama, etc.
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=your-key  # プロバイダーに応じたキー

# Embedding
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

# サーバー
LOG_LEVEL=INFO
```

### 対応LLMプロバイダー

esperantoを通じて以下のプロバイダーに対応:

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Google (Gemini)
- Ollama (ローカルLLM)
- Azure OpenAI
- AWS Bedrock
- Groq
- その他多数...

## 開発

### テスト実行

```bash
# 全テスト
pytest

# カバレッジ付き
pytest --cov=tenjin --cov-report=html

# 特定のテスト
pytest tests/unit/test_entities.py -v
```

### 型チェック

```bash
mypy src/tenjin
```

### コードフォーマット

```bash
ruff format src tests
ruff check --fix src tests
```

## ディレクトリ構造

```
tenjin/
├── src/tenjin/
│   ├── __init__.py
│   ├── __main__.py
│   ├── domain/              # ドメイン層
│   │   ├── entities/        # エンティティ
│   │   ├── value_objects/   # 値オブジェクト
│   │   └── repositories/    # リポジトリインターフェース
│   ├── application/         # アプリケーション層
│   │   └── services/        # ビジネスロジックサービス
│   ├── infrastructure/      # インフラ層
│   │   ├── adapters/        # 外部システムアダプター
│   │   ├── repositories/    # リポジトリ実装
│   │   ├── config/          # 設定
│   │   └── data/            # データローダー
│   └── interface/           # インターフェース層
│       ├── mcp/             # MCPサーバー
│       │   ├── server.py
│       │   ├── tools/       # MCPツール
│       │   ├── resources/   # MCPリソース
│       │   └── prompts/     # MCPプロンプト
│       └── api/             # REST API（オプション）
├── data/
│   └── theories/            # 教育理論JSONデータ
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/
│   └── load_data.py         # データロードスクリプト
├── docs/                    # ドキュメント
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## 貢献

プルリクエストを歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)を参照してください。

## 関連プロジェクト

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [esperanto](https://github.com/lfnovo/esperanto)
- [Neo4j](https://neo4j.com/)
- [ChromaDB](https://www.trychroma.com/)

---

**TENJIN** - 教育理論の知恵をAIの力で
