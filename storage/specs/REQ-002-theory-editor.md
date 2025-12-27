# 要件仕様書: 教育理論エディター

**ID**: REQ-002
**Feature**: Education Theory Editor
**Version**: 1.1
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Status**: Implemented
**Author**: GitHub Copilot

---

## 1. 概要

### 1.1 背景

TENJINプロジェクトでは、教育理論データベース（theories.json）に175件の教育理論が収録されている。これらの理論データの追加・編集・削除を効率的に行うためのツールが必要とされている。

### 1.2 目的

教育理論データベースを管理するためのWebベースのエディターを提供し、以下を実現する：
- 理論データのCRUD操作（Create, Read, Update, Delete）
- 効率的な検索・フィルタリング機能
- データのインポート/エクスポート機能
- バージョン管理による変更履歴の追跡

### 1.3 スコープ

| 項目 | スコープ内 | スコープ外 | 備考 |
|------|-----------|-----------|------|
| 理論データのCRUD操作 | ✅ | | |
| 検索・フィルタリング機能 | ✅ | | |
| JSON インポート/エクスポート | ✅ | | |
| ローカルバージョン管理 | ✅ | | |
| 差分表示機能 | ✅ | | |
| エラーハンドリング | ✅ | | |
| アクセシビリティ対応 | ✅ | | キーボード操作 |
| CLIインターフェース | 🔜 | | 将来対応 |
| コアロジックのライブラリ化 | 🔜 | | 将来対応 |
| サーバーサイド実装 | | ❌ | |
| ユーザー認証 | | ❌ | |
| 複数ユーザー同時編集 | | ❌ | |
| Neo4jとの直接連携 | | ❌ | |

### 1.4 Constitution準拠

本要件は以下のConstitution条項に関連する：

| 条項 | 準拠状況 | 対応方針 |
|------|---------|----------|
| Article I: Library-First | 🔜 将来対応 | v2.0でコアロジックをライブラリ化 |
| Article II: CLI Interface | 🔜 将来対応 | v2.0でCLIインターフェース追加 |
| Article III: Test-First | ✅ 準拠 | 受け入れ基準でテスト項目定義 |

---

## 2. 機能要件

### 2.1 理論データ管理（FR-CRUD）

#### FR-CRUD-001: 理論一覧表示

| 項目 | 内容 |
|------|------|
| ID | FR-CRUD-001 |
| 要件種別 | Ubiquitous |
| 優先度 | Must Have |
| EARS形式 | The system shall display a list of all theories in the sidebar. |

**詳細仕様**:
- サイドバーに全理論のリストを表示する
- 各理論は名前（日本語優先）を表示する
- 現在選択中の理論をハイライト表示する
- 総理論数と表示中の理論数を統計として表示する

#### FR-CRUD-002: 理論詳細表示

| 項目 | 内容 |
|------|------|
| ID | FR-CRUD-002 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user selects a theory from the list, the system shall display the theory details in the editor panel. |

**詳細仕様**:
- 以下のフィールドを表示・編集可能にする：
  - 基本情報: ID、名前（英語）、名前（日本語）
  - 分類: カテゴリ、優先度
  - 関連者: 理論家（配列）
  - 説明: 概要（英語）、概要（日本語）
  - 詳細情報: 主要原則、応用例、強み、限界
- 未保存の変更がある場合は警告表示する

#### FR-CRUD-003: 理論追加

| 項目 | 内容 |
|------|------|
| ID | FR-CRUD-003 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user clicks the add button, the system shall create a new empty theory with a generated ID. |

**詳細仕様**:
- 新規理論のIDは自動生成（theory-XXX形式、次の連番）
- 新規理論はデフォルトカテゴリ「learning」、優先度「medium」で作成
- 作成後、自動的にエディタで選択状態にする

#### FR-CRUD-004: 理論保存

| 項目 | 内容 |
|------|------|
| ID | FR-CRUD-004 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user clicks the save button, the system shall validate and save the theory data. |

**詳細仕様**:
- 必須フィールド（ID、名前）の入力検証を行う
- 配列フィールド（theorists, key_principles等）はカンマ区切りで入力
- 保存成功時はステータスメッセージを表示
- 保存時に自動でバージョンを記録する

#### FR-CRUD-005: 理論削除

| 項目 | 内容 |
|------|------|
| ID | FR-CRUD-005 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user clicks the delete button, the system shall display a confirmation dialog before deleting. |

