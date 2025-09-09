"""Google message types and conversion utilities."""

import json
from collections.abc import Iterator, Sequence
from functools import lru_cache
from typing import Literal

from google.genai import types as genai_types
from google.genai.types import GenerateContentConfig

from ...content import (
    AssistantContentPart,
    ContentPart,
    Text,
    TextChunk,
    TextEndChunk,
    TextStartChunk,
    ToolCall,
    ToolCallChunk,
    ToolCallEndChunk,
    ToolCallStartChunk,
)
from ...formatting import (
    FormatInfo,
    FormatT,
    _utils as _formatting_utils,
)
from ...messages import AssistantMessage, Message, UserMessage, assistant
from ...responses import ChunkIterator, FinishReason, FinishReasonChunk, RawChunk
from ...tools import (
    FORMAT_TOOL_NAME,
    Tool,
)
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

UNKNOWN_TOOL_ID = "<unknown>"


def _encode_content(content: Sequence[ContentPart]) -> list[genai_types.PartDict]:
    """Returns a list of google `PartDicts` converted from a sequence of Mirascope `ContentPart`s"""
    result = []
    for part in content:
        if part.type == "text":
            result.append(genai_types.PartDict(text=part.text))
        elif part.type == "tool_call":
            result.append(
                genai_types.PartDict(
                    function_call=genai_types.FunctionCallDict(
                        name=part.name,
                        args=json.loads(part.args),
                        id=part.id if part.id != UNKNOWN_TOOL_ID else None,
                    )
                )
            )
        elif part.type == "tool_output":
            result.append(
                genai_types.PartDict(
                    function_response=genai_types.FunctionResponseDict(
                        id=part.id if part.id != UNKNOWN_TOOL_ID else None,
                        name=part.name,
                        response={"output": str(part.value)},
                    )
                )
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
    elif part.code_execution_result:
        raise NotImplementedError("Support for code execution results not implemented.")
    elif part.executable_code:
        raise NotImplementedError("Support for executable code not implemented.")
    elif function_call := part.function_call:
        id = function_call.id
        name = function_call.name
        args = function_call.args
        if not name or args is None:
            raise ValueError(
                "Google function_call does not match spec"
            )  # pragma: no cover
        return ToolCall(id=id or UNKNOWN_TOOL_ID, name=name, args=json.dumps(args))
    elif part.function_response:
        raise NotImplementedError(
            "function_response part does not decode to AssistantContent."
        )
    elif part.thought_signature:
        raise NotImplementedError("Support for thought signature not implemented.")
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
    return genai_types.ContentDict(
        role="model" if message.role == "assistant" else message.role,
        parts=_encode_content(message.content),
    )


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
                for name, prop in (schema_dict.get("properties", {})).items()
            },
            required=schema_dict.get("required", []),
        ),
    )


