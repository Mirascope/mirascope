from collections.abc import Sequence
from functools import cached_property
from typing import Any
from unittest.mock import Mock, patch

import pytest
from openai import AsyncOpenAI, OpenAI
from pydantic import computed_field

from mirascope.core.base import (
    BaseCallKwargs,
    BaseCallParams,
    BaseCallResponse,
    BaseStream,
    BaseTool,
    Metadata,
)
from mirascope.core.base._utils import BaseMessageParamConverter
from mirascope.core.base.types import CostMetadata, FinishReason
from mirascope.llm._call import (
    _get_local_provider_call,
    _get_provider_call,
    _wrap_result,
    call,
)
from mirascope.llm._context import context
from mirascope.llm.call_response import CallResponse
from mirascope.llm.stream import Stream


class DummyCallParams(BaseCallParams): ...


class ConcreteResponse(BaseCallResponse[Any, Any, Any, Any, Any, Any, Any, Any]):
    _message_converter: type = BaseMessageParamConverter

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
    def cached_tokens(self): ...

    @property
    def output_tokens(self): ...

    @property
    def cost(self): ...

    @computed_field
    @cached_property
    def message_param(self) -> Any: ...

    @cached_property
    def tools(self) -> Any: ...

    @cached_property
    def tool(self) -> Any: ...

    @classmethod
    def tool_message_params(cls, tools_and_outputs: Sequence[tuple[BaseTool, str]]): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        # Just return ["stop"] as a string to avoid AttributeError
        return ["stop"]

    @property
    def common_message_param(self): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def common_user_message_param(self): ...

    @property
    def common_tools(self): ...

    @property
    def common_usage(self): ...

    def common_construct_call_response(self): ...

    def common_construct_message_param(
        self, tool_calls: list | None, content: str | None
    ): ...

    @property
    def cost_metadata(self) -> CostMetadata: ...


class ConcreteStream(BaseStream):
    def _construct_message_param(self, *args, **kwargs): ...

    def construct_call_response(self): ...

    @property
    def cost(self): ...

    @property
    def cost_metadata(self) -> CostMetadata: ...


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


def test_wrap_result_with_base_tool():
    """Test that _wrap_result can handle a response containing a BaseTool."""

    # Create a custom BaseTool for testing
    class CustomBaseTool(BaseTool): ...

    # Create a response instance
    resp = ConcreteResponse(
        metadata=Metadata(),
        response={},
        tool_types=[CustomBaseTool],  # Use the BaseTool subclass
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

    # Create a stream instance
    resp = ConcreteStream(
        stream=Mock(),
        metadata=Metadata(),
        tool_types=[CustomBaseTool],  # Use the BaseTool subclass
        call_response_type=Mock(),  # pyright: ignore [reportArgumentType]
        model=Mock(),  # pyright: ignore [reportArgumentType]
        prompt_template=Mock(),
        fn_args={},
        dynamic_config={},
        messages=[],
        call_params=DummyCallParams(),
        call_kwargs=BaseCallKwargs(),
    )

    result = _wrap_result(resp)
    assert isinstance(result, Stream)


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


def test_get_provider_call_google():
    with patch("mirascope.core.google.google_call", new="google_mock"):
        func = _get_provider_call("google")
        assert func == "google_mock"


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


def test_get_provider_call_xai():
    with patch("mirascope.core.xai.xai_call", new="xai_mock"):
        func = _get_provider_call("xai")
        assert func == "xai_mock"


def test_get_local_provider_call_ollama():
    with patch("mirascope.core.openai.openai_call", new="openai_ollama_mock"):
        func, client = _get_local_provider_call("ollama", None, False)
        assert func == "openai_ollama_mock"
        assert (
            isinstance(client, OpenAI)
            and client.api_key == "ollama"
            and str(client.base_url) == "http://localhost:11434/v1/"
        )
        func, client = _get_local_provider_call("ollama", None, True)
        assert func == "openai_ollama_mock"
        assert (
            isinstance(client, AsyncOpenAI)
            and client.api_key == "ollama"
            and str(client.base_url) == "http://localhost:11434/v1/"
        )
        mock_client = Mock()
        _, client = _get_local_provider_call("ollama", mock_client, False)
        assert client == mock_client


def test_get_local_provider_call_vllm():
    with patch("mirascope.core.openai.openai_call", new="openai_vllm_mock"):
        func, client = _get_local_provider_call("vllm", None, False)
        assert func == "openai_vllm_mock"
        assert (
            isinstance(client, OpenAI)
            and client.api_key == "ollama"
            and str(client.base_url) == "http://localhost:8000/v1/"
        )
        func, client = _get_local_provider_call("vllm", None, True)
        assert func == "openai_vllm_mock"
        assert (
            isinstance(client, AsyncOpenAI)
            and client.api_key == "ollama"
            and str(client.base_url) == "http://localhost:8000/v1/"
        )
        mock_client = Mock()
        _, client = _get_local_provider_call("vllm", mock_client, False)
        assert client == mock_client


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
        "mirascope.llm._call._get_provider_call", return_value=dummy_provider_call
    ):

        @call(provider="openai", model="gpt-4o-mini")
        def dummy_function(): ...

        res = dummy_function()
        assert isinstance(res, CallResponse)
        # finish_reasons is ["stop"] due to our override
        assert res.finish_reasons == ["stop"]

    with patch(
        "mirascope.llm._call._get_local_provider_call",
        return_value=(dummy_provider_call, None),
    ):

        @call(provider="ollama", model="gpt-4o-mini")
        def dummy_local_function(): ...

        res = dummy_local_function()
        assert isinstance(res, CallResponse)
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
        "mirascope.llm._call._get_provider_call",
        return_value=dummy_async_provider_call,
    ):

        @call(provider="openai", model="gpt-4o-mini")
        async def dummy_async_function(): ...

        res = await dummy_async_function()
        assert isinstance(res, CallResponse)
        assert res.finish_reasons == ["stop"]

    with patch(
        "mirascope.llm._call._get_local_provider_call",
        return_value=(dummy_async_provider_call, None),
    ):

        @call(provider="ollama", model="gpt-4o-mini")
        async def dummy_local_async_function(): ...

        res = await dummy_local_async_function()
        assert isinstance(res, CallResponse)
        assert res.finish_reasons == ["stop"]


