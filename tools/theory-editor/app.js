/**
 * TENJIN 教育理論エディター
 * theories.json を編集するためのWebアプリケーション
 * 
 * @version 2.0.0
 * @description リファクタリング版 - モジュール分離済み
 * 
 * 設計書: DESIGN-002-theory-editor.md
 * 要件: REQ-002-theory-editor.md
 * 
 * モジュール依存:
 *   - validation.js: TheoryValidation (データバリデーション)
 *   - diff.js: TheoryDiff (差分計算)
 *   - storage.js: TheoryStorage (LocalStorage管理) - VERSION_STORAGE_KEY, MAX_VERSIONS定義
 *   - error-handler.js: エラーハンドリング
 */

// ===== Constants =====
// VERSION_STORAGE_KEY と MAX_VERSIONS は storage.js で定義済み

// カテゴリ名のマッピング（グローバル定数として移動）
const CATEGORY_NAMES = {
    'learning_theory': '学習理論',
    'developmental': '発達理論',
    'motivation': '動機づけ理論',
    'instructional_design': '教授設計',
    'social_learning': '社会的学習',
    'curriculum': 'カリキュラム',
    'assessment': '評価',
    'technology_enhanced': 'テクノロジー活用',
    'asian_education': 'アジア教育思想',
    'modern_education': '現代教育',
    'critical_alternative_special': '批判的・代替教育',
    'critical_alternative': '批判的・代替教育'
};

// ===== State Management (TASK-005) =====
/**
 * アプリケーション状態（単一ステートオブジェクトパターン）
 * @type {Object}
 * @property {Object[]} theories - 理論データ配列
 * @property {Object|null} metadata - ファイルメタデータ
 * @property {string|null} currentTheoryId - 選択中の理論ID
 * @property {boolean} isModified - 未保存変更フラグ
 * @property {string} searchQuery - 検索クエリ
 * @property {string} categoryFilter - カテゴリフィルタ
 * @property {Object[]} versions - バージョン履歴
 */
const state = {
    theories: [],
    metadata: null,
    currentTheoryId: null,
    isModified: false,
    searchQuery: '',
    categoryFilter: '',
    versions: []
};

/**
 * State更新関数 - 状態変更を一元管理
 * @param {Object} updates - 更新するプロパティ
 */
function updateState(updates) {
    Object.assign(state, updates);
}

/**
 * State取得関数（デバッグ・テスト用）
 * @returns {Object} 現在の状態のコピー
 */
function getState() {
    return { ...state };
}

// ===== DOM Elements =====
let elements = {};

/**
 * DOM要素を初期化
 */
function initializeElements() {
    elements = {
        theoryList: document.getElementById('theory-list'),
        searchInput: document.getElementById('search-input'),
        categoryFilter: document.getElementById('category-filter'),
        statsCount: document.getElementById('stats-count'),
        statsFiltered: document.getElementById('stats-filtered'),
        editorForm: document.getElementById('editor-form'),
        editorPlaceholder: document.getElementById('editor-placeholder'),
        editorTitle: document.getElementById('editor-title'),
        statusMessage: document.getElementById('status-message'),
        statusModified: document.getElementById('status-modified'),
        btnAdd: document.getElementById('btn-add'),
        btnDelete: document.getElementById('btn-delete'),
        btnImport: document.getElementById('btn-import'),
        btnExport: document.getElementById('btn-export'),
        btnHistory: document.getElementById('btn-history'),
        fileInput: document.getElementById('file-input'),
        modalDelete: document.getElementById('modal-delete'),
        modalDeleteName: document.getElementById('modal-delete-name'),
        btnConfirmDelete: document.getElementById('btn-confirm-delete'),
        modalHistory: document.getElementById('modal-history'),
        versionList: document.getElementById('version-list'),
        versionCount: document.getElementById('version-count'),
        storageUsage: document.getElementById('storage-usage'),
        btnClearHistory: document.getElementById('btn-clear-history'),
        modalSaveVersion: document.getElementById('modal-save-version'),
        versionDescription: document.getElementById('version-description'),
        btnConfirmSaveVersion: document.getElementById('btn-confirm-save-version'),
        modalDiff: document.getElementById('modal-diff'),
        diffContent: document.getElementById('diff-content')
    };
}

// 後方互換性のためcategoryNamesも保持
const categoryNames = CATEGORY_NAMES;

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    initializeEventListeners();
    initializeVersions();
    initializeWebSocket();
    loadDefaultData();
});

/**
 * WebSocket接続を初期化
 */
