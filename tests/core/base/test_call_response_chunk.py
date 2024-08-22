"""Tests the `call_response_chunk` module."""

from unittest.mock import patch

from mirascope.core.base.call_response_chunk import BaseCallResponseChunk


def test_base_call_response_chunk() -> None:
    class MyCallResponseChunk(BaseCallResponseChunk):
        @property
        def content(self) -> str:
            return "content"

    patch.multiple(MyCallResponseChunk, __abstractmethods__=set()).start()
    call_response_chunk = MyCallResponseChunk(chunk="")  # type: ignore
    assert str(call_response_chunk) == "content"
