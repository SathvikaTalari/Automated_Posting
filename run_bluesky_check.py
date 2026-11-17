import asyncio

from app.platforms.bluesky import BlueskyPlatform


async def main():
    platform = BlueskyPlatform()

    result = await platform.publish(
        "Testing my Automated Multi-Platform Posting System! https://example.com"
    )

    print(result.model_dump())


asyncio.run(main())