function initializeWebSocket() {
    if (typeof GraphRAGSync === 'undefined') {
        console.warn('GraphRAGSync module not loaded, WebSocket disabled');
        return;
    }
    
    const wsStatus = document.getElementById('ws-status');
    const statusText = wsStatus?.querySelector('.status-text');
    
    GraphRAGSync.connect({
        onConnectionChange: (connected) => {
            if (wsStatus) {
                wsStatus.className = `ws-status ${connected ? 'connected' : 'disconnected'}`;
                if (statusText) {
                    statusText.textContent = connected ? '接続中' : '未接続';
                }
            }
            console.log(`[WS] Connection: ${connected ? 'CONNECTED' : 'DISCONNECTED'}`);
        },
        
        onUpdate: (data) => {
            console.log('[WS] Theory update received:', data);
            // 他のクライアントからの更新を受信
            if (data.client_id && data.action) {
                setStatus(`📡 ${data.action}: ${data.theory_id || 'unknown'}`, 'info');
            }
        },
        
        onSyncComplete: (result) => {
            console.log('[WS] Sync completed:', result);
            if (result.success) {
                setStatus('✓ GraphRAG同期完了', 'success');
            } else {
                setStatus(`✗ 同期エラー: ${result.error || 'unknown'}`, 'error');
            }
        }
    });
}

/**
 * デフォルトデータを読み込み
 * 1. まず theories.json を自動読み込み試行
 * 2. 失敗した場合はサンプルデータを表示
 */
async function loadDefaultData() {
    setStatus('データを読み込み中...', 'info');
    
    // 現在のURLからベースパスを取得
    const currentPath = window.location.pathname;
    const basePath = currentPath.substring(0, currentPath.lastIndexOf('/tools/theory-editor/') + 1);
    
    // 複数のパスを試行（ローカルサーバーとファイル直接の両方に対応）
    const paths = [
        basePath + 'data/theories/theories.json',  // 動的ベースパス
        '/data/theories/theories.json',             // 絶対パス
        '../../data/theories/theories.json',        // 相対パス
        '../data/theories/theories.json',
        'data/theories/theories.json',
        './data/theories/theories.json'
    ];
    
    console.log('Trying paths:', paths);
    
    for (const path of paths) {
        try {
            console.log(`Trying: ${path}`);
            const response = await fetch(path);
            if (response.ok) {
                const data = await response.json();
                if (data.theories && Array.isArray(data.theories) && data.theories.length > 0) {
                    state.metadata = data.metadata || {};
                    state.theories = data.theories;
                    updateCategoryFilter();
                    renderTheoryList();
                    setStatus(`✓ ${state.theories.length}件の理論を読み込みました`, 'success');
                    console.log(`✓ Loaded from: ${path}`);
                    return;
                }
            }
        } catch (e) {
            // このパスは失敗、次を試行
            console.log(`✗ Path ${path} failed:`, e.message);
        }
    }
    
    // すべて失敗した場合はサンプルデータ
    console.log('Auto-load failed, showing sample data. Use Import button to load data.');
    loadSampleData();
    setStatus('📂 「インポート」ボタンから theories.json を読み込んでください', 'info');
}

