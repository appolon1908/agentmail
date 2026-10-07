from typing import Any

from agentmail import AgentMail

from .config import Settings
from .models import InboxCreate, ReplyMessageRequest, SendMessageRequest


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
        return value
    return str(value)


class AgentMailProvider:
    def __init__(self, settings: Settings):
        kwargs: dict[str, Any] = {"api_key": settings.api_key}
        if settings.api_base_url:
            kwargs["base_url"] = settings.api_base_url
        self.client = AgentMail(**kwargs)

    def list_inboxes(self) -> Any:
        return to_jsonable(self.client.inboxes.list())

    def create_inbox(self, request: InboxCreate) -> Any:
        kwargs: dict[str, Any] = {}
        if request.username is not None:
            kwargs["username"] = request.username
        if request.domain is not None:
            kwargs["domain"] = request.domain
        if request.client_id is not None:
            kwargs["client_id"] = request.client_id
        return to_jsonable(self.client.inboxes.create(**kwargs))

    def list_messages(self, inbox_id: str, limit: int) -> Any:
        return to_jsonable(self.client.inboxes.messages.list(inbox_id=inbox_id, limit=limit))

    def get_message(self, inbox_id: str, message_id: str) -> Any:
        return to_jsonable(self.client.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id))

    def send_message(self, inbox_id: str, request: SendMessageRequest) -> Any:
        return to_jsonable(
            self.client.inboxes.messages.send(
                inbox_id=inbox_id,
                to=request.to,
                cc=request.cc or None,
                bcc=request.bcc or None,
                subject=request.subject,
                text=request.text,
                html=request.html,
                labels=request.labels or None,
                headers={
                    "X-Codestra-Tenant": request.tenant_id,
                    "X-Codestra-Actor": request.actor_id,
                },
                idempotency_key=request.idempotency_key,
            )
        )

    def reply_message(self, inbox_id: str, message_id: str, request: ReplyMessageRequest) -> Any:
        return to_jsonable(
            self.client.inboxes.messages.reply(
                inbox_id=inbox_id,
                message_id=message_id,
                text=request.text,
                html=request.html,
                reply_all=request.reply_all,
                headers={
                    "X-Codestra-Tenant": request.tenant_id,
                    "X-Codestra-Actor": request.actor_id,
                },
                idempotency_key=request.idempotency_key,
            )
        )
