from aiohttp import web

clients = set()
current_items = {}


async def handle_clipboard(request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400)

    items = data.get("items")
    if not isinstance(items, dict):
        return web.json_response({"error": "items must be a dict"}, status=400)

    global current_items
    current_items = items

    # Push to all WebSocket clients
    msg = {"type": "update", "items": items}
    for ws in set(clients):
        try:
            await ws.send_json(msg)
        except Exception:
            clients.discard(ws)

    return web.json_response({"status": "ok"}, headers={"Access-Control-Allow-Origin": "*"})


async def handle_ws(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)

    # Send current state on connect
    if current_items:
        await ws.send_json({"type": "update", "items": current_items})

    try:
        async for msg in ws:
            pass  # We don't expect client messages
    finally:
        clients.discard(ws)

    return ws


def create_app():
    app = web.Application()
    app.router.add_post("/clipboard", handle_clipboard)
    app.router.add_get("/ws", handle_ws)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="127.0.0.1", port=52780)