@pytest.mark.asyncio
async def test_context_in_async_function():
    """Test that context is properly applied in async functions."""
    # Create a mock provider call that captures the effective call args
    captured_args = {}

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
                # Store the args that were passed to the provider call
                nonlocal captured_args
                captured_args = {
                    "model": model,
                    "stream": stream,
                    "tools": tools,
                    "response_model": response_model,
                    "output_parser": output_parser,
                    "json_mode": json_mode,
                    "call_params": call_params,
                    "client": client,
                }

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
        "mirascope.llm._call._get_provider_call",
        return_value=dummy_async_provider_call,
    ):
        # Create a function with the openai provider
        @call(provider="openai", model="gpt-4o-mini")
        async def dummy_async_function():
            pass  # pragma: no cover

        # Call the function with a context that overrides the model
        with context(provider="openai", model="gpt-4o"):
            await dummy_async_function()

        # Check that the context override was applied
        assert captured_args["model"] == "gpt-4o", (
            "Context model override was not applied in async function"
        )


@pytest.mark.asyncio
async def test_context_in_async_function_with_gather():
    """Test that context is properly applied in async functions when using asyncio.gather."""
    # Create a mock provider call that captures the effective call args for each call
    captured_args_list = []

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
                # Store the args that were passed to the provider call
                captured_args = {
                    "model": model,
                    "stream": stream,
                    "tools": tools,
                    "response_model": response_model,
                    "output_parser": output_parser,
                    "json_mode": json_mode,
                    "call_params": call_params,
                    "client": client,
                }
                captured_args_list.append(captured_args)

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
        "mirascope.llm._call._get_provider_call",
        return_value=dummy_async_provider_call,
    ):
        # Create a function with the openai provider
        @call(provider="openai", model="gpt-4o-mini")
        async def dummy_async_function():
            pass  # pragma: no cover

        # Create futures first, then await them together
        import asyncio

        # Create the first future with default provider/model
        future1 = dummy_async_function()

        # Create the second future with a different context
        with context(provider="anthropic", model="claude-3-5-sonnet"):
            future2 = dummy_async_function()

        # Await both futures together
        await asyncio.gather(future1, future2)

        # Check that we have two captured args
        assert len(captured_args_list) == 2

        # The first should use the original model
        assert captured_args_list[0]["model"] == "gpt-4o-mini"

        # The second should use the context-overridden model
        assert captured_args_list[1]["model"] == "claude-3-5-sonnet", (
            "Context model override was not applied when using asyncio.gather"
        )
