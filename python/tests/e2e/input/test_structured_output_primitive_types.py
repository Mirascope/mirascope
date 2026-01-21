"""End-to-end tests for structured output."""

import pytest
from pydantic import BaseModel, Field

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
    rating: int = Field(description="For testing purposes, the rating should be 7")


@pytest.mark.parametrize("model_id", MODEL_IDS)
@pytest.mark.vcr
def test_structured_output_with_primitive_types_list(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test a list of BaseModels"""

    @llm.call(model_id, format=list[Book])
    def recommend_book() -> str:
        return "Please recommend three books to me!"

    with snapshot_test(snapshot) as snap:
        response = recommend_book()
        snap.set_response(response)

        books = response.parse()
        assert len(books) == 3


@pytest.mark.parametrize("model_id", MODEL_IDS)
@pytest.mark.vcr
def test_structured_output_with_primitive_types_int(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test outputting an integer"""

    @llm.call(model_id, format=int)
    def lucky_number() -> str:
        return "Please choose a lucky number between 1 and 100"

    with snapshot_test(snapshot) as snap:
        response = lucky_number()
        snap.set_response(response)

        num = response.parse()
        assert int(num) == num
