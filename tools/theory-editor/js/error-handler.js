/**
 * TENJIN 教育理論エディター - エラーハンドラーモジュール
 * 
 * @module error-handler
 * @version 1.0.0
 * @description 統一的なエラー処理とユーザーフィードバック
 * 
 * 設計書: DESIGN-002-theory-editor.md Section 7
 * タスク: TASK-009
 */

(function(global) {
    'use strict';

    // ===== エラーコンテキスト定義 =====
    const ERROR_CONTEXTS = {
        'import-parse': {
            message: 'JSONの解析に失敗しました',
            severity: 'error',
            recoverable: true
        },
        'import-validate': {
            message: '有効なtheoriesデータが見つかりません',
            severity: 'error',
            recoverable: true
        },
        'import-file': {
            message: 'ファイルの読み込みに失敗しました',
            severity: 'error',
            recoverable: true
        },
        'save-validate': {
            message: '必須フィールドが未入力です',
            severity: 'warning',
            recoverable: true
        },
        'save-storage': {
            message: '保存に失敗しました',
            severity: 'error',
            recoverable: false
        },
        'load-fetch': {
            message: 'データの読み込みに失敗しました',
            severity: 'error',
            recoverable: true
        },
        'storage-quota': {
            message: 'ストレージ容量が不足しています。古い履歴を削除してください',
            severity: 'warning',
            recoverable: true
        },
        'storage-parse': {
            message: '履歴データが破損しています',
            severity: 'warning',
            recoverable: true
        },
        'version-restore': {
            message: 'バージョンの復元に失敗しました',
            severity: 'error',
            recoverable: true
        },
        'version-delete': {
            message: 'バージョンの削除に失敗しました',
            severity: 'error',
            recoverable: true
        },
        'export-create': {
            message: 'エクスポートファイルの作成に失敗しました',
            severity: 'error',
            recoverable: true
        },
        'unknown': {
            message: '予期しないエラーが発生しました',
            severity: 'error',
            recoverable: false
        }
    };

    // ===== エラーログ =====
    const errorLog = [];
    const MAX_ERROR_LOG = 100;

    /**
     * エラーを処理する
     * @param {Error|string} error - エラーオブジェクトまたはメッセージ
     * @param {string} context - エラーコンテキスト
     * @param {Object} [options] - 追加オプション
     * @returns {Object} エラー情報
     */
    function handleError(error, context, options = {}) {
        const errorInfo = ERROR_CONTEXTS[context] || ERROR_CONTEXTS['unknown'];
        const errorMessage = error instanceof Error ? error.message : error;
        
        // エラーログに記録
        const logEntry = {
            timestamp: new Date().toISOString(),
            context: context,
            message: errorMessage,
            severity: errorInfo.severity,
            details: options.details || null
        };
        
        errorLog.unshift(logEntry);
        if (errorLog.length > MAX_ERROR_LOG) {
            errorLog.pop();
        }
        
        // コンソールにログ
        const logMethod = errorInfo.severity === 'error' ? console.error : console.warn;
        logMethod(`[TENJIN:${context}]`, errorMessage, options.details || '');
        
        // ステータス表示関数があれば呼び出す
        if (typeof global.setStatus === 'function') {
            const displayMessage = options.customMessage || errorInfo.message;
            global.setStatus(displayMessage, errorInfo.severity);
        }
        
        return {
            context,
            message: errorInfo.message,
            originalError: errorMessage,
            severity: errorInfo.severity,
            recoverable: errorInfo.recoverable,
            timestamp: logEntry.timestamp
        };
    }

    /**
     * エラーメッセージを取得する
     * @param {string} context - エラーコンテキスト
     * @returns {string} エラーメッセージ
     */
    function getErrorMessage(context) {
        const errorInfo = ERROR_CONTEXTS[context];
        return errorInfo ? errorInfo.message : ERROR_CONTEXTS['unknown'].message;
    }

    /**
     * コンテキストに基づいてエラーが回復可能か判定
     * @param {string} context - エラーコンテキスト
     * @returns {boolean}
     */
    function isRecoverable(context) {
        const errorInfo = ERROR_CONTEXTS[context];
        return errorInfo ? errorInfo.recoverable : false;
    }

    /**
     * エラーログを取得
     * @param {number} [limit] - 取得件数
     * @returns {Object[]}
     */
    function getErrorLog(limit) {
        return limit ? errorLog.slice(0, limit) : [...errorLog];
    }

    /**
     * エラーログをクリア
     */
    function clearErrorLog() {
        errorLog.length = 0;
    }

    /**
     * try-catchラッパー
     * @param {Function} fn - 実行する関数
     * @param {string} context - エラーコンテキスト
     * @param {*} fallback - エラー時の戻り値
     * @returns {*}
     */
    function tryCatch(fn, context, fallback = null) {
        try {
            return fn();
        } catch (error) {
            handleError(error, context);
            return fallback;
        }
    }

    /**
     * 非同期try-catchラッパー
     * @param {Function} fn - 実行する非同期関数
     * @param {string} context - エラーコンテキスト
     * @param {*} fallback - エラー時の戻り値
     * @returns {Promise<*>}
     */
    async function tryCatchAsync(fn, context, fallback = null) {
        try {
            return await fn();
        } catch (error) {
            handleError(error, context);
            return fallback;
        }
    }

    // ===== モジュールエクスポート =====
    const TheoryErrorHandler = {
        handleError,
        getErrorMessage,
        isRecoverable,
        getErrorLog,
        clearErrorLog,
        tryCatch,
        tryCatchAsync,
        ERROR_CONTEXTS
    };

    // ブラウザ環境
    if (typeof window !== 'undefined') {
        window.TheoryErrorHandler = TheoryErrorHandler;
    }
    
    // Node.js環境（テスト用）
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = TheoryErrorHandler;
    }

})(typeof window !== 'undefined' ? window : global);
