import io
import itertools
import json
from collections.abc import Iterable, Sequence
from functools import lru_cache
from typing import Literal

from mlx_lm.generate import GenerationResponse
from openai_harmony import (
    Author as HarmonyAuthor,
    Conversation,
    DeveloperContent as HarmonyDeveloperContent,
    HarmonyEncoding as _HarmonyEncoding,
    HarmonyEncodingName,
    Message as HarmonyMessage,
    ReasoningEffort,
    Role,
    StreamableParser,
    StreamState,
    SystemContent as HarmonySystemContent,
    TextContent as HarmonyTextContent,
    ToolDescription,
    ToolNamespaceConfig,
    load_harmony_encoding,
)

from ....content import (
    AssistantContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    Thought,
    ThoughtChunk,
    ThoughtEndChunk,
    ThoughtStartChunk,
    ToolCall,
    ToolCallEndChunk,
)
from ....formatting import Format, FormattableT
from ....messages import AssistantContent, AssistantMessage, Message, UserMessage
from ....responses import (
    ChunkIterator,
    FinishReasonChunk,
    RawStreamEventChunk,
)
from ....tools import AnyToolSchema, BaseToolkit
from ...base import _utils as _base_utils
from .. import _utils
from .base import BaseEncoder, TokenIds


@lru_cache(maxsize=256)
def _load_harmony_encoding(encoding_name: HarmonyEncodingName) -> _HarmonyEncoding:
    return load_harmony_encoding(encoding_name)


def _encode_assistant_message(
    message: AssistantMessage | UserMessage,
) -> Iterable[HarmonyMessage]:
    for content in message.content:
        if content.type == "text":
            yield HarmonyMessage.from_role_and_contents(
                role=Role.ASSISTANT,
                contents=[HarmonyTextContent(text=content.text)],
            ).with_channel("final")
        elif content.type == "thought":
            yield HarmonyMessage.from_role_and_contents(
                role=Role.ASSISTANT,
                contents=[HarmonyTextContent(text=content.thought)],
            ).with_channel("analysis")
        elif content.type == "tool_call":
            yield (
                HarmonyMessage.from_role_and_contents(
                    role=Role.ASSISTANT,
                    contents=[HarmonyTextContent(text=content.args)],
                )
                .with_channel("commentary")
                .with_recipient(f"functions.{content.name}")
            )
        elif content.type == "tool_output":
            yield HarmonyMessage.from_author_and_content(
                author=HarmonyAuthor.new(Role.TOOL, f"functions.{content.name}"),
                content=json.dumps(content.value),
            )
        else:
            raise NotImplementedError(
                f"Assistant content part {content} is not supported"
            )


def _encode_message(message: Message) -> Iterable[HarmonyMessage]:
    if message.role == "system":
        yield HarmonyMessage.from_role_and_contents(
            role=Role.DEVELOPER,
            contents=[HarmonyTextContent(text=message.content.text)],
        )
        return
    elif message.role == "assistant" or message.role == "user":
        yield from _encode_assistant_message(message)
        return


def decode_harmony_message(message: HarmonyMessage) -> Iterable[AssistantContentPart]:
    for content in message.content:
        match content:
            case HarmonyTextContent(text=text):
                if message.channel == "analysis":
                    yield Thought(thought=text)
                elif message.channel == "final":
                    yield Text(text=text)
                elif message.channel == "commentary" and isinstance(
                    message.recipient, str
                ):
                    function_name = message.recipient[len("functions.") :]
                    yield ToolCall(id="", name=function_name, args=text)
                else:
                    raise NotImplementedError(f"Message {message} is not supported")
            case _:
                raise NotImplementedError(
                    f"Content part {content} currently not supported"
                )


def _encode_tool(tool: AnyToolSchema) -> ToolDescription:
    return ToolDescription(
        name=tool.name,
        description=tool.description,
        parameters=tool.parameters.properties,
    )


