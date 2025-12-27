# Docker デプロイメントガイド

このドキュメントでは、TENJIN を Docker を使ってデプロイする方法を説明します。

## 🐳 クイックスタート

### 1. 基本的な起動

データベース（Neo4j, ChromaDB, Redis）を起動します：

```bash
docker-compose up -d neo4j chromadb redis
```

### 2. データの初期化

教育理論データをデータベースにロードします：

```bash
# initプロファイルを使用してデータローダーを実行
docker-compose --profile init run --rm data-loader
```

### 3. TENJIN サーバーの起動（オプション）

MCP サーバーをコンテナで起動する場合：

```bash
docker-compose --profile full up -d tenjin
```

## 📦 プリロード済みイメージの作成

教育理論データが事前にロードされた Docker イメージを作成できます。

### ビルドスクリプトを使用

```bash
./scripts/build-preloaded-image.sh
```

### 手動でビルド

```bash
# 1. データベースを起動
docker-compose -f docker-compose.preload.yml up -d neo4j chromadb

# 2. データベースが健康になるまで待機
docker-compose -f docker-compose.preload.yml ps

# 3. データをロード
docker-compose -f docker-compose.preload.yml run --rm data-loader

# 4. ボリュームをエクスポート（オプション）
docker run --rm -v tenjin_neo4j_preload:/source:ro -v $(pwd)/build:/backup alpine tar czf /backup/neo4j-data.tar.gz -C /source .
```

## 🔧 Docker イメージのビルド

### 基本イメージ

```bash
docker build -t tenjin:latest .
```

### データローダーイメージ

```bash
docker build --target data-loader -t tenjin:data-loader .
```

### ランタイムイメージ

```bash
docker build --target runtime -t tenjin:runtime .
```

## 🌐 環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j 接続 URI |
| `NEO4J_USERNAME` | `neo4j` | Neo4j ユーザー名 |
| `NEO4J_PASSWORD` | `password` | Neo4j パスワード |
| `CHROMADB_HOST` | `localhost` | ChromaDB ホスト |
| `CHROMADB_PORT` | `8000` | ChromaDB ポート |
| `EMBEDDING_PROVIDER` | `ollama` | 埋め込みプロバイダー |
| `EMBEDDING_MODEL` | `nomic-embed-text` | 埋め込みモデル |
| `OLLAMA_HOST` | `http://host.docker.internal:11434` | Ollama サーバー |

## 📁 Docker Compose プロファイル

| プロファイル | 説明 | 使用方法 |
|-------------|------|---------|
| (なし) | neo4j, chromadb, redis のみ | `docker-compose up -d` |
| `init` | データローダーを含む | `docker-compose --profile init run data-loader` |
| `full` | TENJIN サーバーを含む | `docker-compose --profile full up -d` |

## 🗂️ ボリューム

| ボリューム名 | 説明 |
|-------------|------|
| `neo4j_data` | Neo4j データベースファイル |
| `neo4j_logs` | Neo4j ログファイル |
| `redis_data` | Redis 永続化データ |
| `chromadb_data` | ChromaDB ベクトルデータ |

## 🔍 トラブルシューティング

### データベースの状態確認

```bash
# Neo4j のノード数を確認
docker-compose exec neo4j cypher-shell -u neo4j -p password "MATCH (n) RETURN count(n)"

# ChromaDB のコレクションを確認
curl http://localhost:8000/api/v1/collections
```

### ログの確認

```bash
# すべてのログ
docker-compose logs

# 特定のサービス
docker-compose logs neo4j
docker-compose logs data-loader
```

### データの再初期化

```bash
# ボリュームを削除してから再起動
docker-compose down -v
docker-compose up -d neo4j chromadb redis
docker-compose --profile init run --rm data-loader
```

## 🚀 本番環境へのデプロイ

本番環境では、以下を推奨します：

1. **セキュリティ**: 環境変数でパスワードを管理
2. **リソース制限**: CPU/メモリの制限を設定
3. **永続化**: 外部ボリュームまたはクラウドストレージを使用
4. **監視**: ヘルスチェックとログ収集を設定

```yaml
# 本番用の設定例
services:
  neo4j:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```
