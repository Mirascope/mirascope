from typing import ClassVar, Literal

import requests
from pydantic import Field

from mirascope.tools.base import ConfigurableTool, _ToolConfig


class RequestsConfig(_ToolConfig):
    """Configuration for HTTP requests"""

    timeout: int = Field(default=5, description="Request timeout in seconds")

    @classmethod
    def from_env(cls) -> "RequestsConfig":
        return cls()


class Requests(ConfigurableTool):
    """Tool for making HTTP requests to fetch content from URLs."""

    __config__ = RequestsConfig()

    __prompt_usage_description__: ClassVar[str] = """
    Use this tool to make HTTP requests to web URLs.
    """
    url: str = Field(..., description="URL to request")
    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(
        "GET", description="HTTP method"
    )
    data: dict | None = Field(None, description="Data to send with POST/PUT requests")
    headers: dict | None = Field(None, description="Request headers")

    def call(self) -> str:
        """Make an HTTP request to the given URL."""
        try:
            response = requests.request(
                method=self.method,
                url=self.url,
                json=self.data,
                headers=self.headers,
                timeout=self._config().timeout,
            )
            response.raise_for_status()
            return response.text

        except Exception as e:
            return f"{type(e)}: Failed to extract content from URL {self.url}"
