import xml.etree.ElementTree as ET
from typing import Annotated

from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    # title and summary will be auto-populated from the call args
    title: Annotated[str, llm.formatting.FromCallArgs()]
    author: Annotated[str, llm.formatting.FromCallArgs()]
    themes: list[str]

    @classmethod
    def parse(cls, response: llm.Response, *, title: str, author: str) -> "Book":
        """Parse XML response into a Book instance."""

        try:
            # Wrap content in a root element for parsing
            wrapped_xml = f"<root>{str(response)}</root>"
            root = ET.fromstring(wrapped_xml)

            # Extract themes
            themes = []
            for theme_element in root.findall("theme"):
                if theme_element.text:
                    themes.append(theme_element.text.strip())

            return Book(title=title, author=author, themes=themes)
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML response: {e}")

    @classmethod
    def formatting_instructions(cls):
        return """Structure your response according to the following xml format:
        
        <theme>{theme1}</theme>
        <theme>{theme2}</theme>
        ...

        For example, for The Name of the Wind by Patrick Rothfuss:
        <theme>Power of Stories and Names</theme>
        <theme>Coming of Age / Hero's Journey</theme>
        <theme>Magic and Education</theme>
        <theme>Music and Performance</theme>
        """


@llm.call("openai:gpt-4o-mini", format=Book)
def summarize_book(title: str, author: str):
    return f"Extract themes from {title} by {author}"


def main():
    response: llm.Response[Book] = summarize_book(
        "The Name of the Wind", "Patrick Rothfuss"
    )
    book: Book = response.format()
    print(book)


main()
