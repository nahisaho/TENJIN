/**
 * E2E Test Scenarios
 * TENJIN Theory Editor
 * 
 * Manual E2E test checklist for acceptance testing
 */

/**
 * E2E-001: 基本ワークフロー
 * 
 * 前提条件: 新しいブラウザセッション、LocalStorageクリア
 * 
 * 手順:
 * 1. エディタを開く
 * 2. サンプルデータをインポート
 * 3. 理論を1件選択
 * 4. 名前を編集
 * 5. 保存
 * 6. ページをリロード
 * 7. 編集が保持されていることを確認
 * 
 * 期待結果:
 * - 編集内容が保存される
 * - リロード後もデータが維持される
 * - ステータスメッセージが適切に表示される
 */
const E2E_001_BASIC_WORKFLOW = {
    id: 'E2E-001',
    name: '基本ワークフロー',
    steps: [
        { action: 'open', target: 'index.html', expected: 'エディタが表示される' },
        { action: 'click', target: '#btn-import', expected: 'ファイル選択ダイアログが開く' },
        { action: 'select', target: '#theory-list option:first-child', expected: '理論が選択される' },
        { action: 'edit', target: '#input-name', value: 'Modified Name', expected: '入力が反映される' },
        { action: 'click', target: '#editor-form button[type=submit]', expected: '保存成功メッセージ' },
        { action: 'reload', expected: 'データが維持される' }
    ]
};

/**
 * E2E-002: バリデーションエラー
 * 
 * 手順:
 * 1. 新規理論を追加
 * 2. ID欄を空のまま保存を試行
 * 3. エラーメッセージを確認
 * 4. IDを入力して再度保存
 * 
 * 期待結果:
 * - バリデーションエラーが表示される
 * - エラーフィールドがハイライトされる
 * - 修正後は正常に保存できる
 */
const E2E_002_VALIDATION = {
    id: 'E2E-002',
    name: 'バリデーションエラー',
    steps: [
        { action: 'click', target: '#btn-add-theory', expected: '新規フォームが表示される' },
        { action: 'clear', target: '#input-id', expected: 'ID欄が空になる' },
        { action: 'submit', expected: 'エラーメッセージが表示される' },
        { action: 'verify', target: '.field-error', expected: 'エラー表示が存在する' },
        { action: 'input', target: '#input-id', value: 'test-theory', expected: '入力が反映される' },
        { action: 'submit', expected: '保存成功' }
    ]
};

/**
 * E2E-003: 検索機能
 * 
 * 手順:
 * 1. データをインポート
 * 2. 検索ボックスにテキストを入力
 * 3. フィルタ結果を確認
 * 4. 検索をクリア
 * 
 * 期待結果:
 * - 検索結果がリアルタイムでフィルタされる
 * - 名前、説明、理論家がすべて検索対象
 * - クリアで全件表示に戻る
 */
const E2E_003_SEARCH = {
    id: 'E2E-003',
    name: '検索機能',
    steps: [
        { action: 'import', target: 'sample-data.json', expected: 'データがロードされる' },
        { action: 'input', target: '#search-input', value: 'constructivism', expected: 'フィルタされる' },
        { action: 'verify', target: '#theory-list', expected: '検索結果のみ表示' },
        { action: 'clear', target: '#search-input', expected: '全件表示に戻る' }
    ]
};

/**
 * E2E-004: バージョン管理
 * 
 * 手順:
 * 1. データを編集
 * 2. バージョンを保存
 * 3. さらに編集
 * 4. 履歴を開く
 * 5. 以前のバージョンを復元
 * 
 * 期待結果:
 * - バージョンが保存される
 * - 履歴一覧に表示される
 * - 復元が正常に動作する
 */
