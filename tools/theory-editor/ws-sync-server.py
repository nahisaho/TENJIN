#!/usr/bin/env python3
"""
Theory Editor WebSocket Sync Server
リアルタイム同期をサポートするWebSocket + HTTPサーバー

使用方法:
    cd /home/nahisaho/GitHub/TENJIN
    python3 tools/theory-editor/ws-sync-server.py [--port 8081]

エンドポイント:
    WebSocket:
        ws://localhost:8081/ws - リアルタイム同期
    
    HTTP (REST):
        POST /api/graphrag/sync - seed_dataを実行
        GET /api/graphrag/status - 同期ステータス
        POST /api/graphrag/export - theories.jsonを更新
        GET /health - ヘルスチェック
"""

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Set

try:
    from starlette.applications import Starlette
    from starlette.routing import Route, WebSocketRoute
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.websockets import WebSocket, WebSocketDisconnect
    import uvicorn
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install starlette uvicorn websockets")
    sys.exit(1)

# パス設定
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_SOURCE = PROJECT_ROOT / "data" / "theories" / "theories.json"
GRAPHRAG_DATA = (
    PROJECT_ROOT / "References" / "TENGIN-GraphRAG" / "data" / "theories" / "theories.json"
)
GRAPHRAG_ROOT = PROJECT_ROOT / "References" / "TENGIN-GraphRAG"

# 同期ステータス
sync_status = {
    "synced": False,
    "last_sync": None,
    "message": "",
    "connected_clients": 0,
}

# WebSocket接続管理
connected_clients: Set[WebSocket] = set()


async def broadcast(message: dict) -> None:
    """全クライアントにメッセージをブロードキャスト"""
    if not connected_clients:
        return
    
    data = json.dumps(message, ensure_ascii=False)
    disconnected = set()
    
    for client in connected_clients:
        try:
            await client.send_text(data)
        except Exception:
            disconnected.add(client)
    
    # 切断されたクライアントを削除
    for client in disconnected:
        connected_clients.discard(client)
    
    sync_status["connected_clients"] = len(connected_clients)


async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket接続ハンドラ"""
    await websocket.accept()
    connected_clients.add(websocket)
    sync_status["connected_clients"] = len(connected_clients)
    
    print(f"[WS] Client connected. Total: {len(connected_clients)}")
    
    # 初期ステータス送信
    await websocket.send_json({
        "type": "connected",
        "status": sync_status,
        "timestamp": datetime.now().isoformat(),
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")
            
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif msg_type == "theory_update":
                # 理論更新通知を他のクライアントにブロードキャスト
                await broadcast({
                    "type": "theory_update",
                    "theory_id": data.get("theory_id"),
                    "action": data.get("action"),  # create/update/delete
                    "timestamp": datetime.now().isoformat(),
                })
            
            elif msg_type == "sync_request":
                # 同期リクエスト
                await websocket.send_json({
                    "type": "sync_started",
                    "timestamp": datetime.now().isoformat(),
                })
                result = await run_sync()
                await broadcast({
                    "type": "sync_completed",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })
            
            elif msg_type == "export":
                # エクスポート
                theories = data.get("theories", [])
                result = await save_theories(theories)
                await broadcast({
                    "type": "export_completed",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        connected_clients.discard(websocket)
        sync_status["connected_clients"] = len(connected_clients)
        print(f"[WS] Client disconnected. Total: {len(connected_clients)}")


async def run_sync() -> dict:
    """GraphRAGインデックス再作成"""
    global sync_status
    
    try:
        # theories.jsonをGraphRAGにコピー
        if DATA_SOURCE.exists():
            GRAPHRAG_DATA.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(DATA_SOURCE, GRAPHRAG_DATA)
            print(f"✓ Copied {DATA_SOURCE} -> {GRAPHRAG_DATA}")
        
        # seed_dataスクリプトを実行
        process = await asyncio.create_subprocess_exec(
            "uv", "run", "python", "-m", "tengin_mcp.scripts.seed_data",
            cwd=str(GRAPHRAG_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120
            )
        except asyncio.TimeoutError:
            process.kill()
            return {"success": False, "message": "タイムアウト（120秒）"}
        
        if process.returncode == 0:
            sync_status.update({
                "synced": True,
                "last_sync": datetime.now().isoformat(),
                "message": "インデックス再作成完了",
            })
            return {
                "success": True,
                "message": "GraphRAGインデックスを再作成しました",
                "output": stdout.decode()[-500:],
            }
        else:
            sync_status["message"] = f"Error: {stderr.decode()}"
            return {
                "success": False,
                "message": "seed_data実行エラー",
                "error": stderr.decode()[-500:],
            }
    
    except FileNotFoundError:
        return {"success": False, "message": "uvが見つかりません"}
    except Exception as e:
        return {"success": False, "message": str(e)}


async def save_theories(theories: list) -> dict:
    """理論データを保存"""
    try:
        data = {"theories": theories}
        
        # メインデータを保存
        DATA_SOURCE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_SOURCE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # GraphRAGにもコピー
        GRAPHRAG_DATA.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DATA_SOURCE, GRAPHRAG_DATA)
        
        return {
            "success": True,
            "message": f"{len(theories)}件の理論を保存しました",
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# HTTP Endpoints
async def health(request: Request) -> JSONResponse:
    """ヘルスチェック"""
    return JSONResponse({"status": "ok", "websocket_clients": len(connected_clients)})


async def get_status(request: Request) -> JSONResponse:
    """同期ステータス取得"""
    return JSONResponse(sync_status)


async def post_sync(request: Request) -> JSONResponse:
    """同期実行"""
    result = await run_sync()
    status = 200 if result["success"] else 500
    
    # WebSocketクライアントに通知
    await broadcast({
        "type": "sync_completed",
        "result": result,
        "timestamp": datetime.now().isoformat(),
    })
    
    return JSONResponse(result, status_code=status)


async def post_export(request: Request) -> JSONResponse:
    """エクスポート"""
    try:
        body = await request.json()
        theories = body.get("theories", [])
        result = await save_theories(theories)
        status = 200 if result["success"] else 500
        
        # WebSocketクライアントに通知
        await broadcast({
            "type": "export_completed",
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        return JSONResponse(result, status_code=status)
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


# アプリケーション定義
app = Starlette(
    routes=[
        Route("/health", health),
        Route("/api/graphrag/status", get_status),
        Route("/api/graphrag/sync", post_sync, methods=["POST"]),
        Route("/api/graphrag/export", post_export, methods=["POST"]),
        WebSocketRoute("/ws", websocket_endpoint),
    ],
)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Theory Editor WebSocket Sync Server")
    parser.add_argument("--port", type=int, default=8081, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Theory Editor WebSocket Sync Server")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Data source: {DATA_SOURCE}")
    print("")
    print("Endpoints:")
    print(f"  WebSocket: ws://localhost:{args.port}/ws")
    print(f"  HTTP POST: http://localhost:{args.port}/api/graphrag/sync")
    print(f"  HTTP GET:  http://localhost:{args.port}/api/graphrag/status")
    print(f"  HTTP POST: http://localhost:{args.port}/api/graphrag/export")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
