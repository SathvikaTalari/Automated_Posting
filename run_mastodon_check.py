import asyncio

from app.platforms.mastodon import MastodonPlatform


async def main():
    platform = MastodonPlatform()

    result = await platform.publish(
        "Testing my Automated Multi-Platform Posting System! https://example.com"
    )

    print(result.model_dump())


asyncio.run(main())