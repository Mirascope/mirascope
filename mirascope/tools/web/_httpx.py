from typing import ClassVar, Literal

import httpx
from pydantic import Field

from mirascope.tools.base import ConfigurableTool, _ConfigurableToolConfig


class HTTPXConfig(_ConfigurableToolConfig):
    """Configuration for HTTPX requests"""

    timeout: int = Field(
        default=5,
        description="Request timeout in seconds. When None, no timeout will be applied",
    )


class _BaseHTTPX(ConfigurableTool):
    """Tool for making HTTP requests using HTTPX with configurable timeout and error handling."""

    __configurable_tool_config__ = HTTPXConfig()

    __prompt_usage_description__: ClassVar[str] = """
    - `HTTPX`: Makes HTTP requests to web URLs with HTTPX client
        - Supports standard HTTP methods (GET, POST, PUT, DELETE, etc.)
        - Allows configuration of request data, headers, and parameters
        - Automatically handles encoding/decoding of request/response content
        - Handles redirects automatically (configurable)
        - Returns response text or error message on failure
        - Configurable timeout for requests
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


class HTTPX(_BaseHTTPX):
    def call(self) -> str:
        """
        Make an HTTP request to the given URL using HTTPX.

        Returns:
            str: Response text if successful, error message if request fails
        """
        try:
            # Configure timeout - None means no timeout
            timeout = (
                httpx.Timeout(self._get_config().timeout)
                if self._get_config().timeout is not None
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


class AsyncHTTPX(_BaseHTTPX):
    async def call(self) -> str:
        """
        Make an asynchronous HTTP request to the given URL using HTTPX.

        Returns:
            str: Response text if successful, error message if request fails
        """
        try:
            # Configure timeout - None means no timeout
            timeout = (
                httpx.Timeout(self._get_config().timeout)
                if self._get_config().timeout is not None
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
