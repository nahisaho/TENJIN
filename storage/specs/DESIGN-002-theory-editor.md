# アーキテクチャ設計書: 教育理論エディター

**ID**: DESIGN-002
**Feature**: Education Theory Editor
**Version**: 1.1
**Created**: 2025-12-27
**Updated**: 2025-12-27
**Status**: Implemented
**Related Requirements**: REQ-002 v1.1

---

## 1. C4モデル

### 1.1 Level 1: System Context Diagram

```
                         ┌─────────────────────────────────────────┐
                         │              ユーザー                    │
                         │         (教育コンテンツ管理者)           │
                         └─────────────────┬───────────────────────┘
                                           │
                                           │ HTTP (localhost:8080)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        TENJIN 教育理論エディター                              │
│                                                                              │
│   教育理論データベース（theories.json）を管理するWebベースエディター          │
│   CRUD操作、検索、バージョン管理機能を提供                                    │
│                                                                              │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │theories.json │ │ LocalStorage │ │   ブラウザ   │
           │  (データ)    │ │  (履歴)      │ │Download API │
           └──────────────┘ └──────────────┘ └──────────────┘
```

### 1.2 Level 2: Container Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TENJIN 教育理論エディター                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Presentation Layer                              │  │
│  │                          (index.html)                                  │  │
│  │                                                                        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐    │  │
│  │  │     Header      │  │    Sidebar      │  │    Editor Panel     │    │  │
│  │  │                 │  │                 │  │                     │    │  │
│  │  │ - タイトル       │  │ - 検索ボックス   │  │ - フォーム          │    │  │
│  │  │ - 履歴ボタン     │  │ - カテゴリ選択   │  │ - 保存/削除ボタン   │    │  │
│  │  │ - インポート     │  │ - 理論リスト     │  │ - フィールド一覧    │    │  │
│  │  │ - エクスポート   │  │ - 新規追加      │  │                     │    │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘    │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                        Modal Layer                               │  │  │
│  │  │  削除確認 │ バージョン履歴 │ バージョン保存 │ 差分表示           │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                        Status Bar                                │  │  │
│  │  │              メッセージ表示 │ 未保存インジケータ                  │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                       │                                      │
│                                       ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Style Layer (styles.css)                        │  │
│  │                                                                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │   Layout    │  │ Components  │  │   Modals    │  │   States    │   │  │
│  │  │             │  │             │  │             │  │             │   │  │
│  │  │ - Grid      │  │ - Buttons   │  │ - Overlay   │  │ - Active    │   │  │
│  │  │ - Flexbox   │  │ - Inputs    │  │ - Content   │  │ - Error     │   │  │
│  │  │ - Sidebar   │  │ - Cards     │  │ - Actions   │  │ - Modified  │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                       │                                      │
│                                       ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Application Layer (app.js)                        │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                      State Management                            │  │  │
│  │  │  state = { theories, metadata, currentTheoryId, isModified,     │  │  │
│  │  │            searchQuery, categoryFilter, versions }               │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │    CRUD     │  │   Search    │  │   Import/   │  │  Version    │   │  │
│  │  │  Services   │  │   Service   │  │   Export    │  │  Manager    │   │  │
│  │  │             │  │             │  │             │  │             │   │  │
│  │  │ - handleAdd │  │ - search    │  │ - import    │  │ - save      │   │  │
│  │  │ - handleSave│  │ - filter    │  │ - export    │  │ - restore   │   │  │
│  │  │ - delete    │  │ - render    │  │ - validate  │  │ - diff      │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                       UI Services                                │  │  │
│  │  │  renderTheoryList │ populateForm │ setStatus │ showModal        │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
         │                                        │
         ▼                                        ▼
  ┌──────────────────┐                    ┌──────────────────┐
  │   theories.json   │                    │   LocalStorage    │
  │                   │                    │                   │
  │ - metadata        │                    │ - versions[]      │
  │ - theories[]      │                    │ - max 50 entries  │
  └──────────────────┘                    └──────────────────┘
