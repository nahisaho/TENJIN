# タスク分解書: 教育理論エディター

**ID**: TASKS-002
**Feature**: Education Theory Editor
**Version**: 1.0
**Created**: 2025-12-27
**Status**: Ready for Implementation
**Related Documents**: REQ-002 v1.1, DESIGN-002 v1.1

---

## 1. タスク概要

### 1.1 スコープ

教育理論エディターのリファクタリングおよび機能強化。既存実装（app.js 848行）を設計書に基づいて整理し、テスト可能なコードに改善する。

### 1.2 前提条件

- [x] REQ-002 v1.1 承認済み
- [x] DESIGN-002 v1.1 承認済み
- [x] 既存実装（tools/theory-editor/）存在

### 1.3 完了基準

- 全15件の受入テスト（AT-001〜AT-015）合格
- エラーハンドリング実装完了
- アクセシビリティ要件充足
- コードレビュー完了

---

## 2. タスク一覧

### Phase 1: テスト基盤構築（Article III準拠）

| タスクID | タスク名 | 優先度 | 見積 | 依存 | 要件ID |
|---------|---------|-------|------|------|--------|
| TASK-001 | テストファイル構造作成 | HIGH | 0.5h | - | NFR-TESTABILITY |
| TASK-002 | validation.js 抽出とユニットテスト | HIGH | 1h | TASK-001 | FR-ERROR-002 |
| TASK-003 | diff.js 抽出とユニットテスト | HIGH | 1h | TASK-001 | FR-VERSION-004 |
| TASK-004 | storage.js 抽出とユニットテスト | HIGH | 1h | TASK-001 | FR-VERSION-001 |

### Phase 2: コアモジュール実装

| タスクID | タスク名 | 優先度 | 見積 | 依存 | 要件ID |
|---------|---------|-------|------|------|--------|
| TASK-005 | State管理の明確化 | HIGH | 0.5h | TASK-002,003,004 | DESIGN ADR-004 |
| TASK-006 | CRUD Module リファクタリング | HIGH | 1h | TASK-005 | FR-CRUD-001〜005 |
| TASK-007 | Search Module リファクタリング | MEDIUM | 0.5h | TASK-005 | FR-SEARCH-001〜003 |
| TASK-008 | Version Module リファクタリング | MEDIUM | 1h | TASK-004 | FR-VERSION-001〜005 |

### Phase 3: エラーハンドリング実装

| タスクID | タスク名 | 優先度 | 見積 | 依存 | 要件ID |
|---------|---------|-------|------|------|--------|
| TASK-009 | エラーハンドラー実装 | HIGH | 1h | TASK-002 | FR-ERROR-001〜003 |
| TASK-010 | バリデーションUI連携 | HIGH | 0.5h | TASK-009 | FR-ERROR-002 |
| TASK-011 | ステータス表示強化 | MEDIUM | 0.5h | TASK-009 | NFR-USABILITY-002 |

### Phase 4: アクセシビリティ実装

| タスクID | タスク名 | 優先度 | 見積 | 依存 | 要件ID |
|---------|---------|-------|------|------|--------|
| TASK-012 | ARIA属性追加 | MEDIUM | 0.5h | TASK-006 | NFR-ACCESSIBILITY-001,002 |
| TASK-013 | キーボードナビゲーション | MEDIUM | 0.5h | TASK-012 | NFR-ACCESSIBILITY-001 |
| TASK-014 | フォーカス管理 | MEDIUM | 0.5h | TASK-012 | NFR-ACCESSIBILITY-002 |

### Phase 5: 統合テスト（Article IX準拠）

| タスクID | タスク名 | 優先度 | 見積 | 依存 | 要件ID |
|---------|---------|-------|------|------|--------|
| TASK-015 | E2Eテストシナリオ実装 | HIGH | 2h | TASK-006〜014 | AT-001〜AT-015 |
| TASK-016 | 手動テスト実行・修正 | HIGH | 1h | TASK-015 | 全要件 |

---

## 3. タスク詳細

### TASK-001: テストファイル構造作成

**目的**: ユニットテスト・E2Eテスト用のファイル構造を準備

**成果物**:
```
tools/theory-editor/
├── tests/
│   ├── unit/
│   │   ├── validation.test.js
│   │   ├── diff.test.js
│   │   └── storage.test.js
│   └── e2e/
│       └── editor.test.js
├── js/
│   ├── validation.js
│   ├── diff.js
│   ├── storage.js
│   └── app.js (refactored)
└── test.html (テストランナー)
```

**完了条件**:
- [ ] ディレクトリ構造作成
- [ ] 基本テストランナー（test.html）作成
- [ ] 最小限のテストケース動作確認

---

### TASK-002: validation.js 抽出とユニットテスト

**目的**: バリデーションロジックを分離し、テスト可能にする

**抽出対象関数**:
```javascript
// validation.js
export function validateTheory(theory) { ... }
export function validateImportData(data) { ... }
export function validateRequiredFields(theory, fields) { ... }
```

