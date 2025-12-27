# Theory Editor API リファレンス

JavaScriptモジュールのAPIドキュメントです。

---

## 目次

1. [TheoryValidation](#theoryvalidation)
2. [TheoryDiff](#theorydiff)
3. [TheoryStorage](#theorystorage)
4. [ErrorHandler](#errorhandler)
5. [GraphRAGSync](#graphragsync)
6. [App State](#app-state)

---

## TheoryValidation

データバリデーションを担当するモジュール。

### `validateTheory(theory)`

理論データのバリデーションを実行します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| theory | Object | バリデーション対象の理論データ |

**戻り値:**
```javascript
{
  isValid: boolean,
  errors: Array<{ field: string, message: string }>
}
```

**使用例:**
```javascript
const result = TheoryValidation.validateTheory({
  id: 'theory-001',
  name: 'Constructivism',
  category: 'learning'
});

if (!result.isValid) {
  result.errors.forEach(err => {
    console.error(`${err.field}: ${err.message}`);
  });
}
```

**バリデーションルール:**
- `id`: 必須、`theory-` プレフィックス推奨
- `name` または `name_ja`: どちらか必須
- `category`: 必須
- `priority`: 1-5の整数（デフォルト: 3）

---

### `validateImportData(data)`

インポートデータの形式をバリデーションします。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| data | Object | インポートするJSONデータ |

**戻り値:**
```javascript
{
  isValid: boolean,
  errors: Array<{ field: string, message: string }>,
  warnings: Array<string>
}
```

**使用例:**
```javascript
const fileContent = JSON.parse(jsonString);
const result = TheoryValidation.validateImportData(fileContent);

if (result.isValid) {
  // インポート処理
} else {
  alert('Invalid import data');
}
```

---

### `validateRequiredFields(theory, fields)`

指定したフィールドの存在チェックを行います。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| theory | Object | チェック対象のオブジェクト |
| fields | Array\<string\> | 必須フィールド名の配列 |

**戻り値:**
```javascript
{
  isValid: boolean,
  missing: Array<string>  // 欠落しているフィールド名
}
```

---

## TheoryDiff

バージョン間の差分計算を担当するモジュール。

### `computeDiff(oldData, newData)`

2つのデータセット間の差分を計算します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| oldData | Array | 古いデータの配列 |
| newData | Array | 新しいデータの配列 |

**戻り値:**
```javascript
{
  added: Array<Object>,    // 追加されたアイテム
  removed: Array<Object>,  // 削除されたアイテム
  modified: Array<{
    id: string,
    changes: Array<{
      field: string,
      oldValue: any,
      newValue: any
    }>
  }>,
  unchanged: number        // 変更なしの件数
}
```

**使用例:**
```javascript
const diff = TheoryDiff.computeDiff(oldTheories, newTheories);

console.log(`追加: ${diff.added.length}件`);
console.log(`削除: ${diff.removed.length}件`);
console.log(`変更: ${diff.modified.length}件`);
```

---

### `formatDiffResult(diff)`

差分結果を人間が読みやすい形式に整形します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| diff | Object | `computeDiff()` の戻り値 |

**戻り値:**
```javascript
{
  summary: string,  // 概要テキスト
  details: string   // 詳細テキスト（HTML形式）
}
```

---

### `computeFieldDiff(oldObj, newObj)`

2つのオブジェクト間のフィールド単位の差分を計算します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| oldObj | Object | 古いオブジェクト |
| newObj | Object | 新しいオブジェクト |

**戻り値:**
```javascript
Array<{
  field: string,
  oldValue: any,
  newValue: any
}>
```

---

## TheoryStorage

LocalStorageを使用したバージョン管理を担当するモジュール。

### 定数

```javascript
TheoryStorage.VERSION_STORAGE_KEY  // 'theory-editor-versions'
TheoryStorage.MAX_VERSIONS         // 50
```

### `loadVersionsFromStorage()`

保存されているバージョン履歴を読み込みます。

**戻り値:**
```javascript
Array<{
  id: string,
  timestamp: string,      // ISO 8601形式
  description: string,    // バージョンの説明
  data: {
    metadata: Object,
    theories: Array
  }
}>
```

**使用例:**
```javascript
const versions = TheoryStorage.loadVersionsFromStorage();
console.log(`${versions.length}件のバージョンが保存されています`);
```

---

### `saveVersionsToStorage(versions)`

バージョン履歴をLocalStorageに保存します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| versions | Array | バージョン履歴の配列 |

**戻り値:** `void`

**注意:** 自動的に `MAX_VERSIONS` を超えた古いバージョンは削除されます。

---

### `enforceVersionLimit(versions, maxVersions)`

バージョン数の上限を適用します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| versions | Array | バージョン履歴の配列 |
| maxVersions | number | 最大バージョン数 |

**戻り値:** 制限後の配列（元の配列は変更されません）

---

### `getVersionById(versionId)`

指定IDのバージョンを取得します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| versionId | string | バージョンID |

**戻り値:** バージョンオブジェクト、または `null`

---

### `getTheoryHistory(theoryId)`

特定の理論の変更履歴を取得します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| theoryId | string | 理論ID |

**戻り値:**
```javascript
Array<{
  versionId: string,
  timestamp: string,
  description: string,
  theoryData: Object | null  // その時点の理論データ
}>
```

---

### `clearAllVersions()`

すべてのバージョン履歴を削除します。

**戻り値:** `void`

---

## ErrorHandler

統一的なエラーハンドリングを担当するモジュール。

### 定数

```javascript
ErrorHandler.ERROR_CONTEXTS = {
  IMPORT: 'import',
  EXPORT: 'export',
  SAVE: 'save',
  DELETE: 'delete',
  VALIDATION: 'validation',
  STORAGE: 'storage',
  SYNC: 'sync'
};
```

### `handleError(error, context)`

エラーを処理し、ユーザーフレンドリーなメッセージを生成します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| error | Error \| string | エラーオブジェクトまたはメッセージ |
| context | string | エラーのコンテキスト（ERROR_CONTEXTS参照） |

**戻り値:**
```javascript
{
  message: string,      // ユーザー向けメッセージ
  technical: string,    // 技術的な詳細
  recoverable: boolean  // 復旧可能かどうか
}
```

**使用例:**
```javascript
try {
  // 処理
} catch (error) {
  const result = ErrorHandler.handleError(error, ErrorHandler.ERROR_CONTEXTS.SAVE);
  setStatus(result.message, 'error');
  
  if (!result.recoverable) {
    // 重大なエラー処理
  }
}
```

---

### `logError(error, context)`

エラーをコンソールにログ出力します（開発時用）。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| error | Error | エラーオブジェクト |
| context | string | エラーのコンテキスト |

---

### `createValidationError(field, message)`

バリデーションエラーオブジェクトを生成します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| field | string | エラーが発生したフィールド名 |
| message | string | エラーメッセージ |

**戻り値:**
```javascript
{
  field: string,
  message: string,
  type: 'validation'
}
```

---

## GraphRAGSync

GraphRAG（Neo4j）との同期を担当するモジュール。

### 定数

```javascript
GraphRAGSync.SYNC_SERVER_URL  // 'http://localhost:8081'
```

### `triggerReindex()`

GraphRAGのインデックス再作成をトリガーします。

**戻り値:** Promise
```javascript
{
  success: boolean,
  message: string,
  output?: string  // 成功時の出力
}
```

**使用例:**
```javascript
const result = await GraphRAGSync.triggerReindex();

if (result.success) {
  console.log('同期完了:', result.message);
} else {
  console.error('同期失敗:', result.message);
}
```

---

### `getStatus()`

同期サーバーのステータスを取得します。

**戻り値:** Promise
```javascript
{
  synced: boolean,
  last_sync: string | null,  // ISO 8601形式
  message: string
}
```

---

### `exportToGraphRAG(theories)`

理論データをGraphRAGサーバーにエクスポートします。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| theories | Array | エクスポートする理論データ |

**戻り値:** Promise
```javascript
{
  success: boolean,
  message: string
}
```

---

## App State

メインアプリケーション（app.js）のステート管理。

### State オブジェクト

```javascript
const state = {
  theories: [],           // 理論データの配列
  metadata: null,         // メタデータ
  currentTheoryId: null,  // 選択中の理論ID
  searchQuery: '',        // 検索クエリ
  categoryFilter: 'all',  // カテゴリフィルタ
  isModified: false,      // 未保存の変更があるか
  versions: []            // バージョン履歴
};
```

### `updateState(updates)`

ステートを更新します（イミュータブル）。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| updates | Object | 更新するプロパティ |

**使用例:**
```javascript
updateState({
  currentTheoryId: 'theory-001',
  isModified: true
});
```

---

### UI関数

#### `setStatus(message, type)`

ステータスメッセージを表示します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| message | string | 表示するメッセージ |
| type | string | 'info' \| 'success' \| 'error' \| 'warning' |

#### `showFieldError(field, message)`

フォームフィールドにエラーを表示します。

**パラメータ:**
| 名前 | 型 | 説明 |
|------|-----|------|
| field | string | フィールド名（'name', 'category' など） |
| message | string | エラーメッセージ |

#### `clearFieldErrors()`

すべてのフィールドエラーをクリアします。

---

## イベント

### カスタムイベント

Theory Editorは以下のカスタムイベントを発火します：

| イベント名 | 発火タイミング | detail |
|-----------|---------------|--------|
| `theory:saved` | 理論保存後 | `{ theory, isNew }` |
| `theory:deleted` | 理論削除後 | `{ theoryId }` |
| `version:saved` | バージョン保存後 | `{ versionId }` |
| `sync:completed` | GraphRAG同期後 | `{ success, message }` |

**使用例:**
```javascript
document.addEventListener('theory:saved', (e) => {
  console.log('Saved:', e.detail.theory.name);
});
```

---

## エラーコード

| コード | 説明 |
|--------|------|
| `E001` | バリデーションエラー |
| `E002` | インポートエラー |
| `E003` | エクスポートエラー |
| `E004` | ストレージエラー |
| `E005` | 同期エラー |
| `E006` | ネットワークエラー |

---

## 型定義（TypeScript参考）

```typescript
interface Theory {
  id: string;
  name: string;
  name_ja?: string;
  category: string;
  priority: number;
  theorists: string[];
  description: string;
  description_ja?: string;
  key_principles: string[];
  applications: string[];
  strengths: string[];
  limitations: string[];
}

interface Version {
  id: string;
  timestamp: string;
  description: string;
  data: {
    metadata: Metadata;
    theories: Theory[];
  };
}

interface Metadata {
  version: string;
  total_theories: number;
  last_updated: string;
}

interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

interface ValidationError {
  field: string;
  message: string;
}

interface DiffResult {
  added: Theory[];
  removed: Theory[];
  modified: ModifiedItem[];
  unchanged: number;
}

interface ModifiedItem {
  id: string;
  changes: FieldChange[];
}

interface FieldChange {
  field: string;
  oldValue: any;
  newValue: any;
}
```

---

## 関連ドキュメント

- [README](../README.md) - 使い方ガイド
- [設計書](../../../storage/specs/DESIGN-002-theory-editor.md)
- [要件定義](../../../storage/specs/REQ-002-theory-editor.md)
