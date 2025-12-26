"""End-to-end tests for a LLM call with audio input."""

from collections.abc import Callable
from typing import Annotated, Any

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
def test_from_call_args_missing_args(
    model_id: llm.ModelId,
) -> None:
    class Book(BaseModel):
        """A book with title, author, and summary."""

        title: Annotated[str, llm.FromCallArgs()]
        author: Annotated[str, llm.FromCallArgs()]
        summary: str

    @llm.call(model_id, format=Book)
    def summarize_book(title: str) -> str:
        # Missing author
        return f"Summarize the book {title}"

    with pytest.raises(ValueError, match="Missing required call arguments"):
        summarize_book("The Name of the Wind")


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
def test_from_call_args_unserializable(
    model_id: llm.ModelId,
) -> None:
    class Output(BaseModel):
        """A book with title, author, and summary."""

        arg: Annotated[Any, llm.FromCallArgs()]
        summary: str

    @llm.call(model_id, format=Output)
    def call_with_fn_arg(arg: Callable[..., None]) -> str:
        return "What is the meaning of life?"

    def a_function() -> None: ...

    with pytest.raises(ValueError, match="is not JSON-serializable"):
        call_with_fn_arg(a_function)
