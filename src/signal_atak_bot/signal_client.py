import asyncio
import json
import logging

import aiohttp

logger = logging.getLogger(__name__)


class SignalClient:
    """Connects to signal-cli daemon via TCP (receive) and HTTP (send)."""

    def __init__(self, tcp_host: str, tcp_port: int, http_url: str, account: str):
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.http_url = http_url
        self.account = account
        self._rpc_id = 0

    async def listen(self):
        """Connect to signal-cli TCP socket and yield incoming messages."""
        reader, writer = await asyncio.open_connection(self.tcp_host, self.tcp_port)
        logger.info("Connected to signal-cli at %s:%s", self.tcp_host, self.tcp_port)

        # Subscribe to receive messages
        self._rpc_id += 1
        subscribe = json.dumps({
            "jsonrpc": "2.0",
            "method": "subscribeReceive",
            "id": self._rpc_id,
        }) + "\n"
        writer.write(subscribe.encode())
        await writer.drain()

        try:
            async for line in reader:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON from signal-cli: %s", line[:200])
                    continue

                # Incoming messages arrive as JSON-RPC notifications (no "id")
                if "method" in data and data["method"] == "receive":
                    params = data.get("params", {})
                    envelope = params.get("envelope", {})
                    yield envelope
                elif "result" in data:
                    logger.debug("RPC response: %s", data)
                elif "error" in data:
                    logger.warning("RPC error: %s", data["error"])
        finally:
            writer.close()
            await writer.wait_closed()

    async def send_message(self, recipient: str, message: str) -> dict:
        """Send a message via signal-cli HTTP JSON-RPC."""
        self._rpc_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": "send",
            "params": {
                "recipient": [recipient],
                "message": message,
                "account": self.account,
            },
            "id": self._rpc_id,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.http_url}/api/v1/rpc",
                json=payload,
            ) as resp:
                result = await resp.json()
                if "error" in result:
                    logger.error("Failed to send: %s", result["error"])
                return result

    async def send_group_message(self, group_id: str, message: str) -> dict:
        """Send a message to a group via signal-cli HTTP JSON-RPC."""
        self._rpc_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": "send",
            "params": {
                "groupId": group_id,
                "message": message,
                "account": self.account,
            },
            "id": self._rpc_id,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.http_url}/api/v1/rpc",
                json=payload,
            ) as resp:
                result = await resp.json()
                if "error" in result:
                    logger.error("Failed to send to group: %s", result["error"])
                return result
