from typing import Literal

from mirascope.core import BaseToolKit, openai, prompt_template, toolkit_tool


class BookTools(BaseToolKit):
    __namespace__ = "book_tools"
    reading_level: Literal["beginner", "intermediate", "advanced"]

    @toolkit_tool
    def recommend_book_by_level(self, title: str, author: str) -> str:
        """Recommend a book based on reading level.

        Reading Level: {self.reading_level}
        """
        return f"{title} by {author}"


toolkit = BookTools(reading_level="beginner")


@openai.call("gpt-4o-mini", tools=toolkit.create_tools())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("science")
print(response.content)
# > Astrophysics for Young People in a Hurry by Neil deGrasse Tyson