```

### 1.3 Level 3: Component Diagram - Application Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Application Layer (app.js)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Constants & Config                           │    │
│  │                                                                      │    │
│  │   VERSION_STORAGE_KEY = 'tenjin_theory_versions'                     │    │
│  │   MAX_VERSIONS = 50                                                  │    │
│  │   categoryNames = { ... }  // カテゴリ名マッピング                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           State Object                               │    │
│  │                                                                      │    │
│  │   state = {                                                          │    │
│  │     theories: Theory[],      // 理論データ配列                        │    │
│  │     metadata: Metadata,      // メタデータ                            │    │
│  │     currentTheoryId: string, // 選択中の理論ID                        │    │
│  │     isModified: boolean,     // 未保存フラグ                          │    │
│  │     searchQuery: string,     // 検索文字列                            │    │
│  │     categoryFilter: string,  // カテゴリフィルタ                      │    │
│  │     versions: Version[]      // バージョン履歴                        │    │
│  │   }                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌───────────────────────────────────┐  ┌───────────────────────────────┐  │
│  │        CRUD Module                │  │       Search Module            │  │
│  │                                   │  │                                │  │
│  │  handleAdd()                      │  │  handleSearch(event)           │  │
│  │  └─ 新規理論作成                   │  │  └─ 検索クエリ処理              │  │
│  │  └─ 自動ID生成                    │  │                                │  │
│  │                                   │  │  handleFilter(event)           │  │
│  │  handleSave(event)                │  │  └─ カテゴリフィルタ処理        │  │
│  │  └─ バリデーション                 │  │                                │  │
│  │  └─ 配列フィールド変換             │  │  filterTheories()              │  │
│  │  └─ 状態更新                      │  │  └─ 複合条件フィルタリング       │  │
│  │  └─ バージョン自動保存             │  │  └─ 名前・説明・理論家検索       │  │
│  │                                   │  │                                │  │
│  │  handleDeleteClick()              │  │  updateCategoryOptions()       │  │
│  │  └─ 削除確認モーダル表示           │  │  └─ カテゴリ動的取得            │  │
│  │                                   │  │                                │  │
│  │  handleConfirmDelete()            │  └───────────────────────────────┘  │
│  │  └─ バージョン自動保存             │                                     │
│  │  └─ 状態から削除                  │  ┌───────────────────────────────┐  │
│  │  └─ 次の理論選択                  │  │      Import/Export Module     │  │
│  └───────────────────────────────────┘  │                                │  │
│                                          │  handleImport(event)           │  │
│  ┌───────────────────────────────────┐  │  └─ FileReader使用             │  │
│  │       Version Module              │  │  └─ JSON検証                   │  │
│  │                                   │  │  └─ theories配列確認           │  │
│  │  loadVersionsFromStorage()        │  │  └─ 自動バックアップ            │  │
│  │  └─ LocalStorage読み込み          │  │                                │  │
│  │                                   │  │  handleExport()                │  │
│  │  saveVersionsToStorage()          │  │  └─ Blob生成                   │  │
│  │  └─ LocalStorage保存              │  │  └─ ダウンロードリンク作成       │  │
│  │  └─ 容量管理                      │  │  └─ 日付付きファイル名          │  │
│  │                                   │  │                                │  │
│  │  saveVersion(description)         │  └───────────────────────────────┘  │
│  │  └─ スナップショット作成           │                                     │
│  │  └─ MAX_VERSIONS制限              │  ┌───────────────────────────────┐  │
│  │                                   │  │        UI Module              │  │
│  │  restoreVersion(versionId)        │  │                                │  │
│  │  └─ 現状バックアップ              │  │  renderTheoryList()            │  │
│  │  └─ データ復元                    │  │  └─ サイドバー描画              │  │
│  │  └─ UI更新                        │  │  └─ 統計更新                   │  │
│  │                                   │  │                                │  │
│  │  computeDiff(oldData, newData)    │  │  populateForm(theory)          │  │
│  │  └─ 追加/削除/変更検出             │  │  └─ エディタフォーム描画        │  │
│  │                                   │  │                                │  │
│  │  renderDiff(diffData)             │  │  setStatus(message, type)      │  │
│  │  └─ 差分HTML生成                  │  │  └─ ステータスバー更新          │  │
│  │                                   │  │  └─ 自動クリア (3秒)           │  │
│  │  deleteVersion(versionId)         │  │                                │  │
│  │  handleClearHistory()             │  │  openModal(modalId)            │  │
│  └───────────────────────────────────┘  │  closeModal(modalId)           │  │
│                                          └───────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Event Listeners                               │    │
│  │                                                                      │    │
│  │   DOMContentLoaded → initializeEventListeners() → loadData()         │    │
│  │                                                                      │    │
│  │   Input Events:                                                      │    │
│  │   - searchInput.input → handleSearch                                 │    │
│  │   - categoryFilter.change → handleFilter                             │    │
│  │   - editorForm.submit → handleSave                                   │    │
│  │                                                                      │    │
│  │   Click Events:                                                      │    │
│  │   - btnAdd.click → handleAdd                                         │    │
│  │   - btnDelete.click → handleDeleteClick                              │    │
│  │   - btnImport.click → fileInput.click                                │    │
│  │   - btnExport.click → handleExport                                   │    │
│  │   - btnHistory.click → openHistoryModal                              │    │
│  │                                                                      │    │
│  │   Modal Events:                                                      │    │
│  │   - modal-overlay.click → closeModal                                 │    │
│  │   - btnConfirmDelete.click → handleConfirmDelete                     │    │
│  │   - btnConfirmSaveVersion.click → handleConfirmSaveVersion           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. トレーサビリティマトリクス（Article V準拠）

### 2.1 要件 ↔ 設計 対応表

| 要件ID | 要件名 | 設計コンポーネント | 実装ファイル |
|--------|--------|-------------------|-------------|
| FR-CRUD-001 | 理論一覧表示 | UI Module > renderTheoryList | app.js |
| FR-CRUD-002 | 理論詳細表示 | UI Module > populateForm | app.js |
| FR-CRUD-003 | 理論追加 | CRUD Module > handleAdd | app.js |
| FR-CRUD-004 | 理論保存 | CRUD Module > handleSave | app.js |
| FR-CRUD-005 | 理論削除 | CRUD Module > handleConfirmDelete | app.js |
| FR-SEARCH-001 | テキスト検索 | Search Module > handleSearch | app.js |
| FR-SEARCH-002 | カテゴリフィルタ | Search Module > handleFilter | app.js |
| FR-SEARCH-003 | 複合フィルタ | Search Module > filterTheories | app.js |
| FR-IO-001 | JSONエクスポート | Import/Export Module > handleExport | app.js |
| FR-IO-002 | JSONインポート | Import/Export Module > handleImport | app.js |
| FR-VERSION-001 | 自動バージョン保存 | Version Module > saveVersion | app.js |
| FR-VERSION-002 | バージョン履歴表示 | Version Module > openHistoryModal | app.js |
| FR-VERSION-003 | バージョン復元 | Version Module > restoreVersion | app.js |
| FR-VERSION-004 | 差分表示 | Version Module > computeDiff, renderDiff | app.js |
| FR-VERSION-005 | バージョン削除 | Version Module > deleteVersion | app.js |
| FR-ERROR-001 | JSONインポートエラー | Error Handler > validateImportData | app.js |
| FR-ERROR-002 | バリデーションエラー | Error Handler > validateTheory | app.js |
| FR-ERROR-003 | ファイル読み込みエラー | Error Handler > handleLoadError | app.js |
| NFR-USABILITY-001 | 直感的なUI | Presentation Layer | index.html, styles.css |
| NFR-USABILITY-002 | フィードバック表示 | UI Module > setStatus | app.js |
| NFR-ACCESSIBILITY-001 | キーボード操作 | Event Listeners > keyboard events | app.js |
| NFR-ACCESSIBILITY-002 | フォーム操作性 | Presentation Layer > form-group | index.html, styles.css |
| NFR-SECURITY-001 | 入力サニタイズ | Security > escapeHtml | app.js |
| NFR-SECURITY-002 | データ検証 | Security > validateImportData | app.js |

### 2.2 設計 ↔ テスト 対応表

| 設計コンポーネント | テストID | テスト種別 |
|-------------------|---------|----------|
| CRUD Module | AT-001〜AT-005 | 機能テスト |
| Search Module | AT-006〜AT-007 | 機能テスト |
| Import/Export Module | AT-008〜AT-009 | 機能テスト |
| Version Module | AT-010〜AT-012 | 機能テスト |
| Error Handler | AT-013〜AT-014 | 機能テスト |
| Accessibility | AT-015 | 機能テスト |
| validation.js | UT-VAL-* | ユニットテスト |
| diff.js | UT-DIFF-* | ユニットテスト |
| storage.js | UT-STOR-* | ユニットテスト |

---

## 3. アーキテクチャ決定記録（ADR）

### ADR-002-001: クライアントサイドオンリーアーキテクチャ

| 項目 | 内容 |
|------|------|
| **決定** | サーバーサイド処理を行わず、全てブラウザ内で完結するアーキテクチャを採用 |
| **状況** | 教育理論データの編集ツールを迅速に提供する必要がある |
| **選択肢** | 1. Webサーバー + DB構成 <br> 2. Node.js + Express <br> 3. クライアントサイドオンリー |
| **決定理由** | - 開発速度を最優先 <br> - 単一ユーザー利用を想定 <br> - 依存関係を最小化 <br> - オフライン動作可能 |
| **影響** | - データ永続化はエクスポート/インポートで対応 <br> - 同時編集は非対応 <br> - 大規模データには不向き |

### ADR-002-002: Vanilla JavaScript採用

| 項目 | 内容 |
|------|------|
| **決定** | React/Vue等のフレームワークを使用せず、Vanilla JavaScriptで実装 |
| **状況** | 軽量で高速なエディターを短期間で開発する必要がある |
| **選択肢** | 1. React + TypeScript <br> 2. Vue.js <br> 3. Vanilla JavaScript |
| **決定理由** | - ビルドプロセス不要 <br> - 学習コストなし <br> - ファイル数最小化 <br> - 高速な初期表示 |
| **影響** | - 大規模化時にコード管理が複雑化する可能性 <br> - 型安全性なし |

### ADR-002-003: LocalStorage バージョン管理

| 項目 | 内容 |
|------|------|
| **決定** | バージョン履歴をブラウザのLocalStorageに保存 |
| **状況** | ユーザーの編集履歴を保持し、誤操作からの復旧を可能にする |
| **選択肢** | 1. IndexedDB <br> 2. LocalStorage <br> 3. サーバーサイドDB |
| **決定理由** | - API がシンプル <br> - 同期的アクセス可能 <br> - 十分な容量（約5MB） <br> - ブラウザ間で標準化 |
| **影響** | - 50バージョンの上限を設定 <br> - ブラウザ変更時にデータ消失 <br> - プライベートモードでは永続化されない場合あり |

### ADR-002-004: 単一ステートオブジェクトパターン

| 項目 | 内容 |
|------|------|
| **決定** | アプリケーション状態を単一の`state`オブジェクトで管理 |
| **状況** | UIとデータの同期を簡潔に保つ必要がある |
| **選択肢** | 1. グローバル変数分散 <br> 2. 単一ステートオブジェクト <br> 3. 状態管理ライブラリ（Redux等） |
| **決定理由** | - 状態の把握が容易 <br> - デバッグしやすい <br> - 外部ライブラリ不要 |
| **影響** | - 状態変更時は手動でUI更新が必要 |

---

## 4. データフロー

### 4.1 理論編集フロー

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   ユーザー   │───▶│  UI Event   │───▶│  Handler    │───▶│   State     │
│   入力      │    │  (click等)  │    │  Function   │    │   Update    │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
                   ┌─────────────┐    ┌─────────────┐           │
                   │   UI        │◀───│  Render     │◀──────────┘
                   │  更新       │    │  Functions  │
                   └─────────────┘    └─────────────┘
```

