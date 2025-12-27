#!/usr/bin/env python3
"""
GraphRAG Sync Server
Theory EditorからGraphRAGへのデータ同期を行う軽量HTTPサーバー

使用方法:
    cd /home/nahisaho/GitHub/TENJIN
    python3 tools/theory-editor/sync-server.py

エンドポイント:
    POST /api/graphrag/sync - seed_dataを実行
    GET /api/graphrag/status - 同期ステータス
    POST /api/graphrag/export - theories.jsonを更新
"""

import http.server
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# パス設定
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_SOURCE = PROJECT_ROOT / "data" / "theories" / "theories.json"
GRAPHRAG_DATA = PROJECT_ROOT / "References" / "TENGIN-GraphRAG" / "data" / "theories" / "theories.json"
GRAPHRAG_ROOT = PROJECT_ROOT / "References" / "TENGIN-GraphRAG"

# 同期ステータス
sync_status = {
    "synced": False,
    "last_sync": None,
    "message": ""
}


class SyncHandler(http.server.BaseHTTPRequestHandler):
    """GraphRAG同期用HTTPハンドラ"""
    
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_OPTIONS(self):
        """CORSプリフライト対応"""
        self._set_headers(200)
    
    def do_GET(self):
        """GETリクエスト処理"""
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/graphrag/status":
            self._set_headers()
            self.wfile.write(json.dumps(sync_status).encode())
        
        elif parsed.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """POSTリクエスト処理"""
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/graphrag/sync":
            self._handle_sync()
        
        elif parsed.path == "/api/graphrag/export":
            self._handle_export()
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def _handle_sync(self):
        """GraphRAGインデックス再作成"""
        global sync_status
        
        try:
            # 1. theories.jsonをGraphRAGにコピー
            if DATA_SOURCE.exists():
                GRAPHRAG_DATA.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(DATA_SOURCE, GRAPHRAG_DATA)
                print(f"✓ Copied {DATA_SOURCE} -> {GRAPHRAG_DATA}")
            
            # 2. seed_dataスクリプトを実行
            result = subprocess.run(
                ["uv", "run", "python", "-m", "tengin_mcp.scripts.seed_data"],
                cwd=str(GRAPHRAG_ROOT),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                sync_status = {
                    "synced": True,
                    "last_sync": datetime.now().isoformat(),
                    "message": "インデックス再作成完了"
                }
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "GraphRAGインデックスを再作成しました",
                    "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
                }).encode())
            else:
                sync_status["message"] = f"Error: {result.stderr}"
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "seed_data実行エラー",
                    "error": result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
                }).encode())
                
        except subprocess.TimeoutExpired:
            self._set_headers(504)
            self.wfile.write(json.dumps({
                "success": False,
                "message": "タイムアウト（120秒）"
            }).encode())
        except FileNotFoundError:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "message": "uvが見つかりません。GraphRAG環境をセットアップしてください。"
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "message": str(e)
            }).encode())
    
    def _handle_export(self):
        """theories.jsonを受け取って保存"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            
            # メインデータを保存
            with open(DATA_SOURCE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # GraphRAGにもコピー
            GRAPHRAG_DATA.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(DATA_SOURCE, GRAPHRAG_DATA)
            
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "message": f"{len(data.get('theories', []))}件の理論を保存しました"
            }).encode())
            
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "success": False,
                "message": str(e)
            }).encode())
    
    def log_message(self, format, *args):
        """ログ出力"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def run_server(port=8081):
    """サーバー起動"""
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, SyncHandler)
    
    print("=" * 50)
    print("GraphRAG Sync Server")
    print("=" * 50)
    print(f"Port: {port}")
    print(f"Data source: {DATA_SOURCE}")
    print(f"GraphRAG data: {GRAPHRAG_DATA}")
    print("")
    print("Endpoints:")
    print(f"  POST http://localhost:{port}/api/graphrag/sync   - Reindex")
    print(f"  GET  http://localhost:{port}/api/graphrag/status - Status")
    print(f"  POST http://localhost:{port}/api/graphrag/export - Export")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print("")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    run_server(port)
