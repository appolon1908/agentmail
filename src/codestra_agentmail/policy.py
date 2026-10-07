from dataclasses import dataclass
from email.utils import parseaddr

from .config import Settings


class EffectDenied(PermissionError):
    pass


@dataclass(frozen=True)
class DeliveryDecision:
    allowed: bool
    reason: str


def _normalize_address(address: str) -> str:
    parsed = parseaddr(address.strip())[1]
    return (parsed or address.strip()).lower()


def _matches_allowlist(address: str, allowlist: tuple[str, ...]) -> bool:
    normalized = _normalize_address(address)
    domain = normalized.rsplit("@", 1)[-1] if "@" in normalized else ""
    for rule in allowlist:
        if rule.startswith("@") and domain == rule[1:]:
            return True
        if normalized == rule:
            return True
    return False


def authorize_delivery(settings: Settings, recipients: list[str]) -> DeliveryDecision:
    if not settings.live_send_enabled:
        return DeliveryDecision(False, "live_send_disabled")
    if not settings.production_approved:
        return DeliveryDecision(False, "production_not_approved")
    if not recipients:
        return DeliveryDecision(False, "recipient_missing")
    if len(recipients) > settings.max_recipients:
        return DeliveryDecision(False, "recipient_limit_exceeded")
    if not settings.recipient_allowlist:
        return DeliveryDecision(False, "recipient_allowlist_empty")
    if not all(_matches_allowlist(address, settings.recipient_allowlist) for address in recipients):
        return DeliveryDecision(False, "recipient_not_allowlisted")
    return DeliveryDecision(True, "approved")


def enforce_delivery(settings: Settings, recipients: list[str]) -> None:
    decision = authorize_delivery(settings, recipients)
    if not decision.allowed:
        raise EffectDenied(decision.reason)
