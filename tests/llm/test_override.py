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
