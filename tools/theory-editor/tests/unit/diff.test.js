/**
 * diff.test.js - 差分計算モジュールのユニットテスト
 * 
 * テストケース: UT-DIFF-001〜005
 * 要件: FR-VERSION-004
 */

// テストフレームワーク
const TestRunner = {
    passed: 0,
    failed: 0,
    results: [],
    
    reset() {
        this.passed = 0;
        this.failed = 0;
        this.results = [];
    },
    
    test(name, fn) {
        try {
            fn();
            this.passed++;
            this.results.push({ name, status: 'PASS' });
        } catch (e) {
            this.failed++;
            this.results.push({ name, status: 'FAIL', error: e.message });
        }
    },
    
    assertEqual(actual, expected, message = '') {
        const actualStr = JSON.stringify(actual);
        const expectedStr = JSON.stringify(expected);
        if (actualStr !== expectedStr) {
            throw new Error(`${message}\n  Expected: ${expectedStr}\n  Actual: ${actualStr}`);
        }
    },
    
    assertTrue(value, message = 'Expected true') {
        if (value !== true) {
            throw new Error(message);
        }
    },
    
    assertFalse(value, message = 'Expected false') {
        if (value !== false) {
            throw new Error(message);
        }
    },
    
    report() {
        console.log('\n=== Diff Tests ===');
        this.results.forEach(r => {
            const icon = r.status === 'PASS' ? '✓' : '✗';
            console.log(`${icon} ${r.name}`);
            if (r.error) {
                console.log(`  Error: ${r.error}`);
            }
        });
        console.log(`\nTotal: ${this.passed + this.failed}, Passed: ${this.passed}, Failed: ${this.failed}`);
        return this.failed === 0;
    }
};

// テスト対象のモジュールをロード
let diff;
if (typeof window !== 'undefined' && window.TheoryDiff) {
    diff = window.TheoryDiff;
} else if (typeof require !== 'undefined') {
    const path = require('path');
    diff = require(path.join(process.cwd(), 'js', 'diff.js'));
}

// テストデータ
const theory1 = { id: 'theory-001', name: 'Theory 1', description: 'Description 1' };
const theory2 = { id: 'theory-002', name: 'Theory 2', description: 'Description 2' };
const theory3 = { id: 'theory-003', name: 'Theory 3', description: 'Description 3' };
const theory1Modified = { id: 'theory-001', name: 'Theory 1', description: 'Modified Description' };

// ===== テストケース =====

// UT-DIFF-001: 追加検出
TestRunner.test('UT-DIFF-001: 追加された理論を検出する', () => {
    const oldTheories = [theory1, theory2];
    const newTheories = [theory1, theory2, theory3];
    
    const result = diff.computeDiff(oldTheories, newTheories);
    
    TestRunner.assertEqual(result.added.length, 1, 'Should detect 1 added');
    TestRunner.assertEqual(result.added[0].id, 'theory-003', 'Added theory should be theory-003');
    TestRunner.assertEqual(result.removed.length, 0, 'Should have no removed');
    TestRunner.assertEqual(result.modified.length, 0, 'Should have no modified');
});

// UT-DIFF-002: 削除検出
TestRunner.test('UT-DIFF-002: 削除された理論を検出する', () => {
    const oldTheories = [theory1, theory2, theory3];
    const newTheories = [theory1, theory2];
    
    const result = diff.computeDiff(oldTheories, newTheories);
    
    TestRunner.assertEqual(result.removed.length, 1, 'Should detect 1 removed');
    TestRunner.assertEqual(result.removed[0].id, 'theory-003', 'Removed theory should be theory-003');
    TestRunner.assertEqual(result.added.length, 0, 'Should have no added');
    TestRunner.assertEqual(result.modified.length, 0, 'Should have no modified');
});

// UT-DIFF-003: 変更検出
TestRunner.test('UT-DIFF-003: 変更された理論を検出する', () => {
    const oldTheories = [theory1, theory2];
    const newTheories = [theory1Modified, theory2];
    
    const result = diff.computeDiff(oldTheories, newTheories);
    
    TestRunner.assertEqual(result.modified.length, 1, 'Should detect 1 modified');
    TestRunner.assertEqual(result.modified[0].old.id, 'theory-001', 'Modified theory should be theory-001');
    TestRunner.assertEqual(result.modified[0].new.description, 'Modified Description');
    TestRunner.assertEqual(result.added.length, 0, 'Should have no added');
    TestRunner.assertEqual(result.removed.length, 0, 'Should have no removed');
});

// UT-DIFF-004: 変更なし
TestRunner.test('UT-DIFF-004: 同一データは変更なしを返す', () => {
    const oldTheories = [theory1, theory2];
    const newTheories = [theory1, theory2];
    
    const result = diff.computeDiff(oldTheories, newTheories);
    
    TestRunner.assertEqual(result.added.length, 0, 'Should have no added');
    TestRunner.assertEqual(result.removed.length, 0, 'Should have no removed');
    TestRunner.assertEqual(result.modified.length, 0, 'Should have no modified');
});

// UT-DIFF-005: 空データ比較
TestRunner.test('UT-DIFF-005: 空データ同士の比較は変更なし', () => {
    const result = diff.computeDiff([], []);
    
    TestRunner.assertEqual(result.added.length, 0, 'Should have no added');
    TestRunner.assertEqual(result.removed.length, 0, 'Should have no removed');
    TestRunner.assertEqual(result.modified.length, 0, 'Should have no modified');
});

// ===== 追加テスト =====

TestRunner.test('computeDiff: null入力を空配列として扱う', () => {
    const result = diff.computeDiff(null, [theory1]);
    
    TestRunner.assertEqual(result.added.length, 1, 'Should treat null as empty array');
});

TestRunner.test('getChangedFields: 変更されたフィールドを正しく検出', () => {
    const changedFields = diff.getChangedFields(theory1, theory1Modified);
    
    TestRunner.assertTrue(changedFields.includes('description'), 'Should detect description change');
    TestRunner.assertFalse(changedFields.includes('name'), 'Should not include unchanged name');
});

TestRunner.test('getDiffStats: 統計情報を正しく計算', () => {
    const testDiff = {
        added: [theory3],
        removed: [theory2],
        modified: [{ old: theory1, new: theory1Modified }]
    };
    
    const stats = diff.getDiffStats(testDiff);
    
    TestRunner.assertEqual(stats.totalChanges, 3);
    TestRunner.assertEqual(stats.addedCount, 1);
    TestRunner.assertEqual(stats.removedCount, 1);
    TestRunner.assertEqual(stats.modifiedCount, 1);
});

TestRunner.test('formatDiffResult: 差分を文字列にフォーマット', () => {
    const testDiff = {
        added: [theory3],
        removed: [],
        modified: []
    };
    
    const formatted = diff.formatDiffResult(testDiff);
    
    TestRunner.assertTrue(formatted.includes('追加'), 'Should contain "追加"');
    TestRunner.assertTrue(formatted.includes('theory-003'), 'Should contain added theory ID');
});

TestRunner.test('formatDiffResult: 変更なしの場合', () => {
    const emptyDiff = { added: [], removed: [], modified: [] };
    const formatted = diff.formatDiffResult(emptyDiff);
    
    TestRunner.assertEqual(formatted, '変更なし');
});

// レポート出力
if (typeof window !== 'undefined') {
    window.runDiffTests = () => {
        TestRunner.reset();
        TestRunner.report();
        return TestRunner;
    };
} else {
    const success = TestRunner.report();
    process.exit(success ? 0 : 1);
}
