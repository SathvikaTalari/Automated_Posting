
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform


class DiscordPlatform(BasePlatform):
    platform_name = "Discord"

    async def publish(self, message: str) -> PlatformResult:
        webhook_url = settings.discord_webhook_url

        if not webhook_url:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error="Discord webhook is not configured."
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get webhook details to obtain server and channel IDs.
                webhook_response = await client.get(webhook_url)
                webhook_response.raise_for_status()
                webhook = webhook_response.json()

                # Publish the message.
                response = await client.post(
                    webhook_url,
                    params={"wait": "true"},
                    json={"content": message}
                )
                response.raise_for_status()
                post = response.json()

            created_at = datetime.fromisoformat(
                post["timestamp"].replace("Z", "+00:00")
            )

            guild_id = webhook.get("guild_id")
            channel_id = post.get("channel_id")
            message_id = post.get("id")

            posted_url = None

            if guild_id and channel_id and message_id:
                posted_url = (
                    f"https://discord.com/channels/"
                    f"{guild_id}/{channel_id}/{message_id}"
                )

            return PlatformResult(
                platform=self.platform_name,
                status="success",
                posted_url=posted_url,
                public_access=False,
                date=created_at.date(),
                time=created_at.time().replace(tzinfo=None)
            )

        except httpx.HTTPStatusError as exc:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error=(
                    f"Discord HTTP error: {exc.response.status_code} - "
                    f"{exc.response.text}"
                )
            )

        except Exception as exc:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error=str(exc)
            )
