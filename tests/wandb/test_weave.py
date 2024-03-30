"""Tests for the Mirascope + Weave integration."""
import weave

from mirascope.openai import OpenAICall
from mirascope.wandb.weave import with_weave


@with_weave
class MyCall(OpenAICall):
    prompt_template = "test"


def test_call_with_weave() -> None:
    my_base_call = MyCall()
    assert isinstance(my_base_call.call, weave.Op)
    assert isinstance(my_base_call.call_async, weave.Op)
    assert isinstance(my_base_call.stream, weave.Op)
    assert isinstance(my_base_call.stream_async, weave.Op)
    assert my_base_call.call_params.weave is not None
