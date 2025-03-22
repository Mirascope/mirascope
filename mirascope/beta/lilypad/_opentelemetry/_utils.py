"""Utility classes and functions for Lilypad OpenTelemetry instrumentation."""
# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications copyright (C) 2024 Mirascope

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any, Generic, Protocol, TypeVar
from urllib.parse import urlparse

from httpx import URL
from opentelemetry.semconv._incubating.attributes import (
    server_attributes,
)
from opentelemetry.semconv.attributes import error_attributes
from opentelemetry.trace import Status, StatusCode

T = TypeVar("T")
ChunkType = TypeVar("ChunkType", contravariant=True)


class StreamProtocol(Protocol):
    def __iter__(self) -> Iterator: ...

    def __next__(self) -> Any: ...

    def close(self) -> None: ...


class AsyncStreamProtocol(Protocol):
    def __aiter__(self) -> AsyncIterator: ...

    async def __anext__(self) -> Any: ...

    async def aclose(self) -> None: ...


class ChoiceBuffer:
    def __init__(self, index: int) -> None:
        self.index = index
        self.finish_reason = None
        self.text_content = []
        self.tool_calls_buffers = []

    def append_text_content(self, content: str) -> None:
        self.text_content.append(content)

    def append_tool_call(self, tool_call: Any) -> None:
        idx = tool_call.index
        # make sure we have enough tool call buffers
        for _ in range(len(self.tool_calls_buffers), idx + 1):
            self.tool_calls_buffers.append(None)

        if not self.tool_calls_buffers[idx]:
            self.tool_calls_buffers[idx] = ToolCallBuffer(
                self.index, tool_call.id, tool_call.function.name
            )
        self.tool_calls_buffers[idx].append_arguments(tool_call.function.arguments)


class ChunkHandler(Protocol[ChunkType]):
    def extract_metadata(self, chunk: ChunkType, metadata: Any) -> None:
        """Extract metadata from chunk and update StreamMetadata"""
        pass

    def process_chunk(self, chunk: ChunkType, buffers: list[ChoiceBuffer]) -> None:
        """Process chunk and update choice buffers"""
        pass


class BaseStreamWrapper(ABC, Generic[T]):
    def __init__(
        self,
        span: Any,
        stream: T,
        metadata: Any,
        chunk_handler: ChunkHandler,
        cleanup_handler: Callable[[Any, Any, list[ChoiceBuffer]], None] | None = None,
    ) -> None:
        self.span = span
        self.stream = stream
        self.chunk_handler = chunk_handler
        self.cleanup_handler = cleanup_handler
        self.metadata = metadata
        self.choice_buffers: list[ChoiceBuffer] = []
        self._span_started = False
        self.setup()

    def setup(self) -> None:
        if not self._span_started:
            self._span_started = True

    def process_chunk(self, chunk: Any) -> None:
        # Extract metadata from chunk
        self.chunk_handler.extract_metadata(chunk, self.metadata)

        # Process chunk content
        self.chunk_handler.process_chunk(chunk, self.choice_buffers)

    def cleanup(self) -> None:
        if self._span_started:
            if self.cleanup_handler:
                self.cleanup_handler(self.span, self.metadata, self.choice_buffers)
            self.span.end()
            self._span_started = False

    @abstractmethod
    async def close(self) -> None:
        pass


class StreamWrapper(BaseStreamWrapper[StreamProtocol]):
    def __enter__(self) -> "StreamWrapper":
        self.setup()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        try:
            if exc_type is not None:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.set_attribute(
                    error_attributes.ERROR_TYPE, exc_type.__qualname__
                )
        finally:
            self.cleanup()
        return False

    async def close(self) -> None:
        self.stream.close()
        self.cleanup()

    def __iter__(self) -> "StreamWrapper":
        return self

    def __next__(self) -> Any:
        try:
            chunk = next(self.stream)
            self.process_chunk(chunk)
            return chunk
        except StopIteration:
            self.cleanup()
            raise
        except Exception as error:
            self.span.set_status(Status(StatusCode.ERROR, str(error)))
            self.span.set_attribute(
                error_attributes.ERROR_TYPE, type(error).__qualname__
            )
            self.cleanup()
            raise


class AsyncStreamWrapper(BaseStreamWrapper[AsyncStreamProtocol]):
    async def __aenter__(self) -> "AsyncStreamWrapper":
        self.setup()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        try:
            if exc_type is not None:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.set_attribute(
                    error_attributes.ERROR_TYPE, exc_type.__qualname__
                )
        finally:
            self.cleanup()
        return False

    async def close(self) -> None:
        await self.stream.aclose()
        self.cleanup()

    def __aiter__(self) -> "AsyncStreamWrapper":
        return self

    async def __anext__(self) -> Any:
        try:
            chunk = await self.stream.__anext__()
            self.process_chunk(chunk)
            return chunk
        except StopAsyncIteration:
            self.cleanup()
            raise
        except Exception as error:
            self.span.set_status(Status(StatusCode.ERROR, str(error)))
            self.span.set_attribute(
                error_attributes.ERROR_TYPE, type(error).__qualname__
            )
            self.cleanup()
            raise


class ToolCallBuffer:
    def __init__(self, index: int, tool_call_id: str, function_name: str) -> None:
        self.index = index
        self.function_name = function_name
        self.tool_call_id = tool_call_id
        self.arguments: list[dict] = []

    def append_arguments(self, arguments: dict) -> None:
        self.arguments.append(arguments)


def set_server_address_and_port(
    client_instance: Any, attributes: dict[str, Any]
) -> None:
    base_client = getattr(client_instance, "_client", None)
    base_url = getattr(base_client, "base_url", None)
    if not base_url:
        return

    port = -1
    if isinstance(base_url, URL):
        attributes[server_attributes.SERVER_ADDRESS] = base_url.host
        port = base_url.port
    elif isinstance(base_url, str):
        url = urlparse(base_url)
        attributes[server_attributes.SERVER_ADDRESS] = url.hostname
        port = url.port

    if port and port != 443 and port > 0:
        attributes[server_attributes.SERVER_PORT] = port
