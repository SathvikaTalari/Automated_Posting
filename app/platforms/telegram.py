
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform


class TelegramPlatform(BasePlatform):
    platform_name = "Telegram"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error="Telegram credentials are not configured."
            )

        api_url = (
            f"https://api.telegram.org/bot"
            f"{settings.telegram_bot_token}/sendMessage"
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    json={
                        "chat_id": settings.telegram_chat_id,
                        "text": message
                    }
                )

                response.raise_for_status()
                result = response.json()

                if not result.get("ok"):
                    raise ValueError(
                        result.get("description", "Telegram API error")
                    )

            telegram_message = result["result"]
            created_at = datetime.fromtimestamp(
                telegram_message["date"],
                tz=timezone.utc
            )

            chat = telegram_message["chat"]
            message_id = telegram_message["message_id"]
            username = chat.get("username")

            posted_url = (
                f"https://t.me/{username}/{message_id}"
                if username else None
            )

            return PlatformResult(
                platform=self.platform_name,
                status="success",
                posted_url=posted_url,
                public_access=bool(username),
                date=created_at.date(),
                time=created_at.time().replace(tzinfo=None)
            )

        except httpx.HTTPStatusError as exc:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error=f"Telegram HTTP error: {exc.response.status_code} - "
                      f"{exc.response.text}"
            )

        except Exception as exc:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error=str(exc)
            )
