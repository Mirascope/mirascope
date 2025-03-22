"""Instrumentation for Outlines models."""

from __future__ import annotations

from collections.abc import Collection
from contextlib import suppress
from typing import Any

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from lilypad._opentelemetry._opentelemetry_outlines.patch import (
    model_generate,
    model_generate_async,
    model_generate_stream,
)

_patched_targets: list[tuple[str, ...]] = []


class OutlinesInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ("outlines>=0.1.10,<1.0",)

    def _instrument(self, **kwargs: Any) -> None:
        """Enable Outlines instrumentation."""
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "0.1.0",  # Lilypad version or plugin version
            tracer_provider,
            schema_url=Schemas.V1_28_0.value,
        )
        # Instrument ExLlamaV2Model
        wrap_function_wrapper(
            "outlines.models.exllamav2",
            "ExLlamaV2Model.generate",
            model_generate(tracer),
        )
        _patched_targets.append(
            ("outlines.models.exllamav2", "ExLlamaV2Model", "generate")
        )

        wrap_function_wrapper(
            "outlines.models.exllamav2",
            "ExLlamaV2Model.stream",
            model_generate_stream(tracer),
        )
        _patched_targets.append(
            ("outlines.models.exllamav2", "ExLlamaV2Model", "stream")
        )

        # LlamaCpp
        wrap_function_wrapper(
            "outlines.models.llamacpp",
            "LlamaCpp.generate",
            model_generate(tracer),
        )
        _patched_targets.append(("outlines.models.llamacpp", "LlamaCpp", "generate"))

        wrap_function_wrapper(
            "outlines.models.llamacpp",
            "LlamaCpp.stream",
            model_generate_stream(tracer),
        )
        _patched_targets.append(("outlines.models.llamacpp", "LlamaCpp", "stream"))

        # MLXLM
        wrap_function_wrapper(
            "outlines.models.mlxlm",
            "MLXLM.generate",
            model_generate(tracer),
        )
        _patched_targets.append(("outlines.models.mlxlm", "MLXLM", "generate"))

        wrap_function_wrapper(
            "outlines.models.mlxlm",
            "MLXLM.stream",
            model_generate_stream(tracer),
        )
        _patched_targets.append(("outlines.models.mlxlm", "MLXLM", "stream"))

        # OpenAI
        wrap_function_wrapper(
            "outlines.models.openai",
            "OpenAI.__call__",
            model_generate(tracer),
        )
        _patched_targets.append(("outlines.models.openai", "OpenAI", "__call__"))

        wrap_function_wrapper(
            "outlines.models.openai",
            "OpenAI.stream",
            model_generate_stream(tracer),
        )
        _patched_targets.append(("outlines.models.openai", "OpenAI", "stream"))

        # Transformers
        wrap_function_wrapper(
            "outlines.models.transformers",
            "Transformers.generate",
            model_generate(tracer),
        )
        _patched_targets.append(
            ("outlines.models.transformers", "Transformers", "generate")
        )

        wrap_function_wrapper(
            "outlines.models.transformers",
            "Transformers.stream",
            model_generate_stream(tracer),
        )
        _patched_targets.append(
            ("outlines.models.transformers", "Transformers", "stream")
        )

        # TransformersVision
        wrap_function_wrapper(
            "outlines.models.transformers_vision",
            "TransformersVision.generate",
            model_generate(tracer),
        )
        _patched_targets.append(
            ("outlines.models.transformers_vision", "TransformersVision", "generate")
        )

        wrap_function_wrapper(
            "outlines.models.transformers_vision",
            "TransformersVision.stream",
            model_generate_stream(tracer),
        )
        _patched_targets.append(
            ("outlines.models.transformers_vision", "TransformersVision", "stream")
        )

        # VLLM
        wrap_function_wrapper(
            "outlines.models.vllm",
            "VLLM.generate",
            model_generate(tracer),
        )
        _patched_targets.append(("outlines.models.vllm", "VLLM", "generate"))

        wrap_function_wrapper(
            "outlines.models.vllm",
            "VLLM.stream",
            model_generate_stream(tracer),
        )
        _patched_targets.append(("outlines.models.vllm", "VLLM", "stream"))

    def _uninstrument(self, **kwargs: Any) -> None:
        """Disable the instrumentation by restoring original methods."""
        for module_name, class_name, method_name in reversed(_patched_targets):
            with suppress(Exception):
                unwrap(__import__(module_name, fromlist=[class_name]), method_name)

        _patched_targets.clear()
