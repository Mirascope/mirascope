"""Message encoding utilities for xAI SDK."""

from collections.abc import Sequence
from typing import Literal, TypedDict
from typing_extensions import Required

from xai_sdk import chat as xai_chat
from xai_sdk.chat import chat_pb2

from ....content import ContentPart
from ....exceptions import FeatureNotSupportedError, FormattingModeNotSupportedError
from ....formatting import (
    Format,
    FormattableT,
    _utils as _formatting_utils,
    resolve_format,
)
from ....messages import AssistantMessage, Message, SystemMessage, UserMessage
from ....tools import FORMAT_TOOL_NAME, BaseToolkit, ToolSchema
from ...base import Params, _utils as _base_utils
from ..model_ids import GrokModelId

UNKNOWN_TOOL_ID = "xai_unknown_tool_id"


class ChatCreateKwargs(TypedDict, total=False):
    """Kwargs for xAI chat.create method."""

    model: Required[str]
    messages: Required[list[chat_pb2.Message]]
    tools: list[chat_pb2.Tool] | None
    tool_choice: chat_pb2.ToolChoice | str | None
    temperature: float
    max_tokens: int
    top_p: float
    seed: int
    stop: list[str]
    reasoning_effort: str
    response_format: str


def encode_tools(tools: Sequence[ToolSchema] | None) -> list[chat_pb2.Tool]:
    """Convert Mirascope tools to xAI SDK tool format."""
    if not tools:
        return []

    xai_tools: list[chat_pb2.Tool] = []
    for tool in tools:
        parameters = tool.parameters.model_dump(by_alias=True, exclude_none=True)

        xai_tool = xai_chat.tool(
            name=tool.name,
            description=tool.description or "",
            parameters=parameters,
        )
        xai_tools.append(xai_tool)

    return xai_tools


def _encode_content_part(part: ContentPart) -> chat_pb2.Content | chat_pb2.Message:
    """Returns xAI SDK Content or Message from Mirascope content part."""
    if part.type == "text":
        return xai_chat.text(part.text)
    elif part.type == "image":
        raise FeatureNotSupportedError(
            "image",
            "xai",
            message=(
                "This Grok model does not support image inputs. "
                "Use grok-2-vision for image understanding, or download the image locally and convert it to text instead."
            ),
        )
    elif part.type == "audio":
        raise NotImplementedError("Audio content not supported by xAI SDK")
    elif part.type == "document":
        raise NotImplementedError("Document content not supported by xAI SDK")
    elif part.type == "tool_output":
        return xai_chat.tool_result(str(part.value))
    else:
        raise NotImplementedError(f"Unsupported content type: {part.type}")


def encode_message(
    message: Message, *, encode_thoughts: bool = False
) -> chat_pb2.Message | list[chat_pb2.Message]:
    """Convert a Mirascope Message to xAI SDK message format."""
    if isinstance(message, SystemMessage):
        return xai_chat.system(xai_chat.text(message.content.text))
    elif isinstance(message, UserMessage):
        tool_outputs = [part for part in message.content if part.type == "tool_output"]
        other_parts = [part for part in message.content if part.type != "tool_output"]

        messages = []

        if other_parts:
            content_parts = []
            for part in other_parts:
                converted = _encode_content_part(part)
                if converted is not None:
                    content_parts.append(converted)

            if content_parts:
                messages.append(xai_chat.user(*content_parts))
            else:
                messages.append(xai_chat.user(xai_chat.text("")))

        for tool_output in tool_outputs:
            messages.append(xai_chat.tool_result(str(tool_output.value)))

        if not messages:
            return xai_chat.user(xai_chat.text(""))
        elif len(messages) == 1:
            return messages[0]
        else:
            return messages
    elif isinstance(message, AssistantMessage):
        if (
            message.provider == "xai"
            and message.raw_message
            and isinstance(message.raw_message, dict)
            and not encode_thoughts
            and "tool_calls" in message.raw_message
        ):
            msg = chat_pb2.Message()
            msg.role = chat_pb2.MessageRole.ROLE_ASSISTANT

            content_list = message.raw_message.get("content", [])
            if isinstance(content_list, list):
                for content_dict in content_list:
                    if not isinstance(content_dict, dict):
                        continue
                    if content_dict.get("type") == "text":
                        text_val = content_dict.get("text")
                        if isinstance(text_val, str):
                            msg.content.append(xai_chat.text(text_val))
                    elif content_dict.get("type") == "thought":
                        thought_val = content_dict.get("thought")
                        if isinstance(thought_val, str):
                            msg.reasoning_content = thought_val

            tool_calls_list = message.raw_message.get("tool_calls", [])
            if isinstance(tool_calls_list, list):
                for tc_dict in tool_calls_list:
                    if not isinstance(tc_dict, dict):
                        continue
                    tc_id = tc_dict.get("id")
                    tc_function = tc_dict.get("function")
                    if isinstance(tc_id, str) and isinstance(tc_function, dict):
                        func_name = tc_function.get("name")
                        func_args = tc_function.get("arguments")
                        if isinstance(func_name, str) and isinstance(func_args, str):
                            tc = chat_pb2.ToolCall()
                            tc.id = tc_id
                            tc.function.name = func_name
                            tc.function.arguments = func_args
                            msg.tool_calls.append(tc)

            return msg

        parts = []
        for part in message.content:
            if part.type == "text":
                parts.append(xai_chat.text(part.text))
            elif part.type == "tool_call":
                parts.append(xai_chat.text(f"[Tool call: {part.name}]"))
            elif part.type == "thought" and encode_thoughts:
                parts.append(xai_chat.text(f"**Thinking:** {part.thought}"))

        if not parts:
            parts = [xai_chat.text("")]

        return xai_chat.assistant(*parts)
    else:
        raise ValueError(f"Unknown message type: {type(message)}")


