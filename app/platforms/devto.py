
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform


class DevToPlatform(BasePlatform):
    platform_name = "DEV Community"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.devto_api_key:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error="DEV Community API key is not configured."
            )

        api_url = "https://dev.to/api/articles"

        headers = {
            "api-key": settings.devto_api_key,
            "Accept": "application/vnd.forem.api-v1+json",
            "User-Agent": "AutomatedMultiPlatformPostingSystem/1.0"
        }

        # Start with a draft to verify the integration safely.
        article = {
            "title": "Automated Posting System - Integration Test",
            "body_markdown": message,
            "published": True
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json={"article": article}
                )

                response.raise_for_status()
                post = response.json()

            created_at_value = post.get("published_at") or post.get("created_at")

            if created_at_value:
                created_at = datetime.fromisoformat(
                    created_at_value.replace("Z", "+00:00")
                )
            else:
                created_at = datetime.now(timezone.utc)

            posted_url = post.get("url")

            return PlatformResult(
                platform=self.platform_name,
                status="success",
                posted_url=posted_url,
                public_access=bool(post.get("published_at")),
                date=created_at.date(),
                time=created_at.time().replace(tzinfo=None),
                error=None
            )

        except httpx.HTTPStatusError as exc:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error=(
                    f"DEV Community HTTP error: "
                    f"{exc.response.status_code} - {exc.response.text}"
                )
            )

        except Exception as exc:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error=str(exc)
            )
