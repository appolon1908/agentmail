from codestra_agentmail.config import Settings
from codestra_agentmail.policy import authorize_delivery


def settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "live_send_enabled": False,
        "production_approved": False,
        "recipient_allowlist_raw": "",
    }
    values.update(overrides)
    return Settings(**values)


def test_delivery_is_fail_closed() -> None:
    decision = authorize_delivery(settings(), ["qa@codestra.co"])
    assert not decision.allowed
    assert decision.reason == "live_send_disabled"


def test_allowlist_is_required() -> None:
    cfg = settings(live_send_enabled=True, production_approved=True)
    decision = authorize_delivery(cfg, ["qa@codestra.co"])
    assert not decision.allowed
    assert decision.reason == "recipient_allowlist_empty"


def test_exact_address_and_domain_rules_are_allowed() -> None:
    cfg = settings(
        live_send_enabled=True,
        production_approved=True,
        recipient_allowlist_raw="qa@example.com,@codestra.co",
    )
    assert authorize_delivery(cfg, ["qa@example.com"]).allowed
    assert authorize_delivery(cfg, ["person@codestra.co"]).allowed
    assert authorize_delivery(cfg, ["Person <person@codestra.co>"]).allowed
    assert not authorize_delivery(cfg, ["person@external.example"]).allowed
