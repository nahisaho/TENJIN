/**
 * storage.test.js - ストレージモジュールのユニットテスト
 * 
 * テストケース: UT-STOR-001〜004
 * 要件: FR-VERSION-001, FR-VERSION-005
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
        console.log('\n=== Storage Tests ===');
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

// LocalStorageのモック（Node.js環境用）
if (typeof localStorage === 'undefined') {
    global.localStorage = {
        _data: {},
        getItem(key) {
            return this._data[key] || null;
        },
        setItem(key, value) {
            this._data[key] = value;
        },
        removeItem(key) {
            delete this._data[key];
        },
        clear() {
            this._data = {};
        }
    };
}

// テスト対象のモジュールをロード
let storage;
if (typeof window !== 'undefined' && window.TheoryStorage) {
    storage = window.TheoryStorage;
} else if (typeof require !== 'undefined') {
    const path = require('path');
    storage = require(path.join(process.cwd(), 'js', 'storage.js'));
}

// テストデータ
function createTestVersion(id, description) {
    return {
        id: id,
        timestamp: new Date().toISOString(),
        description: description,
        theoryCount: 1,
        data: {
            metadata: {},
            theories: [{ id: 'theory-001', name: 'Test' }]
        }
    };
}

// テスト前のクリーンアップ
function cleanup() {
    localStorage.clear();
}

// ===== テストケース =====

// UT-STOR-001: 保存と読み込み
TestRunner.test('UT-STOR-001: 保存したデータを正しく読み込める', () => {
    cleanup();
    
    const versions = [
        createTestVersion(1, 'Version 1'),
        createTestVersion(2, 'Version 2')
    ];
    
    const saveResult = storage.saveVersionsToStorage(versions);
    TestRunner.assertTrue(saveResult.success, 'Save should succeed');
    
    const loaded = storage.loadVersionsFromStorage();
    TestRunner.assertEqual(loaded.length, 2, 'Should load 2 versions');
    TestRunner.assertEqual(loaded[0].description, 'Version 1');
    TestRunner.assertEqual(loaded[1].description, 'Version 2');
});

// UT-STOR-002: 上限超過時の削除
TestRunner.test('UT-STOR-002: 上限超過時に古いバージョンを削除する', () => {
    // 51件のバージョンを作成
    const versions = [];
    for (let i = 0; i < 51; i++) {
        versions.push(createTestVersion(i, `Version ${i}`));
    }
    
    const limited = storage.enforceVersionLimit(versions, 50);
    
    TestRunner.assertEqual(limited.length, 50, 'Should limit to 50 versions');
    TestRunner.assertEqual(limited[0].description, 'Version 0', 'First version should be preserved');
});

// UT-STOR-003: 空の読み込み
TestRunner.test('UT-STOR-003: 空のLocalStorageから読み込むと空配列を返す', () => {
    cleanup();
    
    const loaded = storage.loadVersionsFromStorage();
    
    TestRunner.assertEqual(loaded.length, 0, 'Should return empty array');
    TestRunner.assertTrue(Array.isArray(loaded), 'Should be an array');
});

// UT-STOR-004: 不正データ読み込み
TestRunner.test('UT-STOR-004: 不正なJSONデータの場合は空配列を返す', () => {
    cleanup();
    localStorage.setItem(storage.CONSTANTS.VERSION_STORAGE_KEY, 'invalid json {{{');
    
    const loaded = storage.loadVersionsFromStorage();
    
    TestRunner.assertEqual(loaded.length, 0, 'Should return empty array for invalid JSON');
    TestRunner.assertTrue(Array.isArray(loaded), 'Should be an array');
});

// ===== 追加テスト =====

TestRunner.test('createVersion: 正しい形式のバージョンを作成', () => {
    const data = {
        metadata: { version: '1.0' },
        theories: [{ id: 'theory-001', name: 'Test' }]
    };
    
    const version = storage.createVersion(data, 'Test Version');
    
    TestRunner.assertTrue(typeof version.id === 'number', 'ID should be a number');
    TestRunner.assertTrue(typeof version.timestamp === 'string', 'Timestamp should be a string');
    TestRunner.assertEqual(version.description, 'Test Version');
    TestRunner.assertEqual(version.theoryCount, 1);
    TestRunner.assertEqual(version.data.theories.length, 1);
});

TestRunner.test('enforceVersionLimit: 上限以下の場合はそのまま返す', () => {
    const versions = [
        createTestVersion(1, 'V1'),
        createTestVersion(2, 'V2')
    ];
    
    const result = storage.enforceVersionLimit(versions, 50);
    
    TestRunner.assertEqual(result.length, 2, 'Should keep all versions');
});

TestRunner.test('enforceVersionLimit: null入力は空配列を返す', () => {
    const result = storage.enforceVersionLimit(null, 50);
    
    TestRunner.assertEqual(result.length, 0, 'Should return empty array for null');
});

TestRunner.test('removeVersion: 指定IDのバージョンを削除', () => {
    const versions = [
        createTestVersion(1, 'V1'),
        createTestVersion(2, 'V2'),
        createTestVersion(3, 'V3')
    ];
    
    const result = storage.removeVersion(versions, 2);
    
    TestRunner.assertEqual(result.length, 2, 'Should have 2 versions');
    TestRunner.assertFalse(result.some(v => v.id === 2), 'Version 2 should be removed');
});

TestRunner.test('getStorageUsage: 使用量を取得', () => {
    cleanup();
    const versions = [createTestVersion(1, 'Test')];
    storage.saveVersionsToStorage(versions);
    
    const usage = storage.getStorageUsage();
    
    TestRunner.assertTrue(usage.used > 0, 'Used should be greater than 0');
    TestRunner.assertTrue(typeof usage.usedKB === 'string', 'usedKB should be a string');
});

TestRunner.test('clearVersionHistory: 履歴をクリア', () => {
    cleanup();
    const versions = [createTestVersion(1, 'Test')];
    storage.saveVersionsToStorage(versions);
    
    const result = storage.clearVersionHistory();
    TestRunner.assertTrue(result.success, 'Clear should succeed');
    
    const loaded = storage.loadVersionsFromStorage();
    TestRunner.assertEqual(loaded.length, 0, 'Should be empty after clear');
});

// レポート出力
if (typeof window !== 'undefined') {
    window.runStorageTests = () => {
        TestRunner.reset();
        TestRunner.report();
        return TestRunner;
    };
} else {
    cleanup();
    const success = TestRunner.report();
    process.exit(success ? 0 : 1);
}
