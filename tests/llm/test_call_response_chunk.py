from typing import Any, cast

from mirascope.core.base import BaseCallResponseChunk
from mirascope.core.base.types import CostMetadata, FinishReason, Usage
from mirascope.llm.call_response_chunk import CallResponseChunk


class DummyCallResponseChunk(BaseCallResponseChunk[Any, str]):
    @property
    def content(self) -> str:
        return "chunk_content"

    @property
    def finish_reasons(self) -> list[str] | None:
        return ["stop"]

    @property
    def model(self) -> str | None: ...

    @property
    def id(self) -> str | None: ...

    @property
    def usage(self) -> Any: ...

    @property
    def input_tokens(self) -> int | float | None:
        return 2

    @property
    def cached_tokens(self) -> int | float | None:
        return 1

    @property
    def output_tokens(self) -> int | float | None:
        return 3

    @property
    def common_finish_reasons(self) -> list[FinishReason] | None:
        return cast(list[FinishReason], self.finish_reasons)

    @property
    def common_usage(self) -> Usage:
        input_tokens = int(self.input_tokens or 0)
        cached_tokens = int(self.cached_tokens or 0)
        output_tokens = int(self.output_tokens or 0)
        return Usage(
            input_tokens=input_tokens,
            cached_tokens=cached_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )

    @property
    def cost_metadata(self) -> CostMetadata:
        return super().cost_metadata


def test_call_response_chunk():
    chunk_response_instance = DummyCallResponseChunk(chunk={})
    call_response_chunk_instance = CallResponseChunk(response=chunk_response_instance)  # pyright: ignore [reportAbstractUsage]
    assert call_response_chunk_instance.finish_reasons == ["stop"]
    assert call_response_chunk_instance.usage is not None
    assert call_response_chunk_instance.content == "chunk_content"
    assert call_response_chunk_instance.common_usage is not None
    assert call_response_chunk_instance.common_usage.total_tokens == 5
    assert call_response_chunk_instance.cost_metadata == CostMetadata(
        input_tokens=2,
        output_tokens=3,
        cached_tokens=1,
    )
