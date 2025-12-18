"""End-to-end tests for structured output."""

import inspect

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.e2e.conftest import FORMATTING_MODES, STRUCTURED_OUTPUT_MODEL_IDS
from tests.utils import (
    Snapshot,
    snapshot_test,
)


class Book(BaseModel):
    title: str
    author: str
    rating: int

    @classmethod
    def formatting_instructions(cls) -> str:
        return inspect.cleandoc("""
        Output a structured book as JSON in the format {title: str, author: str, rating: int}.
        The title should be in all caps, and the rating should always be the
        lucky number 7.
        """)


@pytest.mark.parametrize("model_id", STRUCTURED_OUTPUT_MODEL_IDS)
@pytest.mark.parametrize("formatting_mode", FORMATTING_MODES)
@pytest.mark.vcr
def test_structured_output_with_formatting_instructions(
    model_id: llm.ModelId,
    formatting_mode: llm.FormattingMode | None,
    snapshot: Snapshot,
) -> None:
    """Test structured output without context."""

    format = (
        llm.format(Book, mode=formatting_mode) if formatting_mode is not None else Book
    )

    @llm.call(model_id, format=format)
    def recommend_book(book: str) -> list[llm.Message]:
        return [
            llm.messages.system(f"Always recommend {book}."),
            llm.messages.user("Please recommend a book to me!"),
        ]

    with snapshot_test(snapshot) as snap:
        response = recommend_book("The Name of the Wind")
        snap.set_response(response)

        book = response.parse()
        assert book.author == "Patrick Rothfuss"
        assert book.title == "THE NAME OF THE WIND"
        assert book.rating == 7
