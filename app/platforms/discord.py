
from datetime import datetime

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
                webhook_response = await client.get(webhook_url)
                webhook_response.raise_for_status()
                webhook = webhook_response.json()

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
                time=created_at.time().replace(tzinfo=None),
                error=None
            )

        except httpx.TimeoutException:
            error = "Discord request timed out."

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            if status_code in (401, 403, 404):
                error = "Discord webhook is invalid or access was denied."
            elif status_code == 429:
                error = "Discord rate limit exceeded. Try again later."
            else:
                error = f"Discord API returned HTTP {status_code}."

        except httpx.RequestError:
            error = "Could not connect to the Discord server."

        except Exception as exc:
            error = f"Discord publishing failed ({type(exc).__name__})."

        return PlatformResult(
            platform=self.platform_name,
            status="failed",
            error=error
        )
