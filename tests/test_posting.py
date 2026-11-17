
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PlatformResult
from app.services.posting_service import posting_service


client = TestClient(app)


# 1. Message without a URL
def test_message_without_url():
    response = client.post(
        "/posting",
        json={"message": "Hello everyone"}
    )

    assert response.status_code == 422


# 2. Message containing two URLs
def test_message_with_two_urls():
    response = client.post(
        "/posting",
        json={
            "message": "Visit https://example.com and https://openai.com"
        }
    )

    assert response.status_code == 422


# 3. Invalid URL
def test_invalid_url():
    response = client.post(
        "/posting",
        json={"message": "Visit https://"}
    )

    assert response.status_code == 422


# 4. Message exceeding 200 characters
def test_message_exceeds_maximum_length():
    message = "a" * 190 + " https://example.com"

    response = client.post(
        "/posting",
        json={"message": message}
    )

    assert response.status_code == 422


# 5. One platform fails, but another succeeds
class SuccessfulPlatform:
    platform_name = "Test Success"

    async def publish(self, message):
        return PlatformResult(
            platform=self.platform_name,
            status="success",
            posted_url="https://example.com/post/1",
            public_access=True
        )


class FailingPlatform:
    platform_name = "Test Failure"

    async def publish(self, message):
        raise RuntimeError("Simulated platform failure")


def test_one_platform_failure_does_not_stop_others(monkeypatch):
    monkeypatch.setattr(
        posting_service,
        "platforms",
        [SuccessfulPlatform(), FailingPlatform()]
    )

    response = client.post(
        "/posting",
        json={
            "message": "Testing failure handling https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "partial"
    assert data["successful"] == 1
    assert data["failed"] == 1
    assert data["total_platforms"] == 2


# 6. All platforms fail
def test_all_platforms_fail(monkeypatch):
    monkeypatch.setattr(
        posting_service,
        "platforms",
        [FailingPlatform(), FailingPlatform()]
    )

    response = client.post(
        "/posting",
        json={
            "message": "Testing total failure https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "failed"
    assert data["successful"] == 0
    assert data["failed"] == 2
