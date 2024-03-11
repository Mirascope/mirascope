"""Tests for the `BaseCall` class."""
from typing import ClassVar
from unittest.mock import patch

from mirascope.base.calls import BaseCall
from mirascope.base.prompts import BasePrompt


@patch.multiple(BaseCall, __abstractmethods__=set())
def test_base_call() -> None:
    """Tests the `BaseCall` interface."""
    model = "gpt-3.5-turbo-1106"

    class Call(BaseCall):
        call_params = BaseCall.CallParams(model=model)

    call = Call()  # type: ignore
    assert isinstance(call, BasePrompt)
    assert call.call_params.model == model


@patch.multiple(BaseCall, __abstractmethods__=set())
def test_extending_base_call() -> None:
    """Tests extending the `BaseCall` interface."""

    class ExtendedCall(BaseCall):
        class CallParams(BaseCall.CallParams):
            additional_param: str

        call_params: ClassVar[CallParams] = CallParams(
            model="model", additional_param="param"
        )

    extended_call = ExtendedCall()  # type: ignore
    assert extended_call.call_params.additional_param == "param"

    class MyCall(ExtendedCall):
        call_params = ExtendedCall.CallParams(
            model="model", additional_param="my_param"
        )

    my_call = MyCall()  # type: ignore
    assert my_call.call_params.additional_param == "my_param"
