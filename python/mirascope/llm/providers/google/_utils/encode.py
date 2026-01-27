"""Google message encoding and request preparation."""

from __future__ import annotations

import base64
import json
from collections.abc import Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, Any, TypedDict, cast
from typing_extensions import Required

from google.genai import types as genai_types

from ....content import ContentPart
from ....exceptions import FeatureNotSupportedError
from ....formatting import (
    Format,
    FormatSpec,
    FormattableT,
    resolve_format,
)
from ....messages import AssistantMessage, Message, UserMessage
from ....tools import (
    FORMAT_TOOL_NAME,
    AnyToolSchema,
    BaseToolkit,
    ProviderTool,
    WebSearchTool,
)
from ...base import _utils as _base_utils
from ..model_id import GoogleModelId, model_name
from ..model_info import MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT

if TYPE_CHECKING:
    from ....models import Params, ThinkingConfig, ThinkingLevel

UNKNOWN_TOOL_ID = "google_unknown_tool_id"

# Thinking level to a float multiplier % of max tokens (for 2.5 models using budget)
THINKING_LEVEL_TO_BUDGET_MULTIPLIER: dict[ThinkingLevel, float] = {
    "none": 0,
    "minimal": 0.1,
    "low": 0.2,
    "medium": 0.4,
    "high": 0.6,
    "max": 0.8,
}

# Gemini 3 Pro supports only LOW or HIGH
# https://ai.google.dev/gemini-api/docs/gemini-3#thinking_level
THINKING_LEVEL_FOR_GEMINI_3_PRO: dict[ThinkingLevel, genai_types.ThinkingLevel] = {
    "default": genai_types.ThinkingLevel.THINKING_LEVEL_UNSPECIFIED,
    "none": genai_types.ThinkingLevel.LOW,
    "minimal": genai_types.ThinkingLevel.LOW,
    "low": genai_types.ThinkingLevel.LOW,
    "medium": genai_types.ThinkingLevel.HIGH,
    "high": genai_types.ThinkingLevel.HIGH,
    "max": genai_types.ThinkingLevel.HIGH,
}

# Gemini 3 Flash supports MINIMAL, LOW, MEDIUM, HIGH
# https://ai.google.dev/gemini-api/docs/gemini-3#thinking_level
THINKING_LEVEL_FOR_GEMINI_3_FLASH: dict[ThinkingLevel, genai_types.ThinkingLevel] = {
    "default": genai_types.ThinkingLevel.THINKING_LEVEL_UNSPECIFIED,
    "none": genai_types.ThinkingLevel.MINIMAL,
    "minimal": genai_types.ThinkingLevel.MINIMAL,
    "low": genai_types.ThinkingLevel.LOW,
    "medium": genai_types.ThinkingLevel.MEDIUM,
    "high": genai_types.ThinkingLevel.HIGH,
    "max": genai_types.ThinkingLevel.HIGH,
}


def google_thinking_config(
    thinking_config: ThinkingConfig,
    max_tokens: int | None,
    model_id: GoogleModelId,
) -> genai_types.ThinkingConfigDict:
    """Compute Google thinking configuration based on model version.

    Args:
        thinking_config: The ThinkingConfig from params
        max_tokens: Max output tokens (used to compute budget for 2.5 models)
        model_id: The Google model ID to determine version

    Returns:
        ThinkingConfigDict with either thinking_level or thinking_budget set.

    Notes:
        - Gemini 2.5 models use thinking_budget (token count)
        - Gemini 3.0 Pro supports thinking_level "low" or "high"
        - Gemini 3.0 Flash supports thinking_level "minimal", "low", "medium", "high"

    See: https://ai.google.dev/gemini-api/docs/gemini-3#thinking_level
    """
    level: ThinkingLevel = thinking_config.get("level", "default")
    include_thoughts = thinking_config.get("include_thoughts")

    result = genai_types.ThinkingConfigDict()

    if "gemini-3-flash" in model_id:
        result["thinking_level"] = THINKING_LEVEL_FOR_GEMINI_3_FLASH.get(
            level, genai_types.ThinkingLevel.THINKING_LEVEL_UNSPECIFIED
        )
    elif "gemini-3-pro" in model_id:
        result["thinking_level"] = THINKING_LEVEL_FOR_GEMINI_3_PRO.get(
            level, genai_types.ThinkingLevel.THINKING_LEVEL_UNSPECIFIED
        )
    else:  # Fall back to 2.5-style budgets
        # 2.5 models use thinking_budget
        if level == "default":
            budget = -1  # Dynamic budget
        elif level == "none":
            budget = 0  # Disable thinking
        else:
            # Compute budget as percentage of max_tokens
            if max_tokens is None:
                max_tokens = 16000
            multiplier = THINKING_LEVEL_TO_BUDGET_MULTIPLIER.get(level, 0.4)
            budget = int(multiplier * max_tokens)

        result["thinking_budget"] = budget
    if include_thoughts is not None:
        result["include_thoughts"] = include_thoughts

    return result


