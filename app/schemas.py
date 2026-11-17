from datetime import date as DateType
from datetime import time as TimeType
from typing import Literal
import re

from pydantic import BaseModel, Field, HttpUrl, TypeAdapter, field_validator


url_adapter = TypeAdapter(HttpUrl)


class PostingRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Message to publish across platforms"
    )

    @field_validator("message")
    @classmethod
    def validate_message_url(cls, value: str) -> str:
        urls = re.findall(r"https?://[^\s]+", value)

        if len(urls) != 1:
            raise ValueError("Message must contain exactly one URL")

        url = urls[0].rstrip(".,!?;:)")

        try:
            url_adapter.validate_python(url)
        except Exception:
            raise ValueError("Message must contain a valid HTTP or HTTPS URL")

        return value

class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: HttpUrl | None = None
    public_access: bool = False
    date: DateType | None = None
    time: TimeType | None = None
    error: str | None = None