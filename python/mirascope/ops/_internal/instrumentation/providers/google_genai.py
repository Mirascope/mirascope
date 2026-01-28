"""OpenTelemetry instrumentation for Google GenAI SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry.instrumentation.google_genai import GoogleGenAiSdkInstrumentor

from .base import BaseInstrumentation, ContentCaptureMode

if TYPE_CHECKING:
    from opentelemetry.trace import TracerProvider


class GoogleGenAIInstrumentation(BaseInstrumentation[GoogleGenAiSdkInstrumentor]):
    """Manages OpenTelemetry instrumentation lifecycle for the Google GenAI SDK."""

    def _create_instrumentor(self) -> GoogleGenAiSdkInstrumentor:
        """Create a new Google GenAI instrumentor instance."""
        return GoogleGenAiSdkInstrumentor()

    def _configure_capture_content(self, capture_content: ContentCaptureMode) -> None:
        """Configure environment variables for Google GenAI content capture."""
        # Google GenAI uses ContentCapturingMode enum instead of true/false.
        # Valid values: NO_CONTENT, SPAN_ONLY, EVENT_ONLY, SPAN_AND_EVENT
        if capture_content == "enabled":
            self._set_env_var(
                "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
                "SPAN_AND_EVENT",
            )
        elif capture_content == "disabled":
            self._set_env_var(
                "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "NO_CONTENT"
            )


def instrument_google_genai(
    *,
    tracer_provider: TracerProvider | None = None,
    capture_content: ContentCaptureMode = "default",
) -> None:
    """Enable OpenTelemetry instrumentation for the Google GenAI Python SDK.

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
        ops.instrument_google_genai()
        ```

        Enable instrumentation with content capture:
        ```python
        from mirascope import ops

        ops.configure()
        ops.instrument_google_genai(capture_content="enabled")
        ```
    """
    GoogleGenAIInstrumentation().instrument(
        tracer_provider=tracer_provider,
        capture_content=capture_content,
    )


def uninstrument_google_genai() -> None:
    """Disable previously configured Google GenAI instrumentation."""
    GoogleGenAIInstrumentation().uninstrument()


def is_google_genai_instrumented() -> bool:
    """Return whether Google GenAI instrumentation is currently active."""
    return GoogleGenAIInstrumentation().is_instrumented