**詳細仕様**:
- 削除前に確認モーダルを表示する
- 削除対象の理論名を確認ダイアログに表示する
- 削除前に自動でバージョンを記録する
- 削除後は次の理論を自動選択する

---

### 2.2 検索・フィルタリング（FR-SEARCH）

#### FR-SEARCH-001: テキスト検索

| 項目 | 内容 |
|------|------|
| ID | FR-SEARCH-001 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user enters text in the search field, the system shall filter theories by name, description, and theorists. |

**詳細仕様**:
- 検索対象フィールド：
  - 名前（英語・日本語）
  - 説明（英語・日本語）
  - 理論家名
- 大文字小文字を区別しない
- リアルタイムで検索結果を反映

#### FR-SEARCH-002: カテゴリフィルタ

| 項目 | 内容 |
|------|------|
| ID | FR-SEARCH-002 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user selects a category from the dropdown, the system shall filter theories by the selected category. |

**詳細仕様**:
- カテゴリリストはデータから動的に取得する
- 現在の主要カテゴリ（参考）：
  - learning（学習理論）
  - development（発達理論）
  - instruction（教授理論）
  - motivation（動機づけ理論）
  - assessment（評価理論）
  - social（社会的学習理論）
  - cognitive（認知理論）
  - curriculum（カリキュラム理論）
- 「すべて」オプションでフィルタ解除
- 新規カテゴリが追加された場合、自動的にドロップダウンに反映

#### FR-SEARCH-003: 複合フィルタ

| 項目 | 内容 |
|------|------|
| ID | FR-SEARCH-003 |
| 要件種別 | Complex |
| 優先度 | Should Have |
| EARS形式 | While a category filter is active, when the user enters search text, the system shall apply both filters simultaneously. |

**詳細仕様**:
- テキスト検索とカテゴリフィルタはAND条件で適用
- フィルタ結果件数を統計に表示

---

### 2.3 データ入出力（FR-IO）

#### FR-IO-001: JSONエクスポート

| 項目 | 内容 |
|------|------|
| ID | FR-IO-001 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user clicks the export button, the system shall download the complete theories data as a JSON file. |

**詳細仕様**:
- ファイル名形式: theories_YYYY-MM-DD.json
- メタデータ（last_updated, version）を含める
- pretty-print形式（インデント2スペース）でエクスポート
- エクスポート前にバージョンを自動記録

#### FR-IO-002: JSONインポート

| 項目 | 内容 |
|------|------|
| ID | FR-IO-002 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user selects a JSON file for import, the system shall validate and load the theories data. |

**詳細仕様**:
- 有効なJSONファイルのみ受け入れる
- theories配列の存在を検証する
- インポート前に現在のデータをバージョンとして自動バックアップ
- インポート成功時にUIを更新

---

### 2.4 バージョン管理（FR-VERSION）

#### FR-VERSION-001: 自動バージョン保存

| 項目 | 内容 |
|------|------|
| ID | FR-VERSION-001 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user performs a save, delete, import, or export operation, the system shall automatically save a version snapshot. |

**詳細仕様**:
- 以下の操作時に自動でバージョンを保存：
  - 理論の保存
  - 理論の削除
  - データのインポート
  - データのエクスポート
- バージョンには操作種別を自動で説明として付与

#### FR-VERSION-002: バージョン履歴表示

| 項目 | 内容 |
|------|------|
| ID | FR-VERSION-002 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user clicks the history button, the system shall display a modal with all saved versions. |

**詳細仕様**:
- バージョンごとに以下を表示：
  - 保存日時
  - 説明
  - 理論数
- 最大50バージョンを保持（古いものから自動削除）
- ストレージ使用量を表示

#### FR-VERSION-003: バージョン復元

| 項目 | 内容 |
|------|------|
| ID | FR-VERSION-003 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user clicks the restore button for a version, the system shall restore the data after creating a backup of the current state. |

**詳細仕様**:
- 復元前に現在のデータを自動バックアップ
- 復元後にUIを更新
- 成功メッセージを表示

#### FR-VERSION-004: 差分表示

| 項目 | 内容 |
|------|------|
| ID | FR-VERSION-004 |
| 要件種別 | Event-Driven |
| 優先度 | Should Have |
| EARS形式 | When the user clicks the diff button for a version, the system shall display the differences between that version and the current data. |

**詳細仕様**:
- 以下の変更を検出・表示：
  - 追加された理論（緑色表示）
  - 削除された理論（赤色表示）
  - 変更された理論（黄色表示）
