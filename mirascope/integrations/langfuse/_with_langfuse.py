"""Mirascope x Langfuse Integration."""

from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from langfuse.decorators import observe

from .._middleware_factory import middleware_factory
from ._utils import (
    handle_call_response,
    handle_call_response_async,
    handle_response_model,
    handle_response_model_async,
    handle_stream,
    handle_stream_async,
    handle_structured_stream,
    handle_structured_stream_async,
)

F = TypeVar("F", bound=Callable[..., Any])


def custom_decorator(fn: Callable) -> Callable[[F], F]:
    return observe(
        name=fn.__name__,
        as_type="generation",
        capture_input=False,
        capture_output=False,
    )


_P = ParamSpec("_P")
_R = TypeVar("_R")


def with_langfuse() -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Wraps a Mirascope function with Langfuse.

    Example:

    ```python
    from mirascope.core import anthropic, prompt_template
    from mirascope.integrations.langfuse import with_langfuse


    def format_book(title: str, author: str):
        return f"{title} by {author}"


    @with_langfuse()
    @anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    print(recommend_book("fantasy"))
    ```
    """

    return middleware_factory(
        custom_decorator=custom_decorator,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_response_model=handle_response_model,
        handle_response_model_async=handle_response_model_async,
        handle_structured_stream=handle_structured_stream,
        handle_structured_stream_async=handle_structured_stream_async,
    )
