"""End-to-end tests for structured output."""

import re
import xml.etree.ElementTree as ET

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.utils import (
    Snapshot,
    snapshot_test,
)

# This behavior is largely model-agnostic, so we will test on just one model
# to reduce test bloat.
MODEL_IDS = ["anthropic/claude-haiku-4-5"]


class Book(BaseModel):
    title: str
    rating: int


@pytest.mark.parametrize("model_id", MODEL_IDS)
@pytest.mark.vcr
def test_structured_output_with_output_parser(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test using output parser"""

    instructions = (
        "Return book as XML: <book><title>Mistborn</title><rating>7</rating></book>"
    )

    @llm.output_parser(formatting_instructions=instructions)
    def parse_book(response: llm.AnyResponse) -> Book:
        text = "".join(t.text for t in response.texts)
        # Strip markdown code fences if present
        xml_match = re.search(r"<book>.*</book>", text, re.DOTALL)
        xml_text = xml_match.group(0) if xml_match else text
        root = ET.fromstring(xml_text)
        title = root.findtext("title") or ""
        rating = int(root.findtext("rating") or "0")
        return Book(title=title, rating=rating)

    @llm.call(model_id, format=parse_book)
    def recommend_book() -> str:
        return "The Name of the Wind, Rating 7"

    with snapshot_test(snapshot) as snap:
        response = recommend_book()
        snap.set_response(response)

        book: Book = response.parse()
        assert book.title == "The Name of the Wind"
        assert book.rating == 7
