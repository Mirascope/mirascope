from collections.abc import Collection
from typing import Any

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from .patch import (
    mistral_complete_async_patch,
    mistral_complete_patch,
    mistral_stream_async_patch,
    mistral_stream_patch,
)


class MistralInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ("mistralai>=1.0.0,<2",)

    def _instrument(self, **kwargs: Any) -> None:
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "0.1.0",  # Lilypad version
            tracer_provider,
            schema_url=Schemas.V1_28_0.value,
        )

        # Patch sync complete
        wrap_function_wrapper(
            "mistralai.chat", "Chat.complete", mistral_complete_patch(tracer)
        )

        # Patch async complete
        wrap_function_wrapper(
            "mistralai.chat",
            "Chat.complete_async",
            mistral_complete_async_patch(tracer),
        )

        wrap_function_wrapper(
            "mistralai.chat", "Chat.stream", mistral_stream_patch(tracer)
        )
        wrap_function_wrapper(
            "mistralai.chat", "Chat.stream_async", mistral_stream_async_patch(tracer)
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        import mistralai.chat

        unwrap(mistralai.chat.Chat, "complete")
        unwrap(mistralai.chat.Chat, "complete_async")
        unwrap(mistralai.chat.Chat, "stream")
        unwrap(mistralai.chat.Chat, "stream_async")