function initializeEventListeners() {
    // 検索・フィルター
    elements.searchInput.addEventListener('input', handleSearch);
    elements.categoryFilter.addEventListener('change', handleFilter);
    
    // フォーム
    elements.editorForm.addEventListener('submit', handleSave);
    
    // ボタン
    elements.btnAdd.addEventListener('click', handleAdd);
    elements.btnDelete.addEventListener('click', handleDeleteClick);
    elements.btnConfirmDelete.addEventListener('click', handleConfirmDelete);
    elements.btnImport.addEventListener('click', () => elements.fileInput.click());
    elements.btnExport.addEventListener('click', handleExport);
    
    // バージョン管理
    elements.btnHistory.addEventListener('click', openHistoryModal);
    elements.btnClearHistory.addEventListener('click', handleClearHistory);
    elements.btnConfirmSaveVersion.addEventListener('click', handleConfirmSaveVersion);
    
    // 理論別履歴ボタン
    document.getElementById('btn-history-theory')?.addEventListener('click', openTheoryHistoryModal);
    
    // GraphRAG同期ボタン
    document.getElementById('btn-sync-graphrag')?.addEventListener('click', handleGraphRAGSync);
    
    // ファイル入力
    elements.fileInput.addEventListener('change', handleImport);
    
    // 文字数カウント
    document.getElementById('theory-description').addEventListener('input', (e) => {
        document.getElementById('desc-count').textContent = e.target.value.length;
        markModified();
    });
    document.getElementById('theory-description-ja').addEventListener('input', (e) => {
        document.getElementById('desc-ja-count').textContent = e.target.value.length;
        markModified();
    });
    
    // フォームフィールドの変更検知
    elements.editorForm.querySelectorAll('input, select, textarea').forEach(el => {
        el.addEventListener('change', markModified);
    });
    
    // キーボードショートカット (TASK-013: アクセシビリティ)
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

/**
 * キーボードショートカット処理 (WCAG 2.1対応)
 * @param {KeyboardEvent} e
 */
function handleKeyboardShortcuts(e) {
    // Escapeでモーダルを閉じる
    if (e.key === 'Escape') {
        closeAllModals();
    }
    
    // Ctrl+S で保存
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        if (state.currentTheoryId && state.isModified) {
            elements.editorForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Ctrl+N で新規作成
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        handleAdd();
    }
}

/**
 * 全モーダルを閉じる
 */
function closeAllModals() {
    ['delete', 'history', 'save-version', 'diff'].forEach(name => {
        const modal = document.getElementById(`modal-${name}`);
        if (modal) modal.classList.add('hidden');
    });
}

/**
 * バージョン履歴を初期化 (TASK-008: storage.js統合)
 */
function initializeVersions() {
    if (typeof TheoryStorage !== 'undefined') {
        // モジュール版を使用
        updateState({ versions: TheoryStorage.loadVersionsFromStorage() });
    } else {
        // フォールバック: 従来の実装
        loadVersionsFromStorage();
    }
}

// ===== Data Loading =====
function loadSampleData() {
    // サンプルデータ
    state.metadata = {
        version: "2.0.0",
        total_theories: 0,
        generated_at: new Date().toISOString().split('T')[0],
        last_updated: new Date().toISOString()
    };
    state.theories = [
        {
            id: "theory-sample",
            name: "Sample Theory",
            name_ja: "サンプル理論",
            category: "learning_theory",
            priority: 4,
            theorists: ["Sample Author"],
            description: "This is a sample theory. Import your theories.json file to edit real data.",
            description_ja: "これはサンプル理論です。実際のデータを編集するにはtheories.jsonをインポートしてください。",
            key_principles: ["Principle 1", "Principle 2"],
            applications: ["Application 1"],
            strengths: ["Strength 1"],
            limitations: ["Limitation 1"]
        }
    ];
    
    updateCategoryFilter();
    renderTheoryList();
}

// ===== Rendering =====
function renderTheoryList() {
    const filtered = getFilteredTheories();
    
    elements.theoryList.innerHTML = filtered.map(theory => `
        <li class="theory-item ${theory.id === state.currentTheoryId ? 'active' : ''}" 
            data-id="${theory.id}"
            role="option"
            aria-selected="${theory.id === state.currentTheoryId}"
            tabindex="0"
            onclick="selectTheory('${theory.id}')"
            onkeydown="handleTheoryItemKeydown(event, '${theory.id}')">
            <div class="theory-item-id">${escapeHtml(theory.id)}</div>
            <div class="theory-item-name">${escapeHtml(theory.name)}</div>
            <div class="theory-item-category">
                <span class="badge">${CATEGORY_NAMES[theory.category] || theory.category}</span>
            </div>
        </li>
    `).join('');
    
    // 統計更新
    elements.statsCount.textContent = `全${state.theories.length}件`;
    if (filtered.length !== state.theories.length) {
        elements.statsFiltered.textContent = `(${filtered.length}件表示)`;
    } else {
        elements.statsFiltered.textContent = '';
    }
}

/**
 * 理論アイテムのキーボード操作 (アクセシビリティ)
 * @param {KeyboardEvent} e
 * @param {string} id
 */
function handleTheoryItemKeydown(e, id) {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectTheory(id);
    }
}

// ===== Search Module (TASK-007) =====
function getFilteredTheories() {
    return state.theories.filter(theory => {
        // 検索クエリのマッチング（拡張版）
        const matchesSearch = !state.searchQuery || 
            theory.name.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
            (theory.name_ja && theory.name_ja.includes(state.searchQuery)) ||
            theory.id.includes(state.searchQuery) ||
            (theory.description && theory.description.toLowerCase().includes(state.searchQuery.toLowerCase())) ||
            (theory.theorists && theory.theorists.some(t => t.toLowerCase().includes(state.searchQuery.toLowerCase())));
        
        const matchesCategory = !state.categoryFilter || 
            theory.category === state.categoryFilter;
        
        return matchesSearch && matchesCategory;
    });
}

function updateCategoryFilter() {
    const categories = [...new Set(state.theories.map(t => t.category))].sort();
    
    elements.categoryFilter.innerHTML = `
        <option value="">すべてのカテゴリ</option>
        ${categories.map(cat => `
            <option value="${cat}">${CATEGORY_NAMES[cat] || cat}</option>
        `).join('')}
    `;
}

// ===== CRUD Module - Theory Selection (TASK-006) =====
function selectTheory(id) {
    if (state.isModified) {
        if (!confirm('未保存の変更があります。破棄しますか？')) {
            return;
        }
    }
    
    updateState({
        currentTheoryId: id,
        isModified: false
    });
    elements.statusModified.classList.add('hidden');
    
    const theory = state.theories.find(t => t.id === id);
    if (theory) {
        populateForm(theory);
        elements.editorPlaceholder.classList.add('hidden');
        elements.editorForm.classList.remove('hidden');
        elements.editorTitle.textContent = `${theory.name} を編集`;
    }
    
    renderTheoryList();
}

function populateForm(theory) {
    // 基本情報
    document.getElementById('theory-id').value = theory.id;
    document.getElementById('theory-name').value = theory.name || '';
    document.getElementById('theory-name-ja').value = theory.name_ja || '';
    document.getElementById('theory-category').value = theory.category || '';
    document.getElementById('theory-priority').value = theory.priority || 4;
    document.getElementById('theory-theorists').value = (theory.theorists || []).join(', ');
    
    // 説明
    document.getElementById('theory-description').value = theory.description || '';
    document.getElementById('theory-description-ja').value = theory.description_ja || '';
    document.getElementById('desc-count').textContent = (theory.description || '').length;
    document.getElementById('desc-ja-count').textContent = (theory.description_ja || '').length;
    
    // 配列フィールド
    populateArrayField('principles', theory.key_principles || []);
    populateArrayField('applications', theory.applications || []);
    populateArrayField('strengths', theory.strengths || []);
    populateArrayField('limitations', theory.limitations || []);
}

