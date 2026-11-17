
import asyncio

from app.platforms.discord import DiscordPlatform


async def main():
    platform = DiscordPlatform()

    result = await platform.publish(
        "Testing my Automated Multi-Platform Posting System! https://example.com"
    )

    print(result.model_dump())


asyncio.run(main())
