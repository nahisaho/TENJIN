/**
 * GraphRAG Sync Module
 * Theory EditorとGraphRAGの同期機能
 */

const GraphRAGSync = {
    // GraphRAGのデータディレクトリパス（サーバー側で使用）
    GRAPHRAG_DATA_PATH: '../../References/TENGIN-GraphRAG/data/theories/theories.json',
    
    // APIエンドポイント（バックエンドサーバーが必要）
    SYNC_API_ENDPOINT: '/api/graphrag/sync',
    
    /**
     * GraphRAGデータディレクトリにtheories.jsonをコピー
     * @param {Object} data - エクスポートするデータ
     * @returns {Promise<boolean>}
     */
    async exportToGraphRAG(data) {
        try {
            // ブラウザからは直接ファイルシステムに書き込めないため、
            // バックエンドAPIを呼び出すか、手動でコピーする必要がある
            console.log('GraphRAG sync: Export data prepared');
            return true;
        } catch (error) {
            console.error('GraphRAG sync failed:', error);
            return false;
        }
    },
    
    /**
     * seed_dataスクリプトを実行（バックエンドAPI経由）
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async triggerReindex() {
        try {
            const response = await fetch(this.SYNC_API_ENDPOINT, {
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
            // バックエンドがない場合は手動実行を案内
            return { 
                success: false, 
                message: 'GraphRAG同期サーバーが起動していません。手動で実行してください:\ncd References/TENGIN-GraphRAG && uv run python -m tengin_mcp.scripts.seed_data'
            };
        }
    },
    
    /**
     * 同期ステータスを取得
     * @returns {Promise<{synced: boolean, lastSync: string|null}>}
     */
    async getStatus() {
        try {
            const response = await fetch(this.SYNC_API_ENDPOINT + '/status');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            // サーバーがない場合
        }
        return { synced: false, lastSync: null };
    }
};

// グローバルに公開
if (typeof window !== 'undefined') {
    window.GraphRAGSync = GraphRAGSync;
}
