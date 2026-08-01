from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

try:
    from backend.app.services.websocket_service import connect as ws_connect, disconnect as ws_disconnect, broadcast as ws_broadcast
except Exception:
    from ...services.websocket_service import connect as ws_connect, disconnect as ws_disconnect, broadcast as ws_broadcast


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """Accept websocket connections and broadcast received messages using websocket_service."""
    await websocket.accept()
    ws_connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_broadcast(data)
    except WebSocketDisconnect:
        ws_disconnect(websocket)
