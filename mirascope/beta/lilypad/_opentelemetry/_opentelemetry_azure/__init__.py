from collections.abc import Collection
from typing import Any

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from .patch import (
    chat_completions_complete,
    chat_completions_complete_async,
)


class AzureInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ("azure-ai-inference>=1.0.0b9,<2.0",)

    def _instrument(self, **kwargs: Any) -> None:
        """Enable Azure instrumentation."""
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "0.1.0",  # Lilypad version
            tracer_provider,
            schema_url=Schemas.V1_28_0.value,
        )
        wrap_function_wrapper(
            module="azure.ai.inference",
            name="ChatCompletionsClient.complete",
            wrapper=chat_completions_complete(tracer),
        )
        wrap_function_wrapper(
            module="azure.ai.inference.aio",
            name="ChatCompletionsClient.complete",
            wrapper=chat_completions_complete_async(tracer),
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        from azure.ai.inference import ChatCompletionsClient
        from azure.ai.inference.aio import (
            ChatCompletionsClient as AsyncChatCompletionsClient,
        )

        unwrap(ChatCompletionsClient, "complete")  # pyright: ignore[reportAttributeAccessIssue]
        unwrap(AsyncChatCompletionsClient, "complete")  # pyright: ignore[reportAttributeAccessIssue]
