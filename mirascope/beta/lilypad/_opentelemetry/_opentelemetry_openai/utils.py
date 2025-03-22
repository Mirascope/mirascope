# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications copyright (C) 2024 Mirascope
import json
from typing import Any, TypedDict

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.trace import Span
from opentelemetry.util.types import AttributeValue
from pydantic import BaseModel

from lilypad._opentelemetry._utils import ChoiceBuffer


class OpenAIMetadata(TypedDict, total=False):
    response_id: str | None
    response_model: str | None
    service_tier: str | None
    finish_reasons: list[str]
    prompt_tokens: int | None
    completion_tokens: int | None


class OpenAIChunkHandler:
    def extract_metadata(self, chunk: Any, metadata: OpenAIMetadata) -> None:
        if not metadata.get("response_model") and hasattr(chunk, "model"):
            metadata["response_model"] = chunk.model
        if not metadata.get("response_id") and hasattr(chunk, "id"):
            metadata["response_id"] = chunk.id
        if not metadata.get("service_tier") and hasattr(chunk, "service_tier"):
            metadata["service_tier"] = chunk.service_tier
        if hasattr(chunk, "usage"):
            if hasattr(chunk.usage, "completion_tokens"):
                metadata["completion_tokens"] = chunk.usage.completion_tokens
            if hasattr(chunk.usage, "prompt_tokens"):
                metadata["prompt_tokens"] = chunk.usage.prompt_tokens

    def process_chunk(self, chunk: Any, buffers: list[ChoiceBuffer]) -> None:
        if not hasattr(chunk, "choices"):
            return

        for choice in chunk.choices:
            if not choice.delta:
                continue

            # Ensure enough choice buffers
            while len(buffers) <= choice.index:
                buffers.append(ChoiceBuffer(len(buffers)))

            if choice.finish_reason:
                buffers[choice.index].finish_reason = choice.finish_reason

            if choice.delta.content is not None:
                buffers[choice.index].append_text_content(choice.delta.content)

            if choice.delta.tool_calls is not None:
                for tool_call in choice.delta.tool_calls:
                    buffers[choice.index].append_tool_call(tool_call)


def default_openai_cleanup(
    span: Span, metadata: OpenAIMetadata, buffers: list[ChoiceBuffer]
) -> None:
    """Default OpenAI cleanup handler"""
    attributes: dict[str, AttributeValue] = {}
    if response_model := metadata.get("response_model"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_MODEL] = response_model
    if response_id := metadata.get("response_id"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_ID] = response_id
    if prompt_tokens := metadata.get("prompt_tokens"):
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = prompt_tokens
    if completion_tokens := metadata.get("completion_tokens"):
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = completion_tokens
    if service_tier := metadata.get("service_tier"):
        attributes[gen_ai_attributes.GEN_AI_OPENAI_RESPONSE_SERVICE_TIER] = service_tier
    if finish_reasons := metadata.get("finish_reasons"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = finish_reasons

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

        event_attributes: dict[str, AttributeValue] = {
            gen_ai_attributes.GEN_AI_SYSTEM: "openai",
            "index": idx,
            "finish_reason": choice.finish_reason or "none",
            "message": json.dumps(message),
        }
        span.add_event("gen_ai.choice", attributes=event_attributes)


def get_tool_calls(message: dict | BaseModel) -> list[dict[str, Any]] | None:
    if isinstance(message, BaseModel):
        tool_calls = message.tool_calls  # pyright: ignore[reportAttributeAccessIssue]
    else:
        tool_calls = message.get("tool_calls")
    if tool_calls is None:
        return None
    calls = []
    for tool_call in tool_calls:
        tool_call_dict = {}
        if isinstance(tool_call, BaseModel):
            call_id = tool_call.id  # pyright: ignore[reportAttributeAccessIssue]
            tool_type = tool_call.type  # pyright: ignore[reportAttributeAccessIssue]
            tool_call_dict["function"] = tool_call.function.model_dump()  # pyright: ignore[reportAttributeAccessIssue]
        else:
            call_id = tool_call.get("id")
            tool_type = tool_call.get("type")
            if func := tool_call.get("function"):
                tool_call_dict["function"] = {}

                if name := func.get("name"):
                    tool_call_dict["function"]["name"] = name

                if arguments := func.get("arguments"):
                    tool_call_dict["function"]["arguments"] = arguments
        tool_call_dict["id"] = call_id
        tool_call_dict["type"] = tool_type
        calls.append(tool_call_dict)
    return calls


def set_message_event(span: Span, message: dict) -> None:
    attributes = {
        gen_ai_attributes.GEN_AI_SYSTEM: gen_ai_attributes.GenAiSystemValues.OPENAI.value
    }
    role = message.get("role", "")
    if content := message.get("content"):
        if not isinstance(content, str):
            content = json.dumps(content)
        attributes["content"] = content
    elif role == "assistant" and (tool_calls := get_tool_calls(message)):
        attributes["tool_calls"] = json.dumps(tool_calls)
    elif role == "tool" and (tool_call_id := message.get("tool_call_id")):
        attributes["id"] = tool_call_id
    # TODO: Convert to using Otel Events API
    span.add_event(
        f"gen_ai.{role}.message",
        attributes=attributes,
    )


def get_choice_event(choice: Any) -> dict[str, AttributeValue]:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_SYSTEM: gen_ai_attributes.GenAiSystemValues.OPENAI.value
    }

    if message := choice.message:
        message_dict = {
            "role": message.role,
        }
        if content := message.content:
            message_dict["content"] = content
        if tool_calls := get_tool_calls(message):
            message_dict["tool_calls"] = tool_calls

        attributes["message"] = json.dumps(message_dict)
        attributes["index"] = choice.index
        attributes["finish_reason"] = choice.finish_reason or "error"
    return attributes


def set_response_attributes(span: Span, response: Any) -> None:
    attributes: dict[str, AttributeValue] = {
        gen_ai_attributes.GEN_AI_RESPONSE_MODEL: response.model
    }
    if choices := getattr(response, "choices", None):
        finish_reasons = []
        for choice in choices:
            choice_attributes = get_choice_event(choice)
            span.add_event(
                "gen_ai.choice",
                attributes=choice_attributes,
            )
            finish_reasons.append(choice.finish_reason)
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = finish_reasons
    if id := getattr(response, "id", None):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_ID] = id

    if service_tier := getattr(response, "service_tier", None):
        attributes[gen_ai_attributes.GEN_AI_OPENAI_REQUEST_SERVICE_TIER] = service_tier

    if usage := getattr(response, "usage", None):
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = usage.prompt_tokens
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = (
            usage.completion_tokens
        )
    span.set_attributes(attributes)
