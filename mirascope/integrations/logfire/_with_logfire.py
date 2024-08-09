"""Mirascope x Logfire Integration."""

from ..middleware_factory import middleware_decorator
from ._utils import (
    custom_context_manager,
    handle_response_model,
    handle_response_model_async,
    handle_call_response,
    handle_call_response_async,
    handle_stream,
    handle_stream_async,
    handle_structured_stream,
    handle_structured_stream_async,
)


def with_logfire(
    fn,
):
    """Wraps a Mirascope function with Logfire tracing."""
    return middleware_decorator(
        fn,
        custom_context_manager=custom_context_manager,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_response_model=handle_response_model,
        handle_response_model_async=handle_response_model_async,
        handle_structured_stream=handle_structured_stream,
        handle_structured_stream_async=handle_structured_stream_async,
    )
