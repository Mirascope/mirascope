"""Google message encoding and request preparation."""

import json
from collections.abc import Sequence
from functools import lru_cache
from typing import Any, cast

from google.genai import types as genai_types

from ....content import ContentPart
from ....exceptions import FeatureNotSupportedError
from ....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....tools import FORMAT_TOOL_NAME, BaseToolkit, ToolSchema
from ...base import BaseKwargs, Params, _utils as _base_utils
from ..model_ids import GoogleModelId

UNKNOWN_TOOL_ID = "google_unknown_tool_id"


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


def _encode_content(
    content: Sequence[ContentPart], encode_thoughts: bool
) -> list[genai_types.PartDict]:
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
        elif part.type == "thought":
            if encode_thoughts:
                result.append(
                    genai_types.PartDict(text="**Thinking:** " + part.thought)
                )
        else:
            raise NotImplementedError(
                f"Have not implemented conversion for {part.type}"
            )
    return result


def _encode_message(
    message: UserMessage | AssistantMessage,
    model_id: GoogleModelId,
    encode_thoughts: bool,
) -> genai_types.ContentDict:
    """Returns a Google `ContentDict` converted from a Mirascope `Message`"""
    if (
        message.role == "assistant"
        and message.provider == "google"
        and message.model_id == model_id
        and message.raw_message
        and not encode_thoughts
    ):
        return cast(genai_types.ContentDict, message.raw_message)
    return genai_types.ContentDict(
        role="model" if message.role == "assistant" else message.role,
        parts=_encode_content(message.content, encode_thoughts),
    )


def _encode_messages(
    messages: Sequence[UserMessage | AssistantMessage],
    model_id: GoogleModelId,
    encode_thoughts: bool,
) -> genai_types.ContentListUnionDict:
    """Returns a `ContentListUnionDict` converted from a sequence of user or assistant `Messages`s"""
    return [_encode_message(message, model_id, encode_thoughts) for message in messages]


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


def encode_request(
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
    google_config: GoogleKwargs = GoogleKwargs()
    encode_thoughts = False

    with _base_utils.ensure_all_params_accessed(
        params=params, provider="google"
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
        if param_accessor.thinking is not None:
            if param_accessor.thinking:
                google_config["thinking_config"] = genai_types.ThinkingConfigDict(
                    thinking_budget=-1,  # automatic budget
                    include_thoughts=True,
                )
            else:
                google_config["thinking_config"] = genai_types.ThinkingConfigDict(
                    include_thoughts=False, thinking_budget=0
                )
        if param_accessor.encode_thoughts_as_text:
            encode_thoughts = True

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

    return (
        messages,
        format,
        _encode_messages(remaining_messages, model_id, encode_thoughts),
        google_config,
    )