def encode_messages(
    messages: Sequence[Message], *, encode_thoughts: bool = False
) -> list[chat_pb2.Message]:
    """Convert a sequence of Mirascope Messages to xAI SDK message format."""
    result = []
    for msg in messages:
        encoded = encode_message(msg, encode_thoughts=encode_thoughts)
        if isinstance(encoded, list):
            result.extend(encoded)
        else:
            result.append(encoded)
    return result


def _map_params_to_kwargs(params: Params, *, model_id: GrokModelId) -> dict:
    """Returns xAI SDK chat.create() kwargs from Mirascope Params."""
    kwargs = {}

    if "temperature" in params:
        kwargs["temperature"] = params["temperature"]
    if "max_tokens" in params:
        kwargs["max_tokens"] = params["max_tokens"]
    if "top_p" in params:
        kwargs["top_p"] = params["top_p"]
    if "seed" in params:
        kwargs["seed"] = params["seed"]
    if "stop_sequences" in params:
        kwargs["stop"] = params["stop_sequences"]
    thinking = params.get("thinking")
    if thinking is True:
        raise FeatureNotSupportedError(
            "thinking",
            "xai",
            model_id=model_id,
            message=(
                "xAI Grok models do not currently support the thinking parameter "
                "(the API will reject requests that include reasoning_effort)."
            ),
        )

    return kwargs


def _apply_format(
    *,
    format: type[FormattableT] | Format[FormattableT] | None,
    model_id: GrokModelId,
    tools: list[chat_pb2.Tool],
    messages: Sequence[Message],
) -> tuple[Format[FormattableT] | None, list[chat_pb2.Tool], Sequence[Message], dict]:
    """Returns tuple of (resolved_format, updated_tools, updated_messages, format_kwargs)."""
    format = resolve_format(format, default_mode="tool")
    format_kwargs = {}

    if format is None:
        return None, tools, messages, format_kwargs

    if format.mode == "strict":
        raise FormattingModeNotSupportedError(
            formatting_mode="strict", provider="xai", model_id=model_id
        )
    elif format.mode == "json":
        raise FeatureNotSupportedError(
            "structured_output_json",
            "xai",
            message="Grok JSON format output may deviate from expected schema; use tool mode or strict mode instead.",
        )
    elif format.mode == "tool":
        format_tool_schema = _formatting_utils.create_tool_schema(format)
        format_tool = encode_tools([format_tool_schema])[0]

        has_tool_outputs = any(
            isinstance(msg, UserMessage)
            and any(part.type == "tool_output" for part in msg.content)
            for msg in messages
        )

        if tools:
            tools = list(tools) + [format_tool]
            if has_tool_outputs:
                tool_choice = chat_pb2.ToolChoice()
                tool_choice.mode = chat_pb2.TOOL_MODE_REQUIRED
                tool_choice.function_name = FORMAT_TOOL_NAME
                format_kwargs["tool_choice"] = tool_choice
        else:
            tools = [format_tool]
            tool_choice = chat_pb2.ToolChoice()
            tool_choice.mode = chat_pb2.TOOL_MODE_REQUIRED
            tool_choice.function_name = FORMAT_TOOL_NAME
            format_kwargs["tool_choice"] = tool_choice

        if format.formatting_instructions:
            messages = _base_utils.add_system_instructions(
                messages, format.formatting_instructions
            )

    return format, tools, messages, format_kwargs


def encode_request(
    *,
    model_id: GrokModelId,
    messages: Sequence[Message],
    tools: Sequence[ToolSchema] | BaseToolkit | None,
    format: type[FormattableT] | Format[FormattableT] | None,
    params: Params,
    provider: Literal["xai"],
) -> tuple[Sequence[Message], Format[FormattableT] | None, dict]:
    """Encode request for xAI Grok API.

    Args:
        model_id: Model identifier.
        messages: Messages to send.
        tools: Optional tools.
        format: Optional response format.
        params: Additional parameters.
        provider: Provider name.

    Returns:
        Tuple of (input_messages, resolved_format, create_kwargs).
    """
    input_messages = list(messages)
    encode_thoughts = params.get("encode_thoughts_as_text") is True

    if tools is None:
        tool_list = None
    elif isinstance(tools, BaseToolkit):
        tool_list = tools.tools
    else:
        tool_list = list(tools)
    xai_tools = encode_tools(tool_list)

    format, xai_tools, input_messages, format_kwargs = _apply_format(
        format=format,
        model_id=model_id,
        tools=xai_tools,
        messages=input_messages,
    )

    xai_messages = encode_messages(input_messages, encode_thoughts=encode_thoughts)

    create_kwargs = _map_params_to_kwargs(params, model_id=model_id)
    create_kwargs.update(format_kwargs)
    create_kwargs["model"] = model_id
    create_kwargs["messages"] = xai_messages
    create_kwargs["tools"] = xai_tools if xai_tools else None

    return input_messages, format, create_kwargs