### 4.2 バージョン保存フロー

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   保存/     │───▶│ saveVersion │───▶│  Snapshot   │───▶│LocalStorage │
│   削除操作  │    │  (auto)     │    │   作成      │    │    保存     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │  MAX_VERSIONS│
                                      │  チェック    │
                                      │  (50件超削除)│
                                      └─────────────┘
```

### 4.3 インポート/エクスポートフロー

```
インポート:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  File       │───▶│ FileReader  │───▶│JSON.parse   │───▶│  Validate   │
│  Select     │    │  readAsText │    │             │    │  Structure  │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
                   ┌─────────────┐    ┌─────────────┐           │ (OK)
                   │   UI        │◀───│ Auto Backup │◀──────────┘
                   │  更新       │    │ + Update    │
                   └─────────────┘    └─────────────┘


エクスポート:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Export     │───▶│ JSON.       │───▶│   Blob      │───▶│  Download   │
│  Click      │    │ stringify   │    │   生成      │    │   Link      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 5. コンポーネント詳細

### 5.1 State Management

```javascript
// State構造
const state = {
    theories: [],           // Theory[] - 理論データ配列
    metadata: null,         // Metadata - ファイルメタデータ
    currentTheoryId: null,  // string | null - 選択中の理論ID
    isModified: false,      // boolean - 未保存変更フラグ
    searchQuery: '',        // string - 検索クエリ
    categoryFilter: '',     // string - カテゴリフィルタ
    versions: []            // Version[] - バージョン履歴
};
```

