/**
 * diff.js - 教育理論エディター 差分計算モジュール
 * @module diff
 * 
 * 設計書: DESIGN-002-theory-editor.md
 * 要件: FR-VERSION-004
 */

/**
 * 2つの理論配列の差分を計算する
 * @param {Array} oldTheories - 古い理論配列
 * @param {Array} newTheories - 新しい理論配列
 * @returns {{ added: Array, removed: Array, modified: Array }}
 */
function computeDiff(oldTheories, newTheories) {
    // 空配列のデフォルト処理
    const oldList = Array.isArray(oldTheories) ? oldTheories : [];
    const newList = Array.isArray(newTheories) ? newTheories : [];
    
    const oldMap = new Map(oldList.map(t => [t.id, t]));
    const newMap = new Map(newList.map(t => [t.id, t]));
    
    const added = [];
    const removed = [];
    const modified = [];
    
    // 追加されたもの（新しい配列にあって、古い配列にない）
    for (const [id, theory] of newMap) {
        if (!oldMap.has(id)) {
            added.push(theory);
        }
    }
    
    // 削除されたもの（古い配列にあって、新しい配列にない）
    for (const [id, theory] of oldMap) {
        if (!newMap.has(id)) {
            removed.push(theory);
        }
    }
    
    // 変更されたもの（両方にあって、内容が異なる）
    for (const [id, newTheory] of newMap) {
        const oldTheory = oldMap.get(id);
        if (oldTheory && !isTheoryEqual(oldTheory, newTheory)) {
            modified.push({ 
                old: oldTheory, 
                new: newTheory,
                changedFields: getChangedFields(oldTheory, newTheory)
            });
        }
    }
    
    return { added, removed, modified };
}

/**
 * 2つの理論が同一かどうかを比較する
 * @param {Object} a - 理論A
 * @param {Object} b - 理論B
 * @returns {boolean}
 */
function isTheoryEqual(a, b) {
    return JSON.stringify(a) === JSON.stringify(b);
}

/**
 * 変更されたフィールドを取得する
 * @param {Object} oldTheory - 古い理論
 * @param {Object} newTheory - 新しい理論
 * @returns {string[]}
 */
function getChangedFields(oldTheory, newTheory) {
    const changes = [];
    
    // 単一値フィールド
    const fields = ['name', 'name_ja', 'description', 'description_ja', 'category', 'priority'];
    for (const field of fields) {
        if (oldTheory[field] !== newTheory[field]) {
            changes.push(field);
        }
    }
    
    // 配列フィールド
    const arrayFields = ['theorists', 'key_principles', 'applications', 'strengths', 'limitations'];
    for (const field of arrayFields) {
        if (JSON.stringify(oldTheory[field]) !== JSON.stringify(newTheory[field])) {
            changes.push(field);
        }
    }
    
    return changes;
}

/**
 * 差分の統計情報を取得する
 * @param {{ added: Array, removed: Array, modified: Array }} diff - 差分オブジェクト
 * @returns {{ totalChanges: number, addedCount: number, removedCount: number, modifiedCount: number }}
 */
function getDiffStats(diff) {
    return {
        totalChanges: diff.added.length + diff.removed.length + diff.modified.length,
        addedCount: diff.added.length,
        removedCount: diff.removed.length,
        modifiedCount: diff.modified.length
    };
}

/**
 * 差分結果をフォーマットする（表示用）
 * @param {{ added: Array, removed: Array, modified: Array }} diff - 差分オブジェクト
 * @returns {string}
 */
function formatDiffResult(diff) {
    const lines = [];
    
    if (diff.added.length > 0) {
        lines.push(`追加: ${diff.added.length}件`);
        diff.added.forEach(t => lines.push(`  + ${t.id}: ${t.name}`));
    }
    
    if (diff.removed.length > 0) {
        lines.push(`削除: ${diff.removed.length}件`);
        diff.removed.forEach(t => lines.push(`  - ${t.id}: ${t.name}`));
    }
    
    if (diff.modified.length > 0) {
        lines.push(`変更: ${diff.modified.length}件`);
        diff.modified.forEach(m => {
            const fields = m.changedFields || getChangedFields(m.old, m.new);
            lines.push(`  ~ ${m.new.id}: ${m.new.name} (${fields.join(', ')})`);
        });
    }
    
    if (lines.length === 0) {
        return '変更なし';
    }
    
    return lines.join('\n');
}

// ES Module対応（ブラウザ用）
if (typeof window !== 'undefined') {
    window.TheoryDiff = {
        computeDiff,
        isTheoryEqual,
        getChangedFields,
        getDiffStats,
        formatDiffResult
    };
}

// CommonJS対応（テスト用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        computeDiff,
        isTheoryEqual,
        getChangedFields,
        getDiffStats,
        formatDiffResult
    };
}