function populateArrayField(fieldName, values) {
    const container = document.getElementById(`${fieldName}-container`);
    container.innerHTML = values.map((value, index) => createArrayItemHTML(fieldName, index, value)).join('');
    
    if (values.length === 0) {
        container.innerHTML = createArrayItemHTML(fieldName, 0, '');
    }
}

function createArrayItemHTML(fieldName, index, value) {
    return `
        <div class="array-item" data-field="${fieldName}" data-index="${index}">
            <input type="text" value="${escapeHtml(value)}" 
                   placeholder="${getPlaceholder(fieldName)}"
                   aria-label="${fieldName} ${index + 1}"
                   onchange="markModified()">
            <button type="button" class="btn-remove" onclick="removeArrayItem(this)" aria-label="削除">✕</button>
        </div>
    `;
}

function getPlaceholder(fieldName) {
    const placeholders = {
        'principles': '主要原則を入力...',
        'applications': '応用例を入力...',
        'strengths': '強みを入力...',
        'limitations': '限界を入力...'
    };
    return placeholders[fieldName] || '';
}

// ===== Array Field Management =====
function addArrayItem(fieldName) {
    const container = document.getElementById(`${fieldName}-container`);
    const items = container.querySelectorAll('.array-item');
    const newIndex = items.length;
    
    const div = document.createElement('div');
    div.innerHTML = createArrayItemHTML(fieldName, newIndex, '');
    container.appendChild(div.firstElementChild);
    
    // 新しいフィールドにフォーカス
    container.querySelector('.array-item:last-child input').focus();
    markModified();
}

function removeArrayItem(button) {
    const item = button.closest('.array-item');
    const container = item.parentElement;
    
    // 最後の1つは削除しない
    if (container.querySelectorAll('.array-item').length > 1) {
        item.remove();
        markModified();
    } else {
        item.querySelector('input').value = '';
        markModified();
    }
}

// ===== CRUD Module - Form Handling (TASK-006 with validation.js) =====
function handleSave(e) {
    e.preventDefault();
    
    // 前回のエラー表示をクリア
    clearFieldErrors();
    
    const theoryData = collectFormData();
    
    // バリデーション（validation.js モジュールを使用）
    if (typeof TheoryValidation !== 'undefined') {
        const validation = TheoryValidation.validateTheory(theoryData);
        if (!validation.isValid) {
            // エラーをUIに表示
            validation.errors.forEach(err => {
                showFieldError(err.field, err.message);
            });
            
            const errorMessages = validation.errors.map(err => err.message).join('\n');
            setStatus(errorMessages, 'error');
            
            // 最初のエラーフィールドにフォーカス
            if (validation.errors.length > 0) {
                const firstError = validation.errors[0];
                const field = document.getElementById(`theory-${firstError.field}`);
                if (field) field.focus();
            }
            return;
        }
    } else {
        // フォールバック: 従来のバリデーション
        if (!theoryData.name || !theoryData.category) {
            showFieldError('name', '英語名は必須です');
            showFieldError('category', 'カテゴリは必須です');
            setStatus('英語名とカテゴリは必須です', 'error');
            return;
        }
    }
    
    const index = state.theories.findIndex(t => t.id === state.currentTheoryId);
    const isNew = index === -1;
    
    if (index !== -1) {
        state.theories[index] = theoryData;
    } else {
        state.theories.push(theoryData);
    }
    
    // バージョンを自動保存
    const action = isNew ? '新規追加' : '編集';
    saveVersion(`${theoryData.name} を${action}`);
    
    // WebSocket通知を送信
    if (typeof GraphRAGSync !== 'undefined') {
        GraphRAGSync.notifyTheoryUpdate(theoryData.id, isNew ? 'create' : 'update');
    }
    
    updateState({ isModified: false });
    elements.statusModified.classList.add('hidden');
    
    updateCategoryFilter();
    renderTheoryList();
    setStatus(`「${theoryData.name}」を保存しました（履歴に記録）`, 'success');
}

function collectFormData() {
    return {
        id: document.getElementById('theory-id').value,
        name: document.getElementById('theory-name').value.trim(),
        name_ja: document.getElementById('theory-name-ja').value.trim() || undefined,
        category: document.getElementById('theory-category').value,
        priority: parseInt(document.getElementById('theory-priority').value),
        theorists: document.getElementById('theory-theorists').value
            .split(',')
            .map(s => s.trim())
            .filter(s => s),
        description: document.getElementById('theory-description').value.trim(),
        description_ja: document.getElementById('theory-description-ja').value.trim() || undefined,
        key_principles: collectArrayField('principles'),
        applications: collectArrayField('applications'),
        strengths: collectArrayField('strengths'),
        limitations: collectArrayField('limitations')
    };
}

