import asyncio

from app.platforms.telegram import TelegramPlatform


async def main():
    platform = TelegramPlatform()

    result = await platform.publish(
        "Testing my Automated Multi-Platform Posting System! https://example.com"
    )

    print(result.model_dump())


asyncio.run(main())