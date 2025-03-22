"""Bedrock OpenTelemetry utilities."""

from __future__ import annotations

import json
from typing import Any

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.trace import Span
from opentelemetry.util.types import AttributeValue
from typing_extensions import TypedDict

from lilypad._opentelemetry._utils import ChoiceBuffer


class BedrockMetadata(TypedDict, total=False):
    """Metadata container for bedrock attributes such as prompt/completion tokens, model, and finish reasons."""

    finish_reasons: list[str]
    prompt_tokens: int | None
    completion_tokens: int | None
    response_model: str | None


class BedrockChunkHandler:
    """Handler to process partial bedrock output from streaming events and extract text or usage info."""

    def extract_metadata(self, chunk: Any, metadata: BedrockMetadata) -> None:
        """Extract fields like usage tokens or finish reasons from a streaming chunk."""
        if not isinstance(chunk, dict):
            return
        meta = chunk.get("metadata")
        if isinstance(meta, dict):
            usage = meta.get("usage")
            if isinstance(usage, dict):
                p_tokens = usage.get("inputTokens")
                c_tokens = usage.get("outputTokens")
                if isinstance(p_tokens, int):
                    metadata["prompt_tokens"] = p_tokens
                if isinstance(c_tokens, int):
                    metadata["completion_tokens"] = c_tokens
        message_stop = chunk.get("messageStop")
        if isinstance(message_stop, dict):
            stop_reason = message_stop.get("stopReason")
            if stop_reason:
                metadata.setdefault("finish_reasons", [])
                if stop_reason not in metadata["finish_reasons"]:  # pyright: ignore [reportTypedDictNotRequiredAccess]
                    metadata["finish_reasons"].append(stop_reason)  # pyright: ignore [reportTypedDictNotRequiredAccess]

    def process_chunk(self, chunk: Any, buffers: list[ChoiceBuffer]) -> None:
        """Process partial text or tool calls from a chunk and append to ChoiceBuffers."""
        if not isinstance(chunk, dict):
            return
        content_delta = chunk.get("contentBlockDelta")
        if not isinstance(content_delta, dict):
            return
        index = content_delta.get("contentBlockIndex", 0)
        while len(buffers) <= index:
            buffers.append(ChoiceBuffer(index))
        delta = content_delta.get("delta", {})
        if isinstance(delta, dict):
            text_fragment = delta.get("text")
            if isinstance(text_fragment, str):
                buffers[index].append_text_content(text_fragment)


def default_bedrock_cleanup(
    span: Span, metadata: BedrockMetadata, buffers: list[ChoiceBuffer]
) -> None:
    """Cleanup function to set final bedrock usage info and produce choice events."""
    attributes: dict[str, AttributeValue] = {}
    if (resp_model := metadata.get("response_model")) and isinstance(resp_model, str):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_MODEL] = resp_model
    if (p_tokens := metadata.get("prompt_tokens")) and isinstance(p_tokens, int):
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = p_tokens
    if (c_tokens := metadata.get("completion_tokens")) and isinstance(c_tokens, int):
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = c_tokens
    if (fr := metadata.get("finish_reasons")) and isinstance(fr, list):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = fr
    span.set_attributes(attributes)
    for idx, choice in enumerate(buffers):
        msg: dict[str, Any] = {"role": "assistant"}
        if choice.text_content:
            msg["content"] = "".join(choice.text_content)
        if choice.tool_calls_buffers:
            tool_calls = []
            for tool_call in choice.tool_calls_buffers:
                fn_data = {
                    "name": tool_call.function_name,
                    "arguments": "".join(tool_call.arguments),
                }
                tool_call_dict = {
                    "id": tool_call.tool_call_id,
                    "type": "function",
                    "function": fn_data,
                }
                tool_calls.append(tool_call_dict)
            msg["tool_calls"] = tool_calls
        event_attrs: dict[str, AttributeValue] = {
            gen_ai_attributes.GEN_AI_SYSTEM: "bedrock",
            "index": idx,
            "finish_reason": choice.finish_reason or "none",
            "message": json.dumps(msg),
        }
        span.add_event("gen_ai.choice", attributes=event_attrs)


def set_bedrock_message_event(span: Span, message: dict[str, Any]) -> None:
    """Record a user/system message in the span as an event."""
    if not span.is_recording():
        return
    role = message.get("role", "")
    content_val = message.get("content")
    if isinstance(content_val, list | dict):
        try:
            content_str = json.dumps(content_val)
        except (TypeError, ValueError):
            content_str = str(content_val)
    elif isinstance(content_val, str):
        content_str = content_val
    else:
        content_str = ""
    evt_name = f"gen_ai.{role}.message"
    attributes = {gen_ai_attributes.GEN_AI_SYSTEM: "bedrock", "content": content_str}
    span.add_event(evt_name, attributes=attributes)


def get_bedrock_llm_request_attributes(
    params: dict[str, Any],
    instance: Any | None = None,
) -> dict[str, AttributeValue]:
    """Return bedrock request attributes such as modelId, temperature, topP, maxTokens, and stop sequences."""
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_OPERATION_NAME: "chat",
        gen_ai_attributes.GEN_AI_SYSTEM: "bedrock",
    }
    model_id = params.get("modelId")
    if isinstance(model_id, str):
        attributes[gen_ai_attributes.GEN_AI_REQUEST_MODEL] = model_id
    inference_config = params.get("inferenceConfig")
    if not isinstance(inference_config, dict):
        inference_config = {}
    temp = inference_config.get("temperature")
    if isinstance(temp, int | float):
        attributes[gen_ai_attributes.GEN_AI_REQUEST_TEMPERATURE] = float(temp)
    top_p = inference_config.get("topP")
    if isinstance(top_p, int | float):
        attributes[gen_ai_attributes.GEN_AI_REQUEST_TOP_P] = float(top_p)
    max_tokens = inference_config.get("maxTokens") or params.get("maxTokens")
    if isinstance(max_tokens, int):
        attributes[gen_ai_attributes.GEN_AI_REQUEST_MAX_TOKENS] = max_tokens
    stops = inference_config.get("stopSequences")
    if isinstance(stops, str):
        stops = [stops]
    if isinstance(stops, list):
        attributes[gen_ai_attributes.GEN_AI_REQUEST_STOP_SEQUENCES] = stops
    return {k: v for k, v in attributes.items() if v is not None}
