import json
from typing import Any

from fastapi import HTTPException, Request
from svix.webhooks import Webhook, WebhookVerificationError

from .config import Settings


async def verify_agentmail_webhook(request: Request, settings: Settings) -> dict[str, Any]:
    if not settings.webhook_secret:
        raise HTTPException(status_code=503, detail="webhook_verification_not_configured")

    body = await request.body()
    try:
        verified = Webhook(settings.webhook_secret).verify(body, dict(request.headers))
    except WebhookVerificationError as exc:
        raise HTTPException(status_code=401, detail="invalid_webhook_signature") from exc

    if isinstance(verified, dict):
        return verified
    if isinstance(verified, str):
        parsed = json.loads(verified)
        if isinstance(parsed, dict):
            return parsed
    raise HTTPException(status_code=400, detail="invalid_webhook_payload")
