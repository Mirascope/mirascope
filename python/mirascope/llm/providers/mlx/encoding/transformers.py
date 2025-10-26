from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal, cast
from typing_extensions import TypedDict

from mlx_lm.generate import GenerationResponse
from transformers import PreTrainedTokenizer

from ....formatting import Format, FormattableT
from ....messages import AssistantContent, Message
from ....responses import ChunkIterator, FinishReasonChunk, RawStreamEventChunk
from ....tools import AnyToolSchema, BaseToolkit
from ....types import Jsonable
from .. import _utils
from .base import BaseEncoder, TokenIds
from .stream_processors import SpecialTokens, TextProcessor

HFRole = Literal["system", "user", "assistant", "tool"] | str


class TransformersTextMessage(TypedDict):
    """Text message in Transformers format."""

    role: HFRole
    content: str


class TransformersThoughtMessage(TypedDict):
    role: Literal["assistant"]
    reasoning_content: str


class TransformersToolCall(TypedDict):
    id: str
    name: str
    arguments: Jsonable


class TransformersToolCallMessage(TypedDict):
    role: Literal["assistant"]
    tool_calls: list[TransformersToolCall]


class TransformersToolOutputMessage(TypedDict):
    role: Literal["tool"]
    content: str


TransformersMessage = (
    TransformersTextMessage
    | TransformersThoughtMessage
    | TransformersToolCallMessage
    | TransformersToolOutputMessage
)


def _encode_message(message: Message) -> TransformersMessage:
    """Encode a Mirascope message into Transformers format.

    Args:
        message: The message to encode.

    Returns:
        The encoded message in Transformers format.

    Raises:
        ValueError: If the message role is not supported.
    """
    if message.role == "system":
        return TransformersTextMessage(role="system", content=message.content.text)
    elif message.role == "assistant" or message.role == "user":
        for part in message.content:
            if part.type == "text":
                return TransformersTextMessage(role=message.role, content=part.text)
            elif part.type == "thought":
                return TransformersThoughtMessage(
                    role="assistant", reasoning_content=part.thought
                )
            elif part.type == "tool_call":
                return TransformersToolCallMessage(
                    role="assistant",
                    tool_calls=[
                        TransformersToolCall(
                            id=part.id, name=part.name, arguments=part.args
                        )
                    ],
                )
            elif part.type == "tool_output":
                return TransformersToolOutputMessage(
                    role="tool", content=str(part.value)
                )

    raise ValueError(f"Unsupported message: {message}")


@dataclass(frozen=True)
class TransformersEncoder(BaseEncoder):
    """Encoder for Transformers models."""

    tokenizer: PreTrainedTokenizer
    special_tokens: SpecialTokens

    def encode_request(
        self,
        messages: Sequence[Message],
        tools: Sequence[AnyToolSchema] | BaseToolkit[AnyToolSchema] | None,
        format: type[FormattableT] | Format[FormattableT] | None,
    ) -> tuple[Sequence[Message], Format[FormattableT] | None, TokenIds]:
        """Encode a request into a format suitable for the model."""
        tool_schemas = tools.tools if isinstance(tools, BaseToolkit) else tools or []
        if len(tool_schemas) > 0:
            raise NotImplementedError("Tool usage is not supported.")
        if format is not None:
            raise NotImplementedError("Formatting is not supported.")

        hf_messages: list[TransformersMessage] = [
            _encode_message(msg) for msg in messages
        ]
        prompt_text = cast(
            str,
            self.tokenizer.apply_chat_template(  # pyright: ignore[reportUnknownMemberType]
                cast(list[dict[str, str]], hf_messages),
                tokenize=False,
                add_generation_prompt=True,
            ),
        )
        return (
            messages,
            format,
            self.tokenizer.encode(prompt_text, add_special_tokens=False),  # pyright: ignore[reportUnknownMemberType]
        )

    def decode_response(
        self, stream: Iterable[GenerationResponse]
    ) -> tuple[AssistantContent, GenerationResponse | None]:
        """Decode a response into a format suitable for the model."""
        last_response: GenerationResponse | None = None

        def _response_texts(stream: Iterable[GenerationResponse]) -> Iterable[str]:
            nonlocal last_response
            for response in stream:
                last_response = response
                yield response.text

        content = list(
            TextProcessor.process_text_stream_to_contents(
                text_stream=_response_texts(stream),
                special_tokens=self.special_tokens,
            )
        )
        return content, last_response

    def decode_stream(self, stream: Iterable[GenerationResponse]) -> ChunkIterator:
        """Decode a stream of responses into a format suitable for the model."""
        processor = TextProcessor(special_tokens=self.special_tokens, min_length=0)

        response: GenerationResponse | None = None
        for response in stream:
            yield RawStreamEventChunk(raw_stream_event=response)
            yield from processor.process_text(response.text)

        assert response is not None
        finish_reason = _utils.extract_finish_reason(response)
        if finish_reason is not None:
            yield from processor.flush_contents()
            yield FinishReasonChunk(finish_reason=finish_reason)
        else:
            yield from processor.flush()
