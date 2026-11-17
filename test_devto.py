
import asyncio

from app.platforms.devto import DevToPlatform


async def main():
    platform = DevToPlatform()

    result = await platform.publish(
        "Testing my Automated Multi-Platform Posting System! "
        "https://example.com"
    )

    print(result.model_dump())


asyncio.run(main())
