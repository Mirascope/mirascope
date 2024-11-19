from typing import ClassVar, Literal

import requests
from pydantic import Field

from mirascope.tools.base import ConfigurableTool, _ConfigurableToolConfig


class RequestsConfig(_ConfigurableToolConfig):
    """Configuration for HTTP requests"""

    timeout: int = Field(default=5, description="Request timeout in seconds")


class Requests(ConfigurableTool):
    """Tool for making HTTP requests with built-in requests library."""

    __configurable_tool_config__ = RequestsConfig()

    __prompt_usage_description__: ClassVar[str] = """
    - `Requests`: Makes HTTP requests to web URLs using requests library
        - Supports common HTTP methods (GET, POST, PUT, DELETE)
        - Accepts custom headers and request data
        - Returns response text content
        - Automatically raises for HTTP errors (4xx, 5xx)
        - Returns error message if request fails
        - Configurable timeout for all requests
    """
    url: str = Field(..., description="URL to request")
    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(
        "GET", description="HTTP method"
    )
    data: dict | None = Field(None, description="Data to send with POST/PUT requests")
    headers: dict | None = Field(None, description="Request headers")

    def call(self) -> str:
        """Make an HTTP request to the given URL.

        Returns:
            str: Response text content if successful, error message if request fails
        """
        try:
            response = requests.request(
                method=self.method,
                url=self.url,
                json=self.data,
                headers=self.headers,
                timeout=self._get_config().timeout,
            )
            response.raise_for_status()
            return response.text

        except Exception as e:
            return f"{type(e)}: Failed to extract content from URL {self.url}"