### 5.2 Theory Entity

```typescript
// 理論データ型（TypeScript表記）
interface Theory {
    id: string;                    // "theory-001" 形式
    name: string;                  // 英語名
    name_ja?: string;              // 日本語名
    category: string;              // カテゴリ識別子
    priority: 'high' | 'medium' | 'low';
    theorists: string[];           // 理論家リスト
    description: string;           // 英語説明
    description_ja?: string;       // 日本語説明
    key_principles: string[];      // 主要原則
    applications: string[];        // 応用例
    strengths: string[];           // 強み
    limitations: string[];         // 限界
}
```

### 5.3 Version Entity

```typescript
// バージョンデータ型
interface Version {
    id: string;           // "v-{timestamp}" 形式
    timestamp: number;    // Unix timestamp
    description: string;  // バージョン説明
    data: {
        metadata: Metadata;
        theories: Theory[];
    };
}
```

---

## 6. UI コンポーネント構成

### 6.1 レイアウト構造

```html
<body>
  <!-- Header -->
  <header class="header">
    <h1>TENJIN 教育理論エディター</h1>
    <nav class="header-actions">
      <button id="btn-history">📜 履歴</button>
      <button id="btn-import">📥 インポート</button>
      <button id="btn-export">📤 エクスポート</button>
    </nav>
  </header>

  <!-- Main Content -->
  <main class="main-content">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="search-box">...</div>
      <div class="category-filter">...</div>
      <div class="stats">...</div>
      <ul id="theory-list">...</ul>
      <button id="btn-add">＋ 新規追加</button>
    </aside>

    <!-- Editor Panel -->
    <section class="editor-panel">
      <form id="editor-form">
        <!-- 基本情報 -->
        <!-- 説明 -->
        <!-- 詳細情報 -->
        <!-- アクションボタン -->
      </form>
    </section>
  </main>

  <!-- Status Bar -->
  <footer class="status-bar">...</footer>

  <!-- Modals -->
  <div id="modal-delete" class="modal">...</div>
  <div id="modal-history" class="modal">...</div>
  <div id="modal-save-version" class="modal">...</div>
  <div id="modal-diff" class="modal">...</div>
</body>
```

