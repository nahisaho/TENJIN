// @ts-check
const { defineConfig } = require('@playwright/test');
const path = require('path');

// プロジェクトルートを動的に検出
const projectRoot = path.resolve(__dirname, '../..');

module.exports = defineConfig({
    testDir: './tests/e2e',
    fullyParallel: false,
    forbidOnly: !!process.env.CI,
    retries: 0,
    workers: 1,
    reporter: 'list',
    use: {
        baseURL: 'http://localhost:8080',
        trace: 'on-first-retry',
        headless: true,
    },
    webServer: {
        command: 'python3 -m http.server 8080',
        cwd: projectRoot,
        url: 'http://localhost:8080',
        reuseExistingServer: true,
        timeout: 10000,
    },
});
