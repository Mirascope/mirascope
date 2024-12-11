from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Literal, TypeAlias, TypeVar

from pydantic import ConfigDict, model_validator

from mirascope.core.base.call_response_chunk import BaseCallResponseChunk
from mirascope.llm._get_provider_converter import _get_provider_converter
from mirascope.llm.call_response import Provider

if TYPE_CHECKING:
    from mirascope.llm._base_provider_converter import BaseProviderConverter

_ChunkT = TypeVar("_ChunkT")

FinishReason: TypeAlias = Literal[
    "stop", "length", "tool_calls", "content_filter", "function_call"
]


class CallResponseChunk(BaseCallResponseChunk[_ChunkT, FinishReason], Generic[_ChunkT]):
    """
    A provider-agnostic call response chunk with a single generic parameter.

    Example:
    CallResponseChunk[ChatCompletionChunk]
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    provider: Provider
    provider_call_response_chunk: BaseCallResponseChunk

    _finish_reasons: list[FinishReason] = []
    _usage: Any | None = None
    _provider_converter: BaseProviderConverter | None = None

    @model_validator(mode="before")
    def _pre_init_validate(cls, values: Any) -> Any:
        provider = values.get("provider")
        if not provider:
            raise ValueError("`provider` must be provided.")
        if provider_converter := _get_provider_converter(provider):
            provider_call_response_chunk = (
                provider_converter.get_call_response_chunk_class().model_validate(
                    values
                )
            )
            return {
                **values,
                "provider_call_response_chunk": provider_call_response_chunk,
                "provider": provider,
            }
        raise ValueError("No provider_converter found for given provider.")

    @model_validator(mode="after")
    def _post_init_normalize(self) -> CallResponseChunk[_ChunkT]:
        if provider_converter := _get_provider_converter(self.provider):
            self._provider_converter = provider_converter
            # self._finish_reasons = (
            #     provider_converter.get_chunk_finish_reasons(
            #         self.provider_call_response_chunk
            #     )
            #     or []
            # )
            usage = self.provider_call_response_chunk.usage
            self._usage = (
                provider_converter.get_usage(usage) if usage is not None else None
            )

        return self

    @property
    def content(self) -> str:
        return self.provider_call_response_chunk.content

    @property
    def finish_reasons(self) -> list[str] | None:
        return self._provider_converter.get_chunk_finish_reasons(
                self.provider_call_response_chunk
            )
        # return self._finish_reasons if self._finish_reasons else None

    @property
    def model(self) -> str | None:
        return self.provider_call_response_chunk.model

    @property
    def id(self) -> str | None:
        return self.provider_call_response_chunk.id

    @property
    def usage(self) -> Any | None:
        # if
        # return self._provider_converter.get_usage(self.provider_call_response_chunk.usage)
        return self._usage

    @property
    def input_tokens(self) -> int | float | None:
        return self.provider_call_response_chunk.input_tokens

    @property
    def output_tokens(self) -> int | float | None:
        return self.provider_call_response_chunk.output_tokens
