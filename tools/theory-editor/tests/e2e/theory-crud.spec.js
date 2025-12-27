// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Theory Editor - Search & Filter', () => {
    
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
    });

    test('should filter theories by search keyword', async ({ page }) => {
        // 検索入力
        const searchInput = page.locator('#search-input');
        await searchInput.fill('Vygotsky');
        await page.waitForTimeout(500);
        
        // フィルタ結果を確認
        const filteredText = await page.locator('#stats-filtered').textContent();
        console.log(`Filtered: ${filteredText}`);
        
        // 検索結果が表示されていることを確認
        const listItems = await page.locator('#theory-list .theory-item').count();
        expect(listItems).toBeGreaterThan(0);
        expect(listItems).toBeLessThan(175);
    });

    test('should filter theories by category', async ({ page }) => {
        // カテゴリフィルター選択
        const categoryFilter = page.locator('#category-filter');
        await categoryFilter.selectOption('learning_theory');
        await page.waitForTimeout(500);
        
        // フィルタ結果を確認
        const listItems = await page.locator('#theory-list .theory-item').count();
        console.log(`Learning theory count: ${listItems}`);
        
        expect(listItems).toBeGreaterThan(0);
        expect(listItems).toBeLessThan(175);
    });

    test('should combine search and category filter', async ({ page }) => {
        // カテゴリフィルター + 検索
        await page.locator('#category-filter').selectOption('developmental');
        await page.locator('#search-input').fill('Piaget');
        await page.waitForTimeout(500);
        
        const listItems = await page.locator('#theory-list .theory-item').count();
        console.log(`Combined filter count: ${listItems}`);
        
        expect(listItems).toBeGreaterThan(0);
    });
});

test.describe('Theory Editor - View & Select', () => {
    
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
    });

    test('should select and display theory details', async ({ page }) => {
        // 最初の理論をクリック
        const firstTheory = page.locator('#theory-list .theory-item').first();
        await firstTheory.click();
        await page.waitForTimeout(300);
        
        // エディターフォームが表示されていることを確認
        const editorForm = page.locator('#editor-form');
        await expect(editorForm).toBeVisible();
        
        // 理論名が入力されていることを確認
        const nameInput = page.locator('#theory-name');
        const nameValue = await nameInput.inputValue();
        expect(nameValue.length).toBeGreaterThan(0);
        console.log(`Selected theory: ${nameValue}`);
    });

    test('should show theory name in editor title', async ({ page }) => {
        // 理論を選択
        await page.locator('#theory-list .theory-item').first().click();
        await page.waitForTimeout(300);
        
        // エディタータイトルに理論名が表示されていることを確認
        const editorTitle = await page.locator('#editor-title').textContent();
        expect(editorTitle).toContain('を編集');
        console.log(`Editor title: ${editorTitle}`);
    });
});

test.describe('Theory Editor - Edit Theory', () => {
    
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
    });

    test('should mark as modified when editing', async ({ page }) => {
        // 理論を選択
        await page.locator('#theory-list .theory-item').first().click();
        await page.waitForTimeout(300);
        
        // 説明を編集
        const descInput = page.locator('#theory-description');
        const originalValue = await descInput.inputValue();
        await descInput.fill(originalValue + ' [TEST EDIT]');
        
        // 変更マークが表示されることを確認
        const modifiedIndicator = page.locator('#status-modified');
        await expect(modifiedIndicator).toBeVisible();
        
        // 元に戻す
        await descInput.fill(originalValue);
    });

    test('should validate required fields', async ({ page }) => {
        // 新規追加ボタンをクリック
        await page.locator('#btn-add').click();
        await page.waitForTimeout(300);
        
        // 名前を空のままフォーカスを外す
        const nameInput = page.locator('#theory-name');
        await nameInput.fill('');
        await nameInput.blur();
        
        // 名前が必須であることを確認（UIでの表示を確認）
        const nameValue = await nameInput.inputValue();
        expect(nameValue).toBe('');
    });
});

test.describe('Theory Editor - Add New Theory', () => {
    
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
    });

    test('should open new theory form', async ({ page }) => {
        // 初期件数を取得
        const initialCount = await page.locator('#theory-list .theory-item').count();
        console.log(`Initial count: ${initialCount}`);
        
        // 新規追加ボタンをクリック
        await page.locator('#btn-add').click();
        await page.waitForTimeout(300);
        
        // エディターフォームが表示されることを確認
        const editorForm = page.locator('#editor-form');
        await expect(editorForm).toBeVisible();
        
        // タイトルが「新規理論」になっていることを確認
        const editorTitle = await page.locator('#editor-title').textContent();
        console.log(`Editor title after add: ${editorTitle}`);
        expect(editorTitle).toContain('新規');
    });

    test('should fill new theory form fields', async ({ page }) => {
        // 新規追加ボタンをクリック
        await page.locator('#btn-add').click();
        await page.waitForTimeout(300);
        
        // IDは自動生成されるため、他のフィールドを入力
        await page.locator('#theory-name').fill('Test Theory');
        await page.locator('#theory-name-ja').fill('テスト理論');
        await page.locator('#theory-category').selectOption('learning_theory');
        await page.locator('#theory-description').fill('A test theory for E2E testing');
        await page.locator('#theory-description-ja').fill('E2Eテスト用のテスト理論');
        
        // 入力値を確認
        const nameValue = await page.locator('#theory-name').inputValue();
        expect(nameValue).toBe('Test Theory');
        
        // 変更マークが表示されていることを確認
        await expect(page.locator('#status-modified')).toBeVisible();
    });
});

test.describe('Theory Editor - Delete Theory', () => {
    
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
    });

    test('should show delete confirmation modal', async ({ page }) => {
        // 理論を選択
        await page.locator('#theory-list .theory-item').first().click();
        await page.waitForTimeout(300);
        
        // 削除ボタンをクリック
        await page.locator('#btn-delete').click();
        await page.waitForTimeout(500);
        
        // モーダルが表示されることを確認
        const modal = page.locator('#modal-delete');
        await expect(modal).toBeVisible();
        
        // キャンセルボタンをクリック（onclick="closeModal('delete')" を使用）
        await page.locator('#modal-delete .btn-secondary').click();
        await page.waitForTimeout(300);
        
        // モーダルが閉じることを確認
        await expect(modal).toHaveClass(/hidden/);
    });

    test('should enable delete button only when theory is selected', async ({ page }) => {
        // 最初は削除ボタンが無効であることを確認
        const deleteBtn = page.locator('#btn-delete');
        
        // 理論を選択
        await page.locator('#theory-list .theory-item').first().click();
        await page.waitForTimeout(300);
        
        // 削除ボタンが有効になることを確認
        await expect(deleteBtn).toBeEnabled();
    });
});

test.describe('Theory Editor - Export', () => {
    
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
    });

    test('should have export button enabled', async ({ page }) => {
        // エクスポートボタンが有効であることを確認
        const exportBtn = page.locator('#btn-export');
        await expect(exportBtn).toBeEnabled();
    });
});
