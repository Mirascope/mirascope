from functools import cached_property
from typing import Any
from unittest.mock import Mock, patch

import pytest
from pydantic import computed_field

from mirascope.core.base import (
    BaseCallKwargs,
    BaseCallParams,
    BaseCallResponse,
    BaseStream,
    BaseTool,
    Metadata,
)
from mirascope.core.base.types import FinishReason
from mirascope.llm.call_response import CallResponse
from mirascope.llm.llm_call import _get_provider_call, _wrap_result, call
from mirascope.llm.stream import Stream


class DummyCallParams(BaseCallParams): ...


class ConcreteResponse(BaseCallResponse[Any, Any, Any, Any, Any, Any, Any]):
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

    @computed_field
    @cached_property
    def message_param(self) -> Any: ...

    @computed_field
    @cached_property
    def tools(self) -> Any: ...

    @computed_field
    @cached_property
    def tool(self) -> Any: ...

    @classmethod
    def tool_message_params(cls, tools_and_outputs: list[tuple[BaseTool, str]]): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        # Just return ["stop"] as a string to avoid AttributeError
        return ["stop"]

    @property
    def common_message_param(self): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def common_tools(self): ...

    @property
    def common_usage(self): ...

    def common_construct_call_response(self): ...

    def common_construct_message_param(
        self, tool_calls: list | None, content: str | None
    ): ...


class ConcreteStream(BaseStream):
    def _construct_message_param(self, *args, **kwargs): ...

    def construct_call_response(self): ...

    @property
    def cost(self): ...


def test_wrap_result():
    resp = ConcreteResponse(
        metadata=Metadata(),
        response={},
        tool_types=None,
        prompt_template=None,
        fn_args={},
        dynamic_config={},
        messages=[],
        call_params=DummyCallParams(),
        call_kwargs=BaseCallKwargs(),
        user_message_param=None,
        start_time=0,
        end_time=0,
    )
    result = _wrap_result(resp)
    assert isinstance(result, CallResponse)
    assert result.finish_reasons == ["stop"]

    strm = ConcreteStream(
        stream=Mock(),
        metadata=Metadata(),
        tool_types=Mock(),
        call_response_type=Mock(),  # pyright: ignore [reportArgumentType]
        model=Mock(),  # pyright: ignore [reportArgumentType]
        prompt_template=Mock(),
        fn_args={},
        dynamic_config={},
        messages=[],
        call_params=DummyCallParams(),
        call_kwargs=BaseCallKwargs(),
    )
    result_stream = _wrap_result(strm)
    assert isinstance(result_stream, Stream)

    output = _wrap_result("parsed output")
    assert isinstance(output, str)
    assert output == "parsed output"


def test_get_provider_call_unsupported():
    with pytest.raises(ValueError, match="Unsupported provider: bad_provider"):
        _get_provider_call("bad_provider")  # pyright: ignore [reportArgumentType]


# Use `new=` instead of `return_value=` so that the call function is replaced by a string directly.
def test_get_provider_call_anthropic():
    with patch("mirascope.core.anthropic.anthropic_call", new="anthropic_mock"):
        func = _get_provider_call("anthropic")
        assert func == "anthropic_mock"


def test_get_provider_call_azure():
    with patch("mirascope.core.azure.azure_call", new="azure_mock"):
        func = _get_provider_call("azure")
        assert func == "azure_mock"


def test_get_provider_call_bedrock():
    with patch("mirascope.core.bedrock.bedrock_call", new="bedrock_mock"):
        func = _get_provider_call("bedrock")
        assert func == "bedrock_mock"


def test_get_provider_call_cohere():
    with patch("mirascope.core.cohere.cohere_call", new="cohere_mock"):
        func = _get_provider_call("cohere")
        assert func == "cohere_mock"


def test_get_provider_call_gemini():
    with patch("mirascope.core.gemini.gemini_call", new="gemini_mock"):
        func = _get_provider_call("gemini")
        assert func == "gemini_mock"


def test_get_provider_call_groq():
    with patch("mirascope.core.groq.groq_call", new="groq_mock"):
        func = _get_provider_call("groq")
        assert func == "groq_mock"


def test_get_provider_call_litellm():
    with patch("mirascope.core.litellm.litellm_call", new="litellm_mock"):
        func = _get_provider_call("litellm")
        assert func == "litellm_mock"


def test_get_provider_call_mistral():
    with patch("mirascope.core.mistral.mistral_call", new="mistral_mock"):
        func = _get_provider_call("mistral")
        assert func == "mistral_mock"


def test_get_provider_call_openai():
    with patch("mirascope.core.openai.openai_call", new="openai_mock"):
        func = _get_provider_call("openai")
        assert func == "openai_mock"


def test_get_provider_call_vertex():
    with patch("mirascope.core.vertex.vertex_call", new="vertex_mock"):
        func = _get_provider_call("vertex")
        assert func == "vertex_mock"


def test_call_decorator_sync():
    def dummy_provider_call(
        model,
        stream,
        tools,
        response_model,
        output_parser,
        json_mode,
        call_params,
        client,
    ):
        def wrapper(fn):
            def inner(*args, **kwargs):
                return ConcreteResponse(
                    metadata=Metadata(),
                    response={},
                    tool_types=None,
                    prompt_template=None,
                    fn_args={},
                    dynamic_config={},
                    messages=[],
                    call_params=DummyCallParams(),
                    call_kwargs=BaseCallKwargs(),
                    user_message_param=None,
                    start_time=0,
                    end_time=0,
                )

            return inner

        return wrapper

    with patch(
        "mirascope.llm.llm_call._get_provider_call", return_value=dummy_provider_call
    ):

        @call(provider="openai", model="gpt-4o-mini")
        def dummy_function(): ...

        res = dummy_function()
        assert isinstance(res, CallResponse)
        # finish_reasons is ["stop"] due to our override
        assert res.finish_reasons == ["stop"]


@pytest.mark.asyncio
async def test_call_decorator_async():
    def dummy_async_provider_call(
        model,
        stream,
        tools,
        response_model,
        output_parser,
        json_mode,
        call_params,
        client,
    ):
        def wrapper(fn):
            async def inner(*args, **kwargs):
                return ConcreteResponse(
                    metadata=Metadata(),
                    response={},
                    tool_types=None,
                    prompt_template=None,
                    fn_args={},
                    dynamic_config={},
                    messages=[],
                    call_params=DummyCallParams(),
                    call_kwargs=BaseCallKwargs(),
                    user_message_param=None,
                    start_time=0,
                    end_time=0,
                )

            return inner

        return wrapper

    with patch(
        "mirascope.llm.llm_call._get_provider_call",
        return_value=dummy_async_provider_call,
    ):

        @call(provider="openai", model="gpt-4o-mini")
        async def dummy_async_function(): ...

        res = await dummy_async_function()
        assert isinstance(res, CallResponse)
        assert res.finish_reasons == ["stop"]
