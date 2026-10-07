from typing import Any

from pydantic import BaseModel, Field, field_validator


def _validate_address(value: str) -> str:
    value = value.strip()
    if "\r" in value or "\n" in value or "@" not in value:
        raise ValueError("invalid email address")
    return value


class InboxCreate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=64)
    domain: str | None = Field(default=None, min_length=3, max_length=253)
    client_id: str | None = Field(default=None, min_length=1, max_length=128)


class SendMessageRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=128)
    actor_id: str = Field(min_length=1, max_length=128)
    to: list[str] = Field(min_length=1)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    subject: str = Field(min_length=1, max_length=998)
    text: str | None = None
    html: str | None = None
    labels: list[str] = Field(default_factory=list)
    idempotency_key: str = Field(min_length=8, max_length=255)

    @field_validator("to", "cc", "bcc")
    @classmethod
    def validate_addresses(cls, values: list[str]) -> list[str]:
        return [_validate_address(v) for v in values]


class ReplyMessageRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=128)
    actor_id: str = Field(min_length=1, max_length=128)
    text: str | None = None
    html: str | None = None
    reply_all: bool = False
    idempotency_key: str = Field(min_length=8, max_length=255)


class CanonicalEmailEvent(BaseModel):
    schema_version: str = "codestra.email-event.v1"
    provider: str = "agentmail"
    event_type: str
    event_id: str | None = None
    inbox_id: str | None = None
    message_id: str | None = None
    thread_id: str | None = None
    occurred_at: str | None = None
    payload: dict[str, Any]
