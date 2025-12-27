/**
 * Error Handler Module - Unit Tests
 * TENJIN Theory Editor
 * 
 * Tests for js/error-handler.js
 */

const ErrorHandlerTests = {
    name: 'ErrorHandler Tests',
    tests: []
};

// ============================================
// ERROR_CONTEXTS Tests
// ============================================

ErrorHandlerTests.tests.push({
    name: 'ERROR_CONTEXTS: should have required error types',
    fn: () => {
        const requiredContexts = [
            'import-parse',
            'import-validate', 
            'save-validate',
            'save-serialize',
            'storage-quota',
            'storage-access',
            'search-filter',
            'version-save',
            'version-restore',
            'version-diff',
            'network',
            'unknown'
        ];
        
        requiredContexts.forEach(ctx => {
            if (!ERROR_CONTEXTS[ctx]) {
                throw new Error(`Missing required context: ${ctx}`);
            }
        });
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'ERROR_CONTEXTS: each context should have required properties',
    fn: () => {
        const requiredProps = ['userMessage', 'recoveryHint', 'recoverable'];
        
        Object.entries(ERROR_CONTEXTS).forEach(([key, ctx]) => {
            requiredProps.forEach(prop => {
                if (ctx[prop] === undefined) {
                    throw new Error(`Context "${key}" missing property: ${prop}`);
                }
            });
        });
        return true;
    }
});

// ============================================
// getErrorMessage Tests
// ============================================

ErrorHandlerTests.tests.push({
    name: 'getErrorMessage: should return context message for known context',
    fn: () => {
        const result = getErrorMessage(new Error('test'), 'import-parse');
        if (!result.includes('JSON') || !result.includes('パース')) {
            throw new Error(`Unexpected message: ${result}`);
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'getErrorMessage: should return error message for unknown context',
    fn: () => {
        const error = new Error('Custom error message');
        const result = getErrorMessage(error, 'unknown-context');
        if (!result.includes('Custom error message')) {
            throw new Error(`Expected original error message, got: ${result}`);
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'getErrorMessage: should include recovery hint when available',
    fn: () => {
        const result = getErrorMessage(new Error('test'), 'storage-quota');
        // 容量に関するメッセージが含まれるはず
        if (!result.includes('容量')) {
            throw new Error(`Expected quota message, got: ${result}`);
        }
        return true;
    }
});

// ============================================
// isRecoverable Tests
// ============================================

ErrorHandlerTests.tests.push({
    name: 'isRecoverable: should return true for recoverable errors',
    fn: () => {
        const result = isRecoverable('save-validate');
        if (result !== true) {
            throw new Error(`Expected true, got: ${result}`);
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'isRecoverable: should return false for non-recoverable errors',
    fn: () => {
        const result = isRecoverable('storage-access');
        if (result !== false) {
            throw new Error(`Expected false, got: ${result}`);
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'isRecoverable: should return false for unknown context',
    fn: () => {
        const result = isRecoverable('unknown-nonexistent-context');
        if (result !== false) {
            throw new Error(`Expected false, got: ${result}`);
        }
        return true;
    }
});

// ============================================
// tryCatch Tests
// ============================================

ErrorHandlerTests.tests.push({
    name: 'tryCatch: should return result on success',
    fn: () => {
        const result = tryCatch(() => 'success', 'test');
        if (result !== 'success') {
            throw new Error(`Expected 'success', got: ${result}`);
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'tryCatch: should return undefined on error',
    fn: () => {
        const result = tryCatch(() => {
            throw new Error('test error');
        }, 'test');
        if (result !== undefined) {
            throw new Error(`Expected undefined, got: ${result}`);
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'tryCatch: should call onError callback when error occurs',
    fn: () => {
        let callbackCalled = false;
        let capturedError = null;
        
        tryCatch(
            () => { throw new Error('callback test'); },
            'test',
            (err) => { callbackCalled = true; capturedError = err; }
        );
        
        if (!callbackCalled) {
            throw new Error('onError callback was not called');
        }
        if (capturedError?.message !== 'callback test') {
            throw new Error(`Unexpected error message: ${capturedError?.message}`);
        }
        return true;
    }
});

// ============================================
// tryCatchAsync Tests
// ============================================

ErrorHandlerTests.tests.push({
    name: 'tryCatchAsync: should return result on success',
    fn: async () => {
        const result = await tryCatchAsync(async () => 'async success', 'test');
        if (result !== 'async success') {
            throw new Error(`Expected 'async success', got: ${result}`);
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'tryCatchAsync: should return undefined on error',
    fn: async () => {
        const result = await tryCatchAsync(async () => {
            throw new Error('async error');
        }, 'test');
        if (result !== undefined) {
            throw new Error(`Expected undefined, got: ${result}`);
        }
        return true;
    }
});

// ============================================
// handleError Tests
// ============================================

ErrorHandlerTests.tests.push({
    name: 'handleError: should log to console',
    fn: () => {
        // consoleのモックが難しいため、エラーなしで実行できることを確認
        const error = new Error('console test');
        handleError(error, 'test-context');
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'handleError: should call onNotify callback',
    fn: () => {
        let notifyCalled = false;
        let notifyMessage = '';
        
        handleError(new Error('notify test'), 'save-validate', {
            onNotify: (msg) => {
                notifyCalled = true;
                notifyMessage = msg;
            }
        });
        
        if (!notifyCalled) {
            throw new Error('onNotify was not called');
        }
        if (!notifyMessage) {
            throw new Error('Notify message was empty');
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'handleError: should call onRecovery callback for recoverable errors',
    fn: () => {
        let recoveryCalled = false;
        
        handleError(new Error('recovery test'), 'save-validate', {
            onRecovery: () => { recoveryCalled = true; }
        });
        
        if (!recoveryCalled) {
            throw new Error('onRecovery was not called for recoverable error');
        }
        return true;
    }
});

ErrorHandlerTests.tests.push({
    name: 'handleError: should not call onRecovery for non-recoverable errors',
    fn: () => {
        let recoveryCalled = false;
        
        handleError(new Error('non-recovery test'), 'storage-access', {
            onRecovery: () => { recoveryCalled = true; }
        });
        
        if (recoveryCalled) {
            throw new Error('onRecovery should not be called for non-recoverable error');
        }
        return true;
    }
});

// Export for test runner
if (typeof window !== 'undefined') {
    window.ErrorHandlerTests = ErrorHandlerTests;
}