- 変更された理論は詳細フィールドの差分を表示

#### FR-VERSION-005: バージョン削除

| 項目 | 内容 |
|------|------|
| ID | FR-VERSION-005 |
| 要件種別 | Event-Driven |
| 優先度 | Should Have |
| EARS形式 | When the user clicks the delete button for a version, the system shall remove that version from history. |

**詳細仕様**:
- 個別バージョンの削除が可能
- 全履歴クリア機能も提供
- 削除確認は不要（即時削除）

---

### 2.5 エラーハンドリング（FR-ERROR）

#### FR-ERROR-001: JSONインポートエラー

| 項目 | 内容 |
|------|------|
| ID | FR-ERROR-001 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user imports an invalid JSON file, the system shall display a specific error message and preserve existing data. |

**詳細仕様**:
- 無効なJSON構文の場合: "JSONの解析に失敗しました" を表示
- theories配列が存在しない場合: "有効なtheoriesデータが見つかりません" を表示
- 既存データは変更しない
- エラーメッセージは3秒後に自動クリア

#### FR-ERROR-002: バリデーションエラー

| 項目 | 内容 |
|------|------|
| ID | FR-ERROR-002 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user saves a theory with missing required fields, the system shall highlight invalid fields and display validation messages. |

**詳細仕様**:
- 必須フィールド: ID、名前（英語または日本語）
- 不正なフィールドにエラースタイルを適用
- 具体的なエラーメッセージを表示（例: "名前は必須です"）
- フィールド修正後、エラースタイルを自動解除

#### FR-ERROR-003: ファイル読み込みエラー

| 項目 | 内容 |
|------|------|
| ID | FR-ERROR-003 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the system fails to load the initial data file, the system shall display an error message with retry option. |

**詳細仕様**:
- ネットワークエラー、ファイル不在時に対応
- "データの読み込みに失敗しました" を表示
- 「再試行」ボタンを提供
- 空のエディター状態で起動を継続可能

---

### 2.6 CLIインターフェース（FR-CLI）【将来対応】

> **注**: 本セクションはConstitution Article II準拠のため、v2.0での実装を予定

#### FR-CLI-001: 理論一覧取得

| 項目 | 内容 |
|------|------|
| ID | FR-CLI-001 |
| 要件種別 | Event-Driven |
| 優先度 | Could Have |
| EARS形式 | When the user runs `theory-editor list [--category <cat>]`, the system shall output all matching theory IDs and names. |

**詳細仕様**:
- 出力形式: `<ID>: <name> (<name_ja>)`
- --category オプションでフィルタリング
- --json オプションでJSON形式出力

#### FR-CLI-002: 理論検索

| 項目 | 内容 |
|------|------|
| ID | FR-CLI-002 |
| 要件種別 | Event-Driven |
| 優先度 | Could Have |
| EARS形式 | When the user runs `theory-editor search <query>`, the system shall output theories matching the query. |

**詳細仕様**:
- 名前、説明、理論家名を検索対象
- 大文字小文字を区別しない
- 結果件数をサマリー表示

#### FR-CLI-003: 理論詳細表示

| 項目 | 内容 |
|------|------|
| ID | FR-CLI-003 |
| 要件種別 | Event-Driven |
| 優先度 | Could Have |
| EARS形式 | When the user runs `theory-editor show <id>`, the system shall output the full details of the specified theory. |

**詳細仕様**:
- 全フィールドを整形して出力
- --json オプションでJSON形式出力
- 存在しないIDの場合はエラーメッセージ

#### FR-CLI-004: データエクスポート

| 項目 | 内容 |
|------|------|
| ID | FR-CLI-004 |
| 要件種別 | Event-Driven |
| 優先度 | Could Have |
| EARS形式 | When the user runs `theory-editor export <file>`, the system shall save the complete data to the specified file. |

**詳細仕様**:
- デフォルトファイル名: theories_YYYY-MM-DD.json
- 既存ファイルの上書き確認（--force で省略）
- pretty-print形式（--minify で圧縮）

---

## 3. 非機能要件

### 3.1 ユーザビリティ（NFR-USABILITY）

#### NFR-USABILITY-001: 直感的なUI

| 項目 | 内容 |
|------|------|
| ID | NFR-USABILITY-001 |
| 要件種別 | Ubiquitous |
| 優先度 | Must Have |
| EARS形式 | The system shall provide an intuitive user interface that requires no training to use. |

