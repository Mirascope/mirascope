from collections.abc import Collection
from typing import Any

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from .patch import chat_completions_create, chat_completions_create_async


class AnthropicInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ("anthropic>=0.29.0,<1.0",)

    def _instrument(self, **kwargs: Any) -> None:
        """Enable Anthropic instrumentation."""
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "0.1.0",  # Lilypad version
            tracer_provider,
            schema_url=Schemas.V1_28_0.value,
        )
        wrap_function_wrapper(
            module="anthropic.resources.messages",
            name="Messages.create",
            wrapper=chat_completions_create(tracer),
        )
        wrap_function_wrapper(
            module="anthropic.resources.messages",
            name="AsyncMessages.create",
            wrapper=chat_completions_create_async(tracer),
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        import anthropic

        unwrap(anthropic.resources.messages.Messages, "create")  # pyright: ignore[reportAttributeAccessIssue]
        unwrap(anthropic.resources.messages.AsyncMessages, "create")  # pyright: ignore[reportAttributeAccessIssue]
