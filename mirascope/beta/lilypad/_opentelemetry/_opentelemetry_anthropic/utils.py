import json
from typing import Any, TypedDict

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.trace import Span
from opentelemetry.util.types import AttributeValue

from lilypad._opentelemetry._utils import ChoiceBuffer, set_server_address_and_port


class AnthropicMetadata(TypedDict, total=False):
    message_id: str | None
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    stop_reason: str | None


class AnthropicChunkHandler:
    def extract_metadata(self, chunk: Any, metadata: AnthropicMetadata) -> None:
        if not metadata.get("model") and hasattr(chunk, "model"):
            metadata["model"] = chunk.model
        if not metadata.get("message_id") and hasattr(chunk, "id"):
            metadata["message_id"] = chunk.id
        if not metadata.get("stop_reason") and hasattr(chunk, "stop_reason"):
            metadata["stop_reason"] = chunk.stop_reason
        if hasattr(chunk, "usage"):
            if hasattr(chunk.usage, "completion_tokens"):
                metadata["input_tokens"] = chunk.usage.input_tokens
            if hasattr(chunk.usage, "prompt_tokens"):
                metadata["output_tokens"] = chunk.usage.output_tokens

    def process_chunk(self, chunk: Any, buffers: list[ChoiceBuffer]) -> None:
        if not hasattr(chunk, "index"):
            return None
        while len(buffers) <= chunk.index:
            buffers.append(ChoiceBuffer(len(buffers)))

        if hasattr(chunk, "stop_reason"):
            buffers[chunk.index].finish_reason = chunk.stop_reason

        if chunk.type == "content_block_delta" and chunk.delta.type == "text_delta":
            buffers[chunk.index].append_text_content(chunk.delta.text)
        if (
            chunk.type == "content_block_delta"
            and chunk.delta.type == "input_json_delta"
        ) and hasattr(chunk.delta, "tool_call"):
            tool_call = chunk.delta.tool_call
            buffers[chunk.index].append_tool_call(tool_call)

        if (
            chunk.type == "content_block_delta"
            and chunk.delta.type == "input_json_delta"
        ) and hasattr(chunk.delta, "partial_json"):
            # TODO: Handle partial_json
            ...


