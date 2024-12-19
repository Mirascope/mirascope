from unittest.mock import patch

from mirascope.core.base import (
    BaseCallKwargs,
    BaseCallParams,
    BaseCallResponse,
    BaseMessageParam,
    BaseTool,
    Metadata,
)
from mirascope.core.base.types import Usage
from mirascope.llm.call_response import CallResponse
from mirascope.llm.llm_call import call


class DummyCallParams(BaseCallParams):
    pass


class DummyMessageParam(BaseMessageParam):
    role: str
    content: str


class DummyTool(BaseTool):
    def call(self):
        return "tool_call"

    @property
    def model_fields(self):
        return []


class DummyProviderCallResponse(BaseCallResponse):
    @property
    def content(self):
        return ""

    @property
    def finish_reasons(self):
        return ["done"]

    @property
    def model(self):
        return "test_model"

    @property
    def id(self):
        return "test_id"

    @property
    def usage(self):
        return None

    @property
    def input_tokens(self):
        return None

    @property
    def output_tokens(self):
        return None

    @property
    def cost(self):
        return None

    @property
    def message_param(self):
        return BaseMessageParam(role="assistant", content="")

    @property
    def tools(self):
        return None

    @property
    def tool(self):
        return None

    @classmethod
    def tool_message_params(cls, tools_and_outputs: list[tuple[BaseTool, str]]):
        return []

    @property
    def common_finish_reasons(self):
        return ["done"]

    @property
    def common_message_param(self):
        return BaseMessageParam(role="assistant", content="")

    @property
    def common_tools(self):
        return None

    @property
    def common_usage(self):
        return Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

    def common_construct_call_response(self):
        return self

    def common_construct_message_param(
        self, tool_calls: list | None, content: str | None
    ):
        return BaseMessageParam(role="assistant", content=content or "")


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
        def dummy_function():
            return "hello"

        result_instance = dummy_function()
        assert isinstance(result_instance, CallResponse)
        assert result_instance.finish_reasons == ["done"]
