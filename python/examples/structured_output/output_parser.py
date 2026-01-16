import re
import xml.etree.ElementTree as ET

from pydantic import BaseModel

from mirascope import llm


class Book(BaseModel):
    title: str
    rating: int


@llm.output_parser(
    formatting_instructions=(
        "Return the book as XML: <book><title>Book Title</title><rating>7</rating></book>"
    )
)
def parse_book_xml(response: llm.AnyResponse) -> Book:
    text = "".join(t.text for t in response.texts)
    # Strip markdown code fences if present
    xml_match = re.search(r"<book>.*</book>", text, re.DOTALL)
    xml_text = xml_match.group(0) if xml_match else text
    root = ET.fromstring(xml_text)
    return Book(
        title=root.findtext("title") or "",
        rating=int(root.findtext("rating") or "0"),
    )


@llm.call("openai/gpt-5-mini", format=parse_book_xml)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
book: Book = response.parse()
print(f"{book.title}, rating: {book.rating}")