function collectArrayField(fieldName) {
    const container = document.getElementById(`${fieldName}-container`);
    const inputs = container.querySelectorAll('.array-item input');
    return Array.from(inputs)
        .map(input => input.value.trim())
        .filter(value => value);
}

// ===== CRUD Module - Add/Delete (TASK-006) =====
function handleAdd() {
    if (state.isModified) {
        if (!confirm('未保存の変更があります。破棄しますか？')) {
            return;
        }
    }
    
    // 新しいIDを生成
    const maxId = state.theories.reduce((max, t) => {
        const num = parseInt(t.id.replace('theory-', ''));
        return num > max ? num : max;
    }, 0);
    
    const newTheory = {
        id: `theory-${String(maxId + 1).padStart(3, '0')}`,
        name: '',
        name_ja: '',
        category: '',
        priority: 4,
        theorists: [],
        description: '',
        description_ja: '',
        key_principles: [],
        applications: [],
        strengths: [],
        limitations: []
    };
    
    updateState({ currentTheoryId: newTheory.id });
    state.theories.push(newTheory);
    
    populateForm(newTheory);
    elements.editorPlaceholder.classList.add('hidden');
    elements.editorForm.classList.remove('hidden');
    elements.editorTitle.textContent = '新規理論を作成';
    
    renderTheoryList();
    document.getElementById('theory-name').focus();
    markModified();
}

function handleDeleteClick() {
    const theory = state.theories.find(t => t.id === state.currentTheoryId);
    if (theory) {
        elements.modalDeleteName.textContent = `${theory.name} (${theory.id})`;
        elements.modalDelete.classList.remove('hidden');
        // フォーカスを確認ボタンに移動（アクセシビリティ）
        elements.btnConfirmDelete.focus();
    }
}

function handleConfirmDelete() {
    const index = state.theories.findIndex(t => t.id === state.currentTheoryId);
    if (index !== -1) {
        const deletedName = state.theories[index].name;
        const deletedId = state.theories[index].id;
        state.theories.splice(index, 1);
        
        // バージョンを保存
        saveVersion(`${deletedName} (${deletedId}) を削除`);
        
        // WebSocket通知を送信
        if (typeof GraphRAGSync !== 'undefined') {
            GraphRAGSync.notifyTheoryUpdate(deletedId, 'delete');
        }
        
        updateState({
            currentTheoryId: null,
            isModified: false
        });
        elements.statusModified.classList.add('hidden');
        
        elements.editorForm.classList.add('hidden');
        elements.editorPlaceholder.classList.remove('hidden');
        
        updateCategoryFilter();
        renderTheoryList();
        closeModal('delete');
        setStatus(`「${deletedName}」を削除しました（履歴に記録）`, 'success');
    }
}

function closeModal(modalName) {
    document.getElementById(`modal-${modalName}`).classList.add('hidden');
}

// ===== Import/Export Module =====
function handleImport(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
        try {
            const data = JSON.parse(event.target.result);
            
            // バリデーション（validation.js モジュールを使用）
            if (typeof TheoryValidation !== 'undefined') {
                if (!TheoryValidation.validateImportData(data)) {
                    throw new Error('有効なtheoriesデータが見つかりません');
                }
            } else if (!data.theories || !Array.isArray(data.theories)) {
                throw new Error('Invalid format: theories array not found');
            }
            
            // インポート前に現在の状態を保存
            if (state.theories.length > 0) {
                saveVersion('インポート前の自動バックアップ');
            }
            
            updateState({
                theories: data.theories,
                metadata: data.metadata || {},
                currentTheoryId: null,
                isModified: false
            });
            
            // インポート後の状態も保存
            saveVersion(`${file.name} をインポート (${data.theories.length}件)`);
            
            elements.editorForm.classList.add('hidden');
            elements.editorPlaceholder.classList.remove('hidden');
            elements.statusModified.classList.add('hidden');
            
            updateCategoryFilter();
            renderTheoryList();
            setStatus(`${state.theories.length}件の理論をインポートしました（履歴に記録）`, 'success');
        } catch (error) {
            setStatus(`JSONファイルの読み込みに失敗しました: ${error.message}`, 'error');
        }
    };
    reader.onerror = () => {
        setStatus('ファイルの読み込みに失敗しました', 'error');
    };
    reader.readAsText(file);
    
    // リセット（同じファイルを再度選択できるように）
    e.target.value = '';
}

