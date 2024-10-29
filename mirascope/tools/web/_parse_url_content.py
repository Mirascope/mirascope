from __future__ import annotations

import re
from typing import ClassVar, TypeVar

import requests
from bs4 import BeautifulSoup
from pydantic import Field

from mirascope.tools.base import ConfigurableTool, _ToolConfig


class ParseURLConfig(_ToolConfig):
    """Configuration for URL content parsing"""

    parser: str = Field(
        "html.parser",
        description="parser to use for parsing HTML content in BeautifulSoup",
        examples=["html.parser", "lxml", "lxml-xml", "html5lib"],
    )
    timeout: int = Field(
        default=5,
        description="Timeout in seconds for URL request",
    )

    @classmethod
    def from_env(cls) -> ParseURLConfig:
        """No environment variables needed for URL parsing"""
        return cls()  # pyright: ignore [reportCallIssue]


_ToolSchemaT = TypeVar("_ToolSchemaT")


class ParseURLContent(ConfigurableTool[ParseURLConfig, _ToolSchemaT]):
    """Tool for parsing and extracting main content from URLs.
    Fetches content from URL, removes unnecessary elements like scripts, styles, navigation, etc.,
    and returns clean text content from the webpage's main body.
    """

    __config__ = ParseURLConfig()  # pyright: ignore [reportCallIssue]
    __prompt_usage_description__: ClassVar[str] = """
    This tool fetches and parses content from a URL:
    1. Fetches HTML content from the provided URL
    2. Removes all unwanted elements (scripts, styles, navigation, etc.)
    3. Attempts to find the main content section
    4. If no main content section is found, extracts all text content
    5. Returns cleaned and formatted text content

    Output Format:
    Returns the main content as clean text.
    If any errors occur during fetching or parsing, error messages are included.

    Common use cases:
    - Extracting article content from web pages
    - Getting readable content from blog posts
    - Parsing documentation pages to extract useful text
    """
    url: str = Field(..., description="URL to fetch and parse")

    def call(self) -> str:
        """Fetch and parse content from the URL."""
        try:
            # Fetch content from URL
            response = requests.get(
                self.url,
                timeout=self._config().timeout,
            )
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.text, self._config().parser)

            # Remove unwanted tags
            unwanted_tags = ["script", "style", "nav", "header", "footer", "aside"]
            for tag in unwanted_tags:
                for element in soup.find_all(tag):
                    element.decompose()

            # Find main content section
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_=re.compile("content|main"))
            )

            # Extract and clean text
            if main_content:
                text = main_content.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)

            # Remove empty lines and format
            lines = (line.strip() for line in text.splitlines())
            content = "\n".join(line for line in lines if line)

            if not content:
                return "No content found on the page"
            return content

        except requests.RequestException as e:
            return f"Failed to fetch content from URL: {str(e)}"
        except Exception as e:  # pragma: no cover
            return f"{type(e).__name__}: Failed to parse content from URL"
