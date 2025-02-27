"""Tests the `xai.call_response` module."""

from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from mirascope.core.base.types import CostMetadata
from mirascope.core.xai.call_response import XAICallResponse


def test_xai_call_response_cost() -> None:
    choices = [
        Choice(
            finish_reason="stop",
            index=0,
            message=ChatCompletionMessage(content="content", role="assistant"),
        )
    ]
    usage = CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2)
    completion = ChatCompletion(
        id="id",
        choices=choices,
        created=0,
        model="grok-3",
        object="chat.completion",
        usage=usage,
    )
    call_response = XAICallResponse(
        metadata={},
        response=completion,  # pyright: ignore [reportArgumentType]
        tool_types=None,
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
        user_message_param=None,
        start_time=0,
        end_time=0,
    )

    assert call_response.cost == 1.4e-5
    assert call_response.cost_metadata == CostMetadata(input_tokens=1, output_tokens=1)