class _HarmonyStreamProcessor:
    def __init__(self, encoding: _HarmonyEncoding) -> None:
        self._parser = StreamableParser(encoding, role=Role.ASSISTANT)
        self._stop_tokens = encoding.stop_tokens()
        self._current_role: Role | None = None
        self._current_recipient: str | None = None
        self._buffer = io.StringIO()
        self._state: Literal["text", "tool_call", "thought"] | None = None

    def _end_content(self) -> ChunkIterator:
        if self._state == "text":
            yield TextEndChunk()
        elif self._state == "tool_call":
            yield ToolCallEndChunk()
        elif self._state == "thought":
            yield ThoughtEndChunk()

        self._state = None

    def _handle_parser_changes(self) -> ChunkIterator:
        if self._parser.state != StreamState.CONTENT:
            return

        delta = self._parser.last_content_delta
        if self._parser.current_channel == "final" and delta:
            if self._state != "text":
                yield from self._end_content()
                yield TextStartChunk()
                self._state = "text"

            yield TextChunk(delta=delta)
        elif self._parser.current_channel == "analysis" and delta:
            if self._state != "thought":
                yield from self._end_content()
                yield ThoughtStartChunk()
                self._state = "thought"

            yield ThoughtChunk(delta=delta)

    def process_token(self, token: int) -> ChunkIterator:
        self._parser.process(token)
        if token in self._stop_tokens:
            yield from self._end_content()
        else:
            yield from self._handle_parser_changes()

    def flush(self) -> ChunkIterator:
        self._parser.process_eos()
        yield from self._handle_parser_changes()


class HarmonyEncoder(BaseEncoder):
    def __init__(self, encoding_name: HarmonyEncodingName) -> None:
        self._encoding = _load_harmony_encoding(encoding_name)

    def encode_request(
        self,
        messages: Sequence[Message],
        tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> tuple[Sequence[Message], Format[FormattableT] | None, TokenIds]:
        tool_schemas = tools.tools if isinstance(tools, BaseToolkit) else tools or []

        if format is not None:
            raise NotImplementedError("Formatting is not supported.")

        # TODO: How to pass custom parameters such as reasoning effort into
        # the model from the llm.call decorator?
        system_content = HarmonySystemContent(
            reasoning_effort=ReasoningEffort.LOW,
        )
        if len(tool_schemas) > 0:
            system_content = system_content.with_tools(
                ToolNamespaceConfig(
                    name="functions",
                    description=None,
                    tools=[_encode_tool(tool) for tool in tool_schemas],
                )
            )

        harmony_messages: list[HarmonyMessage] = [
            HarmonyMessage.from_role_and_contents(
                role=Role.SYSTEM,
                contents=[system_content],
            )
        ]

        system_message_content, remaining_messages = _base_utils.extract_system_message(
            messages
        )
        if system_message_content is not None:
            harmony_messages.append(
                HarmonyMessage.from_role_and_contents(
                    role=Role.DEVELOPER,
                    contents=[
                        HarmonyDeveloperContent(instructions=system_message_content)
                    ],
                )
            )

        for message in remaining_messages:
            harmony_messages.extend(_encode_message(message))
        conversation = Conversation.from_messages(harmony_messages)
        tokens = self._encoding.render_conversation_for_completion(
            conversation,
            next_turn_role=Role.ASSISTANT,
        )
        return messages, format, tokens

    def decode_response(
        self, stream: Iterable[GenerationResponse]
    ) -> tuple[AssistantContent, GenerationResponse | None]:
        tokens: list[int] = []
        stop_tokens = self._encoding.stop_tokens_for_assistant_actions()
        last_response: GenerationResponse | None = None
        for r in stream:
            last_response = r
            tokens.append(r.token)
            if r.token in stop_tokens:
                break

        messages = self._encoding.parse_messages_from_completion_tokens(
            tokens,
            role=Role.ASSISTANT,
        )
        content = list(
            itertools.chain.from_iterable(
                decode_harmony_message(msg) for msg in messages
            )
        )
        return content, last_response

    def decode_stream(self, stream: Iterable[GenerationResponse]) -> ChunkIterator:
        processor = _HarmonyStreamProcessor(encoding=self._encoding)

        response: GenerationResponse | None = None
        for response in stream:
            yield RawStreamEventChunk(raw_stream_event=response)
            yield from processor.process_token(response.token)

        assert response is not None
        finish_reason = _utils.extract_finish_reason(response)
        if finish_reason is not None:
            yield from processor.flush()
            yield FinishReasonChunk(finish_reason=finish_reason)
        else:
            yield from processor.flush()
