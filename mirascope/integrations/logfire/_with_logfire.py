"""Mirascope x Logfire Integration."""

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


def with_logfire():
    """Wraps a Mirascope function with Logfire tracing.

    Example:

    ```python
    import logfire
    from mirascope.core import anthropic, prompt_template
    from mirascope.integrations.logfire import with_logfire

    logfire.configure()


    def format_book(title: str, author: str):
        return f"{title} by {author}"


    @with_logfire()
    @anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
    @prompt_template("Recommend a {genre} book.")
    def recommend_book(genre: str):
        ...


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
