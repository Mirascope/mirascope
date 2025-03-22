"""Utility functions for the OpenTelemetry Outlines integration."""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from typing import Any, ParamSpec, cast

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.trace import Span
from pydantic import BaseModel

P = ParamSpec("P")


def get_fn_args(
    fn: Callable, args: tuple[object, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Returns the `args` and `kwargs` as a dictionary bound by `fn`'s signature."""
    signature = inspect.signature(fn)
    bound_args = signature.bind_partial(*args, **kwargs)
    bound_args.apply_defaults()

    fn_args = {}
    for name, value in bound_args.arguments.items():
        if signature.parameters[name].kind == inspect.Parameter.VAR_KEYWORD:
            fn_args.update(value)
        else:
            fn_args[name] = value

    return fn_args


def record_prompts(span: Span, prompts: str | list[str]) -> None:
    """Record user prompts as events on the span."""
    if not span.is_recording():
        return
    if isinstance(prompts, str):
        span.add_event("gen_ai.user.message", attributes={"content": prompts})
    else:
        for p in prompts:
            span.add_event("gen_ai.user.message", attributes={"content": p})


def record_stop_sequences(span: Span, stop_at: str | list[str] | None) -> None:
    """Record stop sequences as an attribute on the span."""
    if not span.is_recording() or not stop_at:
        return
    stops = stop_at if isinstance(stop_at, list) else [stop_at]
    # stops is now list[str]
    span.set_attribute("outlines.request.stop_sequences", json.dumps(stops))


def set_choice_event(span: Span, result: Any) -> None:
    """Record the final choice as an event."""
    # Consider truncation if `result` is very large
    if span.is_recording():
        message = {"role": "assistant", "index": 0, "finish_reason": "none"}
        if isinstance(result, str):
            message["message"] = result
        elif isinstance(result, BaseModel):
            message["message"] = result.model_dump_json()

        span.add_event("gen_ai.choice", attributes=message)


def extract_arguments(
    wrapped: Callable[P, Any],
    instance: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> tuple[str | list[str], Any, Any, str]:
    bound_args = get_fn_args(wrapped, args, kwargs)
    prompts = cast(str | list[str] | None, bound_args.get("prompts"))
    if prompts is None:
        prompts = args[0]
    generation_parameters = bound_args.get("generation_parameters")
    sampling_parameters = bound_args.get("sampling_parameters")
    model_name = instance.__class__.__name__
    return prompts, generation_parameters, sampling_parameters, model_name


def extract_generation_attributes(
    generation_parameters: Any,
    sampling_parameters: Any,
    model_name: str,
) -> dict[str, Any]:
    """Extract common attributes from generation/sampling parameters."""
    attributes: dict[str, Any] = {
        gen_ai_attributes.GEN_AI_SYSTEM: "outlines",
        gen_ai_attributes.GEN_AI_OPERATION_NAME: "generate",
        gen_ai_attributes.GEN_AI_REQUEST_MODEL: model_name,
    }

    if generation_parameters:
        max_tokens = generation_parameters.max_tokens
        seed = generation_parameters.seed
        if max_tokens is not None:
            attributes[gen_ai_attributes.GEN_AI_REQUEST_MAX_TOKENS] = max_tokens
        if seed is not None:
            attributes["outlines.request.seed"] = seed

    if sampling_parameters:
        # sampling_parameters: (sampler, num_samples, top_p, top_k, temperature)
        top_p = sampling_parameters.top_p
        temperature = sampling_parameters.temperature
        if top_p is not None:
            attributes[gen_ai_attributes.GEN_AI_REQUEST_TOP_P] = top_p
        if temperature is not None:
            attributes[gen_ai_attributes.GEN_AI_REQUEST_TEMPERATURE] = temperature

    return attributes
