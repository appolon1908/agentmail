import logging
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status

from .config import Settings, get_settings
from .klyrow import canonicalize_agentmail_event, forward_to_klyrow
from .models import InboxCreate, ReplyMessageRequest, SendMessageRequest
from .policy import EffectDenied, enforce_delivery
from .provider import AgentMailProvider
from .webhooks import verify_agentmail_webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codestra-agentmail")

app = FastAPI(
    title="Codestra AgentMail",
    version="0.1.0",
    description="Fail-closed AgentMail provider service for Codestra and Klyrow.",
)


def settings_dep() -> Settings:
    return get_settings()


SettingsDep = Annotated[Settings, Depends(settings_dep)]


def provider(settings: Settings) -> AgentMailProvider:
    if not settings.provider_configured:
        raise HTTPException(status_code=503, detail="agentmail_provider_not_configured")
    return AgentMailProvider(settings)


def translate_provider_error(exc: Exception) -> HTTPException:
    logger.exception("AgentMail provider request failed")
    return HTTPException(status_code=502, detail={"code": "agentmail_provider_error", "type": type(exc).__name__})


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz(settings: SettingsDep) -> dict[str, Any]:
    ready = settings.provider_configured and settings.webhook_verification_configured
    return {
        "status": "ready" if ready else "not_ready",
        "provider_configured": settings.provider_configured,
        "webhook_verification_configured": settings.webhook_verification_configured,
        "live_send_enabled": settings.live_send_enabled,
        "production_approved": settings.production_approved,
        "klyrow_callback_configured": bool(settings.klyrow_callback_url),
    }


@app.get("/v1/inboxes")
def list_inboxes(settings: SettingsDep) -> Any:
    try:
        return provider(settings).list_inboxes()
    except HTTPException:
        raise
    except Exception as exc:
        raise translate_provider_error(exc) from exc


@app.post("/v1/inboxes", status_code=status.HTTP_201_CREATED)
def create_inbox(request: InboxCreate, settings: SettingsDep) -> Any:
    try:
        return provider(settings).create_inbox(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise translate_provider_error(exc) from exc


@app.get("/v1/inboxes/{inbox_id}/messages")
def list_messages(
    inbox_id: str,
    settings: SettingsDep,
    limit: int = Query(default=50, ge=1, le=100),
) -> Any:
    try:
        return provider(settings).list_messages(inbox_id, limit)
    except HTTPException:
        raise
    except Exception as exc:
        raise translate_provider_error(exc) from exc


@app.get("/v1/inboxes/{inbox_id}/messages/{message_id}")
def get_message(inbox_id: str, message_id: str, settings: SettingsDep) -> Any:
    try:
        return provider(settings).get_message(inbox_id, message_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise translate_provider_error(exc) from exc


@app.post("/v1/inboxes/{inbox_id}/messages:send")
def send_message(inbox_id: str, request: SendMessageRequest, settings: SettingsDep) -> Any:
    recipients = [*request.to, *request.cc, *request.bcc]
    try:
        enforce_delivery(settings, recipients)
    except EffectDenied as exc:
        raise HTTPException(status_code=403, detail={"code": "effect_denied", "reason": str(exc)}) from exc

    try:
        return provider(settings).send_message(inbox_id, request)
    except HTTPException:
        raise
    except Exception as exc:
        raise translate_provider_error(exc) from exc


@app.post("/v1/inboxes/{inbox_id}/messages/{message_id}:reply")
def reply_message(inbox_id: str, message_id: str, request: ReplyMessageRequest, settings: SettingsDep) -> Any:
    if request.reply_all:
        raise HTTPException(status_code=403, detail={"code": "effect_denied", "reason": "reply_all_not_enabled"})

    mail_provider = provider(settings)
    try:
        source = mail_provider.get_message(inbox_id, message_id)
        reply_to = source.get("reply_to") if isinstance(source, dict) else None
        sender = source.get("from") if isinstance(source, dict) else None
        target = reply_to[0] if isinstance(reply_to, list) and reply_to else sender
        enforce_delivery(settings, [target] if isinstance(target, str) else [])
        return mail_provider.reply_message(inbox_id, message_id, request)
    except EffectDenied as exc:
        raise HTTPException(status_code=403, detail={"code": "effect_denied", "reason": str(exc)}) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise translate_provider_error(exc) from exc


@app.post("/v1/webhooks/agentmail")
async def agentmail_webhook(request: Request, settings: SettingsDep) -> dict[str, Any]:
    payload = await verify_agentmail_webhook(request, settings)
    event = canonicalize_agentmail_event(payload)
    forwarded = await forward_to_klyrow(settings, event)
    return {
        "accepted": True,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "forwarded_to_klyrow": forwarded,
    }
