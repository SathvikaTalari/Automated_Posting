
import httpx
import pytest

from app.config import settings
from app.platforms import mastodon


@pytest.mark.asyncio
async def test_mastodon_successful_publish(monkeypatch):
    original_client = httpx.AsyncClient

    def mock_handler(request):
        assert request.method == "POST"
        assert request.url.path == "/api/v1/statuses"
        return httpx.Response(
            200,
            json={
                "created_at": "2026-11-17T12:00:00.000Z",
                "url": "https://mastodon.social/@test/123",
                "visibility": "public"
            }
        )

    monkeypatch.setattr(
        settings,
        "mastodon_instance_url",
        "https://mastodon.social"
    )
    monkeypatch.setattr(
        settings,
        "mastodon_access_token",
        "test-token"
    )

    monkeypatch.setattr(
        mastodon.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler),
            **kwargs
        )
    )

    platform = mastodon.MastodonPlatform()
    result = await platform.publish(
        "Testing Mastodon https://example.com"
    )

    assert result.status == "success"
    assert result.platform == "Mastodon"
    assert str(result.posted_url) == "https://mastodon.social/@test/123"
    assert result.public_access is True
    assert result.error is None


@pytest.mark.asyncio
async def test_mastodon_authentication_failure(monkeypatch):
    original_client = httpx.AsyncClient

    def mock_handler(request):
        return httpx.Response(
            401,
            json={"error": "Unauthorized"}
        )

    monkeypatch.setattr(
        settings,
        "mastodon_instance_url",
        "https://mastodon.social"
    )
    monkeypatch.setattr(
        settings,
        "mastodon_access_token",
        "invalid-token"
    )

    monkeypatch.setattr(
        mastodon.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler),
            **kwargs
        )
    )

    platform = mastodon.MastodonPlatform()
    result = await platform.publish(
        "Testing authentication https://example.com"
    )

    assert result.status == "failed"
    assert "authentication failed" in result.error.lower()