function handleExport() {
    // エクスポート前にバージョンを保存
    saveVersion('エクスポート時点のスナップショット');
    
    const exportData = {
        metadata: {
            ...state.metadata,
            total_theories: state.theories.length,
            last_updated: new Date().toISOString()
        },
        theories: state.theories
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `theories_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setStatus(`${state.theories.length}件の理論をエクスポートしました（履歴に記録）`, 'success');
}

/**
 * GraphRAGとの同期処理
 * 理論データをGraphRAGにエクスポートしてインデックスを再作成
 */
async function handleGraphRAGSync() {
    if (!confirm('GraphRAGのインデックスを再作成しますか？\n\n' +
                 'この操作は以下を行います：\n' +
                 '1. 現在の理論データをGraphRAGにコピー\n' +
                 '2. Neo4jデータベースのインデックスを再作成\n\n' +
                 '※ Neo4jが起動している必要があります')) {
        return;
    }
    
    // GraphRAGSyncモジュールが読み込まれているか確認
    if (typeof GraphRAGSync === 'undefined') {
        setStatus('GraphRAG同期モジュールが読み込まれていません', 'error');
        console.error('GraphRAGSync module not loaded. Make sure graphrag-sync.js is included.');
        return;
    }
    
    setStatus('GraphRAGと同期中...', 'info');
    
    try {
        const result = await GraphRAGSync.triggerReindex();
        
        if (result.success) {
            setStatus(`✓ GraphRAG同期完了: ${result.message}`, 'success');
            console.log('GraphRAG sync result:', result);
        } else {
            setStatus(`✗ GraphRAG同期エラー: ${result.message}`, 'error');
            console.error('GraphRAG sync failed:', result);
        }
    } catch (error) {
        setStatus(`✗ GraphRAG同期エラー: ${error.message}`, 'error');
        console.error('GraphRAG sync exception:', error);
    }
}

// ===== Search & Filter (TASK-007) =====
function handleSearch(e) {
    updateState({ searchQuery: e.target.value });
    renderTheoryList();
}

function handleFilter(e) {
    updateState({ categoryFilter: e.target.value });
    renderTheoryList();
}

// ===== Utilities =====
function markModified() {
    if (!state.isModified) {
        updateState({ isModified: true });
        elements.statusModified.classList.remove('hidden');
    }
}

/**
 * ステータスメッセージを表示
 * @param {string} message - 表示するメッセージ
 * @param {string} type - 'info' | 'success' | 'error' | 'warning'
 */
function setStatus(message, type = 'info') {
    elements.statusMessage.textContent = message;
    elements.statusMessage.className = `status-message status-${type}`;
    
    // スクリーンリーダー対応（WCAG 2.1）
    elements.statusMessage.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
    
    // 成功・情報メッセージは3秒後にクリア
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            if (elements.statusMessage.textContent === message) {
                elements.statusMessage.textContent = '';
            }
        }, 3000);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ===== TASK-010: Validation UI Functions =====
/**
 * フィールドエラーを表示
 * @param {string} fieldName - フィールド名（theory-接頭辞なし）
 * @param {string} message - エラーメッセージ
 */
function showFieldError(fieldName, message) {
    const field = document.getElementById(`theory-${fieldName}`);
    if (!field) return;
    
    // エラースタイルを追加
    field.classList.add('form-group__input--error');
    
    // 既存のエラーメッセージがあれば削除
    const existingError = field.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // エラーメッセージを追加
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.setAttribute('role', 'alert');
    field.parentElement.appendChild(errorDiv);
    
    // aria-invalid属性を追加
    field.setAttribute('aria-invalid', 'true');
}

/**
 * 全フィールドのエラー表示をクリア
 */
function clearFieldErrors() {
    // エラースタイルを削除
    document.querySelectorAll('.form-group__input--error').forEach(el => {
        el.classList.remove('form-group__input--error');
        el.removeAttribute('aria-invalid');
    });
    
    // エラーメッセージを削除
    document.querySelectorAll('.field-error').forEach(el => {
        el.remove();
    });
}

// グローバル関数として公開
window.selectTheory = selectTheory;
window.addArrayItem = addArrayItem;
window.removeArrayItem = removeArrayItem;
window.closeModal = closeModal;
window.markModified = markModified;
window.restoreVersion = restoreVersion;
window.deleteVersion = deleteVersion;
window.showDiff = showDiff;
window.handleTheoryItemKeydown = handleTheoryItemKeydown;
window.getState = getState; // デバッグ用
window.showFieldError = showFieldError;
window.clearFieldErrors = clearFieldErrors;

// ===== Version Management (TASK-008 with storage.js/diff.js) =====
function loadVersionsFromStorage() {
    try {
        const stored = localStorage.getItem(VERSION_STORAGE_KEY);
        updateState({ versions: stored ? JSON.parse(stored) : [] });
    } catch (e) {
        console.error('Failed to load versions:', e);
        updateState({ versions: [] });
    }
}

function saveVersionsToStorage() {
    try {
        if (typeof TheoryStorage !== 'undefined') {
            TheoryStorage.saveVersionsToStorage(state.versions);
        } else {
            localStorage.setItem(VERSION_STORAGE_KEY, JSON.stringify(state.versions));
        }
    } catch (e) {
        console.error('Failed to save versions:', e);
        setStatus('ストレージの容量が不足しています。古いバージョンを削除してください。', 'error');
    }
}

function saveVersion(description = '') {
    let version;
    
    if (typeof TheoryStorage !== 'undefined') {
        // モジュール版を使用
        version = TheoryStorage.createVersion(
            { metadata: state.metadata, theories: state.theories },
            description || '自動保存'
        );
        state.versions.unshift(version);
        state.versions = TheoryStorage.enforceVersionLimit(state.versions, MAX_VERSIONS);
        TheoryStorage.saveVersionsToStorage(state.versions);
    } else {
        // フォールバック: 従来の実装
        version = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            description: description || '自動保存',
            theoryCount: state.theories.length,
            data: {
                metadata: { ...state.metadata },
                theories: JSON.parse(JSON.stringify(state.theories))
            }
        };
        
        state.versions.unshift(version);
        
        // 最大数を超えたら古いものを削除
        if (state.versions.length > MAX_VERSIONS) {
            state.versions = state.versions.slice(0, MAX_VERSIONS);
        }
        
        saveVersionsToStorage();
    }
    
    return version;
}

function openHistoryModal() {
    renderVersionList();
    elements.modalHistory.classList.remove('hidden');
}

function renderVersionList() {
    if (state.versions.length === 0) {
        elements.versionList.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                    履歴がありません。保存時に自動的に履歴が作成されます。
                </td>
            </tr>
        `;
    } else {
        elements.versionList.innerHTML = state.versions.map((v, index) => {
            const date = new Date(v.timestamp);
            const dateStr = date.toLocaleDateString('ja-JP');
            const timeStr = date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
            const isCurrent = index === 0;
            
            return `
                <tr class="${isCurrent ? 'version-current' : ''}">
                    <td>v${state.versions.length - index}</td>
                    <td>${dateStr} ${timeStr}</td>
                    <td>${escapeHtml(v.description)}</td>
                    <td>${v.theoryCount}件</td>
                    <td class="version-actions">
                        ${index > 0 ? `
                            <button class="btn-icon" onclick="showDiff(${v.id})" title="前バージョンと比較" aria-label="差分表示">📊</button>
                            <button class="btn-icon btn-restore" onclick="restoreVersion(${v.id})" title="このバージョンに戻す" aria-label="復元">↩️</button>
                        ` : '<span style="color: var(--text-light);">現在</span>'}
                        <button class="btn-icon btn-delete-version" onclick="deleteVersion(${v.id})" title="削除" aria-label="削除">🗑️</button>
                    </td>
                </tr>
            `;
        }).join('');
    }
    
    // 統計更新
    elements.versionCount.textContent = `${state.versions.length}件のバージョン`;
    
    // ストレージ使用量表示（storage.jsモジュール使用）
    if (typeof TheoryStorage !== 'undefined') {
        const usage = TheoryStorage.getStorageUsage();
        elements.storageUsage.textContent = `使用容量: ${usage.usedKB} KB`;
    } else {
        const storageSize = new Blob([JSON.stringify(state.versions)]).size;
        elements.storageUsage.textContent = `使用容量: ${(storageSize / 1024).toFixed(1)} KB`;
    }
}