const E2E_004_VERSION = {
    id: 'E2E-004',
    name: 'バージョン管理',
    steps: [
        { action: 'edit', target: '#input-name', value: 'V1 Name', expected: '編集される' },
        { action: 'click', target: '#btn-save-version', expected: 'モーダルが開く' },
        { action: 'input', target: '#version-description', value: 'Version 1', expected: '説明入力' },
        { action: 'click', target: '#btn-confirm-save-version', expected: 'バージョン保存成功' },
        { action: 'edit', target: '#input-name', value: 'V2 Name', expected: '再編集' },
        { action: 'click', target: '#btn-history-theory', expected: '履歴モーダルが開く' },
        { action: 'click', target: '.btn-restore:first', expected: 'V1に復元される' }
    ]
};

/**
 * E2E-005: キーボード操作
 * 
 * 手順:
 * 1. Tab/Shift+Tabでフォーカス移動
 * 2. Enterで選択確定
 * 3. Escでモーダルクローズ
 * 4. Ctrl+Sで保存
 * 
 * 期待結果:
 * - キーボードのみで操作可能
 * - フォーカスが視覚的に表示される
 * - ショートカットが動作する
 */
const E2E_005_KEYBOARD = {
    id: 'E2E-005',
    name: 'キーボード操作',
    steps: [
        { action: 'keypress', key: 'Tab', expected: 'フォーカス移動' },
        { action: 'keypress', key: 'Enter', target: '#theory-list', expected: '理論選択' },
        { action: 'keypress', key: 'Ctrl+S', expected: '保存実行' },
        { action: 'keypress', key: 'Escape', target: 'modal', expected: 'モーダルクローズ' }
    ]
};

/**
 * E2E-006: アクセシビリティ
 * 
 * 手順:
 * 1. スクリーンリーダーでナビゲーション
 * 2. ランドマークの確認
 * 3. フォームラベルの読み上げ確認
 * 4. エラーメッセージのアナウンス確認
 * 
 * 期待結果:
 * - ランドマークが認識される
 * - フォーム要素に適切なラベル
 * - エラーが適切にアナウンスされる
 */
const E2E_006_ACCESSIBILITY = {
    id: 'E2E-006',
    name: 'アクセシビリティ',
    steps: [
        { action: 'verify', target: '[role=banner]', expected: 'ヘッダーランドマーク存在' },
        { action: 'verify', target: '[role=main]', expected: 'メインランドマーク存在' },
        { action: 'verify', target: '[role=navigation]', expected: 'ナビゲーション存在' },
        { action: 'verify', target: 'label[for]', expected: 'すべての入力にラベル' },
        { action: 'verify', target: '[aria-live]', expected: 'ライブリージョン存在' }
    ]
};

/**
 * E2E-007: エラーハンドリング
 * 
 * 手順:
 * 1. 不正なJSONファイルをインポート
 * 2. エラーメッセージを確認
 * 3. LocalStorageを容量上限近くまで使用
 * 4. 保存を試行
 * 
 * 期待結果:
 * - ユーザーフレンドリーなエラーメッセージ
 * - アプリがクラッシュしない
 * - 回復手順が提示される
 */
const E2E_007_ERROR_HANDLING = {
    id: 'E2E-007',
    name: 'エラーハンドリング',
    steps: [
        { action: 'import', target: 'invalid.json', expected: 'パースエラー表示' },
        { action: 'verify', target: '.status-error', expected: 'エラーステータス表示' },
        { action: 'simulate', target: 'storage-quota', expected: '容量エラー表示' }
    ]
};

// ============================================
// Acceptance Test Checklist (AT-001 to AT-015)
// ============================================

