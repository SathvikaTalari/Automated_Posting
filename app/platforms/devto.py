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

        article = {
            "title": "Automated Posting System - Shared Update",
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

            published_at_value = post.get("published_at")

            if published_at_value:
                created_at = datetime.fromisoformat(
                    published_at_value.replace("Z", "+00:00")
                )
            else:
                created_at_value = post.get("created_at")

                if created_at_value:
                    created_at = datetime.fromisoformat(
                        created_at_value.replace("Z", "+00:00")
                    )
                else:
                    created_at = datetime.now(timezone.utc)

            return PlatformResult(
                platform=self.platform_name,
                status="success",
                posted_url=post.get("url"),
                public_access=bool(published_at_value),
                date=created_at.date(),
                time=created_at.time().replace(tzinfo=None),
                error=None
            )

        except httpx.TimeoutException:
            error = "DEV Community request timed out."

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            if status_code in (401, 403):
                error = "DEV Community authentication failed. Check your API key."
            elif status_code == 422:
                error = "DEV Community rejected the article content."
            elif status_code == 429:
                error = "DEV Community rate limit exceeded. Try again later."
            else:
                error = f"DEV Community API returned HTTP {status_code}."

        except httpx.RequestError:
            error = "Could not connect to DEV Community."

        except Exception as exc:
            error = f"DEV Community publishing failed ({type(exc).__name__})."

        return PlatformResult(
            platform=self.platform_name,
            status="failed",
            error=error
        )
