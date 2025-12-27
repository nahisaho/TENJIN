# TENJIN Theory Editor

教育理論データを管理するためのWebベースエディターです。

## 概要

Theory Editorは、175件以上の教育理論データを効率的に編集・管理するためのツールです。GraphRAG（Neo4j）と連携してナレッジグラフを構築できます。

## 機能

### 基本機能
- 📝 **CRUD操作**: 理論の作成・読取・更新・削除
- 🔍 **検索・フィルタ**: 名前、説明、理論家名で検索、カテゴリでフィルタ
- 📁 **インポート/エクスポート**: JSON形式でデータの入出力
- 📜 **バージョン管理**: LocalStorageに50世代まで履歴保存
- 🔄 **GraphRAG同期**: Neo4jデータベースとの同期

### アクセシビリティ (WCAG 2.1 AA)
- ⌨️ キーボードナビゲーション対応
- 🔊 スクリーンリーダー対応
- 🎯 フォーカス管理
- 🌗 高コントラスト・ダークモード対応

## クイックスタート

### 前提条件
- Python 3.x（HTTPサーバー用）
- Node.js 18+（テスト用、オプション）
- Docker（GraphRAG同期用、オプション）

### 起動方法

```bash
# プロジェクトルートに移動
cd /home/nahisaho/GitHub/TENJIN

# HTTPサーバーを起動（ポート8080）
python3 -m http.server 8080

# ブラウザでアクセス
# http://localhost:8080/tools/theory-editor/
```

### GraphRAG同期を使用する場合

```bash
# 1. Neo4jを起動
cd References/TENGIN-GraphRAG
docker compose up -d

# 2. 同期サーバーを起動（別ターミナル）
cd /home/nahisaho/GitHub/TENJIN
python3 tools/theory-editor/sync-server.py

# 3. HTTPサーバーを起動（別ターミナル）
python3 -m http.server 8080

# 4. ブラウザで「🔄 GraphRAG同期」ボタンをクリック
```

## 使い方

### 理論の編集

1. 左側の理論一覧から編集したい理論をクリック
2. 右側のフォームで内容を編集
3. 「💾 保存」ボタンをクリック

### 新規理論の追加

1. 「➕ 新規」ボタンをクリック
2. フォームに情報を入力（IDは自動生成）
3. 「💾 保存」ボタンをクリック

### 理論の削除

1. 削除したい理論を選択
2. 「🗑️ 削除」ボタンをクリック
3. 確認ダイアログで「削除」をクリック

### 検索・フィルタ

- **テキスト検索**: 名前、説明、理論家名で検索
- **カテゴリフィルタ**: ドロップダウンでカテゴリを選択

### バージョン管理

- **履歴表示**: 「📜 履歴」ボタンで全体履歴を表示
- **理論別履歴**: 「📋 理論履歴」で選択中の理論の変更履歴
- **復元**: 履歴から任意のバージョンを復元可能
- **差分表示**: バージョン間の差分をハイライト表示

### インポート/エクスポート

- **インポート**: 「📂 インポート」でJSONファイルを読み込み
- **エクスポート**: 「💾 エクスポート」で現在のデータをダウンロード

## キーボードショートカット

| キー | 機能 |
|------|------|
| `Ctrl + S` | 保存 |
| `Escape` | モーダルを閉じる |
| `Enter` | リスト内で理論を選択 |
| `Tab` | フォーカス移動 |

## データ形式

### theories.json

```json
{
  "metadata": {
    "version": "1.0.0",
    "total_theories": 175,
    "last_updated": "2025-12-27T00:00:00.000Z"
  },
  "theories": [
    {
      "id": "theory-001",
      "name": "Constructivism",
      "name_ja": "構成主義",
      "category": "learning",
      "priority": 1,
      "theorists": ["Jean Piaget", "Lev Vygotsky"],
      "description": "A theory of learning...",
      "description_ja": "学習理論の一つで...",
      "key_principles": ["Active learning", "Prior knowledge"],
      "applications": ["Project-based learning"],
      "strengths": ["Student engagement"],
      "limitations": ["Time-intensive"]
    }
  ]
}
```

### カテゴリ一覧

| カテゴリ | 説明 | 件数 |
|---------|------|------|
| learning | 学習理論 | 25 |
| development | 発達理論 | 20 |
| motivation | 動機づけ | 18 |
| instruction | 教授法 | 17 |
| cognition | 認知理論 | 15 |
| assessment | 評価 | 12 |
| その他 | - | 68 |

## ディレクトリ構造

```
tools/theory-editor/
├── README.md           # このファイル
├── index.html          # メインHTML
├── app.js              # メインアプリケーション
├── styles.css          # スタイルシート
├── sync-server.py      # GraphRAG同期サーバー
├── js/
│   ├── validation.js   # データバリデーション
│   ├── diff.js         # 差分計算
│   ├── storage.js      # LocalStorage管理
│   ├── error-handler.js# エラーハンドリング
│   └── graphrag-sync.js# GraphRAG同期クライアント
├── tests/
│   ├── unit/           # ユニットテスト
│   └── e2e/            # E2Eテスト（Playwright）
├── test.html           # テストランナー
└── playwright.config.js# Playwright設定
```

## テスト

### ユニットテスト

```bash
cd tools/theory-editor

# 全テスト実行
node tests/unit/validation.test.js
node tests/unit/diff.test.js
node tests/unit/storage.test.js
node tests/unit/error-handler.test.js
```

### E2Eテスト（Playwright）

```bash
# 初回セットアップ
npm install
npx playwright install chromium

# テスト実行
npx playwright test
```

### ブラウザテスト

`test.html` をブラウザで開いてテストを実行できます。

## トラブルシューティング

### 理論一覧が表示されない

1. HTTPサーバーが起動しているか確認
2. ブラウザのコンソールでエラーを確認
3. `data/theories/theories.json` が存在するか確認

### GraphRAG同期が失敗する

1. Neo4jが起動しているか確認: `docker compose ps`
2. 同期サーバーが起動しているか確認: `curl http://localhost:8081/health`
3. uvがインストールされているか確認

### バリデーションエラー

- 英語名または日本語名のどちらかは必須
- カテゴリは必須
- IDは自動生成（手動入力不要）

## 技術仕様

- **フロントエンド**: Vanilla JavaScript (ES6+)
- **スタイル**: CSS3 (CSS Variables, Flexbox, Grid)
- **データストア**: LocalStorage (バージョン管理)
- **バックエンド**: Python HTTPサーバー
- **GraphRAG**: Neo4j 5 Community Edition
- **テスト**: Playwright, カスタムテストランナー

## 関連ドキュメント

- [API リファレンス](docs/API.md)
- [設計書](../../storage/specs/DESIGN-002-theory-editor.md)
- [要件定義](../../storage/specs/REQ-002-theory-editor.md)
- [タスク分解](../../storage/specs/TASKS-002-theory-editor.md)
- [GraphRAG ドキュメント](../../References/TENGIN-GraphRAG/README.md)

## ライセンス

MIT License

## 更新履歴

### v1.1.0 (2025-12-27)
- GraphRAG同期機能追加
- バリデーションモジュール分離
- エラーハンドリング強化
- アクセシビリティ対応 (WCAG 2.1 AA)
- Playwrightによるe2eテスト追加

### v1.0.0 (2025-12-25)
- 初期リリース
- CRUD操作
- 検索・フィルタ
- バージョン管理
