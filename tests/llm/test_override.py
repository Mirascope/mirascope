from unittest.mock import patch

import pytest

from mirascope.core.base import (
    BaseCallResponse,
    CommonCallParams,
)
from mirascope.core.openai import OpenAICallParams
from mirascope.llm.llm_call import call
from mirascope.llm.llm_override import override


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


@pytest.fixture
def dummy_provider_agnostic_call():
    @call(provider="openai", model="gpt-4o-mini")
    def dummy_sync_function(book: str) -> str: ...

    return dummy_sync_function


def test_override_error_if_only_provider(dummy_provider_agnostic_call):
    with pytest.raises(ValueError, match="must also be specified"):
        override(  # pyright: ignore [reportCallIssue]
            provider_agnostic_call=dummy_provider_agnostic_call,
            provider="anthropic",
            model=None,  # pyright: ignore [reportArgumentType]
            call_params=None,
        )


def test_override_with_model(dummy_provider_agnostic_call):
    with patch("mirascope.llm.llm_override._call") as mock_call:
        override(
            provider_agnostic_call=dummy_provider_agnostic_call,
            provider="openai",
            model="overridden-model",
            call_params=CommonCallParams(),
        )
        mock_call.assert_called_once()
        _, kwargs = mock_call.call_args
        assert kwargs["provider"] == "openai"
        assert kwargs["model"] == "overridden-model"


def test_override_with_callparams_override(dummy_provider_agnostic_call):
    new_call_params = OpenAICallParams(temperature=0.7, max_tokens=1111)
    with patch("mirascope.llm.llm_override._call") as mock_call:
        override(  # pyright: ignore [reportCallIssue]
            provider_agnostic_call=dummy_provider_agnostic_call,
            provider="openai",
            model=None,  # pyright: ignore [reportArgumentType]
            call_params=new_call_params,
        )
        mock_call.assert_called_once()
        _, kwargs = mock_call.call_args
        assert kwargs["call_params"] is new_call_params


def test_override_with_client(dummy_provider_agnostic_call):
    new_client = object()
    with patch("mirascope.llm.llm_override._call") as mock_call:
        override(
            provider_agnostic_call=dummy_provider_agnostic_call,
            provider="openai",
            model="overridden-model",
            call_params=CommonCallParams(),
            client=new_client,
        )
        mock_call.assert_called_once()
        _, kwargs = mock_call.call_args
        assert kwargs["client"] is new_client