function restoreVersion(versionId) {
    const version = state.versions.find(v => v.id === versionId);
    if (!version) return;
    
    if (!confirm(`このバージョン (${version.description}) に戻しますか？\n現在の変更は失われます。`)) {
        return;
    }
    
    // 現在の状態を保存してから復元
    saveVersion('復元前の自動バックアップ');
    
    updateState({
        theories: JSON.parse(JSON.stringify(version.data.theories)),
        metadata: { ...version.data.metadata },
        currentTheoryId: null,
        isModified: false
    });
    
    elements.editorForm.classList.add('hidden');
    elements.editorPlaceholder.classList.remove('hidden');
    elements.statusModified.classList.add('hidden');
    
    updateCategoryFilter();
    renderTheoryList();
    closeModal('history');
    setStatus(`バージョンを復元しました: ${version.description}`, 'success');
}

function deleteVersion(versionId) {
    const index = state.versions.findIndex(v => v.id === versionId);
    if (index === -1) return;
    
    if (!confirm('このバージョンを削除してもよろしいですか？')) {
        return;
    }
    
    if (typeof TheoryStorage !== 'undefined') {
        updateState({ versions: TheoryStorage.removeVersion(state.versions, versionId) });
        TheoryStorage.saveVersionsToStorage(state.versions);
    } else {
        state.versions.splice(index, 1);
        saveVersionsToStorage();
    }
    
    renderVersionList();
    setStatus('バージョンを削除しました', 'success');
}

function handleClearHistory() {
    if (!confirm('すべての履歴を削除してもよろしいですか？\nこの操作は取り消せません。')) {
        return;
    }
    
    if (typeof TheoryStorage !== 'undefined') {
        TheoryStorage.clearVersionHistory();
    } else {
        localStorage.removeItem(VERSION_STORAGE_KEY);
    }
    
    updateState({ versions: [] });
    renderVersionList();
    setStatus('すべての履歴を削除しました', 'success');
}

function openSaveVersionModal() {
    elements.versionDescription.value = '';
    elements.modalSaveVersion.classList.remove('hidden');
    elements.versionDescription.focus();
}

function handleConfirmSaveVersion() {
    const description = elements.versionDescription.value.trim() || '手動保存';
    saveVersion(description);
    closeModal('save-version');
    setStatus(`バージョンを保存しました: ${description}`, 'success');
}

