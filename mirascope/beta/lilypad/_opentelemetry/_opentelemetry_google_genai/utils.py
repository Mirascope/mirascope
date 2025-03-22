import base64
import json
from io import BytesIO
from typing import Any

import PIL
import PIL.WebPImagePlugin
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.trace import Span
from opentelemetry.util.types import AttributeValue


def get_llm_request_attributes(
    kwargs: dict[str, Any], instance: Any
) -> dict[str, AttributeValue]:
    """Extracts common request attributes from kwargs and instance.

    Sets default operation name, system, and model name.
    Also extracts generation parameters if provided.
    """
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_OPERATION_NAME: "generate_content",
        gen_ai_attributes.GEN_AI_SYSTEM: "google_genai",
        gen_ai_attributes.GEN_AI_REQUEST_MODEL: kwargs.get("model", "unknown"),
    }
    generation_config = kwargs.get("config")
    if generation_config and isinstance(generation_config, dict):
        if (temp := generation_config.get("temperature")) is not None:
            attributes[gen_ai_attributes.GEN_AI_REQUEST_TEMPERATURE] = temp
        if (top_p := generation_config.get("top_p")) is not None:
            attributes[gen_ai_attributes.GEN_AI_REQUEST_TOP_P] = top_p
        if (top_k := generation_config.get("top_k")) is not None:
            attributes[gen_ai_attributes.GEN_AI_REQUEST_TOP_K] = top_k
        if (max_tokens := generation_config.get("max_output_tokens")) is not None:
            attributes[gen_ai_attributes.GEN_AI_REQUEST_MAX_TOKENS] = max_tokens
    if kwargs.get("stream", False):
        attributes["google_genai.stream"] = True
    return {k: v for k, v in attributes.items() if v is not None}


def get_tool_calls(parts: list[Any]) -> list[dict[str, Any]]:
    calls = []
    for part in parts:
        tool_call = part.function_call
        if tool_call:
            tool_call_dict = {"type": "function", "function": {}}

            if name := getattr(tool_call, "name", None):
                tool_call_dict["function"]["name"] = name

                if hasattr(tool_call, "args"):
                    tool_call_dict["function"]["arguments"] = dict(
                        tool_call.args.items()
                    )

            calls.append(tool_call_dict)
    return calls


def set_content_event(span: Span, content: Any) -> None:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_SYSTEM: "google_genai"
    }
    role = content.get("role", "")
    parts = content.get("parts")
    content = []
    if role == "user" and parts:
        for part in parts:
            if isinstance(part, dict) and "mime_type" in part and "data" in part:
                # Handle binary data by base64 encoding it
                content.append(
                    {
                        "mime_type": part["mime_type"],
                        "data": base64.b64encode(part["data"]).decode("utf-8"),
                    }
                )
            elif isinstance(part, PIL.WebPImagePlugin.WebPImageFile):
                buffered = BytesIO()
                part.save(
                    buffered, format="WEBP"
                )  # Use "WEBP" to maintain the original format
                img_bytes = buffered.getvalue()
                content.append(
                    {
                        "mime_type": "image/webp",
                        "data": base64.b64encode(img_bytes).decode("utf-8"),
                    }
                )
            else:
                content.append(part)
        attributes["content"] = json.dumps(content)
    elif role == "model" and (tool_calls := get_tool_calls(parts)):
        attributes["tool_calls"] = json.dumps(tool_calls)
    # TODO: Convert to using Otel Events API
    span.add_event(
        f"gen_ai.{role}.message",
        attributes=attributes,
    )


def get_candidate_event(candidate: Any) -> dict[str, AttributeValue]:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_SYSTEM: "google_genai"
    }
    if content := candidate.content:
        message_dict = {
            "role": content.role,
        }
        if parts := content.parts:
            message_dict["content"] = [part.text for part in parts]
        if tool_calls := get_tool_calls(parts):
            message_dict["tool_calls"] = tool_calls
        attributes["message"] = json.dumps(message_dict)
        attributes["index"] = candidate.index
        attributes["finish_reason"] = (
            candidate.finish_reason.value
            if candidate.finish_reason is not None
            else "none"
        )
    return attributes


def set_response_attributes(span: Span, response: Any) -> None:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_RESPONSE_MODEL: getattr(
            response, "model_version", "unknown"
        )
    }
    if candidates := getattr(response, "candidates", None):
        finish_reasons = []
        for candidate in candidates:
            finish_reason = (
                candidate.finish_reason.value if candidate.finish_reason else "none"
            )
            choice_attributes = get_candidate_event(candidate)
            span.add_event(
                "gen_ai.choice",
                attributes=choice_attributes,
            )
            finish_reasons.append(finish_reason)
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = finish_reasons
    if id := getattr(response, "id", None):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_ID] = id
    if usage := getattr(response, "usage_metadata", None):
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = (
            usage.prompt_token_count
        )
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = (
            usage.candidates_token_count
        )

    span.set_attributes(attributes)


def set_stream(span: Span, stream: Any, instance: Any) -> None:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_RESPONSE_MODEL: getattr(
            instance, "model_version", "unknown"
        )
    }
    finish_reasons = []
    prompt_token_count = 0
    candidates_token_count = 0
    for chunk in stream:
        if candidates := getattr(chunk, "candidates", None):
            for candidate in candidates:
                finish_reason = (
                    candidate.finish_reason.value
                    if candidate.finish_reason
                    else "none",
                )
                choice_attributes = get_candidate_event(candidate)
                span.add_event(
                    "gen_ai.choice",
                    attributes=choice_attributes,
                )
                finish_reasons.append(finish_reason)
        if id := getattr(chunk, "id", None):
            attributes[gen_ai_attributes.GEN_AI_RESPONSE_ID] = id
        if usage := getattr(chunk, "usage_metadata", None):
            prompt_token_count += usage.prompt_token_count or 0
            candidates_token_count += usage.candidates_token_count or 0

    attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = (
        finish_reasons[0] if finish_reasons else "none"
    )
    if prompt_token_count > 0:
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = prompt_token_count
    if candidates_token_count > 0:
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = (
            candidates_token_count
        )
    span.set_attributes(attributes)


async def set_stream_async(span: Any, stream: Any, instance: Any) -> None:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_RESPONSE_MODEL: getattr(
            instance, "model_version", "unknown"
        )
    }
    finish_reasons = []
    prompt_token_count = 0
    candidates_token_count = 0
    async for chunk in stream:
        if candidates := getattr(chunk, "candidates", None):
            for candidate in candidates:
                finish_reason = (
                    candidate.finish_reason.value
                    if candidate.finish_reason
                    else "none",
                )
                choice_attributes = get_candidate_event(candidate)
                span.add_event(
                    "gen_ai.choice",
                    attributes=choice_attributes,
                )
                finish_reasons.append(finish_reason)
        if id := getattr(chunk, "id", None):
            attributes[gen_ai_attributes.GEN_AI_RESPONSE_ID] = id
        if usage := getattr(chunk, "usage_metadata", None):
            prompt_token_count += usage.prompt_token_count or 0
            candidates_token_count += usage.candidates_token_count or 0

    attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = (
        finish_reasons[0] if finish_reasons else "none"
    )
    if prompt_token_count > 0:
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = prompt_token_count
    if candidates_token_count > 0:
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = (
            candidates_token_count
        )
    span.set_attributes(attributes)