**テストケース** (UT-VAL-001〜005):
| ID | ケース | 入力 | 期待値 |
|----|--------|------|--------|
| UT-VAL-001 | 有効データ | 全フィールドあり | isValid: true |
| UT-VAL-002 | ID欠落 | id: null | errors含む |
| UT-VAL-003 | 名前両方欠落 | name/name_ja: null | errors含む |
| UT-VAL-004 | 英語名のみ | name: 'Test' | isValid: true |
| UT-VAL-005 | 日本語名のみ | name_ja: 'テスト' | isValid: true |

**完了条件**:
- [ ] validation.js 作成
- [ ] 5件のテストケース実装
- [ ] 全テスト合格

---

### TASK-003: diff.js 抽出とユニットテスト

**目的**: 差分計算ロジックを分離し、テスト可能にする

**抽出対象関数**:
```javascript
// diff.js
export function computeDiff(oldData, newData) { ... }
export function formatDiffResult(diff) { ... }
```

**テストケース** (UT-DIFF-001〜005):
| ID | ケース | 入力 | 期待値 |
|----|--------|------|--------|
| UT-DIFF-001 | 追加検出 | old:2件→new:3件 | added: 1 |
| UT-DIFF-002 | 削除検出 | old:3件→new:2件 | removed: 1 |
| UT-DIFF-003 | 変更検出 | 同ID異データ | modified: 1 |
| UT-DIFF-004 | 変更なし | 同一データ | 全て0 |
| UT-DIFF-005 | 空データ | [], [] | 空の結果 |

**完了条件**:
- [ ] diff.js 作成
- [ ] 5件のテストケース実装
- [ ] 全テスト合格

---

### TASK-004: storage.js 抽出とユニットテスト

**目的**: LocalStorage操作を分離し、テスト可能にする

**抽出対象関数**:
```javascript
// storage.js
export function loadVersionsFromStorage() { ... }
export function saveVersionsToStorage(versions) { ... }
export function enforceVersionLimit(versions, maxVersions) { ... }
```

**テストケース** (UT-STOR-001〜004):
| ID | ケース | 入力 | 期待値 |
|----|--------|------|--------|
| UT-STOR-001 | 保存と読み込み | Version[] | 同一データ |
| UT-STOR-002 | 上限超過 | 51件 | 50件に削減 |
| UT-STOR-003 | 空読み込み | 空Storage | [] |
| UT-STOR-004 | 不正データ | 壊れたJSON | [] |

**完了条件**:
- [ ] storage.js 作成
- [ ] 4件のテストケース実装
- [ ] 全テスト合格

---

### TASK-005: State管理の明確化

**目的**: 単一ステートオブジェクトパターンを明確に適用

**変更内容**:
```javascript
// app.js 冒頭に明確なState定義
const state = {
    theories: [],
    metadata: null,
    currentTheoryId: null,
    isModified: false,
    searchQuery: '',
    categoryFilter: '',
    versions: []
};

// State更新関数
function updateState(updates) {
    Object.assign(state, updates);
}
```

**完了条件**:
- [ ] State構造の明確化
- [ ] 既存コードからの移行
- [ ] 動作確認

---

### TASK-006: CRUD Module リファクタリング

**目的**: CRUD操作を設計書の構造に整理

**対象関数**:
- handleAdd()
- handleSave()
- handleDeleteClick()
- handleConfirmDelete()

**完了条件**:
- [ ] 関数コメント追加
- [ ] エラーハンドリング統一
- [ ] AT-001〜AT-005 手動テスト合格

---

### TASK-007: Search Module リファクタリング

**目的**: 検索機能を設計書の構造に整理

**対象関数**:
- handleSearch()
- handleFilter()
- filterTheories()

**完了条件**:
- [ ] 関数コメント追加
- [ ] AT-006〜AT-007 手動テスト合格

---

### TASK-008: Version Module リファクタリング

**目的**: バージョン管理機能を設計書の構造に整理

**対象関数**:
- saveVersion()
- restoreVersion()
- computeDiff()
- renderDiff()
- deleteVersion()

**完了条件**:
- [ ] storage.js への委譲
- [ ] diff.js への委譲
- [ ] AT-010〜AT-012 手動テスト合格

---

### TASK-009: エラーハンドラー実装

**目的**: 統一的なエラー処理を実装

**実装内容**:
```javascript
// error-handler.js または app.js内
function handleError(error, context) {
    const message = getErrorMessage(error, context);
    setStatus(message, 'error');
    console.error(`[${context}]`, error);
}

function getErrorMessage(error, context) {
    const messages = {
        'import-parse': 'JSONの解析に失敗しました',
        'import-validate': '有効なtheoriesデータが見つかりません',
        'save-validate': '必須フィールドが未入力です',
        'load-fetch': 'データの読み込みに失敗しました',
        'storage-quota': '履歴の保存に失敗しました'
    };
    return messages[context] || 'エラーが発生しました';
}
```

**完了条件**:
- [ ] エラーハンドラー実装
- [ ] 既存try-catchの統一
- [ ] AT-013〜AT-014 手動テスト合格

---

### TASK-010: バリデーションUI連携

**目的**: バリデーションエラーをUIに反映

