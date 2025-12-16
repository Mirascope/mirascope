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
    "google/gemini-3-pro-preview",
    # TODO: Add models with strict support
]

# Models that do not support strict structured outputs
MODELS_WITHOUT_STRICT_SUPPORT: list[llm.ModelId] = [
    "anthropic/claude-sonnet-4",
    # TODO: Add openai and google models
]

# Models that support strict structured outputs but NOT with tools
MODELS_WITHOUT_STRICT_WITH_TOOLS_SUPPORT: list[llm.ModelId] = [
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
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


# ============= STRICT MODE WITH TOOLS TESTS =============


@pytest.mark.parametrize("model_id", MODELS_WITH_STRICT_SUPPORT)
@pytest.mark.vcr
def test_strict_mode_with_tools(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that strict mode with tools works for models that support it."""

    @llm.tool
    def customAdditionImplementation(a: int, b: int) -> int:
        """Perform computation on integers."""
        return a**2 + b**2

    @llm.call(
        model_id,
        tools=[customAdditionImplementation],
        format=llm.format(IntegerAdditionResponse, mode="strict"),
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with snapshot_test(snapshot) as snap:
        response = get_answer("What is 2 + 3, using the custom addition tool??")
        response = response.resume(response.execute_tools())
        snap.set_response(response)

        result = response.parse()
        assert isinstance(result, IntegerAdditionResponse)
        assert result.answer == 13


@pytest.mark.parametrize("model_id", MODELS_WITH_STRICT_SUPPORT)
@pytest.mark.vcr
def test_strict_mode_with_tools_streamed(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that streaming strict mode with tools works for models that support it."""

    @llm.tool
    def customAdditionImplementation(a: int, b: int) -> int:
        """Perform computation on integers."""
        return a**2 + b**2

    @llm.call(
        model_id,
        tools=[customAdditionImplementation],
        format=llm.format(IntegerAdditionResponse, mode="strict"),
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with snapshot_test(snapshot) as snap:
        response = get_answer.stream("What is 2 + 3, using the custom addition tool?")
        response.finish()
        response = response.resume(response.execute_tools())
        response.finish()
        snap.set_response(response)

        result = response.parse()
        assert isinstance(result, IntegerAdditionResponse)
        assert result.answer == 13


@pytest.mark.parametrize("model_id", MODELS_WITHOUT_STRICT_WITH_TOOLS_SUPPORT)
def test_strict_mode_with_tools_unsupported(
    model_id: llm.ModelId,
) -> None:
    """Test that strict mode with tools raises FeatureNotSupportedError for unsupported models."""

    @llm.tool
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    @llm.call(
        model_id,
        tools=[add_numbers],
        format=llm.format(IntegerAdditionResponse, mode="strict"),
    )
    def get_answer(question: str) -> str:
        return f"Answer this question: {question}"

    with pytest.raises(llm.FeatureNotSupportedError) as exc_info:
        get_answer("What is 2 + 3, using the custom addition tool?")

    error = exc_info.value
    assert "strict" in error.feature.lower() or "tool" in error.feature.lower()
    assert error.provider_id == model_id.split("/")[0]
