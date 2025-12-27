# TENJIN - 教育理論GraphRAG MCPサーバー

<div align="center">

**教育理論の知識をGraphRAGで提供するModel Context Protocol (MCP) サーバー**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.5+-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP%20Complete-brightgreen.svg)]()

[English](README.en.md) | 日本語

</div>

## 概要

TENJINは、175+の教育理論をGraph + Vector RAG（Retrieval-Augmented Generation）技術で提供するMCPサーバーです。AIアシスタントが教育理論の知識を活用して、教育者、研究者、学習者をサポートします。

### 主な機能

- 🎓 **175+ 教育理論**: 学習理論、発達理論、教授法など9カテゴリーの包括的なデータベース
- 🔍 **ハイブリッド検索**: グラフ構造検索 + ベクトル類似検索 + LLMリランキング- 🧠 **高度な推論機能**: 理論推薦、ギャップ分析、関係推論、エビデンス推論 (NEW in v0.2)- 🌐 **マルチLLMサポート**: [esperanto](https://github.com/lfnovo/esperanto)による15+ LLMプロバイダー対応
- 📚 **MCPツール**: 理論検索、分析、比較、推薦、引用生成など
- 🇯🇵 **日本語対応**: 日本語・英語バイリンガルサポート
- 🏗️ **クリーンアーキテクチャ**: 保守性・テスト容易性の高い4層構造
- 🛠️ **Theory Editor**: 教育理論データを編集・管理するWebツール

## クイックスタート

### 前提条件

- Python 3.11以上
- Docker & Docker Compose（Neo4j用）
- Ollama または API Key（OpenAI, Anthropic, 等）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-org/tenjin.git
cd tenjin

# 依存関係をインストール（uvを推奨）
pip install uv
uv sync

# 環境変数を設定
cp .env.example .env
# .envファイルを編集
```

### データベース起動

```bash
# Neo4jを起動
docker-compose up -d neo4j

# データベースが起動するまで待機（初回は約30秒）
sleep 30
```

### データロード

```bash
# 教育理論データをロード
uv run python -m scripts.load_data
```

### VS Code MCPサーバー設定

`.vscode/mcp.json`が既に設定されています。VS Codeで`@tengin-graphrag`として使用可能です。

**Ollama使用時（推奨・無料）:**

```json
{
  "servers": {
    "tengin-graphrag": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "${workspaceFolder}/References/TENGIN-GraphRAG",
      "env": {
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```

> **Note**: Ollamaを使用する場合は、事前に`ollama pull nomic-embed-text`でモデルをダウンロードしてください。

**OpenAI使用時（高精度・有料）:**

```json
{
  "servers": {
    "tengin-graphrag": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "${workspaceFolder}/References/TENGIN-GraphRAG",
      "env": {
        "EMBEDDING_PROVIDER": "openai",
        "EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_API_KEY": "sk-your-openai-key"
      }
    }
  }
}
```

**Azure OpenAI使用時（エンタープライズ向け）:**

```json
{
  "servers": {
    "tengin-graphrag": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "${workspaceFolder}/References/TENGIN-GraphRAG",
      "env": {
        "EMBEDDING_PROVIDER": "azure",
        "EMBEDDING_MODEL": "text-embedding-3-small",
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "your-azure-openai-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-01"
      }
    }
  }
}
```

### Claude Desktopとの連携

`claude_desktop_config.json`に以下を追加:

```json
{
  "mcpServers": {
    "tenjin": {
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "/path/to/tenjin/References/TENGIN-GraphRAG",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text"
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
│  │InferenceSvc  │ │Service       │ │MethodologyService    ││
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

## MCPツール

主要なMCPツール:

| ツール | 説明 |
|--------|------|
| `search_theories` | キーワード・意味検索で理論を検索 |
| `get_theory` | 理論の詳細情報を取得 |
| `traverse_graph` | 関連理論をグラフ探索 |
| `compare_theories` | 複数の理論を比較分析 |
| `cite_theory` | APA/MLA形式で引用生成 |
| `recommend_theories_for_learner` | 🆕 学習者向け理論推薦 |
| `analyze_learning_design_gaps` | 🆕 学習設計ギャップ分析 |
| `infer_theory_relationships` | 🆕 理論関係推論 |
| `reason_about_application` | 🆕 適用推論 |

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

## 設定

### 環境変数

```bash
# データベース
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Embedding (Ollamaを推奨)
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
OLLAMA_HOST=http://localhost:11434

# または OpenAI
# EMBEDDING_PROVIDER=openai
# EMBEDDING_MODEL=text-embedding-3-small
# OPENAI_API_KEY=your-key

# ログ
LOG_LEVEL=INFO
```

### 対応Embeddingプロバイダー

esperantoを通じて以下のプロバイダーに対応:

| プロバイダー | モデル例 | 次元数 |
|-------------|---------|--------|
| **Ollama** (推奨) | nomic-embed-text | 768 |
| OpenAI | text-embedding-3-small | 1536 |
| Google | text-embedding-004 | 768 |
| Azure OpenAI | text-embedding-ada-002 | 1536 |

## ツール

### Theory Editor

教育理論データを編集・管理するWebベースのGUIツール。

```bash
# Theory Editorを起動
cd tools/theory-editor
python -m http.server 8080

# ブラウザで開く
open http://localhost:8080
```

**機能:**
- 理論の追加・編集・削除
- カテゴリー・タグによるフィルタリング
- バージョン管理・差分表示
- Neo4jへのリアルタイム同期（sync-server.py）
- JSON/CSVエクスポート

詳細: [tools/theory-editor/README.md](tools/theory-editor/README.md)

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
├── .vscode/                 # VS Code設定
│   └── mcp.json             # MCPサーバー設定
├── src/tenjin/              # メインソースコード
│   ├── domain/              # ドメイン層
│   │   ├── entities/        # エンティティ
│   │   ├── value_objects/   # 値オブジェクト
│   │   └── repositories/    # リポジトリインターフェース
│   ├── application/         # アプリケーション層
│   │   └── services/        # ビジネスロジックサービス
│   ├── infrastructure/      # インフラ層
│   │   ├── adapters/        # 外部システムアダプター
│   │   └── config/          # 設定
│   └── interface/           # インターフェース層 (MCP)
├── tools/                   # 開発支援ツール
│   └── theory-editor/       # 教育理論エディター (Web GUI)
│       ├── index.html
│       ├── js/              # モジュール化されたJS
│       ├── sync-server.py   # Neo4j同期サーバー
│       └── docs/            # ドキュメント
├── data/theories/           # 教育理論JSONデータ
├── tests/                   # テストスイート
├── scripts/                 # ユーティリティスクリプト
├── steering/                # プロジェクトメモリ (MUSUBI SDD)
├── storage/specs/           # 仕様書
├── docker-compose.yml
└── pyproject.toml
```

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## 貢献

プルリクエストを歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)を参照してください。

## ドキュメント

- [インストールガイド](docs/INSTALLATION_GUIDE.ja.md) - セットアップ手順
- [使用ガイド](docs/USAGE_GUIDE.ja.md) - 基本的な使い方
- [APIリファレンス](docs/API_REFERENCE.md)
- [デプロイメント](docs/DEPLOYMENT.md)
- [Theory Editor](tools/theory-editor/README.md)

## 関連プロジェクト

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [esperanto](https://github.com/lfnovo/esperanto)
- [Neo4j](https://neo4j.com/)
- [Ollama](https://ollama.ai/)

---

**TENJIN** - 教育理論の知恵をAIの力で 🎓
