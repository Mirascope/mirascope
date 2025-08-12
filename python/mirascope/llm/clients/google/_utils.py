"""Google message types and conversion utilities."""

from collections.abc import Iterator, Sequence
from functools import lru_cache
from typing import Literal

from google.genai import types as genai_types
from google.genai.types import GenerateContentConfig

from ...content import (
    AssistantContentPart,
    ContentPart,
    FinishReasonChunk,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
)
from ...messages import AssistantMessage, Message, UserMessage, assistant
from ...responses import ChunkIterator, FinishReason
from ...tools import Tool
from ..base import _utils as _base_utils

GOOGLE_FINISH_REASON_MAP = {  # TODO (mir-285): Audit these
    "STOP": FinishReason.END_TURN,
    "MAX_TOKENS": FinishReason.MAX_TOKENS,
    "SAFETY": FinishReason.REFUSAL,
    "RECITATION": FinishReason.REFUSAL,
    "OTHER": FinishReason.UNKNOWN,
    "BLOCKLIST": FinishReason.REFUSAL,
    "PROHIBITED_CONTENT": FinishReason.REFUSAL,
    "SPII": FinishReason.REFUSAL,
    "MALFORMED_FUNCTION_CALL": FinishReason.UNKNOWN,
    "FUNCTION_CALL": FinishReason.TOOL_USE,
}


def _encode_content(content: Sequence[ContentPart]) -> list[genai_types.PartDict]:
    """Returns a list of google `PartDicts` converted from a sequence of Mirascope `ContentPart`s"""
    result = []
    for part in content:
        if part.type == "text":
            result.append({"text": part.text})
        elif part.type == "tool_call":
            result.append(
                {
                    "function_call": {
                        "name": part.name,
                        "args": part.args,
                        "id": part.id,
                    }
                }
            )
        elif part.type == "tool_output":
            result.append(
                {
                    "function_response": {
                        "id": part.id,
                        "name": part.name,
                        "response": {"output": str(part.value)},
                    }
                }
            )
        else:
            raise NotImplementedError(
                f"Have not implemented conversion for {part.type}"
            )
    return result


def _decode_content_part(part: genai_types.Part) -> AssistantContentPart | None:
    """Returns an `AssistantContentPart` (or `None`) decoded from a google `Part`"""
    if part.text:
        return Text(text=part.text)
    elif part.video_metadata:
        raise NotImplementedError("Support for video metadata not implemented.")
    elif part.thought:
        raise NotImplementedError("Support for thought content not implemented.")
    elif part.inline_data:
        raise NotImplementedError("Support for inline data (Blob) not implemented.")
    elif part.file_data:
        raise NotImplementedError("Support for file data (FileData) not implemented.")
    elif part.thought_signature:
        raise NotImplementedError("Support for thought signature not implemented.")
    elif part.code_execution_result:
        raise NotImplementedError("Support for code execution results not implemented.")
    elif part.executable_code:
        raise NotImplementedError("Support for executable code not implemented.")
    elif function_call := part.function_call:
        id = function_call.id
        name = function_call.name
        args = function_call.args
        if not name or not args:
            raise ValueError(
                "Google function_call does not match spec"
            )  # pragma: no cover
        if not id:
            id = name  # Google treats tool call ids as optional
        return ToolCall(id=id, name=name, args=args)
    elif part.function_response:
        raise NotImplementedError(
            "function_response part does not decode to AssistantContent."
        )
    else:
        # Per Part docstring, this should never happen:
        # >  Exactly one field within a Part should be set, representing the specific type
        # >  of content being conveyed. Using multiple fields within the same `Part`
        # >  instance is considered invalid.
        # However, in testing, this can happen, so we will do our best to handle
        # it as empty content.
        return None


def _decode_candidate_content(
    candidate: genai_types.Candidate,
) -> Sequence[AssistantContentPart]:
    """Returns a sequence of `AssistantContentPart` decoded from a google `Candidate`"""
    content_parts = []
    if candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            decoded_part = _decode_content_part(part)
            if decoded_part:
                content_parts.append(decoded_part)
    return content_parts


def _encode_message(
    message: UserMessage | AssistantMessage,
) -> genai_types.ContentDict:
    """Returns a Google `ContentDict` converted from a Mirascope `Message`"""
    return {
        "role": "model" if message.role == "assistant" else message.role,
        "parts": _encode_content(message.content),
    }


def _encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
) -> genai_types.ContentListUnionDict:
    """Returns a `ContentListUnionDict` converted from a sequence of user or assistant `Messages`s"""
    return [_encode_message(message) for message in messages]


@lru_cache(maxsize=128)
def _convert_tool_to_function_declaration(
    tool: Tool,
) -> genai_types.FunctionDeclaration:
    """Convert a single Mirascope tool to Google FunctionDeclaration format with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"
    return genai_types.FunctionDeclaration(
        name=tool.name,
        description=tool.description,
        parameters=genai_types.Schema(
            type=genai_types.Type.OBJECT,
            properties={
                name: genai_types.Schema.model_validate(prop)
                for name, prop in schema_dict.get("properties", {}).items()
            },
            required=schema_dict.get("required", []),
        ),
    )


def prepare_google_request(
    messages: Sequence[Message],
    tools: Sequence[Tool] | None = None,
) -> tuple[genai_types.ContentListUnionDict, GenerateContentConfig | None]:
    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    config_params = {}

    if system_message_content:
        config_params["system_instruction"] = system_message_content

    if tools:
        function_declarations = [
            _convert_tool_to_function_declaration(tool) for tool in tools
        ]
        config_params["tools"] = [
            genai_types.Tool(function_declarations=function_declarations)
        ]

    config = GenerateContentConfig(**config_params) if config_params else None

    return _encode_messages(remaining_messages), config


def decode_response(
    response: genai_types.GenerateContentResponse,
) -> tuple[AssistantMessage, FinishReason | None]:
    """Returns an `AssistantMessage` and `FinishReason` extracted from a `GenerateContentResponse`"""
    if not response.candidates or not response.candidates[0].content:
        # Unclear under what circumstances this happens (if ever).
        # In testing, when generating no output at all, it creates a part with
        # no fields set.
        return assistant(content=[]), FinishReason.UNKNOWN  # pragma: no cover
    candidate = response.candidates[0]
    assistant_message = assistant(content=_decode_candidate_content(candidate))
    finish_reason = (
        GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason, FinishReason.UNKNOWN)
        if candidate.finish_reason
        else None
    )
    return assistant_message, finish_reason


def convert_google_stream_to_chunk_iterator(
    google_stream: Iterator[genai_types.GenerateContentResponse],
) -> ChunkIterator:
    current_content_type: Literal["text"] | None = None

    for chunk in google_stream:
        candidate = chunk.candidates[0] if chunk.candidates else None
        if not candidate or not candidate.content or not candidate.content.parts:
            continue  # pragma: no cover

        for part in candidate.content.parts:
            if part.thought:
                raise NotImplementedError

            elif part.text:
                if current_content_type is None:
                    yield TextStartChunk(type="text_start_chunk"), chunk
                    current_content_type = "text"
                elif current_content_type != "text":
                    raise NotImplementedError

                yield TextChunk(type="text_chunk", delta=part.text), chunk

        if candidate.finish_reason:
            if current_content_type == "text":
                yield TextEndChunk(type="text_end_chunk"), chunk
            else:
                raise NotImplementedError

            finish_reason = GOOGLE_FINISH_REASON_MAP.get(
                candidate.finish_reason, FinishReason.UNKNOWN
            )
            yield FinishReasonChunk(finish_reason=finish_reason), chunk
