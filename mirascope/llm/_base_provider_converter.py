from abc import ABC, abstractmethod
from typing import Any, Callable

from pydantic import BaseModel

from mirascope.core import BaseMessageParam
from mirascope.core.base import BaseCallResponse, BaseCallResponseChunk, BaseStream
from mirascope.llm.call_response_chunk import FinishReason


class Usage(BaseModel):
    completion_tokens: int
    """Number of tokens in the generated completion."""

    prompt_tokens: int
    """Number of tokens in the prompt."""

    total_tokens: int
    """Total number of tokens used in the request (prompt + completion)."""


class BaseProviderConverter(ABC):
    @staticmethod
    @abstractmethod
    def get_call_factory() -> Callable: ...

    @staticmethod
    @abstractmethod
    def get_message_param(message_param: Any) -> BaseMessageParam: ...

    @staticmethod
    @abstractmethod
    def get_usage(usage: Any) -> Usage: ...

    @staticmethod
    @abstractmethod
    def get_call_response_class() -> type[BaseCallResponse]: ...


    @staticmethod
    @abstractmethod
    def get_stream_class() -> type[BaseStream]: ...

    @staticmethod
    @abstractmethod
    def get_call_response_chunk_class() -> type[BaseCallResponseChunk]: ...

    @staticmethod
    @abstractmethod
    def get_chunk_finish_reasons(chunk: Any) -> list[FinishReason]: ...