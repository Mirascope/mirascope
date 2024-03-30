"""Tests for the Mirascope + Weave integration."""
from typing import Type

import weave

from mirascope.openai import OpenAICall, OpenAIExtractor
from mirascope.wandb.weave import with_weave


@with_weave
class MyCall(OpenAICall):
    prompt_template = "test"


def test_call_with_weave() -> None:
    my_call = MyCall()
    assert isinstance(my_call.call, weave.Op)
    assert isinstance(my_call.call_async, weave.Op)
    assert isinstance(my_call.stream, weave.Op)
    assert isinstance(my_call.stream_async, weave.Op)
    assert my_call.call_params.weave is not None


@with_weave
class MyExtractor(OpenAIExtractor[int]):
    extract_schema: Type[int] = int
    prompt_template = "test"


def test_extractor_with_weave() -> None:
    my_extractor = MyExtractor()
    assert isinstance(my_extractor.extract, weave.Op)
    assert isinstance(my_extractor.extract_async, weave.Op)
    assert my_extractor.call_params.weave is not None
