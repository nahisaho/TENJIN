/**
 * storage.js - 教育理論エディター ストレージモジュール
 * @module storage
 * 
 * 設計書: DESIGN-002-theory-editor.md
 * 要件: FR-VERSION-001, FR-VERSION-005
 */

// 定数
const VERSION_STORAGE_KEY = 'tenjin_theory_versions';
const MAX_VERSIONS = 50;

/**
 * LocalStorageからバージョン履歴を読み込む
 * @returns {Array} バージョン配列
 */
function loadVersionsFromStorage() {
    try {
        const stored = localStorage.getItem(VERSION_STORAGE_KEY);
        if (!stored) {
            return [];
        }
        
        const parsed = JSON.parse(stored);
        
        // 不正なデータの場合は空配列を返す
        if (!Array.isArray(parsed)) {
            return [];
        }
        
        return parsed;
    } catch (e) {
        console.error('Failed to load versions from storage:', e);
        return [];
    }
}

/**
 * LocalStorageにバージョン履歴を保存する
 * @param {Array} versions - バージョン配列
 * @returns {{ success: boolean, error?: string }}
 */
function saveVersionsToStorage(versions) {
    try {
        const data = JSON.stringify(versions);
        localStorage.setItem(VERSION_STORAGE_KEY, data);
        return { success: true };
    } catch (e) {
        console.error('Failed to save versions to storage:', e);
        
        // QuotaExceededError の場合
        if (e.name === 'QuotaExceededError') {
            return { 
                success: false, 
                error: 'ストレージの容量が不足しています。古いバージョンを削除してください。' 
            };
        }
        
        return { success: false, error: 'バージョンの保存に失敗しました。' };
    }
}

/**
 * バージョン数を上限以内に制限する
 * @param {Array} versions - バージョン配列
 * @param {number} maxVersions - 最大バージョン数（デフォルト: 50）
 * @returns {Array} 制限後のバージョン配列
 */
function enforceVersionLimit(versions, maxVersions = MAX_VERSIONS) {
    if (!Array.isArray(versions)) {
        return [];
    }
    
    if (versions.length <= maxVersions) {
        return versions;
    }
    
    // 先頭（新しい方）からmaxVersions件を保持
    return versions.slice(0, maxVersions);
}

/**
 * 新しいバージョンを作成する
 * @param {Object} data - 保存するデータ { metadata, theories }
 * @param {string} description - バージョンの説明
 * @returns {Object} 作成されたバージョン
 */
function createVersion(data, description = '自動保存') {
    return {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        description: description,
        theoryCount: data.theories ? data.theories.length : 0,
        data: {
            metadata: data.metadata ? { ...data.metadata } : {},
            theories: data.theories ? JSON.parse(JSON.stringify(data.theories)) : []
        }
    };
}

/**
 * ストレージ使用量を取得する
 * @returns {{ used: number, usedKB: string, percentage: number }}
 */
function getStorageUsage() {
    try {
        const stored = localStorage.getItem(VERSION_STORAGE_KEY) || '';
        const used = new Blob([stored]).size;
        const estimatedLimit = 5 * 1024 * 1024; // 5MB（一般的な上限）
        
        return {
            used: used,
            usedKB: (used / 1024).toFixed(1),
            percentage: (used / estimatedLimit * 100).toFixed(1)
        };
    } catch (e) {
        return { used: 0, usedKB: '0', percentage: '0' };
    }
}

/**
 * 履歴をクリアする
 * @returns {{ success: boolean }}
 */
function clearVersionHistory() {
    try {
        localStorage.removeItem(VERSION_STORAGE_KEY);
        return { success: true };
    } catch (e) {
        console.error('Failed to clear version history:', e);
        return { success: false };
    }
}

/**
 * 指定したIDのバージョンを削除する
 * @param {Array} versions - バージョン配列
 * @param {number} versionId - 削除するバージョンID
 * @returns {Array} 削除後のバージョン配列
 */
function removeVersion(versions, versionId) {
    if (!Array.isArray(versions)) {
        return [];
    }
    
    return versions.filter(v => v.id !== versionId);
}

// 定数のエクスポート
const CONSTANTS = {
    VERSION_STORAGE_KEY,
    MAX_VERSIONS
};

// ES Module対応（ブラウザ用）
if (typeof window !== 'undefined') {
    window.TheoryStorage = {
        loadVersionsFromStorage,
        saveVersionsToStorage,
        enforceVersionLimit,
        createVersion,
        getStorageUsage,
        clearVersionHistory,
        removeVersion,
        CONSTANTS
    };
}

// CommonJS対応（テスト用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadVersionsFromStorage,
        saveVersionsToStorage,
        enforceVersionLimit,
        createVersion,
        getStorageUsage,
        clearVersionHistory,
        removeVersion,
        CONSTANTS
    };
}
