import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeAlias

from ...content import Text
from ...context import Context, DepsT
from ...formatting import FormatT
from ...messages import AssistantMessage, Message, SystemMessage, UserMessage
from ...responses import (
    AsyncChunkIterator,
    AsyncContextResponse,
    AsyncContextStreamResponse,
    AsyncResponse,
    AsyncStreamResponse,
    ChunkIterator,
    ChunkIteratorT,
    ContextResponse,
    ContextStreamResponse,
    FinishReason,
    Response,
    StreamResponse,
)
from ...tools import (
    AsyncContextTool,
    AsyncContextToolkit,
    AsyncTool,
    AsyncToolkit,
    ContextTool,
    ContextToolkit,
    Tool,
    Toolkit,
)

if TYPE_CHECKING:
    from ..base import BaseParams
    from ..providers import ModelId, Provider

SystemMessageContent: TypeAlias = str | None


@dataclass(kw_only=True)
class CallResult(Generic[FormatT]):
    """The result of calling an LLM API, containing all common response data.

    This is a utility class used internally by client implementations to avoid
    duplicating response construction logic. It contains all the data that every
    response type needs, and provides methods to construct the appropriate
    response objects with the correct toolkit types.
    """

    raw: Any
    provider: "Provider"
    model_id: "ModelId"
    params: "BaseParams | None"
    format_type: type[FormatT] | None
    input_messages: Sequence[Message]
    assistant_message: AssistantMessage
    finish_reason: FinishReason

    def to_response(
        self, *, tools: Sequence[Tool] | None = None
    ) -> Response | Response[FormatT]:
        return Response(
            raw=self.raw,
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            format_type=self.format_type,
            toolkit=Toolkit(tools=tools),
            input_messages=self.input_messages,
            assistant_message=self.assistant_message,
            finish_reason=self.finish_reason,
        )

    def to_context_response(
        self,
        *,
        ctx: Context[DepsT],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
    ) -> ContextResponse[DepsT, None] | ContextResponse[DepsT, FormatT]:
        return ContextResponse(
            raw=self.raw,
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            toolkit=ContextToolkit(tools=tools),
            input_messages=self.input_messages,
            assistant_message=self.assistant_message,
            finish_reason=self.finish_reason,
            format_type=self.format_type,
        )

    def to_async_response(
        self,
        *,
        tools: Sequence[AsyncTool] | None = None,
    ) -> AsyncResponse | AsyncResponse[FormatT]:
        return AsyncResponse(
            raw=self.raw,
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            toolkit=AsyncToolkit(tools=tools),
            format_type=self.format_type,
            input_messages=self.input_messages,
            assistant_message=self.assistant_message,
            finish_reason=self.finish_reason,
        )

    def to_async_context_response(
        self,
        *,
        ctx: Context[DepsT],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format_type: type[FormatT] | None = None,
    ) -> AsyncContextResponse[DepsT, None] | AsyncContextResponse[DepsT, FormatT]:
        return AsyncContextResponse(
            raw=self.raw,
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            toolkit=AsyncContextToolkit(tools=tools),
            format_type=format_type,
            input_messages=self.input_messages,
            assistant_message=self.assistant_message,
            finish_reason=self.finish_reason,
        )


