"""Tests the `call_response` module."""

from unittest.mock import MagicMock, patch

from mirascope.core.base.call_response import BaseCallResponse


def test_base_call_response() -> None:
    class MyCallResponse(BaseCallResponse):
        @property
        def content(self) -> str:
            return "content"

    patch.multiple(MyCallResponse, __abstractmethods__=set()).start()
    call_response = MyCallResponse(
        metadata={},
        response="",
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
    )  # type: ignore
    assert str(call_response) == "content"
    tool = MagicMock()
    tool._name = lambda: "mock_tool"
    assert call_response.serialize_tool_types([tool], info=MagicMock()) == [
        {"type": "function", "name": "mock_tool"}
    ]