**詳細仕様**:
- 3カラムレイアウト（ヘッダー、サイドバー、エディタ）
- アイコン付きボタンで操作を視覚化
- 日本語UIを基本とする

#### NFR-USABILITY-002: フィードバック表示

| 項目 | 内容 |
|------|------|
| ID | NFR-USABILITY-002 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When the user performs any action, the system shall display appropriate feedback within 500ms. |

**詳細仕様**:
- 成功・エラー・警告をステータスバーに表示
- 未保存変更のインジケータを表示
- 3秒後にステータスメッセージを自動クリア

### 3.2 パフォーマンス（NFR-PERFORMANCE）

#### NFR-PERFORMANCE-001: 応答時間

| 項目 | 内容 |
|------|------|
| ID | NFR-PERFORMANCE-001 |
| 要件種別 | Ubiquitous |
| 優先度 | Should Have |
| EARS形式 | The system shall complete all operations within 1 second for datasets up to 500 theories. |

**詳細仕様**:
- 検索・フィルタリング: <100ms
- データ読み込み: <500ms
- データ保存: <200ms

### 3.3 信頼性（NFR-RELIABILITY）

#### NFR-RELIABILITY-001: データ保全

| 項目 | 内容 |
|------|------|
| ID | NFR-RELIABILITY-001 |
| 要件種別 | State-Driven |
| 優先度 | Must Have |
| EARS形式 | While the application is running, the system shall preserve data integrity through automatic version backups. |

**詳細仕様**:
- 破壊的操作前の自動バックアップ
- LocalStorageによる履歴永続化
- 最大50バージョンの履歴保持

### 3.4 互換性（NFR-COMPATIBILITY）

#### NFR-COMPATIBILITY-001: ブラウザ対応

| 項目 | 内容 |
|------|------|
| ID | NFR-COMPATIBILITY-001 |
| 要件種別 | Ubiquitous |
| 優先度 | Must Have |
| EARS形式 | The system shall be compatible with modern browsers (Chrome, Firefox, Edge, Safari). |

**詳細仕様**:
- ES6+ JavaScript対応
- CSS Grid/Flexboxによるレイアウト
- LocalStorage API使用

---

### 3.5 アクセシビリティ（NFR-ACCESSIBILITY）

#### NFR-ACCESSIBILITY-001: キーボード操作

| 項目 | 内容 |
|------|------|
| ID | NFR-ACCESSIBILITY-001 |
| 要件種別 | Ubiquitous |
| 優先度 | Should Have |
| EARS形式 | The system shall support keyboard navigation for all primary operations. |

**詳細仕様**:
- Tab: フォーカス移動（論理的な順序）
- Enter: 選択/実行
- Escape: モーダルクローズ、操作キャンセル
- Ctrl+S: 保存（ショートカット）
- フォーカス可視化（アウトライン表示）

#### NFR-ACCESSIBILITY-002: フォーム操作性

| 項目 | 内容 |
|------|------|
| ID | NFR-ACCESSIBILITY-002 |
| 要件種別 | Ubiquitous |
| 優先度 | Should Have |
| EARS形式 | The system shall provide accessible form controls with proper labels and error messages. |

**詳細仕様**:
- 全入力フィールドにラベルを関連付け
- プレースホルダーテキストで入力例を提示
- エラーメッセージはフィールド近くに表示
- 必須フィールドを明示

---

### 3.6 セキュリティ（NFR-SECURITY）

#### NFR-SECURITY-001: 入力サニタイズ

| 項目 | 内容 |
|------|------|
| ID | NFR-SECURITY-001 |
| 要件種別 | Ubiquitous |
| 優先度 | Must Have |
| EARS形式 | The system shall sanitize user input to prevent XSS attacks when displaying data. |

**詳細仕様**:
- HTMLエスケープ処理を適用
- innerHTMLの直接使用を避ける
- textContentまたはDOM APIを使用
- インポートデータも同様に処理

#### NFR-SECURITY-002: データ検証

| 項目 | 内容 |
|------|------|
| ID | NFR-SECURITY-002 |
| 要件種別 | Event-Driven |
| 優先度 | Must Have |
| EARS形式 | When importing data, the system shall validate the data structure before processing. |

**詳細仕様**:
- JSONスキーマに準拠した構造検証
- 不正なデータ型の検出
- 過度に大きなファイルの拒否（10MB上限）