const ACCEPTANCE_TESTS = [
    {
        id: 'AT-001',
        name: 'インポート機能',
        criteria: 'JSONファイルを選択してインポートできる',
        steps: ['ファイル選択', 'データ読み込み', 'リスト表示'],
        passed: null
    },
    {
        id: 'AT-002',
        name: 'エクスポート機能',
        criteria: 'データをJSONファイルとしてダウンロードできる',
        steps: ['エクスポートボタン', 'ファイル保存', 'ファイル検証'],
        passed: null
    },
    {
        id: 'AT-003',
        name: '理論選択',
        criteria: 'リストから理論を選択してフォームに表示できる',
        steps: ['リスト項目クリック', 'フォーム表示', '値の確認'],
        passed: null
    },
    {
        id: 'AT-004',
        name: '理論編集',
        criteria: 'フォームで理論の各フィールドを編集できる',
        steps: ['各フィールド編集', '未保存マーク表示'],
        passed: null
    },
    {
        id: 'AT-005',
        name: '理論保存',
        criteria: '編集内容を保存できる',
        steps: ['保存ボタン', '成功メッセージ', 'データ反映'],
        passed: null
    },
    {
        id: 'AT-006',
        name: '理論追加',
        criteria: '新規理論を追加できる',
        steps: ['追加ボタン', '空フォーム', '保存', 'リスト追加'],
        passed: null
    },
    {
        id: 'AT-007',
        name: '理論削除',
        criteria: '理論を削除できる（確認ダイアログあり）',
        steps: ['削除ボタン', '確認ダイアログ', '削除実行', 'リスト更新'],
        passed: null
    },
    {
        id: 'AT-008',
        name: '検索フィルタ',
        criteria: '検索ボックスでリストをフィルタできる',
        steps: ['検索入力', 'リアルタイムフィルタ', 'クリア'],
        passed: null
    },
    {
        id: 'AT-009',
        name: 'カテゴリフィルタ',
        criteria: 'カテゴリでリストをフィルタできる',
        steps: ['カテゴリ選択', 'フィルタ適用', '全表示'],
        passed: null
    },
    {
        id: 'AT-010',
        name: 'バリデーション',
        criteria: '必須フィールドの検証が動作する',
        steps: ['空フィールド保存', 'エラー表示', '修正後保存'],
        passed: null
    },
    {
        id: 'AT-011',
        name: 'バージョン保存',
        criteria: 'データのスナップショットを保存できる',
        steps: ['保存ボタン', '説明入力', '保存確認'],
        passed: null
    },
    {
        id: 'AT-012',
        name: 'バージョン履歴',
        criteria: '保存したバージョンの一覧を表示できる',
        steps: ['履歴ボタン', 'モーダル表示', '一覧確認'],
        passed: null
    },
    {
        id: 'AT-013',
        name: 'バージョン復元',
        criteria: '過去のバージョンを復元できる',
        steps: ['履歴選択', '復元ボタン', 'データ確認'],
        passed: null
    },
    {
        id: 'AT-014',
        name: 'キーボード操作',
        criteria: 'キーボードのみで全操作が可能',
        steps: ['Tab移動', 'Enter選択', 'Escape閉じる', 'Ctrl+S保存'],
        passed: null
    },
    {
        id: 'AT-015',
        name: 'スクリーンリーダー対応',
        criteria: 'スクリーンリーダーで操作可能',
        steps: ['ランドマーク認識', 'フォームラベル', 'エラー読み上げ'],
        passed: null
    }
];

// Export for testing
if (typeof window !== 'undefined') {
    window.E2E_SCENARIOS = {
        E2E_001_BASIC_WORKFLOW,
        E2E_002_VALIDATION,
        E2E_003_SEARCH,
        E2E_004_VERSION,
        E2E_005_KEYBOARD,
        E2E_006_ACCESSIBILITY,
        E2E_007_ERROR_HANDLING
    };
    window.ACCEPTANCE_TESTS = ACCEPTANCE_TESTS;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        E2E_001_BASIC_WORKFLOW,
        E2E_002_VALIDATION,
        E2E_003_SEARCH,
        E2E_004_VERSION,
        E2E_005_KEYBOARD,
        E2E_006_ACCESSIBILITY,
        E2E_007_ERROR_HANDLING,
        ACCEPTANCE_TESTS
    };
}
