"""OpenTelemetry instrumentation for OpenAI SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

from .base import BaseInstrumentation, ContentCaptureMode

if TYPE_CHECKING:
    from opentelemetry.trace import TracerProvider


class OpenAIInstrumentation(BaseInstrumentation[OpenAIInstrumentor]):
    """Manages OpenTelemetry instrumentation lifecycle for the OpenAI SDK."""

    def _create_instrumentor(self) -> OpenAIInstrumentor:
        """Create a new OpenAI instrumentor instance."""
        return OpenAIInstrumentor()

    def _configure_capture_content(self, capture_content: ContentCaptureMode) -> None:
        """Configure environment variables for OpenAI content capture."""
        if capture_content == "enabled":
            self._set_env_var(
                "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true"
            )
        elif capture_content == "disabled":
            self._set_env_var(
                "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
            )


def instrument_openai(
    *,
    tracer_provider: TracerProvider | None = None,
    capture_content: ContentCaptureMode = "default",
) -> None:
    """Enable OpenTelemetry instrumentation for the OpenAI Python SDK.

    Uses the provided tracer_provider or the global OpenTelemetry tracer provider.

    Args:
        tracer_provider: Optional tracer provider to use. If not provided,
            uses the global OpenTelemetry tracer provider.
        capture_content: Controls whether to capture message content in spans.
            - "enabled": Capture message content
            - "disabled": Do not capture message content
            - "default": Use the library's default behavior

    Example:

        Enable instrumentation with Mirascope Cloud:
        ```python
        from mirascope import ops

        ops.configure()
        ops.instrument_openai()
        ```

        Enable instrumentation with content capture:
        ```python
        from mirascope import ops

        ops.configure()
        ops.instrument_openai(capture_content="enabled")
        ```
    """
    OpenAIInstrumentation().instrument(
        tracer_provider=tracer_provider,
        capture_content=capture_content,
    )


def uninstrument_openai() -> None:
    """Disable previously configured OpenAI instrumentation."""
    OpenAIInstrumentation().uninstrument()


def is_openai_instrumented() -> bool:
    """Return whether OpenAI instrumentation is currently active."""
    return OpenAIInstrumentation().is_instrumented
