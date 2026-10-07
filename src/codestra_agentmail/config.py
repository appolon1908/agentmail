from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    environment: str = Field(default="development", validation_alias="AGENTMAIL_ENV")
    api_key: str = Field(default="", validation_alias="AGENTMAIL_API_KEY")
    api_base_url: str = Field(default="", validation_alias="AGENTMAIL_API_BASE_URL")
    webhook_secret: str = Field(default="", validation_alias="AGENTMAIL_WEBHOOK_SECRET")

    live_send_enabled: bool = Field(default=False, validation_alias="AGENTMAIL_LIVE_SEND_ENABLED")
    production_approved: bool = Field(default=False, validation_alias="AGENTMAIL_PRODUCTION_APPROVED")
    recipient_allowlist_raw: str = Field(default="", validation_alias="AGENTMAIL_RECIPIENT_ALLOWLIST")
    max_recipients: int = Field(default=10, ge=1, le=100, validation_alias="AGENTMAIL_MAX_RECIPIENTS")

    klyrow_callback_url: str = Field(default="", validation_alias="KLYROW_CALLBACK_URL")
    klyrow_callback_hmac_secret: str = Field(default="", validation_alias="KLYROW_CALLBACK_HMAC_SECRET")
    klyrow_callback_timeout_seconds: float = Field(
        default=10.0, gt=0, le=60, validation_alias="KLYROW_CALLBACK_TIMEOUT_SECONDS"
    )

    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    @property
    def recipient_allowlist(self) -> tuple[str, ...]:
        return tuple(item.strip().lower() for item in self.recipient_allowlist_raw.split(",") if item.strip())

    @property
    def provider_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def webhook_verification_configured(self) -> bool:
        return bool(self.webhook_secret)


@lru_cache
def get_settings() -> Settings:
    return Settings()