def default_anthropic_cleanup(
    span: Span, metadata: AnthropicMetadata, buffers: list[ChoiceBuffer]
) -> None:
    """Default Anthropic cleanup handler."""
    attributes: dict[str, AttributeValue] = {}
    if model := metadata.get("model"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_MODEL] = model
    if message_id := metadata.get("message_id"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_ID] = message_id
    if input_tokens := metadata.get("input_tokens"):
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = input_tokens
    if output_tokens := metadata.get("output_tokens"):
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = output_tokens
    if stop_reason := metadata.get("stop_reason"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = [stop_reason]

    span.set_attributes(attributes)
    for idx, choice in enumerate(buffers):
        message: dict[str, Any] = {"role": "assistant"}
        if choice.text_content:
            message["content"] = "".join(choice.text_content)
        if choice.tool_calls_buffers:
            tool_calls = []
            for tool_call in choice.tool_calls_buffers:
                function = {
                    "name": tool_call.function_name,
                    "arguments": "".join(tool_call.arguments),
                }
                tool_call_dict = {
                    "id": tool_call.tool_call_id,
                    "type": "function",
                    "function": function,
                }
                tool_calls.append(tool_call_dict)
            message["tool_calls"] = tool_calls

        event_attributes = {
            gen_ai_attributes.GEN_AI_SYSTEM: gen_ai_attributes.GenAiSystemValues.ANTHROPIC.value,
            "index": idx,
            "finish_reason": choice.finish_reason or "none",
            "message": json.dumps(message),
        }
        span.add_event("gen_ai.choice", attributes=event_attributes)


def get_llm_request_attributes(
    kwargs: dict[str, Any],
    client_instance: Any,
    operation_name: str = gen_ai_attributes.GenAiOperationNameValues.CHAT.value,
) -> dict[str, AttributeValue]:
    attributes = {
        gen_ai_attributes.GEN_AI_OPERATION_NAME: operation_name,
        gen_ai_attributes.GEN_AI_SYSTEM: gen_ai_attributes.GenAiSystemValues.ANTHROPIC.value,
        gen_ai_attributes.GEN_AI_REQUEST_MODEL: kwargs.get("model"),
        gen_ai_attributes.GEN_AI_REQUEST_TEMPERATURE: kwargs.get("temperature"),
        gen_ai_attributes.GEN_AI_REQUEST_TOP_P: kwargs.get("p") or kwargs.get("top_p"),
        gen_ai_attributes.GEN_AI_REQUEST_TOP_K: kwargs.get("top_k"),
        gen_ai_attributes.GEN_AI_REQUEST_MAX_TOKENS: kwargs.get("max_tokens"),
        gen_ai_attributes.GEN_AI_REQUEST_STOP_SEQUENCES: kwargs.get("stop_sequences"),
        gen_ai_attributes.GEN_AI_REQUEST_PRESENCE_PENALTY: kwargs.get(
            "presence_penalty"
        ),
        gen_ai_attributes.GEN_AI_REQUEST_FREQUENCY_PENALTY: kwargs.get(
            "frequency_penalty"
        ),
        gen_ai_attributes.GEN_AI_OPENAI_REQUEST_RESPONSE_FORMAT: kwargs.get(
            "response_format"
        ),
        gen_ai_attributes.GEN_AI_OPENAI_REQUEST_SEED: kwargs.get("seed"),
    }

    set_server_address_and_port(client_instance, attributes)
    return {k: v for k, v in attributes.items() if v is not None}


def get_tool_call(content: Any) -> dict[str, Any] | None:
    if content.type != "tool_use":
        return None
    tool_call_dict = {}
    if call_id := content.id:
        tool_call_dict["id"] = call_id

    if tool_type := content.type:
        tool_call_dict["type"] = tool_type

    tool_call_dict["function"] = {}
    if func := content.input:
        tool_call_dict["function"]["arguments"] = func

    if name := content.name:
        tool_call_dict["function"]["name"] = name

    return tool_call_dict


def get_tool_calls(messages: list[Any]) -> list[dict[str, Any]]:
    calls = []
    for message in messages:
        if tool_call := get_tool_call(message):
            calls.append(tool_call)
    return calls


def set_message_event(span: Span, message: Any) -> None:
    attributes = {
        gen_ai_attributes.GEN_AI_SYSTEM: gen_ai_attributes.GenAiSystemValues.ANTHROPIC.value
    }
    role = message.get("role")
    if content := message.get("content"):
        if not isinstance(content, str):
            content = json.dumps(content)
        attributes["content"] = content
    elif role == "assistant" and (tool_calls := get_tool_calls(message)):
        attributes["tool_calls"] = json.dumps(tool_calls)
    # TODO: Convert to using Otel Events API
    span.add_event(
        f"gen_ai.{role}.message",
        attributes=attributes,
    )


def get_message_event(message: Any) -> dict[str, AttributeValue]:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_SYSTEM: gen_ai_attributes.GenAiSystemValues.ANTHROPIC.value
    }

    message_dict = {}
    if message.type == "text" and (content := message.text):
        message_dict["content"] = content
    if tool_calls := get_tool_call(message):
        message_dict["tool_calls"] = tool_calls

    attributes["message"] = json.dumps(message_dict)
    return attributes


def set_response_attributes(span: Span, response: Any) -> None:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_RESPONSE_MODEL: response.model
    }
    if content_list := response.content:
        for content in content_list:
            choice_attributes = get_message_event(content)
            span.add_event(
                "gen_ai.choice",
                attributes={
                    **choice_attributes,
                    "role": response.role,
                    "finish_reason": response.stop_reason or "error",
                },
            )
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = [
            response.stop_reason or "error"
        ]
    if id := response.id:
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_ID] = id

    if usage := getattr(response, "usage", None):
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = usage.input_tokens
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = usage.output_tokens
    span.set_attributes(attributes)
