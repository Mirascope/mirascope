"""Configuration for the Mirascope logfire module tests."""
import logfire
import pytest
from logfire.testing import CaptureLogfire, TestExporter
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
)
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import set_tracer_provider

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.types import AnthropicCallParams
from mirascope.logfire.logfire import with_logfire
from mirascope.openai.calls import OpenAICall
from mirascope.openai.types import OpenAICallParams


@pytest.fixture(scope="function", autouse=True)
def fixture_capfire() -> CaptureLogfire:
    """A fixture that returns a CaptureLogfire instance."""
    exporter = TestExporter()
    metrics_reader = InMemoryMetricReader()
    logfire.configure(
        send_to_logfire=False,
        console=False,
        processors=[SimpleSpanProcessor(exporter)],
        metric_readers=[metrics_reader],
    )

    yield CaptureLogfire(exporter=exporter, metrics_reader=metrics_reader)

    set_tracer_provider(None)


@pytest.fixture()
def fixture_anthropic_test_call_with_logfire() -> type[AnthropicCall]:
    @with_logfire
    class AnthropicLogfireCall(AnthropicCall):
        prompt_template = ""
        api_key = "test"
        call_params = AnthropicCallParams()

    return AnthropicLogfireCall


@pytest.fixture()
def fixture_chat_completion() -> ChatCompletion:
    """Returns a chat completion."""
    return ChatCompletion(
        id="test_id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="test content 0", role="assistant"
                ),
                **{"logprobs": None},
            ),
            Choice(
                finish_reason="stop",
                index=1,
                message=ChatCompletionMessage(
                    content="test content 1", role="assistant"
                ),
                **{"logprobs": None},
            ),
        ],
        created=0,
        model="gpt-4",
        object="chat.completion",
        usage=CompletionUsage(completion_tokens=0, prompt_tokens=0, total_tokens=0),
    )


@pytest.fixture()
def fixture_openai_nested_call() -> OpenAICall:
    openai_model = "gpt-3.5-turbo"

    class MyCall(OpenAICall):
        ...

    @with_logfire
    class MyNestedCall(MyCall):
        prompt_template = "test"
        api_key = "test"
        call_params = OpenAICallParams(model=openai_model)

    return MyNestedCall()
