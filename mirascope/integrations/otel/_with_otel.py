"""Mirascope x OpenTelemetry Integration."""

from collections.abc import Callable
from typing import ParamSpec, TypeVar

from .._middleware_factory import middleware_factory
from ._utils import (
    custom_context_manager,
    handle_call_response,
    handle_call_response_async,
    handle_response_model,
    handle_response_model_async,
    handle_stream,
    handle_stream_async,
    handle_structured_stream,
    handle_structured_stream_async,
)

_P = ParamSpec("_P")
_R = TypeVar("_R")


def with_otel() -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Wraps a Mirascope function with OpenTelemetry.

    Example:

    ```python
    from mirascope.core import anthropic, prompt_template
    from mirascope.integrations.otel import with_otel, configure

    configure()


    def format_book(title: str, author: str) -> str:
        return f"{title} by {author}"


    @with_otel()
    @anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    print(recommend_book("fantasy"))
    ```
    """

    return middleware_factory(
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
