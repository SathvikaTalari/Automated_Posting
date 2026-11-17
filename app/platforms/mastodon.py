
from datetime import datetime

import httpx

from app.config import settings
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform


class MastodonPlatform(BasePlatform):
    platform_name = "Mastodon"

    async def publish(self, message: str) -> PlatformResult:
        if not settings.mastodon_instance_url or not settings.mastodon_access_token:
            return PlatformResult(
                platform=self.platform_name,
                status="failed",
                error="Mastodon credentials are not configured."
            )

        base_url = settings.mastodon_instance_url.rstrip("/")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/api/v1/statuses",
                    headers={
                        "Authorization": f"Bearer {settings.mastodon_access_token}"
                    },
                    data={
                        "status": message,
                        "visibility": "public"
                    }
                )

                response.raise_for_status()
                post = response.json()

            created_at = datetime.fromisoformat(
                post["created_at"].replace("Z", "+00:00")
            )

            return PlatformResult(
                platform=self.platform_name,
                status="success",
                posted_url=post.get("url"),
                public_access=post.get("visibility") == "public",
                date=created_at.date(),
                time=created_at.time().replace(tzinfo=None),
                error=None
            )

        except httpx.TimeoutException:
            error = "Mastodon request timed out."

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            if status_code in (401, 403):
                error = "Mastodon authentication failed. Check your access token."
            elif status_code == 429:
                error = "Mastodon rate limit exceeded. Try again later."
            else:
                error = f"Mastodon API returned HTTP {status_code}."

        except httpx.RequestError:
            error = "Could not connect to the Mastodon server."

        except Exception as exc:
            error = f"Mastodon publishing failed ({type(exc).__name__})."

        return PlatformResult(
            platform=self.platform_name,
            status="failed",
            error=error
        )
