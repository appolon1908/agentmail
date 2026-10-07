# Agent rules

## Repository role

This repository owns the Codestra AgentMail integration service only.

## Required workflow

- Work on `development` or an atomic task branch based on it.
- Never push ordinary implementation directly to `main`.
- Promote in order: `development -> testing -> staging -> production`.
- No force pushes.
- Do not commit credentials, API keys, webhook secrets, SMTP passwords, OAuth tokens or private keys.
- Production effects remain disabled by default.

## Completion evidence

A change is complete only when:
- tests pass,
- static checks pass,
- API contract changes are documented,
- effect gates remain fail closed,
- no secret is committed,
- the branch is pushed and reviewable.

## External effects

Agents may implement and test delivery logic with mocks. They must not enable live sending, alter production DNS/MX records, or activate a provider without an explicit production approval.
