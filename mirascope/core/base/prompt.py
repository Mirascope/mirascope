"""The `BasePrompt` class for better prompt engineering."""

from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    ParamSpec,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ._stream import BaseStream
from ._utils import BaseType, format_template, get_metadata, get_prompt_template
from .call_response import BaseCallResponse
from .dynamic_config import BaseDynamicConfig
from .metadata import Metadata

_P = ParamSpec("_P")
_R = TypeVar("_R")
_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BasePrompt(BaseModel):
    """The base class for engineering prompts.

    This class is implemented as the base for all prompting needs. It is intended to
    work across various providers by providing a common prompt interface.

    Example:

    ```python
    from mirascope.core import BasePrompt, metadata

    @metadata({"tags": {"version:0001"}})
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

    def __str__(self) -> str:
        """Returns the formatted template."""
        return format_template(get_prompt_template(self), self.model_dump())

    def dump(self) -> dict[str, Any]:
        """Dumps the contents of the prompt into a dictionary."""
        return {
            "metadata": get_metadata(self, None),
            "prompt": str(self),
            "template": get_prompt_template(self),
            "inputs": self.model_dump(),
        }

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _BaseCallResponseT]
        ],
    ) -> _BaseCallResponseT: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _BaseStreamT]
        ],
    ) -> _BaseStreamT: ...  # pragma: no cover

    @overload
    def run(  # type: ignore
        self,
        decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _ResponseModelT]
        ],
    ) -> _ResponseModelT: ...  # pragma: no cover

    @overload
    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseDynamicConfig]],
            Callable[..., Iterable[_ResponseModelT]],
        ],
    ) -> Iterable[_ResponseModelT]: ...  # pragma: no cover

    def run(
        self,
        decorator: Callable[
            [Callable[..., BaseDynamicConfig]],
            Callable[..., _BaseCallResponseT],
        ]
        | Callable[
            [Callable[..., BaseDynamicConfig]],
            Callable[..., _BaseStreamT],
        ]
        | Callable[
            [Callable[..., BaseDynamicConfig]],
            Callable[..., _ResponseModelT],
        ]
        | Callable[
            [Callable[..., BaseDynamicConfig]],
            Callable[..., Iterable[_ResponseModelT]],
        ],
    ) -> (
        _BaseCallResponseT | _BaseStreamT | _ResponseModelT | Iterable[_ResponseModelT]
    ):
        """Returns the response of calling the API of the provided decorator."""
        kwargs = self.model_dump()
        args_str = ", ".join(kwargs.keys())
        namespace = {}
        exec(f"def fn({args_str}): ...", namespace)
        fn = namespace["fn"]
        return decorator(prompt_template(get_prompt_template(self))(fn))(**kwargs)

    @overload
    def run_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_BaseCallResponseT]],
        ],
    ) -> Awaitable[_BaseCallResponseT]: ...  # pragma: no cover

    @overload
    def run_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_BaseStreamT]],
        ],
    ) -> Awaitable[_BaseStreamT]: ...  # pragma: no cover

    @overload
    def run_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_ResponseModelT]],
        ],
    ) -> Awaitable[_ResponseModelT]: ...  # pragma: no cover

    @overload
    def run_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[AsyncIterable[_ResponseModelT]]],
        ],
    ) -> Awaitable[AsyncIterable[_ResponseModelT]]: ...  # pragma: no cover

    def run_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_BaseCallResponseT]],
        ]
        | Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_BaseStreamT]],
        ]
        | Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_ResponseModelT]],
        ]
        | Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[AsyncIterable[_ResponseModelT]]],
        ],
    ) -> (
        Awaitable[_BaseCallResponseT]
        | Awaitable[_BaseStreamT]
        | Awaitable[_ResponseModelT]
        | Awaitable[AsyncIterable[_ResponseModelT]]
    ):
        kwargs = self.model_dump()
        args_str = ", ".join(kwargs.keys())
        namespace = {}
        exec(f"async def fn({args_str}): ...", namespace)
        fn = namespace["fn"]
        return decorator(prompt_template(get_prompt_template(self))(fn))(**kwargs)


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
        setattr(prompt, "_prompt_template", template)
        return prompt

    return inner


def metadata(metadata: Metadata):
    """A decorator for adding metadata to a `BasePrompt` or `call`.

    Adding this decorator to a `BasePrompt` or `call` updates the `metadata` annotation
    to the given value. This is useful for adding metadata to a `BasePrompt` or `call`
    that can be used for logging or filtering.

    Example:

    ```python
    from mirascope.core import BasePrompt, metadata

    @metadata({"tags": {"version:0001", "books"}})
    class BookRecommendationPrompt(BasePrompt):
        prompt_template = "Recommend a {genre} book."

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")

    print(prompt.dump()["metadata"])
    #> {"metadata": {"version:0001", "books"}}
    ```

    Returns:
        Decorator function that updates the `metadata` attribute of the decorated input.
    """

    @overload
    def inner(prompt: type[_BasePromptT]) -> type[_BasePromptT]: ...  # pragma: no cover

    @overload
    def inner(prompt: Callable[_P, _R]) -> Callable[_P, _R]: ...  # pragma: no cover

    def inner(
        prompt: type[_BasePromptT] | Callable[_P, _R],
    ) -> type[_BasePromptT] | Callable[_P, _R]:
        """Updates the `metadata` class attribute to the given value."""
        setattr(prompt, "_metadata", metadata)
        return prompt

    return inner
