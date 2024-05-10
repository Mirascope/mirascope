import pytest
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
)
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.types import AnthropicCallParams
from mirascope.logfire.logfire import with_logfire


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
