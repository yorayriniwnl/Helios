"""In-memory WebSocket connection service.

Provides simple connect/disconnect and async broadcast utilities using an in-memory list.
Keep this minimal and transport-agnostic (expects objects with an async `send_text()` method).
"""
from typing import List, Any, Optional
import asyncio

_clients: List[Any] = []
_loop: Optional[asyncio.AbstractEventLoop] = None


def connect(client: Any) -> None:
    """Register a client connection and capture the running event loop."""
    global _loop
    try:
        _loop = asyncio.get_running_loop()
    except RuntimeError:
        # no running loop in this context; keep existing loop if any
        pass
    if client not in _clients:
        _clients.append(client)


def disconnect(client: Any) -> None:
    """Unregister a client connection."""
    try:
        _clients.remove(client)
    except ValueError:
        pass


async def broadcast(message: str) -> None:
    """Broadcast a text message to all connected clients.

    Silently ignores errors to keep the broadcaster robust.
    """
    # iterate over a snapshot to avoid modification during iteration
    for client in list(_clients):
        try:
            send = getattr(client, "send_text", None)
            if callable(send):
                await send(message)
            else:
                if callable(client):
                    client(message)
        except Exception:
            try:
                _clients.remove(client)
            except Exception:
                pass


def broadcast_sync(message: str) -> None:
    """Schedule broadcast(message) to run on the app's event loop from sync code."""
    if _loop is None:
        return
    try:
        asyncio.run_coroutine_threadsafe(broadcast(message), _loop)
    except Exception:
        # best-effort: swallow errors to avoid breaking callers
        pass
