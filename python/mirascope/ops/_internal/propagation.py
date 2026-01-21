"""Context propagation utilities for distributed tracing."""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping, MutableMapping
from typing import Literal, TypeAlias

from opentelemetry import propagate
from opentelemetry.context import Context
from opentelemetry.propagators.b3 import B3MultiFormat, B3SingleFormat
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.propagators.textmap import Setter, TextMapPropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from ..exceptions import ConfigurationError
from .session import SESSION_HEADER_NAME, current_session

logger = logging.getLogger(__name__)

PropagatorFormat: TypeAlias = Literal[
    "tracecontext", "b3", "b3multi", "jaeger", "composite"
]
CarrierValue: TypeAlias = str | list[str]

# Environment variable names
ENV_PROPAGATOR_FORMAT = "MIRASCOPE_PROPAGATOR"
ENV_PROPAGATOR_SET_GLOBAL = "_MIRASCOPE_PROPAGATOR_SET_GLOBAL"

_PROPAGATOR: ContextPropagator | None = None


class _StrSetter(Setter[MutableMapping[str, str]]):
    """Setter that writes string header values into the carrier."""

    def set(self, carrier: MutableMapping[str, str], key: str, value: str) -> None:
        """Set a single header value on the carrier."""
        carrier[key] = value


_STR_SETTER = _StrSetter()


class ContextPropagator:
    """Manages OpenTelemetry context propagation across service boundaries."""

    _propagator: TextMapPropagator

    def __init__(self, *, set_global: bool = True) -> None:
        """Initialize propagator and optionally set as global.

        Propagator format is determined by MIRASCOPE_PROPAGATOR environment variable.
        Defaults to "tracecontext" if not set.

        Args:
            set_global: Whether to set this propagator as the global textmap propagator.

        Raises:
            ConfigurationError: If the propagator format is invalid.
        """
        env_format = os.environ.get(ENV_PROPAGATOR_FORMAT, "tracecontext")
        propagator_name: PropagatorFormat
        if env_format in ("tracecontext", "b3", "b3multi", "jaeger", "composite"):
            propagator_name = env_format
        else:
            error_message = (
                f"Invalid propagator format: {env_format}. "
                f"Valid options: tracecontext, b3, b3multi, jaeger, composite"
            )
            logger.error(error_message)
            raise ConfigurationError(error_message)
        logger.debug(f"Initializing ContextPropagator with format: {propagator_name}")

        match propagator_name:
            case "tracecontext":
                self._propagator = TraceContextTextMapPropagator()
            case "b3":
                self._propagator = B3SingleFormat()
            case "b3multi":
                self._propagator = B3MultiFormat()
            case "jaeger":
                self._propagator = JaegerPropagator()
            case "composite":
                propagators: list[TextMapPropagator] = [
                    TraceContextTextMapPropagator(),
                    B3SingleFormat(),
                    B3MultiFormat(),
                    JaegerPropagator(),
                ]
                self._propagator = CompositePropagator(propagators)

        if set_global:
            should_set_global = os.environ.get(ENV_PROPAGATOR_SET_GLOBAL, "true")
            if should_set_global.lower() == "true":
                propagate.set_global_textmap(self._propagator)
                logger.debug(f"Set {propagator_name} as global textmap propagator")

    def extract_context(self, carrier: Mapping[str, CarrierValue]) -> Context:
        """Extract OTEL context from carrier headers.

        Args:
            carrier: Dictionary containing HTTP headers or similar carrier data.

        Returns:
            Extracted OpenTelemetry context. Returns empty context if extraction fails.
        """
        try:
            context = self._propagator.extract(carrier=carrier)
            logger.debug("Successfully extracted context from carrier")
            return context
        except Exception as exception:
            logger.debug(
                f"Failed to extract context from carrier: {type(exception).__name__}: {exception}"
            )
            return Context()

    def inject_context(
        self,
        carrier: MutableMapping[str, str],
        context: Context | None = None,
    ) -> None:
        """Inject current OTEL context into carrier headers.

        This method also injects session context if one is active, adding the
        SESSION_HEADER_NAME header to the carrier.

        Args:
            carrier: Mutable mapping (e.g., HTTP headers dict) to inject context into.
            context: Optional specific context to inject. If None, uses current context.
        """
        try:
            self._propagator.inject(
                carrier=carrier, context=context, setter=_STR_SETTER
            )
            logger.debug("Successfully injected context into carrier")
        except Exception as exception:
            logger.debug(
                f"Failed to inject context into carrier: {type(exception).__name__}: {exception}"
            )

        session_ctx = current_session()
        if session_ctx is not None:
            carrier[SESSION_HEADER_NAME] = session_ctx.id


def get_propagator() -> ContextPropagator:
    """Get or create the singleton ContextPropagator instance.

    Reads propagator format from MIRASCOPE_PROPAGATOR environment variable.

    Returns:
        The global ContextPropagator instance.
    """
    global _PROPAGATOR
    if _PROPAGATOR is None:
        _PROPAGATOR = ContextPropagator()
    return _PROPAGATOR


def reset_propagator() -> None:
    """Reset the singleton ContextPropagator instance.

    This is primarily useful for testing to ensure a clean state between tests.
    The next call to get_propagator() will create a new instance.
    """
    global _PROPAGATOR
    _PROPAGATOR = None


def extract_context(carrier: Mapping[str, CarrierValue]) -> Context:
    """Extract OTEL context from carrier headers using the global propagator.

    Args:
        carrier: Dictionary containing HTTP headers or similar carrier data.

    Returns:
        Extracted OpenTelemetry context.
    """
    return get_propagator().extract_context(carrier)


def inject_context(
    carrier: MutableMapping[str, str],
    *,
    context: Context | None = None,
) -> None:
    """Inject current OTEL context into carrier headers using the global propagator.

    This function also injects session context if one is active, adding the
    SESSION_HEADER_NAME header to the carrier.

    Args:
        carrier: Mutable mapping (e.g., HTTP headers dict) to inject context into.
        context: Optional specific context to inject. If None, uses current context.
    """
    get_propagator().inject_context(carrier, context)
