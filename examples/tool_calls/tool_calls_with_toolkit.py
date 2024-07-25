import os
from typing import ClassVar, Literal

from mirascope.core import openai
from mirascope.core.base import BaseToolKit, toolkit_tool

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class BookRecommendationToolKit(BaseToolKit):
    """A toolkit for recommending books."""

    __namespace__: ClassVar[str | None] = "book_tools"
    reading_level: Literal["beginner", "advanced"]

    @toolkit_tool
    def format_book(self, title: str, author: str) -> str:
        """Returns the title and author of a book nicely formatted.

        Reading level: {self.reading_level}
        """
        return f"{title} by {author}"


@openai.call(model="gpt-4o")
def recommend_book(
    genre: str, reading_level: Literal["beginner", "advanced"]
) -> openai.OpenAIDynamicConfig:
    """Recommend a {genre} book."""
    toolkit = BookRecommendationToolKit(reading_level=reading_level)
    return {"tools": toolkit.create_tools()}


response = recommend_book(genre="fantasy", reading_level="beginner")
if tool := response.tool:
    output = tool.call()
    print(output)
    # > The Name of the Wind by Patrick Rothfuss
else:
    print(response.content)
    # > Sure! I would recommend...
