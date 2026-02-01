"""Base class for OpenTelemetry SDK instrumentation."""

from __future__ import annotations

import os
import threading
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, Literal, Protocol, TypeVar

if TYPE_CHECKING:
    from opentelemetry.trace import TracerProvider

ContentCaptureMode = Literal["enabled", "disabled", "default"]

# OpenTelemetry semantic conventions environment variable
OTEL_SEMCONV_STABILITY_OPT_IN = "OTEL_SEMCONV_STABILITY_OPT_IN"
OTEL_SEMCONV_STABILITY_VALUE = "gen_ai_latest_experimental"


class Instrumentor(Protocol):
    """Protocol for OpenTelemetry instrumentors."""

    def instrument(self, *, tracer_provider: TracerProvider | None = None) -> None:
        """Enable instrumentation."""
        ...

    def uninstrument(self) -> None:
        """Disable instrumentation."""
        ...


InstrumentorT = TypeVar("InstrumentorT", bound=Instrumentor)


class BaseInstrumentation(ABC, Generic[InstrumentorT]):
    """Base class for managing OpenTelemetry instrumentation lifecycle.

    This class provides a thread-safe singleton pattern for SDK instrumentation.
    Subclasses must implement `_create_instrumentor()` and `_configure_capture_content()`.

    Each subclass gets its own `_instance` and `_instance_lock` via `__init_subclass__`,
    ensuring that different providers can be initialized independently without blocking.
    """

    _instance: BaseInstrumentation[InstrumentorT] | None = None
    _instance_lock: threading.Lock
    _lock: threading.Lock
    _instrumentor: InstrumentorT | None
    _original_env: dict[str, str | None]

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Initialize subclass with its own singleton instance and lock."""
        super().__init_subclass__(**kwargs)
        cls._instance = None
        cls._instance_lock = threading.Lock()

    def __new__(cls) -> BaseInstrumentation[InstrumentorT]:
        """Create or return the singleton instance."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._lock = threading.Lock()
                    instance._instrumentor = None
                    instance._original_env = {}
                    cls._instance = instance
        return cls._instance

    @property
    def is_instrumented(self) -> bool:
        """Return whether instrumentation is currently active."""
        return self._instrumentor is not None

    @abstractmethod
    def _create_instrumentor(self) -> InstrumentorT:
        """Create and return a new instrumentor instance.

        Returns:
            A new instance of the SDK-specific instrumentor.
        """
        ...

    @abstractmethod
    def _configure_capture_content(self, capture_content: ContentCaptureMode) -> None:
        """Configure environment variables for content capture.

        Args:
            capture_content: The capture content mode to configure.
        """
        ...

    def instrument(
        self,
        *,
        tracer_provider: TracerProvider | None = None,
        capture_content: ContentCaptureMode = "default",
    ) -> None:
        """Enable OpenTelemetry instrumentation for the SDK.

        Args:
            tracer_provider: Optional tracer provider to use. If not provided,
                uses the global OpenTelemetry tracer provider.
            capture_content: Controls whether to capture message content in spans.
        """
        with self._lock:
            if self.is_instrumented:
                return

            self._set_env_var(
                OTEL_SEMCONV_STABILITY_OPT_IN,
                OTEL_SEMCONV_STABILITY_VALUE,
                use_setdefault=True,
            )

            self._configure_capture_content(capture_content)

            instrumentor = self._create_instrumentor()
            try:
                if tracer_provider is not None:
                    instrumentor.instrument(tracer_provider=tracer_provider)
                else:
                    instrumentor.instrument()
            except Exception:
                self._restore_env_vars()
                raise

            self._instrumentor = instrumentor

    def uninstrument(self) -> None:
        """Disable previously configured instrumentation."""
        with self._lock:
            if self._instrumentor is None:
                return

            self._instrumentor.uninstrument()
            self._instrumentor = None
            self._restore_env_vars()

    def _set_env_var(
        self, key: str, value: str, *, use_setdefault: bool = False
    ) -> None:
        """Set an environment variable and track the original value.

        Args:
            key: The environment variable name.
            value: The value to set.
            use_setdefault: If True, only set if not already present.
        """
        if key not in self._original_env:
            self._original_env[key] = os.environ.get(key)

        if use_setdefault:
            os.environ.setdefault(key, value)
        else:
            os.environ[key] = value

    def _restore_env_vars(self) -> None:
        """Restore all environment variables to their original values."""
        for key, value in self._original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self._original_env.clear()

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset singleton instance for testing.

        This properly cleans up the instrumentor and restores environment variables
        before resetting the instance.
        """
        with cls._instance_lock:
            if cls._instance is not None:
                if cls._instance._instrumentor is not None:
                    cls._instance._instrumentor.uninstrument()
                    cls._instance._instrumentor = None
                cls._instance._restore_env_vars()
            cls._instance = None
