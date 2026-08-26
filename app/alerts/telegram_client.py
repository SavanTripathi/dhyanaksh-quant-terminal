"""
Async HTTP Telegram Bot Client.
Dispatches formatted markdown messages to Telegram Channels and Groups.
"""
from typing import Optional, Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)


class TelegramClient:
    """
    Non-blocking async client for Telegram Bot API.
    """

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, bot_token: Optional[str] = None, default_chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id

    async def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = "Markdown"
    ) -> Dict[str, Any]:
        """
        Sends message to Telegram via async HTTP POST with robust timeout and exception handling.
        """
        target_chat = chat_id or self.default_chat_id
        if not self.bot_token or not target_chat:
            return {
                "success": False,
                "error": "Telegram Bot Token or Chat ID not configured (Simulated Dispatch)"
            }

        url = f"{self.BASE_URL}{self.bot_token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    return {"success": True, "data": resp.json()}
                else:
                    return {
                        "success": False,
                        "status_code": resp.status_code,
                        "error": resp.text
                    }
        except Exception as exc:
            logger.error(f"Telegram dispatch failed: {exc}")
            return {"success": False, "error": str(exc)}
