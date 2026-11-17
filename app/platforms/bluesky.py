import asyncio
from datetime import datetime, timezone

from atproto import Client

from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform


class BlueskyPlatform(BasePlatform):
    platform_name = "Bluesky"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.bluesky_handle or not settings.bluesky_app_password:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error="Bluesky credentials are not configured."
            )

        try:
            return await asyncio.to_thread(
                self._publish_sync, message
            )

        except Exception as exc:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error=str(exc)
            )

    def _publish_sync(self, message: str) -> PlatformResult:
        client = Client()

        client.login(
            settings.bluesky_handle,
            settings.bluesky_app_password
        )

        post = client.send_post(message)

        rkey = post.uri.rsplit("/", 1)[-1]

        posted_url = (
            f"https://bsky.app/profile/"
            f"{settings.bluesky_handle}/post/{rkey}"
        )

        published_at = datetime.now(timezone.utc)

        return PlatformResult(
            platform=self.platform_name,
            status="success",
            posted_url=posted_url,
            public_access=True,
            date=published_at.date(),
            time=published_at.time().replace(tzinfo=None),
            error=None
        )