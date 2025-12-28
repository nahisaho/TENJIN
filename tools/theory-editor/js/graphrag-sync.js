/**
 * GraphRAG Sync Module
 * Theory EditorとGraphRAGの同期機能（WebSocket + HTTP）
 */

const GraphRAGSync = {
    // APIエンドポイント
    SYNC_API_BASE: 'http://localhost:8081',
    WS_ENDPOINT: 'ws://localhost:8081/ws',
    
    // WebSocket接続
    ws: null,
    wsReconnectTimer: null,
    wsReconnectInterval: 5000,
    
    // コールバック
    onUpdate: null,
    onSyncComplete: null,
    onConnectionChange: null,
    
    /**
     * WebSocket接続を開始
     * @param {Object} callbacks - コールバック関数
     */
    connect(callbacks = {}) {
        this.onUpdate = callbacks.onUpdate || null;
        this.onSyncComplete = callbacks.onSyncComplete || null;
        this.onConnectionChange = callbacks.onConnectionChange || null;
        
        this._connectWebSocket();
    },
    
    /**
     * WebSocket接続
     */
    _connectWebSocket() {
        if (this.ws?.readyState === WebSocket.OPEN) {
            return;
        }
        
        try {
            this.ws = new WebSocket(this.WS_ENDPOINT);
            
            this.ws.onopen = () => {
                console.log('[WS] Connected to sync server');
                if (this.wsReconnectTimer) {
                    clearTimeout(this.wsReconnectTimer);
                    this.wsReconnectTimer = null;
                }
                if (this.onConnectionChange) {
                    this.onConnectionChange(true);
                }
            };
            
            this.ws.onclose = () => {
                console.log('[WS] Disconnected from sync server');
                if (this.onConnectionChange) {
                    this.onConnectionChange(false);
                }
                // 自動再接続
                this._scheduleReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('[WS] Error:', error);
            };
            
            this.ws.onmessage = (event) => {
                this._handleMessage(JSON.parse(event.data));
            };
        } catch (error) {
            console.error('[WS] Connection failed:', error);
            this._scheduleReconnect();
        }
    },
    
    /**
     * 再接続スケジュール
     */
    _scheduleReconnect() {
        if (!this.wsReconnectTimer) {
            this.wsReconnectTimer = setTimeout(() => {
                console.log('[WS] Attempting to reconnect...');
                this._connectWebSocket();
            }, this.wsReconnectInterval);
        }
    },
    
    /**
     * WebSocketメッセージ処理
     */
    _handleMessage(data) {
        console.log('[WS] Message:', data.type);
        
        switch (data.type) {
            case 'connected':
                console.log('[WS] Server status:', data.status);
                break;
                
            case 'theory_update':
                if (this.onUpdate) {
                    this.onUpdate(data);
                }
                break;
                
            case 'sync_completed':
            case 'export_completed':
                if (this.onSyncComplete) {
                    this.onSyncComplete(data.result);
                }
                break;
                
            case 'pong':
                // Ping応答
                break;
        }
    },
    
    /**
     * 理論更新を通知
     * @param {string} theoryId - 理論ID
     * @param {string} action - アクション (create/update/delete)
     */
    notifyTheoryUpdate(theoryId, action) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'theory_update',
                theory_id: theoryId,
                action: action,
            }));
        }
    },
    
    /**
     * WebSocket経由で同期リクエスト
     */
    requestSyncViaWebSocket() {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'sync_request' }));
            return true;
        }
        return false;
    },
    
    /**
     * WebSocket経由でエクスポート
     * @param {Array} theories - 理論データ
     */
    exportViaWebSocket(theories) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'export',
                theories: theories,
            }));
            return true;
        }
        return false;
    },
    
    /**
     * 接続状態を取得
     */
    isConnected() {
        return this.ws?.readyState === WebSocket.OPEN;
    },
    
    /**
     * 切断
     */
    disconnect() {
        if (this.wsReconnectTimer) {
            clearTimeout(this.wsReconnectTimer);
            this.wsReconnectTimer = null;
        }
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    },
    
    // ============================================
    // HTTP API (フォールバック)
    // ============================================
    
    /**
     * GraphRAGデータディレクトリにtheories.jsonをエクスポート
     * @param {Object} data - エクスポートするデータ
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async exportToGraphRAG(data) {
        // WebSocket経由を優先
        if (this.exportViaWebSocket(data.theories || [])) {
            return { success: true, message: 'WebSocket経由で送信中...' };
        }
        
        // HTTP API フォールバック
        try {
            const response = await fetch(`${this.SYNC_API_BASE}/api/graphrag/export`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                return { success: false, message: 'APIエラー: ' + response.status };
            }
        } catch (error) {
            return { success: false, message: '同期サーバーに接続できません' };
        }
    },
    
    /**
     * seed_dataスクリプトを実行（バックエンドAPI経由）
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async triggerReindex() {
        // WebSocket経由を優先
        if (this.requestSyncViaWebSocket()) {
            return { success: true, message: 'WebSocket経由で同期開始...' };
        }
        
        // HTTP API フォールバック
        try {
            const response = await fetch(`${this.SYNC_API_BASE}/api/graphrag/sync`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });
            
            if (response.ok) {
                const result = await response.json();
                return { success: true, message: result.message || 'インデックス再作成完了' };
            } else {
                return { success: false, message: 'APIエラー: ' + response.status };
            }
        } catch (error) {
            return { 
                success: false, 
                message: 'GraphRAG同期サーバーが起動していません。\n手動で実行: cd tools/theory-editor && python ws-sync-server.py'
            };
        }
    },
    
    /**
     * 同期ステータスを取得
     * @returns {Promise<{synced: boolean, lastSync: string|null, connected_clients: number}>}
     */
    async getStatus() {
        try {
            const response = await fetch(`${this.SYNC_API_BASE}/api/graphrag/status`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            // サーバーがない場合
        }
        return { synced: false, lastSync: null, connected_clients: 0 };
    }
};

// グローバルに公開
if (typeof window !== 'undefined') {
    window.GraphRAGSync = GraphRAGSync;
}