// ===== Diff Display (TASK-008 with diff.js) =====
function showDiff(versionId) {
    const versionIndex = state.versions.findIndex(v => v.id === versionId);
    if (versionIndex === -1 || versionIndex === 0) return;
    
    const currentVersion = state.versions[versionIndex - 1];
    const oldVersion = state.versions[versionIndex];
    
    let diff;
    if (typeof TheoryDiff !== 'undefined') {
        // モジュール版を使用
        diff = TheoryDiff.computeDiff(oldVersion.data.theories, currentVersion.data.theories);
    } else {
        // フォールバック: 従来の実装
        diff = computeDiff(oldVersion.data.theories, currentVersion.data.theories);
    }
    
    renderDiff(diff, oldVersion, currentVersion);
    elements.modalDiff.classList.remove('hidden');
}

function computeDiff(oldTheories, newTheories) {
    const oldMap = new Map(oldTheories.map(t => [t.id, t]));
    const newMap = new Map(newTheories.map(t => [t.id, t]));
    
    const added = [];
    const removed = [];
    const modified = [];
    
    // 追加されたもの
    for (const [id, theory] of newMap) {
        if (!oldMap.has(id)) {
            added.push(theory);
        }
    }
    
    // 削除されたもの
    for (const [id, theory] of oldMap) {
        if (!newMap.has(id)) {
            removed.push(theory);
        }
    }
    
    // 変更されたもの
    for (const [id, newTheory] of newMap) {
        const oldTheory = oldMap.get(id);
        if (oldTheory && JSON.stringify(oldTheory) !== JSON.stringify(newTheory)) {
            modified.push({ old: oldTheory, new: newTheory });
        }
    }
    
    return { added, removed, modified };
}

function renderDiff(diff, oldVersion, newVersion) {
    const oldDate = new Date(oldVersion.timestamp).toLocaleString('ja-JP');
    const newDate = new Date(newVersion.timestamp).toLocaleString('ja-JP');
    
    // diff.js モジュールがある場合は統計を使用
    let stats = { added: diff.added.length, removed: diff.removed.length, modified: diff.modified.length };
    if (typeof TheoryDiff !== 'undefined' && TheoryDiff.getDiffStats) {
        stats = TheoryDiff.getDiffStats(diff);
    }
    
    let html = `
        <div class="diff-summary">
            <div class="diff-summary-item">
                <span class="badge badge-added">+${stats.added}</span> 追加
            </div>
            <div class="diff-summary-item">
                <span class="badge badge-removed">-${stats.removed}</span> 削除
            </div>
            <div class="diff-summary-item">
                <span class="badge badge-modified">~${stats.modified}</span> 変更
            </div>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">
            ${oldDate} → ${newDate}
        </p>
    `;
    
    if (diff.added.length > 0) {
        html += `
            <div class="diff-section">
                <div class="diff-section-title">➕ 追加された理論 (${diff.added.length}件)</div>
                ${diff.added.map(t => `
                    <div class="diff-added">+ ${escapeHtml(t.id)}: ${escapeHtml(t.name)}</div>
                `).join('')}
            </div>
        `;
    }
    
    if (diff.removed.length > 0) {
        html += `
            <div class="diff-section">
                <div class="diff-section-title">➖ 削除された理論 (${diff.removed.length}件)</div>
                ${diff.removed.map(t => `
                    <div class="diff-removed">- ${escapeHtml(t.id)}: ${escapeHtml(t.name)}</div>
                `).join('')}
            </div>
        `;
    }
    
    if (diff.modified.length > 0) {
        html += `
            <div class="diff-section">
                <div class="diff-section-title">📝 変更された理論 (${diff.modified.length}件)</div>
                ${diff.modified.map(({ old, new: newT }) => {
                    // diff.js モジュールがある場合はそれを使用
                    const changes = typeof TheoryDiff !== 'undefined' 
                        ? TheoryDiff.getChangedFields(old, newT)
                        : getTheoryChanges(old, newT);
                    return `
                        <div class="diff-modified">
                            ~ ${escapeHtml(newT.id)}: ${escapeHtml(newT.name)}
                            <div style="font-size: 0.75rem; margin-top: 0.25rem;">
                                ${changes.join(', ')}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    
    if (diff.added.length === 0 && diff.removed.length === 0 && diff.modified.length === 0) {
        html += '<p style="text-align: center; color: var(--text-secondary);">変更はありません</p>';
    }
    
    elements.diffContent.innerHTML = html;
}

function getTheoryChanges(oldT, newT) {
    const changes = [];
    const fields = ['name', 'name_ja', 'description', 'description_ja', 'category', 'priority'];
    const arrayFields = ['theorists', 'key_principles', 'applications', 'strengths', 'limitations'];
    
    for (const field of fields) {
        if (oldT[field] !== newT[field]) {
            changes.push(field);
        }
    }
    
    for (const field of arrayFields) {
        if (JSON.stringify(oldT[field]) !== JSON.stringify(newT[field])) {
            changes.push(field);
        }
    }
    
    return changes;
}

function openTheoryHistoryModal() {
    // 現在選択中の理論の変更履歴をフィルタして表示
    // TODO: 将来的に理論別の詳細履歴を実装
    openHistoryModal();
}