def prepare_google_request(
    messages: Sequence[Message],
    tools: Sequence[Tool] | None = None,
    format: type[FormatT] | None = None,
) -> tuple[
    Sequence[Message], genai_types.ContentListUnionDict, GenerateContentConfig | None
]:
    config_params = {}
    google_tools: list[genai_types.Tool] = []

    if format:
        resolved_format = _formatting_utils.resolve_formattable(
            format,
            # Google does not support strict outputs when tools are present
            # (Gemini 2.5 will error, 2.0 and below will ignore tools)
            model_supports_strict_mode=not tools,
            model_has_native_json_support=True,
        )

        if resolved_format.mode == "strict":
            config_params["response_mime_type"] = "application/json"
            config_params["response_schema"] = _convert_format_info_to_schema(
                resolved_format.info
            )
        elif resolved_format.mode == "tool":
            format_tool = create_format_tool_declaration(resolved_format.info)
            google_tools.append(genai_types.Tool(function_declarations=[format_tool]))
            function_calling_config: genai_types.FunctionCallingConfigDict = {
                "mode": genai_types.FunctionCallingConfigMode.ANY
            }
            if not tools:
                function_calling_config["allowed_function_names"] = [FORMAT_TOOL_NAME]

            config_params["tool_config"] = {
                "function_calling_config": function_calling_config
            }
        elif resolved_format.mode == "json":
            config_params["response_mime_type"] = "application/json"

        if resolved_format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, resolved_format.formatting_instructions
            )

    if tools:
        function_declarations = [
            _convert_tool_to_function_declaration(tool) for tool in tools
        ]
        google_tools.append(
            genai_types.Tool(function_declarations=function_declarations)
        )

    if google_tools:
        config_params["tools"] = google_tools

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    if system_message_content:
        config_params["system_instruction"] = system_message_content

    config = GenerateContentConfig(**config_params) if config_params else None

    return messages, _encode_messages(remaining_messages), config


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
    current_content_type: Literal["text", "tool_call"] | None = None

    for chunk in google_stream:
        yield RawChunk(raw=chunk)

        candidate = chunk.candidates[0] if chunk.candidates else None
        if not candidate or not candidate.content or not candidate.content.parts:
            continue  # pragma: no cover

        for part in candidate.content.parts:
            if part.thought:
                raise NotImplementedError

            elif part.text:
                if current_content_type == "tool_call":
                    # In testing, Gemini never emits tool calls and text in the same message
                    # (even when specifically asked in system and user prompt), so
                    # the following code is uncovered but included for completeness
                    yield (  # pragma: no cover
                        ToolCallEndChunk(),
                        chunk,
                    )
                    current_content_type = None  # pragma: no cover

                if current_content_type is None:
                    yield TextStartChunk()
                    current_content_type = "text"
                elif current_content_type != "text":
                    raise NotImplementedError

                yield TextChunk(delta=part.text)

            elif function_call := part.function_call:
                if current_content_type == "text":
                    # Similar to above, this does not seem to happen in practice but is
                    # included for safety.
                    yield TextEndChunk()  # pragma: no cover
                    current_content_type = None  # pragma: no cover

                if not function_call.name:
                    raise RuntimeError(
                        "Required name missing on Google function call"
                    )  # pragma: no cover

                yield ToolCallStartChunk(
                    id=function_call.id or UNKNOWN_TOOL_ID,
                    name=function_call.name,
                )

                yield ToolCallChunk(
                    delta=json.dumps(function_call.args)
                    if function_call.args
                    else "{}",
                )
                yield ToolCallEndChunk()

        if candidate.finish_reason:
            if current_content_type == "text":
                yield TextEndChunk()
            elif current_content_type is not None:
                raise NotImplementedError

            current_content_type = None

            finish_reason = GOOGLE_FINISH_REASON_MAP.get(
                candidate.finish_reason, FinishReason.UNKNOWN
            )
            yield FinishReasonChunk(finish_reason=finish_reason)


def _convert_format_info_to_schema(format_info: FormatInfo) -> dict:
    """Convert a Mirascope FormatInfo to Google's response schema format."""
    schema = format_info.schema.copy()
    return schema


def create_format_tool_declaration(
    format_info: FormatInfo,
) -> genai_types.FunctionDeclaration:
    """Create Google FunctionDeclaration for format parsing from a Mirascope FormatInfo.

    Args:
        format_info: The FormatInfo instance containing schema and metadata

    Returns:
        Google FunctionDeclaration for the format tool
    """
    schema_dict = format_info.schema.copy()
    schema_dict["type"] = "object"
    if "properties" in schema_dict and isinstance(schema_dict["properties"], dict):
        schema_dict["required"] = list(schema_dict["properties"].keys())

    description = f"Use this tool to extract data in {format_info.name} format for a final response."
    if format_info.description:
        description += "\n" + format_info.description

    return genai_types.FunctionDeclaration(
        name=FORMAT_TOOL_NAME,
        description=description,
        parameters_json_schema=schema_dict,
    )
