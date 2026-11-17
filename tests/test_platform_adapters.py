
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


@pytest.mark.asyncio
async def test_telegram_successful_publish(monkeypatch):
    from app.platforms import telegram

    original_client = httpx.AsyncClient

    def mock_handler(request):
        return httpx.Response(
            200,
            json={
                "ok": True,
                "result": {
                    "message_id": 123,
                    "date": 1795000000,
                    "chat": {"id": -100123456789, "username": "testchannel"}
                }
            }
        )

    monkeypatch.setattr(settings, "telegram_bot_token", "test-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "@testchannel")
    monkeypatch.setattr(
        telegram.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler), **kwargs
        )
    )

    result = await telegram.TelegramPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "success"
    assert result.platform == "Telegram"
    assert result.public_access is True
    assert result.error is None


@pytest.mark.asyncio
async def test_telegram_authentication_failure(monkeypatch):
    from app.platforms import telegram

    original_client = httpx.AsyncClient

    def mock_handler(request):
        return httpx.Response(401, json={"ok": False, "error_code": 401})

    monkeypatch.setattr(settings, "telegram_bot_token", "invalid-token")
    monkeypatch.setattr(settings, "telegram_chat_id", "@testchannel")
    monkeypatch.setattr(
        telegram.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler), **kwargs
        )
    )

    result = await telegram.TelegramPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "failed"
    assert result.error is not None


@pytest.mark.asyncio
async def test_discord_successful_publish(monkeypatch):
    from app.platforms import discord

    original_client = httpx.AsyncClient

    def mock_handler(request):
        if request.method == "GET":
            return httpx.Response(
                200,
                json={"guild_id": "guild123", "channel_id": "channel456"}
            )

        return httpx.Response(
            200,
            json={
                "id": "message789",
                "channel_id": "channel456",
                "guild_id": "guild123",
                "timestamp": "2026-11-17T12:00:00.000Z"
            }
        )

    monkeypatch.setattr(
        settings,
        "discord_webhook_url",
        "https://discord.com/api/webhooks/test/token"
    )
    monkeypatch.setattr(
        discord.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler), **kwargs
        )
    )

    result = await discord.DiscordPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "success"
    assert result.platform == "Discord"
    assert result.error is None


@pytest.mark.asyncio
async def test_discord_authentication_failure(monkeypatch):
    from app.platforms import discord

    original_client = httpx.AsyncClient

    def mock_handler(request):
        return httpx.Response(401, json={"message": "Unauthorized"})

    monkeypatch.setattr(
        settings,
        "discord_webhook_url",
        "https://discord.com/api/webhooks/test/token"
    )
    monkeypatch.setattr(
        discord.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler), **kwargs
        )
    )

    result = await discord.DiscordPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "failed"
    assert result.error is not None


@pytest.mark.asyncio
async def test_devto_successful_publish(monkeypatch):
    from app.platforms import devto

    original_client = httpx.AsyncClient

    def mock_handler(request):
        assert request.method == "POST"
        assert request.url.path == "/api/articles"
        return httpx.Response(
            201,
            json={
                "id": 123,
                "url": "https://dev.to/testuser/test-article",
                "published_at": "2026-11-17T12:00:00Z"
            }
        )

    monkeypatch.setattr(settings, "devto_api_key", "test-api-key")
    monkeypatch.setattr(
        devto.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler), **kwargs
        )
    )

    result = await devto.DevToPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "success"
    assert result.platform == "DEV Community"
    assert result.public_access is True
    assert result.error is None


@pytest.mark.asyncio
async def test_devto_authentication_failure(monkeypatch):
    from app.platforms import devto

    original_client = httpx.AsyncClient

    def mock_handler(request):
        return httpx.Response(401, json={"error": "Unauthorized"})

    monkeypatch.setattr(settings, "devto_api_key", "invalid-key")
    monkeypatch.setattr(
        devto.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(mock_handler), **kwargs
        )
    )

    result = await devto.DevToPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "failed"
    assert result.error is not None


@pytest.mark.asyncio
async def test_bluesky_successful_publish(monkeypatch):
    from types import SimpleNamespace
    from app.platforms import bluesky

    class MockClient:
        def login(self, handle, password):
            assert handle == "test.bsky.social"
            assert password == "test-password"

        def send_post(self, message):
            assert "https://example.com" in message
            return SimpleNamespace(uri="at://did:plc:test/app.bsky.feed.post/post123")

    monkeypatch.setattr(settings, "bluesky_handle", "test.bsky.social")
    monkeypatch.setattr(settings, "bluesky_app_password", "test-password")
    monkeypatch.setattr(bluesky, "Client", MockClient)

    result = await bluesky.BlueskyPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "success"
    assert result.platform == "Bluesky"
    assert str(result.posted_url) == (
        "https://bsky.app/profile/test.bsky.social/post/post123"
    )
    assert result.public_access is True
    assert result.error is None


@pytest.mark.asyncio
async def test_bluesky_authentication_failure(monkeypatch):
    from app.platforms import bluesky

    class MockClient:
        def login(self, handle, password):
            raise RuntimeError("Authentication failed")

    monkeypatch.setattr(settings, "bluesky_handle", "test.bsky.social")
    monkeypatch.setattr(settings, "bluesky_app_password", "test-password")
    monkeypatch.setattr(bluesky, "Client", MockClient)

    result = await bluesky.BlueskyPlatform().publish(
        "Test message https://example.com"
    )

    assert result.status == "failed"
    assert "Bluesky publishing failed" in result.error
