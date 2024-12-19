from typing import Any

from mirascope.core.base import BaseCallResponseChunk
from mirascope.core.base.types import Usage
from mirascope.llm.call_response_chunk import CallResponseChunk


class DummyCallResponseChunk(BaseCallResponseChunk[Any, str]):
    @property
    def content(self) -> str:
        return "chunk_content"

    @property
    def finish_reasons(self) -> list[str] | None:
        return ["chunk_finish"]

    @property
    def model(self) -> str | None:
        return "chunk_model"

    @property
    def id(self) -> str | None:
        return "chunk_id"

    @property
    def usage(self) -> Any:
        return {"input_tokens": 2, "completion_tokens": 3}

    @property
    def input_tokens(self) -> int | float | None:
        return 2

    @property
    def output_tokens(self) -> int | float | None:
        return 3

    @property
    def common_finish_reasons(self):
        return self.finish_reasons

    @property
    def common_usage(self):
        return Usage(
            prompt_tokens=self.input_tokens,
            completion_tokens=self.output_tokens,
            total_tokens=self.input_tokens + self.output_tokens,
        )


def test_call_response_chunk():
    chunk_response_instance = DummyCallResponseChunk(chunk={})
    call_response_chunk_instance = CallResponseChunk(response=chunk_response_instance)
    assert call_response_chunk_instance.finish_reasons == ["chunk_finish"]
    assert call_response_chunk_instance.usage is not None
    assert call_response_chunk_instance.content == "chunk_content"
    assert call_response_chunk_instance.common_usage.total_tokens == 5