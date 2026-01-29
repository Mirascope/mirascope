"""OpenTelemetry instrumentation for Anthropic SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

from .base import BaseInstrumentation, ContentCaptureMode

if TYPE_CHECKING:
    from opentelemetry.trace import TracerProvider


class AnthropicInstrumentation(BaseInstrumentation[AnthropicInstrumentor]):
    """Manages OpenTelemetry instrumentation lifecycle for the Anthropic SDK."""

    def _create_instrumentor(self) -> AnthropicInstrumentor:
        """Create a new Anthropic instrumentor instance."""
        return AnthropicInstrumentor()

    def _configure_capture_content(self, capture_content: ContentCaptureMode) -> None:
        """Configure environment variables for Anthropic content capture."""
        if capture_content == "enabled":
            self._set_env_var("TRACELOOP_TRACE_CONTENT", "true")
        elif capture_content == "disabled":
            self._set_env_var("TRACELOOP_TRACE_CONTENT", "false")


def instrument_anthropic(
    *,
    tracer_provider: TracerProvider | None = None,
    capture_content: ContentCaptureMode = "default",
) -> None:
    """Enable OpenTelemetry instrumentation for the Anthropic Python SDK.

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
        ops.instrument_anthropic()
        ```

        Enable instrumentation with content capture:
        ```python
        from mirascope import ops

        ops.configure()
        ops.instrument_anthropic(capture_content="enabled")
        ```
    """
    AnthropicInstrumentation().instrument(
        tracer_provider=tracer_provider,
        capture_content=capture_content,
    )


def uninstrument_anthropic() -> None:
    """Disable previously configured Anthropic instrumentation."""
    AnthropicInstrumentation().uninstrument()


def is_anthropic_instrumented() -> bool:
    """Return whether Anthropic instrumentation is currently active."""
    return AnthropicInstrumentation().is_instrumented
