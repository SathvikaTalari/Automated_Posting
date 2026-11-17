from abc import ABC, abstractmethod

from app.schemas import PlatformResult


class BasePlatform(ABC):
    """
    Common interface for all platform integrations.
    """

    platform_name = "Unknown"

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        """
        Publish a message and return its result.
        """
        raise NotImplementedError