---

## 4. データモデル

### 4.1 理論データ構造

```json
{
  "metadata": {
    "last_updated": "2025-12-27",
    "version": "1.0.0",
    "description": "Educational theories database"
  },
  "theories": [
    {
      "id": "theory-001",
      "name": "Theory Name",
      "name_ja": "理論名",
      "category": "learning",
      "priority": "high",
      "theorists": ["Theorist 1", "Theorist 2"],
      "description": "English description",
      "description_ja": "日本語説明",
      "key_principles": ["Principle 1", "Principle 2"],
      "applications": ["Application 1", "Application 2"],
      "strengths": ["Strength 1", "Strength 2"],
      "limitations": ["Limitation 1", "Limitation 2"]
    }
  ]
}
```

### 4.2 バージョンデータ構造

```json
{
  "id": "v-1703644800000",
  "timestamp": 1703644800000,
  "description": "自動保存: 理論保存",
  "data": {
    "metadata": { ... },
    "theories": [ ... ]
  }
}
```

---

## 5. 画面設計

### 5.1 画面構成

```
┌──────────────────────────────────────────────────────────────────┐
│                          HEADER                                   │
│  [TENJIN 教育理論エディター]    [📜履歴] [📥インポート] [📤エクスポート] │
├──────────────────┬───────────────────────────────────────────────┤
│    SIDEBAR       │                  EDITOR                        │
│                  │                                                 │
│  [🔍 検索...]    │  ┌───────────────────────────────────────┐    │
│  [カテゴリ ▼]    │  │ 理論名                                 │    │
│                  │  │ ════════════════════════════════════  │    │
│  統計: 175件     │  │                                        │    │
│  (表示: 50件)    │  │ 基本情報                               │    │
│                  │  │ - ID:                                   │    │
│  ─────────────   │  │ - 名前:                                 │    │
│                  │  │ - 名前(日本語):                         │    │
│  □ 行動主義      │  │ - カテゴリ:                             │    │
│  ■ 構成主義 ←選択│  │ - 優先度:                               │    │
│  □ 認知負荷理論  │  │                                        │    │
│  □ 社会的学習    │  │ 説明                                   │    │
│  □ ...          │  │ - 概要:                                 │    │
│                  │  │ - 概要(日本語):                         │    │
│                  │  │                                        │    │
│  [＋ 新規追加]   │  │ 詳細情報                               │    │
│                  │  │ - 主要原則:                             │    │
│                  │  │ - 応用例:                               │    │
│                  │  │ - 強み:                                 │    │
│                  │  │ - 限界:                                 │    │
│                  │  │                                        │    │
│                  │  │ [💾 保存] [🗑️ 削除] [📜 履歴]           │    │
│                  │  └───────────────────────────────────────┘    │
├──────────────────┴───────────────────────────────────────────────┤
│  STATUS: 保存しました                              [●未保存の変更] │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 モーダル一覧

| モーダル | トリガー | 内容 |
|---------|---------|------|
| 削除確認 | 🗑️ 削除ボタン | 理論名を表示し、削除確認を求める |
| バージョン履歴 | 📜 履歴ボタン | バージョン一覧、復元・差分・削除操作 |
| バージョン保存 | 手動保存時 | 説明入力フィールド |
| 差分表示 | 履歴の差分ボタン | 追加・削除・変更の一覧 |

---

## 6. 技術仕様

### 6.1 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| データストレージ | LocalStorage (バージョン履歴) |
| データ形式 | JSON |
| サーバー | Python HTTP Server（開発用） |

### 6.2 ファイル構成

```
tools/theory-editor/
├── index.html      # メインHTML
├── styles.css      # スタイルシート
└── app.js          # アプリケーションロジック
```

### 6.3 外部依存

- なし（Vanilla JavaScript、フレームワーク不使用）

---

## 7. 制約事項

### 7.1 技術的制約

| 制約 | 説明 |
|------|------|
| TC-001 | LocalStorageの容量制限（約5MB）によりバージョン履歴は最大50件 |
| TC-002 | ファイル直接保存にはブラウザのダウンロードAPIを使用（サーバー不要） |
| TC-003 | シングルページアプリケーションのため、ページ遷移なし |

### 7.2 運用制約

| 制約 | 説明 |
|------|------|
| OC-001 | 同時編集非対応（単一ユーザー想定） |
| OC-002 | オフライン動作可能（初回読み込み後） |
| OC-003 | データ永続化はエクスポート/インポートで対応 |

---

## 8. 受け入れ基準

### 8.1 機能テスト

| ID | テスト項目 | 期待結果 |
|----|-----------|---------|
| AT-001 | 理論一覧の表示 | 175件の理論がサイドバーに表示される |
| AT-002 | 理論の選択と表示 | 選択した理論の全フィールドがエディタに表示される |
| AT-003 | 新規理論の追加 | 新しいIDで理論が作成され、リストに追加される |
| AT-004 | 理論の編集と保存 | 変更が反映され、ステータスメッセージが表示される |
| AT-005 | 理論の削除 | 確認後に理論が削除され、リストから消える |
| AT-006 | テキスト検索 | 入力文字列を含む理論のみが表示される |
| AT-007 | カテゴリフィルタ | 選択カテゴリの理論のみが表示される |
| AT-008 | JSONエクスポート | 正しい形式のJSONファイルがダウンロードされる |
| AT-009 | JSONインポート | 有効なJSONファイルが読み込まれ、UIが更新される |
| AT-010 | バージョン自動保存 | 操作後にバージョンが履歴に追加される |
| AT-011 | バージョン復元 | 選択バージョンのデータが復元される |
| AT-012 | 差分表示 | 追加・削除・変更が正しく表示される |
| AT-013 | エラーハンドリング（インポート） | 無効なJSONファイルでエラーメッセージが表示される |
| AT-014 | エラーハンドリング（バリデーション） | 必須フィールド未入力で保存が阻止される |
| AT-015 | キーボード操作 | Tab/Enter/Escapeで基本操作が可能 |

### 8.2 テスト戦略

| テスト種別 | 対象 | ツール | カバレッジ目標 |
|-----------|------|--------|---------------|
| 単体テスト | バリデーション関数、差分計算 | Jest | 80% |
| 統合テスト | CRUD操作フロー | Playwright | 主要フロー100% |
| E2Eテスト | ユーザーシナリオ | Playwright | 受け入れ基準100% |
| 手動テスト | UI/UX、アクセシビリティ | - | 全画面 |

### 8.3 テストシナリオ（主要）

| ID | シナリオ | 前提条件 | 手順 | 期待結果 |
|----|---------|---------|------|----------|
| TS-001 | 新規理論作成フロー | エディター起動済み | 1. 新規追加クリック<br>2. 必須項目入力<br>3. 保存クリック | リストに追加、バージョン記録 |
| TS-002 | 検索・編集フロー | 理論データあり | 1. 検索キーワード入力<br>2. 理論選択<br>3. 編集・保存 | 変更反映、バージョン記録 |
| TS-003 | インポート・エクスポートフロー | 外部JSONファイルあり | 1. インポート実行<br>2. データ確認<br>3. エクスポート実行 | データ整合性維持 |
| TS-004 | バージョン復元フロー | バージョン履歴あり | 1. 履歴モーダル開く<br>2. 差分確認<br>3. 復元実行 | データ復元、新バージョン記録 |
| TS-005 | エラー回復フロー | - | 1. 無効JSON読み込み<br>2. エラー確認<br>3. 正常操作継続 | データ保護、操作継続可能 |

---

## 9. 用語集

| 用語 | 定義 |
|------|------|
| 理論 (Theory) | 教育理論データの1単位 |
| バージョン (Version) | 特定時点のデータスナップショット |
| CRUD | Create, Read, Update, Delete の略。基本的なデータ操作 |
| EARS | Easy Approach to Requirements Syntax。要件記述形式 |
| LocalStorage | ブラウザ組み込みのデータ永続化API |

---

## 10. 改訂履歴

| バージョン | 日付 | 変更内容 | 著者 |
|-----------|------|---------|------|
| 1.0 | 2025-12-27 | 初版作成 | GitHub Copilot |
| 1.1 | 2025-12-27 | Constitution準拠、エラーハンドリング、アクセシビリティ、セキュリティ、CLI（将来）、テスト戦略を追加 | GitHub Copilot |

---

## 11. 関連ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [REQ-001-education-theory-graphrag.md](REQ-001-education-theory-graphrag.md) | 教育理論GraphRAG MCPサーバー要件 |
| [ADR-001-technology-stack.md](ADR-001-technology-stack.md) | 技術スタック決定記録 |
| [ADR-002-graph-schema.md](ADR-002-graph-schema.md) | グラフスキーマ決定記録 |
