import io
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal, cast
from typing_extensions import TypedDict

from mlx_lm.generate import GenerationResponse
from transformers import PreTrainedTokenizer

from ....content import ContentPart, TextChunk, TextEndChunk, TextStartChunk
from ....formatting import Format, FormattableT
from ....messages import AssistantContent, Message
from ....responses import (
    ChunkIterator,
    FinishReasonChunk,
    RawStreamEventChunk,
    UsageDeltaChunk,
)
from ....tools import AnyToolSchema, BaseToolkit
from .. import _utils
from .base import BaseEncoder, TokenIds

HFRole = Literal["system", "user", "assistant"] | str


class TransformersMessage(TypedDict):
    """Message in Transformers format."""

    role: HFRole
    content: str


def _encode_content(content: Sequence[ContentPart]) -> str:
    """Encode content parts into a string.

    Args:
        content: The sequence of content parts to encode.

    Returns:
        The encoded content as a string.

    Raises:
        NotImplementedError: If content contains non-text parts.
    """
    if len(content) == 1 and content[0].type == "text":
        return content[0].text

    raise NotImplementedError("Only text content is supported in this example.")


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
        return TransformersMessage(role="system", content=message.content.text)
    elif message.role == "assistant" or message.role == "user":
        return TransformersMessage(
            role=message.role, content=_encode_content(message.content)
        )
    else:
        raise ValueError(f"Unsupported message type: {type(message)}")


@dataclass(frozen=True)
class TransformersEncoder(BaseEncoder):
    """Encoder for Transformers models."""

    tokenizer: PreTrainedTokenizer
    """The tokenizer to use for encoding."""

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
        with io.StringIO() as buffer:
            last_response: GenerationResponse | None = None
            for response in stream:
                buffer.write(response.text)
                last_response = response

            return buffer.getvalue(), last_response

    def decode_stream(self, stream: Iterable[GenerationResponse]) -> ChunkIterator:
        """Decode a stream of responses into a format suitable for the model."""
        yield TextStartChunk()

        response: GenerationResponse | None = None
        for response in stream:
            yield RawStreamEventChunk(raw_stream_event=response)
            yield TextChunk(delta=response.text)

        assert response is not None
        finish_reason = _utils.extract_finish_reason(response)
        if finish_reason is not None:
            yield FinishReasonChunk(finish_reason=finish_reason)
        else:
            yield TextEndChunk()

        # Emit usage delta if available
        usage = _utils.extract_usage(response)
        if usage:
            yield UsageDeltaChunk(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cache_read_tokens=usage.cache_read_tokens,
                cache_write_tokens=usage.cache_write_tokens,
                reasoning_tokens=usage.reasoning_tokens,
            )
