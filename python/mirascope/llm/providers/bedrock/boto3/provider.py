"""Bedrock boto3 provider implementation using Bedrock Runtime Converse API."""

from __future__ import annotations

import asyncio
import contextlib
import threading
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, TypedDict, cast
from typing_extensions import Unpack

from ....context import Context, DepsT
from ....formatting import Format, FormattableT, OutputParser
from ....messages import Message
from ....responses import (
    AsyncChunkIterator,
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ChunkIterator,
    ContextResponse,
    ContextStreamResponse,
    Response,
    StreamResponse,
    StreamResponseChunk,
)
from ....tools import (
    AnyToolSchema,
    AsyncContextToolkit,
    AsyncToolkit,
    BaseToolkit,
    ContextToolkit,
    Toolkit,
)
from ...base import BaseProvider
from .. import _utils as bedrock_utils
from ..model_id import BedrockModelId
from . import _utils
from ._utils import ConverseKwargs, ConverseResponse, ConverseStreamEvent

if TYPE_CHECKING:
    from ....models import Params


class BedrockRuntimeClient(Protocol):
    """Structural type for the boto3 Bedrock Runtime client."""

    def converse(self, **kwargs: Unpack[ConverseKwargs]) -> ConverseResponse: ...

    def converse_stream(
        self, **kwargs: Unpack[ConverseKwargs]
    ) -> dict[str, Iterator[ConverseStreamEvent]]: ...


class BedrockSessionKwargs(TypedDict, total=False):
    region_name: str
    profile_name: str


class BedrockClientKwargs(TypedDict, total=False):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str
    endpoint_url: str


class BedrockSession(Protocol):
    def client(
        self, service_name: str, **kwargs: Unpack[BedrockClientKwargs]
    ) -> BedrockRuntimeClient: ...