### 6.2 CSS設計（BEM風）

```css
/* Layout */
.header { }
.main-content { display: grid; grid-template-columns: 300px 1fr; }
.sidebar { }
.editor-panel { }
.status-bar { }

/* Components */
.theory-item { }
.theory-item--active { }
.form-group { }
.form-group__label { }
.form-group__input { }
.form-group__input--error { }

/* Modals */
.modal { }
.modal--active { }
.modal__overlay { }
.modal__content { }
.modal__header { }
.modal__body { }
.modal__footer { }

/* States */
.is-modified { }
.is-loading { }
.is-error { }
```

---

## 7. エラーハンドリング設計

### 7.1 エラー種別と処理

| エラー種別 | 発生箇所 | 処理方法 | ユーザーへの通知 |
|-----------|---------|---------|----------------|
| JSON解析エラー | handleImport | catch(SyntaxError) | "JSONの解析に失敗しました" |
| 構造検証エラー | validateImportData | 検証関数でfalse | "有効なtheoriesデータが見つかりません" |
| 必須フィールド未入力 | handleSave | validateTheory() | "[フィールド名]は必須です" |
| ファイル読み込みエラー | loadData | fetch.catch() | "データの読み込みに失敗しました" |
| LocalStorage容量超過 | saveVersionsToStorage | try-catch | "履歴の保存に失敗しました" |

