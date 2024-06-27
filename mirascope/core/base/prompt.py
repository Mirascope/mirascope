"""The `BasePrompt` class for better prompt engineering."""

import inspect
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    ParamSpec,
    TypeVar,
    Unpack,
    overload,
)

from pydantic import BaseModel

from ._utils import BaseType, format_template
from .call_response import BaseCallResponse
from .function_return import BaseFunctionReturn
from .stream import BaseStream
from .stream_async import BaseAsyncStream

_P = ParamSpec("_P")
_R = TypeVar("_R")
_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseAsyncStreamT = TypeVar("_BaseAsyncStreamT", bound=BaseAsyncStream)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BasePrompt(BaseModel):
    """The base class for engineering prompts.

    This class is implemented as the base for all prompting needs. It is intended to
    work across various providers by providing a common prompt interface.

    Example:

    ```python
    from mirascope.core import BasePrompt, tags

    @tags(["version:0001"])
    class BookRecommendationPrompt(BasePrompt):
        prompt_template = "Recommend a {genre} book."

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")

    prompt.messages()
    #> [{"role": "user", "content": "Please recommend a fantasy book."}]

    print(prompt)
    #> Please recommend a fantasy book.
    ```
    """

    @classmethod
    def _prompt_template(cls) -> str:
        """Returns the prompt template."""
        return cls.__annotations__.get("prompt_template", cls.__doc__)

    @classmethod
    def _tags(cls) -> list[str]:
        """Returns the prompt tags."""
        return cls.__annotations__.get("tags", [])

    def __str__(self) -> str:
        """Returns the formatted template."""
        return format_template(self._prompt_template(), self.model_dump())

    def dump(self) -> dict[str, Any]:
        """Dumps the contents of the prompt into a dictionary."""
        return {
            "tags": self._tags(),
            "prompt": str(self),
            "template": inspect.cleandoc(self._prompt_template()),
            "inputs": self.model_dump(),
        }

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]], Callable[..., _BaseCallResponseT]
        ],
    ) -> _BaseCallResponseT: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]], Callable[..., _BaseStreamT]
        ],
    ) -> _BaseStreamT: ...  # pragma: no cover

    @overload
    def run(  # type: ignore
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]], Callable[..., _ResponseModelT]
        ],
    ) -> _ResponseModelT: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]],
            Callable[..., Iterable[_ResponseModelT]],
        ],
    ) -> Iterable[_ResponseModelT]: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_BaseCallResponseT]],
        ],
    ) -> Awaitable[_BaseCallResponseT]: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_BaseAsyncStreamT]],
        ],
    ) -> Awaitable[_BaseAsyncStreamT]: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_ResponseModelT]],
        ],
    ) -> Awaitable[_ResponseModelT]: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[AsyncIterable[_ResponseModelT]]],
        ],
    ) -> Awaitable[AsyncIterable[_ResponseModelT]]: ...  # pragma: no cover

    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]],
            Callable[..., _BaseCallResponseT],
        ]
        | Callable[
            [Callable[..., BaseFunctionReturn]],
            Callable[..., _BaseStreamT],
        ]
        | Callable[
            [Callable[..., BaseFunctionReturn]],
            Callable[..., _ResponseModelT],
        ]
        | Callable[
            [Callable[..., BaseFunctionReturn]],
            Callable[..., Iterable[_ResponseModelT]],
        ]
        | Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_BaseCallResponseT]],
        ]
        | Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_BaseAsyncStreamT]],
        ]
        | Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_ResponseModelT]],
        ]
        | Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[AsyncIterable[_ResponseModelT]]],
        ],
    ) -> (
        _BaseCallResponseT
        | _BaseStreamT
        | _ResponseModelT
        | Iterable[_ResponseModelT]
        | Awaitable[_BaseCallResponseT]
        | Awaitable[_BaseAsyncStreamT]
        | Awaitable[_ResponseModelT]
        | Awaitable[AsyncIterable[_ResponseModelT]]
    ):
        """Returns the response of calling the API of the provided decorator."""
        kwargs = self.model_dump()
        args_str = ", ".join(f"{k}: {type(v).__name__}" for k, v in kwargs.items())
        fn_def = (
            f"async def fn({args_str}): ..."
            if "async" in decorator.func.__name__
            else f"def fn({args_str}): ..."
        )
        namespace = {}
        exec(fn_def, namespace)
        fn = namespace["fn"]
        return decorator(prompt_template(self._prompt_template())(fn))(**kwargs)


_BasePromptT = TypeVar("_BasePromptT", bound=BasePrompt)


def prompt_template(template: str):
    """A decorator for setting the `prompt_template` of a `BasePrompt` or `call`."""

    @overload
    def inner(prompt: type[_BasePromptT]) -> type[_BasePromptT]: ...  # pragma: no cover

    @overload
    def inner(prompt: Callable[_P, _R]) -> Callable[_P, _R]: ...  # pragma: no cover

    def inner(
        prompt: type[_BasePromptT] | Callable[_P, _R],
    ) -> type[_BasePromptT] | Callable[_P, _R]:
        prompt.__annotations__["prompt_template"] = template
        return prompt

    return inner


def tags(tags: list[str]):
    """A decorator for adding tags to a `BasePrompt` or `call`.

    Adding this decorator to a `BasePrompt` or `call` updates the `tags` annotation to
    the given value. This is useful for adding metadata to a `BasePrompt` or `call` that
    can be used for logging or filtering.

    Example:

    ```python
    from mirascope.core import BasePrompt, tags

    @tags(["version:0001", "books"])
    class BookRecommendationPrompt(BasePrompt):
        prompt_template = "Recommend a {genre} book."

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")

    print(prompt.dump()["tags"])
    #> ["version:0001", "books"]
    ```

    Returns:
        The decorator function that updates the `tags` attribute of the decorated input.
    """

    @overload
    def inner(prompt: type[_BasePromptT]) -> type[_BasePromptT]: ...  # pragma: no cover

    @overload
    def inner(prompt: Callable[_P, _R]) -> Callable[_P, _R]: ...  # pragma: no cover

    def inner(
        prompt: type[_BasePromptT] | Callable[_P, _R],
    ) -> type[_BasePromptT] | Callable[_P, _R]:
        """Updates the `tags` class attribute to the given value."""
        prompt.__annotations__["tags"] = tags
        return prompt

    return inner
