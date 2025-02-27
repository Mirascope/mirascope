"""Tests the `litellm.call_response` module."""

from litellm.types.utils import ModelResponse

from mirascope.core.base.types import CostMetadata
from mirascope.core.litellm.call_response import LiteLLMCallResponse


def test_litellm_call_response_cost() -> None:
    response = ModelResponse(
        model="claude-3-5-sonnet-20240620",
        usage={"completion_tokens": 1, "prompt_tokens": 1, "total_tokens": 2},
    )
    response._hidden_params["response_cost"] = 1.8e-5
    call_response = LiteLLMCallResponse(
        metadata={},
        response=response,  # pyright: ignore [reportArgumentType]
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

    assert call_response.cost == 1.8e-5
    assert call_response.cost_metadata == CostMetadata(cost=1.8e-5)
