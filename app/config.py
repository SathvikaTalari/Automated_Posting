from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    bluesky_handle: str | None = None
    bluesky_app_password: str | None = None

    mastodon_instance_url: str | None = None
    mastodon_access_token: str | None = None

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    discord_webhook_url: str | None = None

    devto_api_key: str | None = None


settings = Settings()