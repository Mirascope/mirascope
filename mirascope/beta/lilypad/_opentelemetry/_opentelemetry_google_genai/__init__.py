from collections.abc import Collection
from typing import Any

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from .patch import generate_content, generate_content_async


class GoogleGenAIInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        # Specifies the dependency range for the Google Gen AI SDK.
        return ("google-genai>=1.3.0,<2",)

    def _instrument(self, **kwargs: Any) -> None:
        """Enable instrumentation for the Google Gen AI SDK."""
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "0.1.0",  # Instrumentor version
            tracer_provider,
            schema_url=Schemas.V1_28_0.value,
        )

        # Wrap the synchronous generate_content method.
        wrap_function_wrapper(
            module="google.genai.models",
            name="Models.generate_content",
            wrapper=generate_content(tracer, stream=False),
        )
        wrap_function_wrapper(
            module="google.genai.models",
            name="Models.generate_content_stream",
            wrapper=generate_content(tracer, stream=True),
        )
        # Wrap the asynchronous generate_content_async method.
        wrap_function_wrapper(
            module="google.genai.models",
            name="AsyncModels.generate_content",
            wrapper=generate_content_async(tracer, stream=False),
        )
        wrap_function_wrapper(
            module="google.genai.models",
            name="AsyncModels.generate_content_stream",
            wrapper=generate_content_async(tracer, stream=True),
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        """Remove instrumentation by unwrapping the patched methods."""
        import google.genai.models
        from opentelemetry.instrumentation.utils import unwrap

        unwrap(google.genai.models.Models, "generate_content")
        unwrap(google.genai.models.Models, "generate_content_stream")
        unwrap(google.genai.models.AsyncModels, "generate_content")
        unwrap(google.genai.models.AsyncModels, "generate_content_stream")
