"""
Async Outbound Webhook Client.
Dispatches structured JSON payloads to external webhook receivers.
"""
from typing import Optional, Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)


class WebhookClient:
    """
    Non-blocking async HTTP client for outbound JSON webhooks.
    """

    def __init__(self, webhook_url: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.webhook_secret = webhook_secret

    async def send_webhook(
        self,
        payload: Dict[str, Any],
        target_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches payload to webhook endpoint with headers and timeout.
        """
        url = target_url or self.webhook_url
        if not url:
            return {
                "success": False,
                "error": "Webhook URL not configured (Simulated Dispatch)"
            }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "HTF-Zone-Scanner-Terminal/3.0"
        }
        if self.webhook_secret:
            headers["X-Webhook-Secret"] = self.webhook_secret

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if 200 <= resp.status_code < 300:
                    return {"success": True, "status_code": resp.status_code}
                else:
                    return {
                        "success": False,
                        "status_code": resp.status_code,
                        "error": resp.text
                    }
        except Exception as exc:
            logger.error(f"Webhook dispatch failed: {exc}")
            return {"success": False, "error": str(exc)}
