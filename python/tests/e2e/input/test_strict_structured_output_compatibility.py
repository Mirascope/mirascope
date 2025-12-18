"""End-to-end tests for strict structured output compatibility across models."""

import pytest
from pydantic import BaseModel

from mirascope import llm
from tests.utils import (
    Snapshot,
    snapshot_test,
)


class IntegerAdditionResponse(BaseModel):
    """A simple response for testing."""

    integer_a: int
    integer_b: int
    answer: int


# Models that support strict structured outputs
MODELS_WITH_STRICT_SUPPORT: list[llm.ModelId] = [
    "anthropic/claude-sonnet-4-5",
    # TODO: Add models with strict support
]

# Models that do not support strict structured outputs
MODELS_WITHOUT_STRICT_SUPPORT: list[llm.ModelId] = [
    "anthropic/claude-sonnet-4",
    # TODO: Add openai and google models
]


@pytest.mark.parametrize("model_id", MODELS_WITH_STRICT_SUPPORT)
@pytest.mark.vcr
def test_strict_mode(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that strict mode works for models that support it."""

    @llm.call(
        model_id,
        format=llm.format(IntegerAdditionResponse, mode="strict"),
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with snapshot_test(snapshot) as snap:
        response = get_answer("What is 2 + 2?")
        snap.set_response(response)

        result = response.parse()
        assert isinstance(result, IntegerAdditionResponse)
        assert result.answer == 4


@pytest.mark.parametrize("model_id", MODELS_WITH_STRICT_SUPPORT)
@pytest.mark.vcr
def test_strict_mode_streamed(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that streaming strict mode works for models that support it."""

    @llm.call(
        model_id,
        format=llm.format(IntegerAdditionResponse, mode="strict"),
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with snapshot_test(snapshot) as snap:
        response = get_answer.stream("What is 2 + 2?")
        response.finish()
        snap.set_response(response)

        result = response.parse()
        assert isinstance(result, IntegerAdditionResponse)
        assert result.answer == 4


@pytest.mark.parametrize("model_id", MODELS_WITH_STRICT_SUPPORT)
@pytest.mark.vcr
def test_strict_mode_with_thinking(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that strict mode works with thinking."""

    @llm.call(
        model_id,
        format=llm.format(IntegerAdditionResponse, mode="strict"),
        thinking=True,
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with snapshot_test(snapshot) as snap:
        response = get_answer("What is 2 + 2?")
        snap.set_response(response)

        result = response.parse()
        assert isinstance(result, IntegerAdditionResponse)
        assert result.answer == 4


@pytest.mark.parametrize("model_id", MODELS_WITH_STRICT_SUPPORT)
@pytest.mark.vcr
def test_strict_mode_with_streamed_thinking(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that strict mode works with thinking and streaming ."""

    @llm.call(
        model_id,
        format=llm.format(IntegerAdditionResponse, mode="strict"),
        thinking=True,
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with snapshot_test(snapshot) as snap:
        response = get_answer.stream("What is 2 + 2?")
        response.finish()
        snap.set_response(response)

        result = response.parse()
        assert isinstance(result, IntegerAdditionResponse)
        assert result.answer == 4


@pytest.mark.parametrize("model_id", MODELS_WITHOUT_STRICT_SUPPORT)
def test_strict_mode_unsupported_models(
    model_id: llm.ModelId,
) -> None:
    """Test that strict mode raises FormattingModeNotSupportedError for unsupported models."""

    @llm.call(
        model_id,
        format=llm.format(IntegerAdditionResponse, mode="strict"),
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with pytest.raises(llm.FormattingModeNotSupportedError) as exc_info:
        get_answer("What is 2 + 2?")

    error = exc_info.value
    assert error.formatting_mode == "strict"
    assert error.model_id == model_id
    assert error.provider_id == model_id.split("/")[0]
