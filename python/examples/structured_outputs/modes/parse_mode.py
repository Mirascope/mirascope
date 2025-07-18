import xml.etree.ElementTree as ET
from typing import Any

from pydantic import BaseModel

from mirascope import llm


@llm.format(mode="parse")
class Book(BaseModel):
    title: str
    author: str
    themes: list[str]

    @classmethod
    def parse(cls, response: llm.Response, **kwargs: Any) -> "Book":
        """Parse XML response into a Book instance."""
        try:
            # Wrap content in a root element for parsing
            wrapped_xml = f"<root>{str(response)}</root>"
            root = ET.fromstring(wrapped_xml)

            # Extract title and author
            title = root.find("title")
            author = root.find("author")

            # Extract themes
            themes = []
            for theme_element in root.findall("theme"):
                if theme_element.text:
                    themes.append(theme_element.text.strip())

            return cls(
                title=title.text.strip() if title is not None and title.text else "",
                author=author.text.strip()
                if author is not None and author.text
                else "",
                themes=themes,
            )
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML response: {e}")

    @classmethod
    def formatting_instructions(cls):
        return """Structure your response according to the following xml format:
        
        <title>{title}</title>
        <author>{author}</author>
        <theme>{theme1}</theme>
        <theme>{theme2}</theme>
        ...

        For example:
        <title>The Name of the Wind</title>
        <author>Patrick Rothfuss</author>
        <theme>Power of Stories and Names</theme>
        <theme>Coming of Age / Hero's Journey</theme>
        <theme>Magic and Education</theme>
        <theme>Music and Performance</theme>
        """


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    response: llm.Response[None, Book] = recommend_book("fantasy")
    book: Book = response.format()

    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Themes: {book.themes}")


if __name__ == "__main__":
    main()
