import asyncio
import aiohttp
import pytest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from server import create_app


class TestClipboard(AioHTTPTestCase):
    async def get_application(self):
        return create_app()

    async def test_post_clipboard_valid(self):
        payload = {"items": {"Betrag": "€ 100", "IBAN": "AT1234"}}
        resp = await self.client.request("POST", "/clipboard", json=payload)
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"

    async def test_post_clipboard_missing_items(self):
        resp = await self.client.request("POST", "/clipboard", json={"foo": "bar"})
        assert resp.status == 400

    async def test_post_clipboard_items_not_dict(self):
        resp = await self.client.request("POST", "/clipboard", json={"items": "string"})
        assert resp.status == 400

    async def test_websocket_receives_update(self):
        async with self.client.ws_connect("/ws") as ws:
            # Drain any initial state message sent on connect
            try:
                import asyncio
                await asyncio.wait_for(ws.receive_json(), timeout=0.1)
            except asyncio.TimeoutError:
                pass

            payload = {"items": {"Key": "Value"}}
            resp = await self.client.request("POST", "/clipboard", json=payload)
            assert resp.status == 200

            msg = await ws.receive_json()
            assert msg["type"] == "update"
            assert msg["items"] == {"Key": "Value"}

    async def test_websocket_receives_current_state_on_connect(self):
        # First, set some data
        payload = {"items": {"Existing": "Data"}}
        await self.client.request("POST", "/clipboard", json=payload)

        # Then connect — should get current state
        async with self.client.ws_connect("/ws") as ws:
            msg = await ws.receive_json()
            assert msg["type"] == "update"
            assert msg["items"] == {"Existing": "Data"}
