"""The `openai_call` decorator for easy OpenAI API typed functions."""
import datetime
import inspect
from typing import Callable, ParamSpec, TypeVar, Unpack

from openai import OpenAI

from .._internal import utils
from .types import OpenAICallParams, OpenAICallResponse

P = ParamSpec("P")
R = TypeVar("R")


def openai_call(
    **kwargs: Unpack[OpenAICallParams],
) -> Callable[[Callable[P, R]], Callable[P, OpenAICallResponse]]:
    '''A decorator for calling the OpenAI API with a typed function.

    This decorator is used to wrap a typed function that calls the OpenAI API. It parses
    the docstring of the wrapped function as the messages array and templates the input
    arguments for the function into each message's template.

    Example:

    ```python
    @openai_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")
    ```

    Args:
        model: The OpenAI model to use for the API call.

    Returns:
        The decorator for turning a typed function into an OpenAI API call.
    '''

    def decorator(fn: Callable[P, R]) -> Callable[P, OpenAICallResponse]:
        def call(*args: P.args, **kwargs: P.kwargs) -> OpenAICallResponse:
            prompt_template = inspect.getdoc(fn)
            assert prompt_template is not None, "The function must have a docstring."
            attrs = inspect.signature(fn).bind(*args, **kwargs).arguments
            messages = utils.parse_prompt_messages(
                roles=["system", "user", "assistant"],
                template=prompt_template,
                attrs=attrs,
            )
            client = OpenAI()  # NEED THIS FIXED
            start_time = datetime.datetime.now().timestamp() * 1000
            response = client.chat.completions.create(messages=messages, **kwargs)
            return OpenAICallResponse(
                response=response,
                user_message_param=messages[-1]
                if messages[-1]["role"] == "user"
                else None,
                start_time=start_time,
                end_time=datetime.datetime.now().timestamp() * 1000,
                cost=None,  # NEED THIS FIXED
                response_format=None,  # NEED THIS FIXED
            )

        return call

    return decorator
