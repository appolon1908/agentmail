from codestra_agentmail.config import Settings
from codestra_agentmail.policy import authorize_delivery


def settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "AGENTMAIL_LIVE_SEND_ENABLED": False,
        "AGENTMAIL_PRODUCTION_APPROVED": False,
        "AGENTMAIL_RECIPIENT_ALLOWLIST": "",
    }
    values.update(overrides)
    return Settings(**values)


def test_delivery_is_fail_closed() -> None:
    decision = authorize_delivery(settings(), ["qa@codestra.co"])
    assert not decision.allowed
    assert decision.reason == "live_send_disabled"


def test_allowlist_is_required() -> None:
    cfg = settings(AGENTMAIL_LIVE_SEND_ENABLED=True, AGENTMAIL_PRODUCTION_APPROVED=True)
    decision = authorize_delivery(cfg, ["qa@codestra.co"])
    assert not decision.allowed
    assert decision.reason == "recipient_allowlist_empty"


def test_exact_address_and_domain_rules_are_allowed() -> None:
    cfg = settings(
        AGENTMAIL_LIVE_SEND_ENABLED=True,
        AGENTMAIL_PRODUCTION_APPROVED=True,
        AGENTMAIL_RECIPIENT_ALLOWLIST="qa@example.com,@codestra.co",
    )
    assert authorize_delivery(cfg, ["qa@example.com"]).allowed
    assert authorize_delivery(cfg, ["person@codestra.co"]).allowed
    assert not authorize_delivery(cfg, ["person@external.example"]).allowed
