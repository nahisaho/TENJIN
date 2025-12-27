// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Theory Editor - Data Loading', () => {
    
    test('should load theories from JSON file', async ({ page }) => {
        // コンソールログを収集
        const logs = [];
        page.on('console', msg => {
            logs.push(`${msg.type()}: ${msg.text()}`);
        });
        
        // ページエラーを収集
        const errors = [];
        page.on('pageerror', err => {
            errors.push(err.message);
        });
        
        // ページを開く
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        
        // ページが読み込まれるまで待機
        await page.waitForLoadState('networkidle');
        
        // 追加の待機（データ読み込み用）
        await page.waitForTimeout(2000);
        
        // コンソールログを出力
        console.log('\n=== Console Logs ===');
        logs.forEach(log => console.log(log));
        
        if (errors.length > 0) {
            console.log('\n=== Page Errors ===');
            errors.forEach(err => console.log(err));
        }
        
        // 理論リストの件数を取得
        const statsText = await page.locator('#stats-count').textContent();
        console.log(`\nStats: ${statsText}`);
        
        // ステータスメッセージを確認
        const statusText = await page.locator('#status-message').textContent();
        console.log(`Status: ${statusText}`);
        
        // 理論リストのアイテム数をカウント
        const listItems = await page.locator('#theory-list .theory-item').count();
        console.log(`List items: ${listItems}`);
        
        // スクリーンショットを保存
        await page.screenshot({ path: 'tests/e2e/screenshot-initial.png' });
        
        // 175件の理論が読み込まれているはず
        expect(listItems).toBeGreaterThan(0);
    });
    
    test('should debug fetch paths', async ({ page }) => {
        // リクエストを監視
        const requests = [];
        page.on('request', req => {
            if (req.url().includes('theories.json')) {
                requests.push({ url: req.url(), method: req.method() });
            }
        });
        
        const responses = [];
        page.on('response', res => {
            if (res.url().includes('theories.json')) {
                responses.push({ url: res.url(), status: res.status() });
            }
        });
        
        await page.goto('http://localhost:8080/tools/theory-editor/index.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(3000);
        
        console.log('\n=== Fetch Requests ===');
        requests.forEach(r => console.log(`${r.method} ${r.url}`));
        
        console.log('\n=== Fetch Responses ===');
        responses.forEach(r => console.log(`${r.status} ${r.url}`));
        
        // 少なくとも1つのリクエストが成功しているはず
        const successfulResponse = responses.find(r => r.status === 200);
        if (!successfulResponse) {
            console.log('\n⚠️ No successful response for theories.json');
        }
    });
});
