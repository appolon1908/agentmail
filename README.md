# Codestra AgentMail

Standalone AgentMail integration service for the Codestra platform.

## Authority model

This repository **does not replace Klyrow** and it does not make AgentMail the business-policy authority.

- **Klyrow** remains the canonical email product/provider authority and keeps its Postal/SMTP capability.
- **Codestra AgentMail** adds an agent-native provider path: inboxes, threads/messages, replies, attachments, webhooks and realtime-compatible event handling.
- **Middleware / identity policy** may sit in front of this service in deployment.
- External sending is **fail closed** by default.

The intended provider topology is:

```text
Klyrow Email Authority
        |
        +-- Postal / SMTP provider
        |
        +-- Codestra AgentMail provider
                 |
                 +-- AgentMail API
                 +-- signed AgentMail webhooks
                 +-- agent inboxes / threads
```

## API

- `GET /healthz`
- `GET /readyz`
- `GET /v1/inboxes`
- `POST /v1/inboxes`
- `GET /v1/inboxes/{inbox_id}/messages`
- `GET /v1/inboxes/{inbox_id}/messages/{message_id}`
- `POST /v1/inboxes/{inbox_id}/messages:send`
- `POST /v1/inboxes/{inbox_id}/messages/{message_id}:reply`
- `POST /v1/webhooks/agentmail`

The service publishes its OpenAPI document automatically at `/openapi.json` and Swagger UI at `/docs`.

## Safety defaults

Outbound delivery is denied unless all of these are true:

1. `AGENTMAIL_LIVE_SEND_ENABLED=true`
2. `AGENTMAIL_PRODUCTION_APPROVED=true`
3. every recipient matches `AGENTMAIL_RECIPIENT_ALLOWLIST`
4. an idempotency key is supplied

AgentMail webhook verification also fails closed when `AGENTMAIL_WEBHOOK_SECRET` is absent.

## Local development

```bash
cp .env.example .env
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn codestra_agentmail.main:app --reload --port 8097
```

Run checks:

```bash
ruff check .
mypy src
pytest -q
```

## Docker

```bash
docker compose up --build
```

## Branch promotion

```text
development -> testing -> staging -> production
```

`main` is the repository bootstrap/reference branch and must not receive ordinary implementation pushes.

See `docs/ARCHITECTURE.md` and `docs/KLYROW_INTEGRATION.md`.
