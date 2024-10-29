from typing import ClassVar, Literal

import httpx
from pydantic import Field

from mirascope.tools.base import ConfigurableTool, _ToolConfig


class HTTPXConfig(_ToolConfig):
    """Configuration for HTTPX requests"""

    timeout: int = Field(
        default=5,
        description="Request timeout in seconds. When None, no timeout will be applied",
    )


class HTTPX(ConfigurableTool):
    """Tool to interact with web APIs using HTTPX. Provide a URL, method and optional data."""

    __config__ = HTTPXConfig()

    __prompt_usage_description__: ClassVar[str] = """
    Use this tool to make HTTP requests to web URLs using HTTPX.
    Supports standard HTTP methods and automatically handles encoding/decoding.
    """
    url: str = Field(..., description="URL to request")
    method: Literal["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"] = Field(
        "GET", description="HTTP method to use"
    )
    data: dict | None = Field(
        None, description="Form data to send with POST/PUT requests"
    )
    json_: dict | None = Field(
        None, description="JSON data to send with POST/PUT requests", alias="json"
    )
    params: dict | None = Field(
        None, description="URL parameters to include in the request"
    )
    headers: dict | None = Field(None, description="Request headers")
    follow_redirects: bool = Field(
        True, description="Whether to follow redirects automatically"
    )

    def call(self) -> str:
        """
        Make an HTTP request to the given URL using HTTPX.

        Returns:
            str: Response text if successful, error message if request fails
        """
        try:
            # Configure timeout - None means no timeout
            timeout = (
                httpx.Timeout(self._config().timeout)
                if self._config().timeout is not None
                else None
            )

            # Make request using context manager for proper resource cleanup
            with httpx.Client(timeout=timeout) as client:
                response = client.request(
                    method=self.method,
                    url=self.url,
                    params=self.params,
                    json=self.json_,
                    data=self.data,
                    headers=self.headers,
                    follow_redirects=self.follow_redirects,
                )
                response.raise_for_status()
                return response.text

        except httpx.RequestError as e:
            return f"Request error occurred: {str(e)}"
        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e.response.status_code} - {str(e)}"
        except Exception as e:
            return f"{type(e).__name__}: Failed to make request to {self.url}"


class AsyncHTTPXConfig(_ToolConfig):
    """Configuration for async HTTPX requests"""

    timeout: int = Field(
        default=5,
        description="Request timeout in seconds. When None, no timeout will be applied",
    )


class AsyncHTTPX(ConfigurableTool):
    """
    Async tool to interact with web APIs using HTTPX.
    Provides asynchronous HTTP requests with configurable timeout and error handling.
    """

    __config__ = AsyncHTTPXConfig()

    __prompt_usage_description__: ClassVar[str] = """
    Use this tool to make asynchronous HTTP requests to web URLs using HTTPX.
    Supports standard HTTP methods and automatically handles encoding/decoding.
    """
    url: str = Field(..., description="URL to request")
    method: Literal["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"] = Field(
        "GET", description="HTTP method to use"
    )
    data: dict | None = Field(
        None, description="Form data to send with POST/PUT requests"
    )
    json_: dict | None = Field(
        None, description="JSON data to send with POST/PUT requests", alias="json"
    )
    params: dict | None = Field(
        None, description="URL parameters to include in the request"
    )
    headers: dict | None = Field(None, description="Request headers")
    follow_redirects: bool = Field(
        True, description="Whether to follow redirects automatically"
    )

    async def call(self) -> str:
        """
        Make an asynchronous HTTP request to the given URL using HTTPX.

        Returns:
            str: Response text if successful, error message if request fails
        """
        try:
            # Configure timeout - None means no timeout
            timeout = (
                httpx.Timeout(self._config().timeout)
                if self._config().timeout is not None
                else None
            )

            # Make async request using async context manager
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=self.method,
                    url=self.url,
                    params=self.params,
                    json=self.json_,
                    data=self.data,
                    headers=self.headers,
                    follow_redirects=self.follow_redirects,
                )
                response.raise_for_status()
                return response.text

        except httpx.RequestError as e:
            return f"Request error occurred: {str(e)}"
        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e.response.status_code} - {str(e)}"
        except Exception as e:
            return f"{type(e).__name__}: Failed to make request to {self.url}"
