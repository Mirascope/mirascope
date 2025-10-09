"""Google message types and conversion utilities."""

import json
import logging
from collections.abc import AsyncIterator, Iterator, Sequence
from functools import lru_cache
from typing import Any, Literal, cast

from google.genai import types as genai_types

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
from ...exceptions import FeatureNotSupportedError
from ...formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ...messages import AssistantMessage, Message, UserMessage
from ...responses import (
    AsyncChunkIterator,
    ChunkIterator,
    FinishReason,
    FinishReasonChunk,
    RawChunk,
)
from ...tools import FORMAT_TOOL_NAME, BaseToolkit, ToolSchema
from ..base import BaseKwargs, Params, _utils as _base_utils
from .model_ids import GoogleModelId

logger = logging.getLogger(__name__)

GOOGLE_FINISH_REASON_MAP = {
    "MAX_TOKENS": FinishReason.MAX_TOKENS,
    "SAFETY": FinishReason.REFUSAL,
    "RECITATION": FinishReason.REFUSAL,
    "BLOCKLIST": FinishReason.REFUSAL,
    "PROHIBITED_CONTENT": FinishReason.REFUSAL,
    "SPII": FinishReason.REFUSAL,
}

UNKNOWN_TOOL_ID = "<unknown>"


class GoogleKwargs(BaseKwargs, genai_types.GenerateContentConfigDict):
    """Google's `GenerateContentConfigDict` typed dict, subclassing BaseKwargs for type safety."""


def _resolve_refs(
    schema: dict[str, Any], defs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Recursively resolve $ref references in a JSON Schema object."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"]
            if ref_path.startswith("#/$defs/"):
                ref_name = ref_path.split("/")[-1]
                if defs and ref_name in defs:
                    return _resolve_refs(defs[ref_name], defs)
            return schema  # pragma: no cover
        else:
            return {k: _resolve_refs(v, defs) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [_resolve_refs(item, defs) for item in schema]
    else:
        return schema


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
    elif part.function_response:  # pragma: no cover
        raise NotImplementedError(
            "function_response part does not decode to AssistantContent."
        )
    elif part.thought_signature:  # pragma: no cover
        raise NotImplementedError("Support for thought signature not implemented.")
    else:  # pragma: no cover
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
    tool: ToolSchema,
) -> genai_types.FunctionDeclarationDict:
    """Convert a single Mirascope tool to Google FunctionDeclaration format with caching."""
    schema_dict = tool.parameters.model_dump(by_alias=True, exclude_none=True)
    schema_dict["type"] = "object"

    defs = schema_dict.get("$defs")
    properties = schema_dict.get("properties", {})
    if defs:
        properties = _resolve_refs(properties, defs)

    return genai_types.FunctionDeclarationDict(
        name=tool.name,
        description=tool.description,
        parameters=genai_types.SchemaDict(
            type=genai_types.Type.OBJECT,
            properties=properties,
            required=schema_dict.get("required", []),
        ),
    )


def prepare_google_request(
    *,
    model_id: GoogleModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
) -> tuple[
    Sequence[Message],
    Format[FormattableT] | None,
    genai_types.ContentListUnionDict,
    GoogleKwargs,
]:
    """Prepares a request for the genai `Client.models.generate_content` method."""
    google_config: GoogleKwargs = {}

    with _base_utils.ensure_all_params_accessed(
        params=params, provider="google", unsupported_params=["thinking"]
    ) as param_accessor:
        if param_accessor.temperature is not None:
            google_config["temperature"] = param_accessor.temperature
        if param_accessor.max_tokens is not None:
            google_config["max_output_tokens"] = param_accessor.max_tokens
        if param_accessor.top_p is not None:
            google_config["top_p"] = param_accessor.top_p
        if param_accessor.top_k is not None:
            google_config["top_k"] = param_accessor.top_k
        if param_accessor.seed is not None:
            google_config["seed"] = param_accessor.seed
        if param_accessor.stop_sequences is not None:
            google_config["stop_sequences"] = param_accessor.stop_sequences

    tools = tools.tools if isinstance(tools, BaseToolkit) else tools or []
    google_tools: list[genai_types.ToolDict] = []

    format = resolve_format(
        format,
        # Google does not support strict outputs when tools are present
        # (Gemini 2.5 will error, 2.0 and below will ignore tools)
        default_mode="strict" if not tools else "tool",
    )
    if format is not None:
        if format.mode in ("strict", "json") and tools:
            raise FeatureNotSupportedError(
                feature=f"formatting_mode:{format.mode} with tools",
                provider="google",
                model_id=model_id,
            )

        if format.mode == "strict":
            google_config["response_mime_type"] = "application/json"
            google_config["response_schema"] = format.schema
        elif format.mode == "tool":
            format_tool_schema = _formatting_utils.create_tool_schema(format)
            format_tool = _convert_tool_to_function_declaration(format_tool_schema)
            google_tools.append(
                genai_types.ToolDict(function_declarations=[format_tool])
            )
            function_calling_config = genai_types.FunctionCallingConfigDict(
                mode=genai_types.FunctionCallingConfigMode.ANY
            )
            if not tools:
                function_calling_config["allowed_function_names"] = [FORMAT_TOOL_NAME]

            google_config["tool_config"] = genai_types.ToolConfigDict(
                function_calling_config=function_calling_config
            )
        elif format.mode == "json":
            google_config["response_mime_type"] = "application/json"

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    if tools:
        function_declarations = [
            _convert_tool_to_function_declaration(tool) for tool in tools
        ]
        google_tools.append(
            genai_types.ToolDict(function_declarations=function_declarations)
        )

    if google_tools:
        google_config["tools"] = cast(genai_types.ToolListUnionDict, google_tools)

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    if system_message_content:
        google_config["system_instruction"] = system_message_content

    return messages, format, _encode_messages(remaining_messages), google_config


