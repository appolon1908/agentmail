# Klyrow integration contract

## Recommended provider model

Add `agentmail` as a provider option inside Klyrow's existing email authority rather than calling AgentMail directly from unrelated Klyrow modules.

Klyrow should retain the final decision over:
- tenant entitlement,
- sender identity,
- compliance policy,
- quotas,
- production/canary approval,
- provider selection.

## Outbound call

Klyrow calls:

`POST /v1/inboxes/{inbox_id}/messages:send`

Example body:

```json
{
  "tenant_id": "tenant-123",
  "actor_id": "service:klyrow-worker",
  "to": ["recipient@example.com"],
  "subject": "Hello",
  "text": "Message body",
  "labels": ["klyrow"],
  "idempotency_key": "delivery-unique-key"
}
```

Klyrow must treat HTTP 403 as a closed effect gate, not as a retryable provider failure.

## Inbound callback

Configure:

```text
KLYROW_CALLBACK_URL=https://<klyrow-internal>/internal/providers/agentmail/events
KLYROW_CALLBACK_HMAC_SECRET=<secret-store-value>
```

The callback receives `codestra.email-event.v1`.

If the HMAC secret is set, verify `X-Codestra-Signature-SHA256` against the exact request body before parsing it.

## Provider coexistence

Do not remove Klyrow's Postal configuration when enabling AgentMail.

Suggested routing:

```text
provider=postal     -> existing Postal/SMTP path
provider=agentmail  -> Codestra AgentMail API
```

Keep `LIVE_EMAIL_DELIVERY=false` and provider-specific live flags closed until canary evidence is approved.
