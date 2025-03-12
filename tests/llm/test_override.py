from unittest.mock import MagicMock, patch

import pytest

from mirascope.core.base import (
    BaseCallResponse,
    CommonCallParams,
)
from mirascope.core.openai import OpenAICallParams
from mirascope.llm._override import override


class ConcreteMockResponse(BaseCallResponse):
    @property
    def content(self): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def finish_reasons(self): ...

    @property
    def model(self): ...

    @property
    def id(self): ...

    @property
    def usage(self): ...

    @property
    def input_tokens(self): ...

    @property
    def output_tokens(self): ...

    @property
    def cost(self): ...

    @property
    def message_param(self): ...  # pyright: ignore [reportIncompatibleVariableOverride]

    @property
    def tools(self): ...  # pyright: ignore [reportIncompatibleVariableOverride]

    @property
    def tool(self): ...  # pyright: ignore [reportIncompatibleVariableOverride]

    @classmethod
    def tool_message_params(cls, tools_and_outputs): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def common_finish_reasons(self): ...

    @property
    def common_message_param(self): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def common_tools(self): ...

    @property
    def common_usage(self): ...

    def common_construct_call_response(self): ...

    def common_construct_message_param(self, tool_calls, content): ...


def test_override_error_if_only_provider():
    with pytest.raises(
        ValueError,
        match="Provider and model must both be overridden if either is overridden.",
    ):
        override(  # pyright: ignore [reportCallIssue]
            provider_agnostic_call=MagicMock(),
            provider="anthropic",
            model=None,  # pyright: ignore [reportArgumentType]
            call_params=None,
        )


def test_override_with_model():
    with patch("mirascope.llm._override._context") as mock_context:
        fn = override(
            provider_agnostic_call=MagicMock(),
            provider="openai",
            model="overridden-model",
            call_params=CommonCallParams(),
        )
        fn()
        mock_context.assert_called_once()
        _, kwargs = mock_context.call_args
        assert kwargs["provider"] == "openai"
        assert kwargs["model"] == "overridden-model"


def test_override_with_callparams_override():
    new_call_params = OpenAICallParams(temperature=0.7, max_tokens=1111)
    with patch("mirascope.llm._override._context") as mock_context:
        fn = override(  # pyright: ignore [reportCallIssue]
            provider_agnostic_call=MagicMock(),
            provider="openai",
            model="gpt-4o-mini",  # pyright: ignore [reportArgumentType]
            call_params=new_call_params,
        )
        fn()
        mock_context.assert_called_once()
        _, kwargs = mock_context.call_args
        assert kwargs["call_params"] is new_call_params


def test_override_with_client():
    new_client = object()
    with patch("mirascope.llm._override._context") as mock_context:
        fn = override(
            provider_agnostic_call=MagicMock(),
            provider="openai",
            model="overridden-model",
            call_params=CommonCallParams(),
            client=new_client,
        )
        fn()
        mock_context.assert_called_once()
        _, kwargs = mock_context.call_args
        assert kwargs["client"] is new_client


@pytest.mark.asyncio
async def test_override_with_async_gather():
    """Test that override works correctly with asyncio.gather."""
    import asyncio

    # Mock the provider_agnostic_call
    async def mock_async_fn():
        return MagicMock()

    # Mock the _context to capture the context parameters
    with patch("mirascope.llm._override._context") as mock_context:
        # Set up the mock to record calls and return a context manager
        context_manager = MagicMock()
        context_manager.__enter__ = MagicMock(return_value=None)
        context_manager.__exit__ = MagicMock(return_value=None)
        mock_context.return_value = context_manager

        # Create two overridden functions with different providers/models
        openai_fn = override(
            provider_agnostic_call=mock_async_fn,
            provider="openai",
            model="gpt-4o-mini",
            call_params=None,
        )

        anthropic_fn = override(
            provider_agnostic_call=mock_async_fn,
            provider="anthropic",
            model="claude-3-5-sonnet",
            call_params=None,
        )

        # Create futures for both functions
        openai_future = openai_fn()
        anthropic_future = anthropic_fn()

        # Await both futures together
        await asyncio.gather(openai_future, anthropic_future)

        # Check that both contexts were created with the correct parameters
        assert mock_context.call_count == 2

        # Extract the call arguments
        call_args_list = mock_context.call_args_list

        # First call should be for openai
        _, kwargs1 = call_args_list[0]
        assert kwargs1["provider"] == "openai"
        assert kwargs1["model"] == "gpt-4o-mini"

        # Second call should be for anthropic
        _, kwargs2 = call_args_list[1]
        assert kwargs2["provider"] == "anthropic"
        assert kwargs2["model"] == "claude-3-5-sonnet"