**実装内容**:
```javascript
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    field.classList.add('form-group__input--error');
    // エラーメッセージ表示
}

function clearFieldErrors() {
    document.querySelectorAll('.form-group__input--error')
        .forEach(el => el.classList.remove('form-group__input--error'));
}
```

**完了条件**:
- [ ] フィールドエラー表示実装
- [ ] エラークリア実装
- [ ] 動作確認

---

### TASK-011: ステータス表示強化

**目的**: ユーザーフィードバックを改善

**実装内容**:
- 成功/エラー/警告の視覚的区別
- 3秒後自動クリア
- アニメーション追加

**完了条件**:
- [ ] CSS追加（status--success, status--error, status--warning）
- [ ] 自動クリア動作確認

---

### TASK-012: ARIA属性追加

**目的**: スクリーンリーダー対応

**実装内容** (index.html):
```html
<input aria-label="理論を検索">
<ul role="listbox" aria-label="理論一覧">
<div role="dialog" aria-modal="true">
<div role="status" aria-live="polite">
```

**完了条件**:
- [ ] 全ARIA属性追加
- [ ] スクリーンリーダーテスト（可能であれば）

---

### TASK-013: キーボードナビゲーション

**目的**: キーボードのみで全操作可能にする

**実装内容**:
```javascript
// Escapeでモーダルを閉じる
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeAllModals();
    }
});

// 理論リストでEnter選択
theoryList.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.target.click();
    }
});
```

**完了条件**:
- [ ] Escape/Enter対応
- [ ] Tab順序確認
- [ ] AT-015 手動テスト合格

---

### TASK-014: フォーカス管理

**目的**: フォーカス状態を視覚的に明確化

**実装内容** (styles.css):
```css
:focus-visible {
    outline: 2px solid #4a90d9;
    outline-offset: 2px;
}
```

**完了条件**:
- [ ] フォーカスリング実装
- [ ] モーダルフォーカストラップ（オプション）

---

### TASK-015: E2Eテストシナリオ実装

**目的**: 統合テストでシステム全体を検証

**テストシナリオ**:
| ID | シナリオ | 検証内容 |
|----|---------|----------|
| E2E-001 | 新規→編集→保存 | データ永続化、バージョン作成 |
| E2E-002 | 検索→選択→削除 | フィルタ、削除確認 |
| E2E-003 | インポート→エクスポート | データ整合性 |
| E2E-004 | バージョン復元 | 差分表示、復元動作 |
| E2E-005 | エラー回復 | エラー表示、データ保護 |

**完了条件**:
- [ ] テストスクリプト作成（手動チェックリスト）
- [ ] 全シナリオ実行・記録

---

### TASK-016: 手動テスト実行・修正

**目的**: 受入テスト（AT-001〜AT-015）を実行し、不具合を修正

**チェックリスト**:
- [ ] AT-001: 理論一覧表示
- [ ] AT-002: 理論詳細表示
- [ ] AT-003: 理論追加
- [ ] AT-004: 理論保存
- [ ] AT-005: 理論削除
- [ ] AT-006: テキスト検索
- [ ] AT-007: カテゴリフィルタ
- [ ] AT-008: JSONエクスポート
- [ ] AT-009: JSONインポート
- [ ] AT-010: バージョン履歴表示
- [ ] AT-011: バージョン復元
- [ ] AT-012: 差分表示
- [ ] AT-013: エラーメッセージ表示
- [ ] AT-014: 必須フィールドバリデーション
- [ ] AT-015: キーボード操作

**完了条件**:
- [ ] 全15件のATが合格
- [ ] 不具合0件

---

## 4. タイムライン

```
Phase 1 (3.5h): テスト基盤
├── TASK-001: 0.5h
├── TASK-002: 1h
├── TASK-003: 1h
└── TASK-004: 1h

Phase 2 (3h): コアモジュール
├── TASK-005: 0.5h
├── TASK-006: 1h
├── TASK-007: 0.5h
└── TASK-008: 1h

Phase 3 (2h): エラーハンドリング
├── TASK-009: 1h
├── TASK-010: 0.5h
└── TASK-011: 0.5h

Phase 4 (1.5h): アクセシビリティ
├── TASK-012: 0.5h
├── TASK-013: 0.5h
└── TASK-014: 0.5h

Phase 5 (3h): 統合テスト
├── TASK-015: 2h
└── TASK-016: 1h

合計: 約13時間
```

---

## 5. リスクと対策

| リスク | 影響度 | 対策 |
|--------|-------|------|
| 既存コードの複雑さ | 中 | 段階的リファクタリング、各Phase後に動作確認 |
| テスト環境の制約 | 低 | ブラウザコンソールでの手動テストで代替 |
| LocalStorage制限 | 低 | 容量チェック機能を先行実装 |

---

## 6. 関連ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [REQ-002-theory-editor.md](REQ-002-theory-editor.md) | 機能要件仕様書 |
| [DESIGN-002-theory-editor.md](DESIGN-002-theory-editor.md) | アーキテクチャ設計書 |

---

## 7. 改訂履歴

| バージョン | 日付 | 変更内容 | 著者 |
|-----------|------|---------|------|
| 1.0 | 2025-12-27 | 初版作成 | GitHub Copilot |
