/**
 * validation.test.js - バリデーションモジュールのユニットテスト
 * 
 * テストケース: UT-VAL-001〜005
 * 要件: FR-ERROR-002
 */

// テストフレームワーク（シンプルな自作版）
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
        console.log('\n=== Validation Tests ===');
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
// ブラウザ環境では window.TheoryValidation、Node.js環境では require
let validation;
if (typeof window !== 'undefined' && window.TheoryValidation) {
    validation = window.TheoryValidation;
} else if (typeof require !== 'undefined') {
    const path = require('path');
    validation = require(path.join(process.cwd(), 'js', 'validation.js'));
}

// ===== テストケース =====

// UT-VAL-001: 有効な理論データ
TestRunner.test('UT-VAL-001: 有効な理論データはisValid: trueを返す', () => {
    const validTheory = {
        id: 'theory-001',
        name: 'Test Theory',
        name_ja: 'テスト理論',
        category: 'learning_theory',
        priority: 4,
        theorists: ['Author'],
        description: 'Test description',
        key_principles: ['Principle 1']
    };
    
    const result = validation.validateTheory(validTheory);
    TestRunner.assertTrue(result.isValid, 'Valid theory should return isValid: true');
    TestRunner.assertEqual(result.errors.length, 0, 'Valid theory should have no errors');
});

// UT-VAL-002: ID欠落
TestRunner.test('UT-VAL-002: ID欠落時はエラーを返す', () => {
    const theoryWithoutId = {
        name: 'Test Theory',
        category: 'learning_theory'
    };
    
    const result = validation.validateTheory(theoryWithoutId);
    TestRunner.assertFalse(result.isValid, 'Theory without ID should be invalid');
    TestRunner.assertTrue(
        result.errors.some(e => e.field === 'id'),
        'Should contain ID error'
    );
});

// UT-VAL-003: 名前欠落（両方）
TestRunner.test('UT-VAL-003: 名前欠落（英語・日本語両方）時はエラーを返す', () => {
    const theoryWithoutName = {
        id: 'theory-001',
        category: 'learning_theory'
    };
    
    const result = validation.validateTheory(theoryWithoutName);
    TestRunner.assertFalse(result.isValid, 'Theory without name should be invalid');
    TestRunner.assertTrue(
        result.errors.some(e => e.field === 'name'),
        'Should contain name error'
    );
});

// UT-VAL-004: 英語名のみ
TestRunner.test('UT-VAL-004: 英語名のみでも有効', () => {
    const theoryWithEnglishName = {
        id: 'theory-001',
        name: 'Test Theory',
        name_ja: null,
        category: 'learning_theory'
    };
    
    const result = validation.validateTheory(theoryWithEnglishName);
    TestRunner.assertTrue(result.isValid, 'Theory with only English name should be valid');
});

// UT-VAL-005: 日本語名のみ
TestRunner.test('UT-VAL-005: 日本語名のみでも有効', () => {
    const theoryWithJapaneseName = {
        id: 'theory-001',
        name: null,
        name_ja: 'テスト理論',
        category: 'learning_theory'
    };
    
    const result = validation.validateTheory(theoryWithJapaneseName);
    TestRunner.assertTrue(result.isValid, 'Theory with only Japanese name should be valid');
});

// ===== 追加テスト: validateImportData =====

TestRunner.test('validateImportData: 有効なデータ', () => {
    const validData = {
        metadata: {},
        theories: [{ id: 'theory-001', name: 'Test' }]
    };
    
    TestRunner.assertTrue(
        validation.validateImportData(validData),
        'Valid import data should return true'
    );
});

TestRunner.test('validateImportData: theories配列がないデータ', () => {
    const invalidData = { metadata: {} };
    
    TestRunner.assertFalse(
        validation.validateImportData(invalidData),
        'Data without theories array should return false'
    );
});

TestRunner.test('validateImportData: 空のtheories配列', () => {
    const emptyData = { theories: [] };
    
    TestRunner.assertFalse(
        validation.validateImportData(emptyData),
        'Empty theories array should return false'
    );
});

TestRunner.test('validateImportData: nullデータ', () => {
    TestRunner.assertFalse(
        validation.validateImportData(null),
        'Null data should return false'
    );
});

// ===== 追加テスト: validateRequiredFields =====

TestRunner.test('validateRequiredFields: 全フィールドあり', () => {
    const theory = {
        id: 'theory-001',
        name: 'Test',
        category: 'learning_theory'
    };
    
    const result = validation.validateRequiredFields(theory, ['id', 'name', 'category']);
    TestRunner.assertTrue(result.isValid, 'All required fields present should be valid');
    TestRunner.assertEqual(result.missingFields.length, 0);
});

TestRunner.test('validateRequiredFields: フィールド欠落', () => {
    const theory = {
        id: 'theory-001'
    };
    
    const result = validation.validateRequiredFields(theory, ['id', 'name', 'category']);
    TestRunner.assertFalse(result.isValid, 'Missing fields should be invalid');
    TestRunner.assertTrue(result.missingFields.includes('name'));
    TestRunner.assertTrue(result.missingFields.includes('category'));
});

// レポート出力
if (typeof window !== 'undefined') {
    // ブラウザ環境
    window.runValidationTests = () => {
        TestRunner.reset();
        // テストを再実行
        TestRunner.report();
        return TestRunner;
    };
} else {
    // Node.js環境
    const success = TestRunner.report();
    process.exit(success ? 0 : 1);
}