class GoogleKwargs(TypedDict, total=False):
    """Kwargs for Google's generate_content method."""

    model: Required[str]
    contents: Required[genai_types.ContentListUnionDict]
    config: genai_types.GenerateContentConfigDict


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
    result: list[genai_types.PartDict] = []

    for part in content:
        if part.type == "text":
            result.append(genai_types.PartDict(text=part.text))
        elif part.type == "image":
            if part.source.type == "base64_image_source":
                result.append(
                    genai_types.PartDict(
                        inline_data=genai_types.BlobDict(
                            data=base64.b64decode(part.source.data),
                            mime_type=part.source.mime_type,
                        )
                    )
                )
            elif part.source.type == "url_image_source":
                raise FeatureNotSupportedError(
                    "url_image_source",
                    "google",
                    message="Google does not support URL-referenced images. Try `llm.Image.download(...) or `llm.Image.download_async(...)`",
                )
        elif part.type == "audio":
            if part.source.type == "base64_audio_source":
                result.append(
                    genai_types.PartDict(
                        inline_data=genai_types.BlobDict(
                            data=base64.b64decode(part.source.data),
                            mime_type=part.source.mime_type,
                        )
                    )
                )
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
                        response={"output": str(part.result)},
                    )
                )
            )
        elif part.type == "thought":
            if encode_thoughts:
                result.append(
                    genai_types.PartDict(text="**Thinking:** " + part.thought)
                )
        else:
            raise NotImplementedError(f"Unsupported content type: {part.type}")
    return result


def _encode_message(
    message: UserMessage | AssistantMessage,
    model_id: GoogleModelId,
    encode_thoughts: bool,
) -> genai_types.ContentDict:
    """Returns a Google `ContentDict` converted from a Mirascope `Message`"""
    if (
        message.role == "assistant"
        and message.provider_id == "google"
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
    tool: AnyToolSchema | ProviderTool,
) -> genai_types.FunctionDeclarationDict:
    """Convert a single Mirascope tool to Google FunctionDeclaration format with caching."""
    if isinstance(tool, ProviderTool):
        raise FeatureNotSupportedError(
            f"Provider tool {tool.name}", provider_id="google"
        )
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
    tools: BaseToolkit[AnyToolSchema],
    format: FormatSpec[FormattableT] | None,
    params: Params,
) -> tuple[Sequence[Message], Format[FormattableT] | None, GoogleKwargs]:
    """Prepares a request for the genai `Client.models.generate_content` method."""
    if not model_id.startswith("google/"):  # pragma: no cover
        raise ValueError(f"Model ID must start with 'google/' prefix, got: {model_id}")

    google_config: genai_types.GenerateContentConfigDict = (
        genai_types.GenerateContentConfigDict()
    )
    encode_thoughts_as_text = False
    google_model_name = model_name(model_id)

    with _base_utils.ensure_all_params_accessed(
        params=params, provider_id="google"
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
            thinking_config = param_accessor.thinking

            # Compute thinking config based on model version
            google_config["thinking_config"] = google_thinking_config(
                thinking_config, param_accessor.max_tokens, model_id
            )

            # Handle encode_thoughts_as_text from ThinkingConfig
            if thinking_config.get("encode_thoughts_as_text"):
                encode_thoughts_as_text = True

    if _base_utils.has_strict_tools(tools.tools):
        raise FeatureNotSupportedError(
            feature="strict tools",
            provider_id="google",
            model_id=model_id,
            message="Google does not support strict mode for tools. "
            "Set strict=False on your tools or omit the strict parameter.",
        )

    google_tools: list[genai_types.ToolDict] = []

    allows_strict_mode_with_tools = (
        google_model_name not in MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT
    )
    # Older google models do not allow strict mode when using tools; if so, we use tool
    # mode when tools are present by default for compatibility. Otherwise, prefer strict mode.
    default_mode = (
        "tool" if tools.tools and not allows_strict_mode_with_tools else "strict"
    )
    format = resolve_format(format, default_mode=default_mode)
    if format is not None:
        if (
            format.mode in ("strict", "json")
            and tools.tools
            and not allows_strict_mode_with_tools
        ):
            raise FeatureNotSupportedError(
                feature=f"formatting_mode:{format.mode} with tools",
                provider_id="google",
                model_id=model_id,
            )

        if format.mode == "strict":
            google_config["response_mime_type"] = "application/json"
            google_config["response_schema"] = format.schema
        elif format.mode == "tool":
            format_tool_schema = format.create_tool_schema()
            format_tool = _convert_tool_to_function_declaration(format_tool_schema)
            google_tools.append(
                genai_types.ToolDict(function_declarations=[format_tool])
            )
            function_calling_config = genai_types.FunctionCallingConfigDict(
                mode=genai_types.FunctionCallingConfigMode.ANY
            )
            if not tools.tools:
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

    if tools.tools:
        # Separate web search tools from function tools
        function_tools = [t for t in tools.tools if not isinstance(t, WebSearchTool)]
        has_web_search = any(isinstance(t, WebSearchTool) for t in tools.tools)

        if function_tools:
            function_declarations = [
                _convert_tool_to_function_declaration(tool) for tool in function_tools
            ]
            google_tools.append(
                genai_types.ToolDict(function_declarations=function_declarations)
            )

        if has_web_search:
            google_tools.append(
                genai_types.ToolDict(google_search=genai_types.GoogleSearchDict())
            )

    if google_tools:
        google_config["tools"] = cast(genai_types.ToolListUnionDict, google_tools)

    system_message_content, remaining_messages = _base_utils.extract_system_message(
        messages
    )

    if system_message_content:
        google_config["system_instruction"] = system_message_content

    kwargs = GoogleKwargs(
        model=model_name(model_id),
        contents=_encode_messages(
            remaining_messages, model_id, encode_thoughts_as_text
        ),
        config=google_config,
    )

    return messages, format, kwargs
