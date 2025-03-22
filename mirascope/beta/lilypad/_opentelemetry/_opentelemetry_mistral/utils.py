from typing import Any

from mistralai import CompletionChunk, CompletionEvent
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.trace import Span
from opentelemetry.util.types import AttributeValue

from lilypad._opentelemetry._utils import ChoiceBuffer


class MistralMetadata(dict):
    finish_reasons: list[str]
    prompt_tokens: int | None
    completion_tokens: int | None
    response_model: str | None


class MistralChunkHandler:
    def extract_metadata(
        self, event: CompletionEvent, metadata: MistralMetadata
    ) -> None:
        chunk: CompletionChunk = event.data
        metadata["response_model"] = chunk.model
        if chunk.usage:
            usage = chunk.usage
            if usage.prompt_tokens:
                metadata["prompt_tokens"] = usage.prompt_tokens
            if usage.completion_tokens:
                metadata["completion_tokens"] = usage.completion_tokens

    def process_chunk(
        self, event: CompletionEvent, buffers: list[ChoiceBuffer]
    ) -> None:
        chunk: CompletionChunk = event.data
        for choice in chunk.choices:
            while len(buffers) <= choice.index:
                buffers.append(ChoiceBuffer(choice.index))
            if choice.finish_reason:
                buffers[choice.index].finish_reason = choice.finish_reason  # pyright: ignore [reportArgumentType, reportAttributeAccessIssue]
            if content := choice.delta.content:
                buffers[choice.index].append_text_content(content)  # pyright: ignore [reportArgumentType, reportAttributeAccessIssue]


def default_mistral_cleanup(
    span: Span, metadata: MistralMetadata, buffers: list[ChoiceBuffer]
) -> None:
    # Called when the stream ends to finalize attributes and events
    attributes: dict[str, AttributeValue] = {}
    if response_model := metadata.get("response_model"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_MODEL] = response_model
    if finish_reasons := metadata.get("finish_reasons"):
        attributes[gen_ai_attributes.GEN_AI_RESPONSE_FINISH_REASONS] = finish_reasons
    if prompt_tokens := metadata.get("prompt_tokens"):
        attributes[gen_ai_attributes.GEN_AI_USAGE_INPUT_TOKENS] = prompt_tokens
    if completion_tokens := metadata.get("completion_tokens"):
        attributes[gen_ai_attributes.GEN_AI_USAGE_OUTPUT_TOKENS] = completion_tokens

    span.set_attributes(attributes)
    for idx, choice in enumerate(buffers):
        message = {"role": "assistant"}
        if choice.text_content:
            message["content"] = "".join(choice.text_content)
        event_attributes: dict[str, AttributeValue] = {
            gen_ai_attributes.GEN_AI_SYSTEM: "mistral",
            "index": idx,
            "finish_reason": choice.finish_reason or "none",
            "message": str(message),
        }
        span.add_event("gen_ai.choice", attributes=event_attributes)


def get_mistral_llm_request_attributes(
    params: dict[str, Any],
) -> dict[str, AttributeValue]:
    attributes = {
        gen_ai_attributes.GEN_AI_OPERATION_NAME: "chat",
        gen_ai_attributes.GEN_AI_SYSTEM: "mistral",
    }
    model = params.get("model")
    if model is not None:
        attributes[gen_ai_attributes.GEN_AI_REQUEST_MODEL] = model
    return {k: v for k, v in attributes.items() if v is not None}
