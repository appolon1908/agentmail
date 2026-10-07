import hashlib
import hmac
import json
from typing import Any

import httpx

from .config import Settings
from .models import CanonicalEmailEvent


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def canonicalize_agentmail_event(payload: dict[str, Any]) -> CanonicalEmailEvent:
    message = _mapping(payload.get("message"))
    thread = _mapping(payload.get("thread"))

    return CanonicalEmailEvent(
        event_type=str(payload.get("eventType") or payload.get("event_type") or payload.get("type") or "unknown"),
        event_id=_optional_str(payload.get("eventId") or payload.get("event_id") or payload.get("id")),
        inbox_id=_optional_str(message.get("inbox_id") or message.get("inboxId") or payload.get("inbox_id")),
        message_id=_optional_str(message.get("message_id") or message.get("messageId") or message.get("id")),
        thread_id=_optional_str(thread.get("thread_id") or thread.get("threadId") or thread.get("id")),
        occurred_at=_optional_str(payload.get("timestamp") or payload.get("created_at")),
        payload=payload,
    )


def _optional_str(value: Any) -> str | None:
    return None if value is None else str(value)


def _signature(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


async def forward_to_klyrow(settings: Settings, event: CanonicalEmailEvent) -> bool:
    if not settings.klyrow_callback_url:
        return False

    body = json.dumps(event.model_dump(mode="json"), separators=(",", ":"), sort_keys=True).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Codestra-Provider": "agentmail",
        "X-Codestra-Schema": event.schema_version,
    }
    if settings.klyrow_callback_hmac_secret:
        headers["X-Codestra-Signature-SHA256"] = _signature(settings.klyrow_callback_hmac_secret, body)

    async with httpx.AsyncClient(timeout=settings.klyrow_callback_timeout_seconds) as client:
        response = await client.post(settings.klyrow_callback_url, content=body, headers=headers)
        response.raise_for_status()
    return True