class BedrockBoto3Provider(BaseProvider[BedrockRuntimeClient]):
    """Provider for Amazon Bedrock using boto3 Bedrock Runtime Converse API."""

    id: ClassVar[str] = "bedrock:boto3"
    default_scope: ClassVar[str | list[str]] = "bedrock/"
    error_map = _utils.BEDROCK_BOTO3_ERROR_MAP

    def __init__(
        self,
        *,
        aws_region: str | None = None,
        aws_access_key: str | None = None,
        aws_secret_key: str | None = None,
        aws_session_token: str | None = None,
        aws_profile: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize the Bedrock boto3 provider.

        Args:
            aws_region: AWS region for Bedrock. Defaults to environment configuration.
            aws_access_key: AWS access key ID. Defaults to environment configuration.
            aws_secret_key: AWS secret access key. Defaults to environment
                configuration.
            aws_session_token: AWS session token for temporary credentials.
            aws_profile: AWS profile name for credentials. Defaults to environment.
            base_url: Custom endpoint URL for Bedrock (e.g., for GovCloud).
        """
        try:
            import boto3
        except ImportError:
            from ....._stubs import make_import_error

            raise make_import_error("bedrock", "BedrockBoto3Provider") from None

        resolved_region = bedrock_utils.resolve_region(
            aws_region, aws_profile=aws_profile
        )
        session_kwargs: BedrockSessionKwargs = {
            "region_name": resolved_region,
        }
        if aws_profile is not None:
            session_kwargs["profile_name"] = aws_profile

        session = cast(BedrockSession, boto3.Session(**session_kwargs))

        client_kwargs: BedrockClientKwargs = {}
        if aws_access_key is not None:
            client_kwargs["aws_access_key_id"] = aws_access_key
        if aws_secret_key is not None:
            client_kwargs["aws_secret_access_key"] = aws_secret_key
        if aws_session_token is not None:
            client_kwargs["aws_session_token"] = aws_session_token
        if base_url is not None:
            client_kwargs["endpoint_url"] = base_url

        self.client = session.client("bedrock-runtime", **client_kwargs)
        self._lock = threading.Lock()

    def get_error_status(self, e: Exception) -> int | None:
        """Extract HTTP status code from boto3 exception."""
        if hasattr(e, "response"):
            response: dict[str, Any] = getattr(e, "response", {})
            metadata: dict[str, Any] = response.get("ResponseMetadata", {})
            status_code: int | None = metadata.get("HTTPStatusCode")
            return status_code
        return None

    def _model_name(self, model_id: str) -> str:
        return bedrock_utils.bedrock_model_name(model_id)

    def _encode_request(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: BaseToolkit[AnyToolSchema],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None,
        params: Params,
    ) -> tuple[Sequence[Message], Format[FormattableT] | None, dict[str, Any]]:
        input_messages, resolved_format, kwargs = _utils.encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        return input_messages, resolved_format, dict(kwargs)

    def _converse(self, kwargs: dict[str, Any]) -> ConverseResponse:
        with self._lock:
            return self.client.converse(**kwargs)

    def _converse_stream(self, kwargs: dict[str, Any]) -> ChunkIterator:
        with self._lock:
            response = self.client.converse_stream(**kwargs)
        return _utils.decode_stream(response["stream"])

    def _stream_to_queue_worker(
        self,
        kwargs: dict[str, Any],
        loop: asyncio.AbstractEventLoop,
        queue: asyncio.Queue[StreamResponseChunk | Exception | None],
    ) -> None:
        """Worker that generates and consumes stream in a single thread."""
        try:
            with self._lock:
                response = self.client.converse_stream(**kwargs)
            for chunk in _utils.decode_stream(response["stream"]):
                asyncio.run_coroutine_threadsafe(queue.put(chunk), loop)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(queue.put(e), loop)
        asyncio.run_coroutine_threadsafe(queue.put(None), loop)

    async def _converse_stream_async(
        self, kwargs: dict[str, Any]
    ) -> AsyncChunkIterator:
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[StreamResponseChunk | Exception | None] = asyncio.Queue()

        worker_task = asyncio.create_task(
            asyncio.to_thread(self._stream_to_queue_worker, kwargs, loop, queue)
        )
        try:
            while item := await queue.get():
                if isinstance(item, Exception):
                    raise item
                yield item
        finally:
            if not worker_task.done():  # pragma: no cover
                worker_task.cancel()  # pragma: no cover
                with contextlib.suppress(asyncio.CancelledError):  # pragma: no cover
                    await worker_task  # pragma: no cover
            else:
                await worker_task

    def _call(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> Response | Response[FormattableT]:
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        raw_response = self._converse(kwargs)
        assistant_message, finish_reason, usage = _utils.decode_response(
            raw_response,
            model_id,
            provider_id=self.id,
        )
        return Response(
            raw=raw_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    def _context_call(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormattableT]:
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        raw_response = self._converse(kwargs)
        assistant_message, finish_reason, usage = _utils.decode_response(
            raw_response,
            model_id,
            provider_id=self.id,
        )
        return ContextResponse(
            raw=raw_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    async def _call_async(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncResponse | AsyncResponse[FormattableT]:
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        raw_response = await asyncio.to_thread(self._converse, kwargs)
        assistant_message, finish_reason, usage = _utils.decode_response(
            raw_response,
            model_id,
            provider_id=self.id,
        )
        return AsyncResponse(
            raw=raw_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    async def _context_call_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormattableT]:
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        raw_response = await asyncio.to_thread(self._converse, kwargs)
        assistant_message, finish_reason, usage = _utils.decode_response(
            raw_response,
            model_id,
            provider_id=self.id,
        )
        return AsyncContextResponse(
            raw=raw_response,
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            assistant_message=assistant_message,
            finish_reason=finish_reason,
            usage=usage,
            format=resolved_format,
        )

    def _stream(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: Toolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> StreamResponse | StreamResponse[FormattableT]:
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        chunk_iterator = self._converse_stream(kwargs)
        return StreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    def _context_stream(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: ContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> ContextStreamResponse[DepsT] | ContextStreamResponse[DepsT, FormattableT]:
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        chunk_iterator = self._converse_stream(kwargs)
        return ContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    async def _stream_async(
        self,
        *,
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncToolkit,
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormattableT]:
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        chunk_iterator = self._converse_stream_async(kwargs)
        return AsyncStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )

    async def _context_stream_async(
        self,
        *,
        ctx: Context[DepsT],
        model_id: BedrockModelId,
        messages: Sequence[Message],
        toolkit: AsyncContextToolkit[DepsT],
        format: type[FormattableT]
        | Format[FormattableT]
        | OutputParser[FormattableT]
        | None = None,
        **params: Unpack[Params],
    ) -> (
        AsyncContextStreamResponse[DepsT]
        | AsyncContextStreamResponse[DepsT, FormattableT]
    ):
        input_messages, resolved_format, kwargs = self._encode_request(
            model_id=model_id,
            messages=messages,
            toolkit=toolkit,
            format=format,
            params=params,
        )
        chunk_iterator = self._converse_stream_async(kwargs)
        return AsyncContextStreamResponse(
            provider_id=self.id,
            model_id=model_id,
            provider_model_name=self._model_name(model_id),
            params=params,
            tools=toolkit,
            input_messages=input_messages,
            chunk_iterator=chunk_iterator,
            format=resolved_format,
        )


class BedrockBoto3RoutedProvider(BedrockBoto3Provider):
    """Bedrock boto3 provider that reports provider_id as 'bedrock'."""

    id: ClassVar[str] = "bedrock"
