# Architecture

## Purpose

Codestra AgentMail is a standalone adapter/service boundary between Codestra/Klyrow and AgentMail.

It intentionally separates four concerns:

1. **Klyrow business authority** — tenant, product and delivery policy.
2. **Codestra AgentMail service** — normalized API, policy enforcement and webhook translation.
3. **AgentMail provider** — agent-native inbox and message transport.
4. **Middleware/identity/security** — optional platform-level authorization and routing.

## Data flow

### Outbound

```text
Klyrow / authorized caller
        |
        v
Codestra AgentMail API
        |
        +--> fail-closed effect policy
        |
        +--> AgentMail SDK + idempotency key
        |
        v
AgentMail delivery
```

### Inbound

```text
Internet sender
   |
   v
AgentMail inbox
   |
 signed webhook
   v
Codestra AgentMail
   |
 canonical email-event.v1
   v
Klyrow callback
```

## Security invariants

- Live delivery is disabled by default.
- A production-approval flag is separately required.
- A non-empty recipient allowlist is required.
- Idempotency keys are mandatory on outbound sends.
- Incoming webhooks require Svix verification.
- Provider secrets live only in environment/secret stores.
- Klyrow callback payloads can be HMAC signed.
- No endpoint activates DNS, MX, SPF, DKIM or DMARC automatically.

## Why AgentMail does not replace Postal

Klyrow already owns a Postal/SMTP delivery path. Keeping provider authority in Klyrow avoids provider lock-in and permits use-case routing:

- Agent/AI mail -> AgentMail
- existing transactional or bulk flows -> Postal/SMTP
- future providers -> additional adapters

AgentMail is therefore an additional provider, not the sole source of truth.