def decode_response(
    response: genai_types.GenerateContentResponse, model_id: GoogleModelId
) -> tuple[AssistantMessage, FinishReason | None]:
    """Returns an `AssistantMessage` and `FinishReason` extracted from a `GenerateContentResponse`"""
    if not response.candidates or not response.candidates[0].content:
        # Unclear under what circumstances this happens (if ever).
        # In testing, when generating no output at all, it creates a part with
        # no fields set.
        return AssistantMessage(
            content=[], provider="google", model_id=model_id, raw_content=[]
        ), None  # pragma: no cover
    candidate = response.candidates[0]
    assistant_message = AssistantMessage(
        content=_decode_candidate_content(candidate),
        provider="google",
        model_id=model_id,
        raw_content=[],
    )
    finish_reason = (
        GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason)
        if candidate.finish_reason
        else None
    )
    return assistant_message, finish_reason


class _GoogleChunkProcessor:
    """Processes Google stream chunks and maintains state across chunks."""

    def __init__(self) -> None:
        self.current_content_type: Literal["text", "tool_call"] | None = None

    def process_chunk(
        self, chunk: genai_types.GenerateContentResponse
    ) -> ChunkIterator:
        """Process a single Google chunk and yield the appropriate content chunks."""
        yield RawChunk(raw=chunk)

        candidate = chunk.candidates[0] if chunk.candidates else None
        if not candidate or not candidate.content or not candidate.content.parts:
            return  # pragma: no cover

        for part in candidate.content.parts:
            if part.thought:
                raise NotImplementedError

            elif part.text:
                if self.current_content_type == "tool_call":
                    # In testing, Gemini never emits tool calls and text in the same message
                    # (even when specifically asked in system and user prompt), so
                    # the following code is uncovered but included for completeness
                    yield ToolCallEndChunk()  # pragma: no cover
                    self.current_content_type = None  # pragma: no cover

                if self.current_content_type is None:
                    yield TextStartChunk()
                    self.current_content_type = "text"
                elif self.current_content_type != "text":
                    raise NotImplementedError

                yield TextChunk(delta=part.text)

            elif function_call := part.function_call:
                if self.current_content_type == "text":
                    # Similar to above, this does not seem to happen in practice but is
                    # included for safety.
                    yield TextEndChunk()  # pragma: no cover
                    self.current_content_type = None  # pragma: no cover

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
            if self.current_content_type == "text":
                yield TextEndChunk()
            elif self.current_content_type is not None:
                raise NotImplementedError

            self.current_content_type = None

            finish_reason = GOOGLE_FINISH_REASON_MAP.get(candidate.finish_reason)
            if finish_reason is not None:
                yield FinishReasonChunk(finish_reason=finish_reason)


def convert_google_stream_to_chunk_iterator(
    google_stream: Iterator[genai_types.GenerateContentResponse],
) -> ChunkIterator:
    """Returns a ChunkIterator converted from a Google stream."""
    processor = _GoogleChunkProcessor()
    for chunk in google_stream:
        yield from processor.process_chunk(chunk)


async def convert_google_stream_to_async_chunk_iterator(
    google_stream: AsyncIterator[genai_types.GenerateContentResponse],
) -> AsyncChunkIterator:
    """Returns an AsyncChunkIterator converted from a Google async stream."""
    processor = _GoogleChunkProcessor()
    async for chunk in google_stream:
        for item in processor.process_chunk(chunk):
            yield item
