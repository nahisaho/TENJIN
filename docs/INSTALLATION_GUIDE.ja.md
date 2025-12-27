# TENJIN インストールガイド

TENJIN教育理論GraphRAG MCPサーバーのインストールと設定の手順を説明します。

## 目次

- [システム要件](#システム要件)
- [インストール方法](#インストール方法)
  - [方法1: Dockerを使用（推奨）](#方法1-dockerを使用推奨)
  - [方法2: ローカル環境](#方法2-ローカル環境)
- [データベースのセットアップ](#データベースのセットアップ)
- [Embeddingプロバイダーの設定](#embeddingプロバイダーの設定)
  - [Ollama（推奨）](#ollama推奨)
  - [OpenAI](#openai)
- [MCPクライアントの設定](#mcpクライアントの設定)
  - [VS Code](#vs-code)
  - [Claude Desktop](#claude-desktop)
- [動作確認](#動作確認)
- [トラブルシューティング](#トラブルシューティング)

---

## システム要件

### 必須

| 項目 | 要件 |
|------|------|
| OS | Linux, macOS, Windows (WSL2推奨) |
| Python | 3.11以上 |
| Docker | 24.0以上 |
| Docker Compose | 2.0以上 |
| メモリ | 4GB以上（8GB推奨） |
| ストレージ | 2GB以上の空き容量 |

### 推奨

| 項目 | 推奨環境 |
|------|----------|
| Embedding | Ollama + nomic-embed-text |
| パッケージマネージャー | uv |
| エディタ | VS Code |

---

## インストール方法

### 方法1: Dockerを使用（推奨）

最も簡単な方法です。Neo4jデータベースをDockerで起動します。

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-org/tenjin.git
cd tenjin

# 2. 環境変数ファイルを作成
cp .env.example .env

# 3. Neo4jを起動
docker-compose up -d neo4j

# 4. 起動を確認（約30秒待機）
docker-compose ps
# neo4j が healthy になるまで待つ

# 5. Python依存関係をインストール
pip install uv
uv sync

# 6. 教育理論データをロード
uv run python -m scripts.load_data
```

### 方法2: ローカル環境

Neo4jをローカルにインストールする場合。

```bash
# 1. Neo4j Community Editionをインストール
# macOS
brew install neo4j

# Ubuntu/Debian
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j

# 2. Neo4jを起動
neo4j start

# 3. リポジトリをクローンして依存関係をインストール
git clone https://github.com/your-org/tenjin.git
cd tenjin
pip install uv
uv sync

# 4. 環境変数を設定
cp .env.example .env
# NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD を編集

# 5. データをロード
uv run python -m scripts.load_data
```

---

## データベースのセットアップ

### Neo4j接続確認

```bash
# Neo4jが起動していることを確認
docker-compose ps

# Neo4j Browser にアクセス（オプション）
# http://localhost:7474
# Username: neo4j
# Password: password
```

### データのロード

```bash
# 教育理論データをNeo4jにロード
uv run python -m scripts.load_data

# 出力例:
# Loading theories... Done (175 theories)
# Loading theorists... Done (89 theorists)
# Loading relationships... Done (342 relationships)
# Creating indexes... Done
```

### データの確認

Neo4j Browserで確認:

```cypher
// 理論数を確認
MATCH (t:Theory) RETURN count(t);

// カテゴリー別の理論数
MATCH (t:Theory) RETURN t.category, count(t) ORDER BY count(t) DESC;
```

---

## Embeddingプロバイダーの設定

### Ollama（推奨）

ローカルで動作し、APIキー不要で無料です。

#### 1. Ollamaのインストール

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# https://ollama.ai/download からインストーラーをダウンロード
```

#### 2. Embeddingモデルをダウンロード

```bash
# nomic-embed-text（768次元、推奨）
ollama pull nomic-embed-text

# 動作確認
ollama list
```

#### 3. 環境変数を設定

`.env`ファイルを編集:

```bash
# Embedding設定
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSIONS=768
OLLAMA_HOST=http://localhost:11434
```

#### リモートOllamaを使用する場合

別のマシンでOllamaが動作している場合:

```bash
OLLAMA_HOST=http://192.168.1.100:11434
```

### OpenAI

APIキーが必要ですが、高品質なEmbeddingを提供します。

#### 1. APIキーを取得

[OpenAI Platform](https://platform.openai.com/) でAPIキーを取得。

#### 2. 環境変数を設定

```bash
# Embedding設定
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
OPENAI_API_KEY=sk-your-api-key-here
```

---

## MCPクライアントの設定

### VS Code

#### 1. 設定ファイルを確認

`.vscode/mcp.json`が既に含まれています:

```json
{
  "servers": {
    "tengin-graphrag": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "${workspaceFolder}/References/TENGIN-GraphRAG",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```

#### 2. VS Code設定を確認

`.vscode/settings.json`:

```json
{
  "chat.mcp.discovery.enabled": true,
  "chat.mcp.enabled": true
}
```

#### 3. MCPサーバーを有効化

1. VS Codeを再起動
2. `Ctrl+Shift+P` → "MCP: List Servers"
3. "tengin-graphrag" が表示されることを確認

#### 4. 使用方法

Copilot Chatで:

```
@tengin-graphrag 認知負荷理論について教えて
```

### Claude Desktop

#### 1. 設定ファイルを編集

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tenjin": {
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "/path/to/tenjin/References/TENGIN-GraphRAG",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```

> **注意**: `cwd` は実際のパスに置き換えてください。

#### 2. Claude Desktopを再起動

設定後、Claude Desktopを完全に終了して再起動します。

#### 3. 使用方法

Claudeに直接質問:

```
TENJINを使って、探究型学習に関連する理論を教えて
```

---

## 動作確認

### 1. Neo4j接続テスト

```bash
cd References/TENGIN-GraphRAG
uv run python << 'EOF'
import asyncio
from tengin_mcp.infrastructure.adapters.neo4j_adapter import Neo4jAdapter
from tengin_mcp.infrastructure.config import Settings

async def test():
    settings = Settings()
    adapter = Neo4jAdapter(settings)
    await adapter.connect()
    result = await adapter.execute_query("MATCH (t:Theory) RETURN count(t) as count")
    print(f"✅ Neo4j接続成功: {result[0]['count']} 理論")
    await adapter.close()

asyncio.run(test())
EOF
```

### 2. MCPサーバーテスト

```bash
cd References/TENGIN-GraphRAG
uv run tengin-server --help
```

### 3. Embedding テスト

```bash
# Ollamaの場合
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "教育理論"
}'
```

---

## トラブルシューティング

### Neo4jに接続できない

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**解決方法**:
1. Neo4jが起動しているか確認: `docker-compose ps`
2. ポートが正しいか確認: `docker-compose logs neo4j`
3. 起動完了まで待機（初回は30-60秒）

### Ollamaに接続できない

```
ConnectionError: Failed to connect to Ollama
```

**解決方法**:
1. Ollamaが起動しているか確認: `ollama list`
2. ホストアドレスを確認（WSLの場合はホストのIPを使用）
3. ファイアウォール設定を確認

### MCPサーバーが認識されない

**VS Codeの場合**:
1. VS Codeを完全に再起動
2. `.vscode/mcp.json`のパスを確認
3. `uv`コマンドがPATHに通っているか確認

**Claude Desktopの場合**:
1. 設定ファイルのJSONが正しいか確認
2. `cwd`のパスが正しいか確認
3. Claude Desktopを完全に終了して再起動

### Python依存関係のエラー

```bash
# 仮想環境をリセット
rm -rf .venv
uv sync
```

### データロードエラー

```bash
# Neo4jを再起動
docker-compose restart neo4j
sleep 30

# データを再ロード
uv run python -m scripts.load_data --clear
```

---

## 次のステップ

インストールが完了したら:

1. **[使用ガイド](USAGE_GUIDE.ja.md)** - 基本的な使い方を学ぶ
2. **[APIリファレンス](API_REFERENCE.md)** - 利用可能なツールの詳細
3. **[Theory Editor](../tools/theory-editor/README.md)** - 理論データの編集

---

## サポート

問題が解決しない場合:

- [GitHub Issues](https://github.com/your-org/tenjin/issues) で報告
- [Discussions](https://github.com/your-org/tenjin/discussions) で質問

---

**TENJIN** - 教育理論の知恵をAIの力で 🎓
