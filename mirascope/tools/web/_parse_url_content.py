from __future__ import annotations

import re
from typing import ClassVar

import requests
from bs4 import BeautifulSoup
from pydantic import Field

from mirascope.tools.base import ConfigurableTool, _ConfigurableToolConfig


class ParseURLConfig(_ConfigurableToolConfig):
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


class ParseURLContent(ConfigurableTool[ParseURLConfig]):
    """Tool for parsing and extracting main content from URLs.

    Fetches content from URL, removes unnecessary elements like scripts, styles, navigation, etc.,
    and returns clean text content from the webpage's main body.
    """

    __configurable_tool_config__ = ParseURLConfig()  # pyright: ignore [reportCallIssue]
    __prompt_usage_description__: ClassVar[str] = """
    - `ParseURLContent`: Returns the given URL's main content as clean text
        - Fetches the raw HTML content for the given URL
        - Removes all unwanted elements (scripts, styles, navigation, etc.)
        - Attempts to find the main content section
        - If no main content section is found, extracts all text content
        - Returns cleaned and formatted text content
        - If any errors occur during fetching or parsing, and error message is returned.
    """

    url: str = Field(..., description="URL to fetch and parse")

    def call(self) -> str:
        """Fetch and parse content from the URL.

        Returns:
            str: Cleaned text content from the URL if successful, error message if parsing fails
        """
        try:
            # Fetch content from URL
            response = requests.get(
                self.url,
                timeout=self._get_config().timeout,
            )
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.text, self._get_config().parser)

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
