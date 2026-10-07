from typing import Any

from agentmail import AgentMail
from agentmail.environment import AgentMailEnvironment
from agentmail.inboxes.types.create_inbox_request import CreateInboxRequest

from .config import Settings
from .models import InboxCreate, ReplyMessageRequest, SendMessageRequest


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True)
    if hasattr(value, "dict"):
        return value.dict()
    if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
        return value
    return str(value)


def _custom_environment(base_url: str) -> AgentMailEnvironment:
    http = base_url.rstrip("/")
    if http.startswith("https://"):
        websocket = "wss://" + http.removeprefix("https://")
    elif http.startswith("http://"):
        websocket = "ws://" + http.removeprefix("http://")
    else:
        raise ValueError("AGENTMAIL_API_BASE_URL must start with http:// or https://")
    return AgentMailEnvironment(http=http, websockets=websocket)


class AgentMailProvider:
    def __init__(self, settings: Settings):
        environment = _custom_environment(settings.api_base_url) if settings.api_base_url else AgentMailEnvironment.PROD
        self.client = AgentMail(api_key=settings.api_key, environment=environment)

    def list_inboxes(self) -> Any:
        return to_jsonable(self.client.inboxes.list())

    def create_inbox(self, request: InboxCreate) -> Any:
        create_request = CreateInboxRequest(
            username=request.username,
            domain=request.domain,
            client_id=request.client_id,
        )
        return to_jsonable(self.client.inboxes.create(request=create_request))

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
                reply_all=False,
                headers={
                    "X-Codestra-Tenant": request.tenant_id,
                    "X-Codestra-Actor": request.actor_id,
                },
                idempotency_key=request.idempotency_key,
            )
        )
