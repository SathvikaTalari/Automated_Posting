
import asyncio

from app.schemas import PlatformResult
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.devto import DevToPlatform


class PostingService:

    def __init__(self):
        self.platforms = [
            BlueskyPlatform(),
            MastodonPlatform(),
            TelegramPlatform(),
            DiscordPlatform(),
            DevToPlatform()
        ]

    async def publish_to_all(self, message: str) -> list[PlatformResult]:

        tasks = [
            platform.publish(message)
            for platform in self.platforms
        ]

        responses = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        results = []

        for platform, response in zip(self.platforms, responses):

            if isinstance(response, Exception):
                results.append(
                    PlatformResult(
                        platform=platform.platform_name,
                        status="failed",
                        error=f"Unexpected publishing error ({type(response).__name__})."
                    )
                )
            else:
                results.append(response)

        return results


posting_service = PostingService()
