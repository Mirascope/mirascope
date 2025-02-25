import xml.etree.ElementTree as ET

from mirascope import llm, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str
    year: int
    summary: str


def parse_book_xml(response: llm.CallResponse) -> Book | None:
    try:
        root = ET.fromstring(response.content)
        if (node := root.find("title")) is None or not (title := node.text):
            raise ValueError("Missing title")
        if (node := root.find("author")) is None or not (author := node.text):
            raise ValueError("Missing author")
        if (node := root.find("year")) is None or not (year := node.text):
            raise ValueError("Missing year")
        if (node := root.find("summary")) is None or not (summary := node.text):
            raise ValueError("Missing summary")
        return Book(title=title, author=author, year=int(year), summary=summary)
    except (ET.ParseError, ValueError) as e:
        print(f"Error parsing XML: {e}")
        return None


@llm.call(provider="openai", model="gpt-4o-mini", output_parser=parse_book_xml)
@prompt_template(
    """
    Recommend a {genre} book. Provide the information in the following XML format:
    <book>
        <title>Book Title</title>
        <author>Author Name</author>
        <year>Publication Year</year>
        <summary>Brief summary of the book</summary>
    </book>
                 
    Output ONLY the XML and no other text.
    """
)
def recommend_book(genre: str): ...


book = recommend_book("science fiction")
if book:
    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Year: {book.year}")
    print(f"Summary: {book.summary}")
else:
    print("Failed to parse the recommendation.")
