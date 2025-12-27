/**
 * validation.js - 教育理論エディター バリデーションモジュール
 * @module validation
 * 
 * 設計書: DESIGN-002-theory-editor.md
 * 要件: FR-ERROR-001, FR-ERROR-002
 */

/**
 * 理論データを検証する
 * @param {Object} theory - 検証対象の理論データ
 * @returns {{ isValid: boolean, errors: Array<{ field: string, message: string }> }}
 */
function validateTheory(theory) {
    const errors = [];
    
    // ID検証
    if (!theory || !theory.id) {
        errors.push({ field: 'id', message: 'IDは必須です' });
    }
    
    // 名前検証（英語名または日本語名のどちらかが必要）
    if (!theory.name && !theory.name_ja) {
        errors.push({ field: 'name', message: '名前（英語または日本語）は必須です' });
    }
    
    // カテゴリ検証
    if (!theory.category) {
        errors.push({ field: 'category', message: 'カテゴリは必須です' });
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

/**
 * インポートデータを検証する
 * @param {Object} data - インポートするデータ
 * @returns {boolean}
 */
function validateImportData(data) {
    // nullまたは非オブジェクトは無効
    if (!data || typeof data !== 'object') {
        return false;
    }
    
    // theories配列が必須
    if (!Array.isArray(data.theories)) {
        return false;
    }
    
    // 空の配列は無効
    if (data.theories.length === 0) {
        return false;
    }
    
    // 各理論の最低限の検証（idと名前）
    return data.theories.every(t => 
        t && t.id && (t.name || t.name_ja)
    );
}

/**
 * 必須フィールドを検証する
 * @param {Object} theory - 検証対象の理論データ
 * @param {string[]} fields - 必須フィールドの配列
 * @returns {{ isValid: boolean, missingFields: string[] }}
 */
function validateRequiredFields(theory, fields) {
    const missingFields = [];
    
    if (!theory) {
        return { isValid: false, missingFields: fields };
    }
    
    for (const field of fields) {
        const value = theory[field];
        
        // 配列の場合は空でないことを確認
        if (Array.isArray(value)) {
            if (value.length === 0 || value.every(v => !v)) {
                missingFields.push(field);
            }
        }
        // 文字列の場合は空でないことを確認
        else if (typeof value === 'string') {
            if (!value.trim()) {
                missingFields.push(field);
            }
        }
        // その他の値は存在確認
        else if (value === undefined || value === null) {
            missingFields.push(field);
        }
    }
    
    return {
        isValid: missingFields.length === 0,
        missingFields: missingFields
    };
}

/**
 * ID形式を検証する
 * @param {string} id - 検証対象のID
 * @returns {boolean}
 */
function validateTheoryId(id) {
    if (!id || typeof id !== 'string') {
        return false;
    }
    
    // theory-XXX 形式（XXXは数字）
    return /^theory-\d{3,}$/.test(id);
}

// ES Module対応（ブラウザ用）
if (typeof window !== 'undefined') {
    window.TheoryValidation = {
        validateTheory,
        validateImportData,
        validateRequiredFields,
        validateTheoryId
    };
}

// CommonJS対応（テスト用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateTheory,
        validateImportData,
        validateRequiredFields,
        validateTheoryId
    };
}