### 7.2 エラー処理フロー

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   操作実行   │───▶│  try-catch  │───▶│  エラー検出  │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                   ┌─────────────┐           │ エラー発生
                   │  setStatus  │◀──────────┘
                   │ (type=error)│
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │ 3秒後自動    │
                   │ クリア       │
                   └─────────────┘
```

### 7.3 バリデーション関数設計

```javascript
// 理論データ検証
function validateTheory(theory) {
    const errors = [];
    
    if (!theory.id) {
        errors.push({ field: 'id', message: 'IDは必須です' });
    }
    if (!theory.name && !theory.name_ja) {
        errors.push({ field: 'name', message: '名前は必須です' });
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

// インポートデータ検証
function validateImportData(data) {
    if (!data || typeof data !== 'object') return false;
    if (!Array.isArray(data.theories)) return false;
    if (data.theories.length === 0) return false;
    
    // 各理論の最低限の検証
    return data.theories.every(t => 
        t.id && (t.name || t.name_ja)
    );
}
```

---

## 8. アクセシビリティ設計

### 8.1 キーボードナビゲーション

| キー | コンテキスト | アクション |
|------|------------|----------|
| Tab | 全体 | フォーカス順序に従って移動 |
| Shift+Tab | 全体 | 逆方向にフォーカス移動 |
| Enter | ボタン | ボタンをクリック |
| Enter | 理論リスト項目 | 理論を選択 |
| Escape | モーダル | モーダルを閉じる |
| Ctrl+S | エディタフォーム | 保存（フォーム送信） |

### 8.2 フォーカス順序

```
1. ヘッダーボタン（履歴 → インポート → エクスポート）
   ↓
2. サイドバー（検索 → カテゴリ → 理論リスト → 新規追加）
   ↓
3. エディタ（ID → 名前 → 名前(日本語) → ... → 保存 → 削除）
```

### 8.3 ARIA属性設計

```html
<!-- 検索フィールド -->
<input type="text" 
       id="search-input" 
       aria-label="理論を検索"
       placeholder="検索...">

<!-- 理論リスト -->
<ul id="theory-list" role="listbox" aria-label="理論一覧">
    <li role="option" 
        aria-selected="true" 
        tabindex="0">理論名</li>
</ul>

<!-- モーダル -->
<div id="modal-delete" 
     role="dialog" 
     aria-modal="true" 
     aria-labelledby="modal-delete-title">
    <h2 id="modal-delete-title">削除確認</h2>
</div>

<!-- ステータスメッセージ -->
<div id="status-message" 
     role="status" 
     aria-live="polite"></div>
```

### 8.4 フォーカス可視化

```css
/* フォーカスリング */
:focus {
    outline: 2px solid #4a90d9;
    outline-offset: 2px;
}

/* フォーカス可視化（キーボード操作時のみ） */
:focus:not(:focus-visible) {
    outline: none;
}

:focus-visible {
    outline: 2px solid #4a90d9;
    outline-offset: 2px;
}
```

---

## 9. 将来拡張設計（v2.0）

### 9.1 ライブラリ化構想（Article I準拠）

```
lib/theory-editor-core/
├── package.json
├── src/
│   ├── index.js           # Public API
│   ├── state.js           # State management
│   ├── validation.js      # Data validation
│   ├── diff.js            # Diff computation
│   └── storage.js         # Storage abstraction
└── tests/
    └── *.test.js
```

### 9.2 CLI構想（Article II準拠）

```bash
# 将来のCLI使用例
theory-editor list --category learning
theory-editor search "constructivism"
theory-editor show theory-001 --json
theory-editor export ./backup.json
theory-editor validate ./theories.json
```

### 9.3 拡張ポイント

| 拡張ポイント | 説明 |
|-------------|------|
| Storage Adapter | LocalStorage以外（IndexedDB, Remote API）への切り替え |
| Export Format | JSON以外（CSV, YAML）のサポート |
| Validation Rules | カスタムバリデーションルールの追加 |
| Theme | ダーク/ライトテーマ切り替え |

---

## 10. セキュリティ考慮

### 10.1 XSS対策

```javascript
// textContentを使用（innerHTML禁止）
element.textContent = userInput;

// 動的HTMLが必要な場合はエスケープ
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

### 10.2 データ検証

```javascript
// インポート時の構造検証
function validateImportData(data) {
    if (!data || typeof data !== 'object') return false;
    if (!Array.isArray(data.theories)) return false;
    if (data.theories.length === 0) return false;
    return data.theories.every(t => t.id && (t.name || t.name_ja));
}
```

---

## 11. テスト設計

### 11.1 ユニットテスト詳細

#### validation.js テストケース

| テストID | テストケース | 入力 | 期待結果 |
|---------|------------|------|----------|
| UT-VAL-001 | 有効な理論データ | 全必須フィールドあり | isValid: true |
| UT-VAL-002 | ID欠落 | id: null | errors: [{field: 'id'}] |
| UT-VAL-003 | 名前欠落（両方） | name: null, name_ja: null | errors: [{field: 'name'}] |
| UT-VAL-004 | 名前あり（英語のみ） | name: 'Test', name_ja: null | isValid: true |
| UT-VAL-005 | 名前あり（日本語のみ） | name: null, name_ja: 'テスト' | isValid: true |

#### diff.js テストケース

| テストID | テストケース | 入力 | 期待結果 |
|---------|------------|------|----------|
| UT-DIFF-001 | 追加検出 | old: 2件, new: 3件 | added: 1件 |
| UT-DIFF-002 | 削除検出 | old: 3件, new: 2件 | removed: 1件 |
| UT-DIFF-003 | 変更検出 | 同ID、異なるdescription | modified: 1件 |
| UT-DIFF-004 | 変更なし | 同一データ | added: 0, removed: 0, modified: 0 |
| UT-DIFF-005 | 空データ比較 | old: [], new: [] | 空の結果 |

#### storage.js テストケース

| テストID | テストケース | 入力 | 期待結果 |
|---------|------------|------|----------|
| UT-STOR-001 | 保存と読み込み | Version[] | 同一データ取得 |
| UT-STOR-002 | 上限超過時の削除 | 51件保存 | 50件に削減（古いものから削除） |
| UT-STOR-003 | 空の読み込み | LocalStorage空 | [] 返却 |
| UT-STOR-004 | 不正データ読み込み | 不正JSON | [] 返却（エラーなし） |

### 11.2 E2Eテストシナリオ詳細

| ID | シナリオ | 前提条件 | 手順 | 検証内容 |
|----|---------|---------|------|----------|
| E2E-001 | 新規作成→編集→保存 | エディター起動済み | 1. 「＋新規追加」クリック<br>2. フォーム入力<br>3. 「保存」クリック | データ永続化、バージョン作成、リスト更新 |
| E2E-002 | 検索→選択→削除 | 理論データあり | 1. 検索ボックス入力<br>2. 結果から選択<br>3. 「削除」→確認 | フィルタ動作、削除確認モーダル、リスト更新 |
| E2E-003 | インポート→エクスポート | 外部JSONあり | 1. インポート実行<br>2. データ確認<br>3. エクスポート実行 | データ整合性、ファイル名形式 |
| E2E-004 | バージョン復元 | バージョン履歴あり | 1. 「履歴」クリック<br>2. 「差分」確認<br>3. 「復元」クリック | 差分表示、復元動作、新バージョン作成 |
| E2E-005 | エラー回復 | - | 1. 不正JSON読み込み<br>2. エラー確認<br>3. 正常操作継続 | エラーメッセージ表示、データ保護 |

---

## 12. 関連ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [REQ-002-theory-editor.md](REQ-002-theory-editor.md) | 機能要件仕様書 |
| [DESIGN-001-architecture.md](DESIGN-001-architecture.md) | GraphRAG MCPサーバー設計 |

---

## 13. 改訂履歴

| バージョン | 日付 | 変更内容 | 著者 |
|-----------|------|---------|------|
| 1.0 | 2025-12-27 | 初版作成 | GitHub Copilot |
| 1.1 | 2025-12-27 | トレーサビリティマトリクス、エラーハンドリング設計、アクセシビリティ設計、テスト詳細を追加 | GitHub Copilot |
