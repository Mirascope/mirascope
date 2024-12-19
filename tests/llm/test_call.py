from unittest.mock import patch

from mirascope.core.base import (
    BaseCallKwargs,
    BaseCallParams,
    BaseCallResponse,
    BaseMessageParam,
    BaseTool,
    Metadata,
)
from mirascope.core.base.types import FinishReason
from mirascope.llm.call_response import CallResponse
from mirascope.llm.llm_call import call


class DummyCallParams(BaseCallParams):
    pass


class DummyMessageParam(BaseMessageParam):
    role: str
    content: str  # pyright: ignore [reportIncompatibleVariableOverride]


class DummyTool(BaseTool):
    def call(self): ...

    @property
    def model_fields(self) -> list[str]: ...  # pyright: ignore [reportIncompatibleMethodOverride]


class DummyProviderCallResponse(BaseCallResponse):
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
    def message_param(self): ...

    @property
    def tools(self):
        return None

    @property
    def tool(self): ...

    @classmethod
    def tool_message_params(cls, tools_and_outputs: list[tuple[BaseTool, str]]): ...  # pyright: ignore [reportIncompatibleMethodOverride]

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
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


def dummy_decorator(*args, **kwargs):
    def wrapper(original_function):
        def inner(*function_args, **function_kwargs):
            return DummyProviderCallResponse(
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


def test_call_function():
    with patch(
        "mirascope.llm.llm_call._get_provider_call", return_value=dummy_decorator
    ):

        @call("openai:gpt-4o-mini")
        def dummy_function(): ...

        result_instance = dummy_function()
        assert isinstance(result_instance, CallResponse)
        assert result_instance.finish_reasons == ["stop"]