@dataclass(kw_only=True)
class StreamResult(Generic[ChunkIteratorT, FormatT]):
    """The result of starting a streaming LLM API call.

    Similar to CallResult but for streaming responses. Contains the common
    data needed to construct streaming response objects.
    """

    provider: "Provider"
    model_id: "ModelId"
    params: "BaseParams | None"
    format_type: type[FormatT] | None
    input_messages: Sequence[Message]
    chunk_iterator: ChunkIteratorT

    def to_stream_response(
        self: "StreamResult[ChunkIterator, None] | StreamResult[ChunkIterator, FormatT]",
        *,
        tools: Sequence[Tool] | None = None,
    ) -> StreamResponse | StreamResponse[FormatT]:
        return StreamResponse[Any](
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            toolkit=Toolkit(tools=tools),
            input_messages=self.input_messages,
            chunk_iterator=self.chunk_iterator,
            format_type=self.format_type,
        )

    def to_context_stream_response(
        self: "StreamResult[ChunkIterator, None] | StreamResult[ChunkIterator, FormatT]",
        *,
        ctx: Context[DepsT],
        tools: Sequence[Tool | ContextTool[DepsT]] | None = None,
    ) -> ContextStreamResponse[DepsT, None] | ContextStreamResponse[DepsT, FormatT]:
        return ContextStreamResponse[DepsT, Any](
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            toolkit=ContextToolkit(tools=tools),
            input_messages=self.input_messages,
            chunk_iterator=self.chunk_iterator,
            format_type=self.format_type,
        )

    def to_async_stream_response(
        self: "StreamResult[AsyncChunkIterator] | StreamResult[AsyncChunkIterator, FormatT]",
        *,
        tools: Sequence[AsyncTool] | None = None,
    ) -> AsyncStreamResponse | AsyncStreamResponse[FormatT]:
        return AsyncStreamResponse[Any](
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            toolkit=AsyncToolkit(tools=tools),
            input_messages=self.input_messages,
            chunk_iterator=self.chunk_iterator,
            format_type=self.format_type,
        )

    def to_async_context_stream_response(
        self: "StreamResult[AsyncChunkIterator, None] | StreamResult[AsyncChunkIterator, FormatT]",
        *,
        ctx: Context[DepsT],
        tools: Sequence[AsyncTool | AsyncContextTool[DepsT]] | None = None,
        format_type: type[FormatT] | None = None,
    ) -> (
        AsyncContextStreamResponse[DepsT, None]
        | AsyncContextStreamResponse[DepsT, FormatT]
    ):
        return AsyncContextStreamResponse(
            provider=self.provider,
            model_id=self.model_id,
            params=self.params,
            toolkit=AsyncContextToolkit(tools=tools),
            input_messages=self.input_messages,
            chunk_iterator=self.chunk_iterator,
            format_type=format_type,
        )


def add_system_instructions(
    messages: Sequence[Message], additional_system_instructions: str
) -> Sequence[Message]:
    """Add system instructions to a sequence of messages.

    If the first message is a system message, appends the additional instructions
    to it with a newline separator. If the instructions already exist at the end
    of the system message, returns the original messages unchanged. Otherwise,
    creates a new system message at the beginning of the sequence.

    Args:
        messages: The sequence of messages to modify.
        additional_system_instructions: The system instructions to add.

    Returns:
        A new sequence of messages with the system instructions added.
    """
    if messages and messages[0].role == "system":
        if messages[0].content.text.endswith(additional_system_instructions):
            return messages
        modified = Text(
            text=messages[0].content.text + "\n" + additional_system_instructions
        )
        return [SystemMessage(role="system", content=modified), *messages[1:]]
    else:
        return [
            SystemMessage(
                role="system", content=Text(text=additional_system_instructions)
            ),
            *messages,
        ]


def extract_system_message(
    messages: Sequence[Message],
) -> tuple[SystemMessageContent, Sequence[UserMessage | AssistantMessage]]:
    """Extract the system message(s) from a list of Messages.

    This takes a list of messages, and returns the list of messages with
    all system messages removed, as well as the textual contents of the first message,
    if that message was a system message. If there are any system messages that are
    not the first message, they will be dropped, and a warning will be emitted.

    This is intended for use in clients where the system message is not included in the
    input messages, but passed as an additional argument or metadata.
    """
    system_message_content = None
    remaining_messages = []

    for i, message in enumerate(messages):
        if message.role == "system":
            if i == 0:
                system_message_content = message.content.text
            else:
                logging.warning(
                    "Skipping system message at index %d because it is not the first message",
                    i,
                )
        else:
            remaining_messages.append(message)

    return system_message_content, remaining_messages
