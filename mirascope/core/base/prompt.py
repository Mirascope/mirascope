"""The `BasePrompt` class for better prompt engineering."""

from textwrap import dedent
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    ClassVar,
    Iterable,
    ParamSpec,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ._utils import BaseType, format_template, parse_prompt_messages
from .call_response import BaseCallResponse
from .function_return import BaseFunctionReturn
from .message_param import BaseMessageParam
from .stream import BaseStream
from .stream_async import BaseAsyncStream

_P = ParamSpec("_P")
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

    tags: ClassVar[list[str]] = []
    prompt_template: ClassVar[str] = ""

    def __str__(self) -> str:
        """Returns the formatted template."""
        return format_template(self.prompt_template, self.model_dump())

    def message_params(self) -> list[BaseMessageParam]:
        """Returns the template as a formatted list of `Message` instances."""
        return parse_prompt_messages(
            roles=["system", "user", "assistant", "model"],
            template=self.prompt_template,
            attrs=self.model_dump(),
        )

    def dump(self) -> dict[str, Any]:
        """Dumps the contents of the prompt into a dictionary."""
        return {
            "tags": self.tags,
            "prompt": str(self),
            "template": dedent(self.prompt_template).strip("\n"),
            "inputs": self.model_dump(),
        }

    @overload
    def call(
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]], Callable[..., _BaseCallResponseT]
        ],
    ) -> _BaseCallResponseT:
        ...  # pragma: no cover

    @overload
    def call(
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]], Callable[..., _BaseStreamT]
        ],
    ) -> _BaseStreamT:
        ...  # pragma: no cover

    @overload
    def call(  # type: ignore
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]], Callable[..., _ResponseModelT]
        ],
    ) -> _ResponseModelT:
        ...  # pragma: no cover

    @overload
    def call(
        self,
        decorator: Callable[
            [Callable[..., BaseFunctionReturn]],
            Callable[..., Iterable[_ResponseModelT]],
        ],
    ) -> Iterable[_ResponseModelT]:
        ...  # pragma: no cover

    def call(
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
        ],
    ) -> (
        _BaseCallResponseT | _BaseStreamT | _ResponseModelT | Iterable[_ResponseModelT]
    ):
        """Returns the response of calling the API of the provided decorator."""

        @decorator
        def _call() -> BaseFunctionReturn:
            return {"messages": self.message_params()}

        return _call()

    @overload
    async def call_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_BaseCallResponseT]],
        ],
    ) -> _BaseCallResponseT:
        ...  # pragma: no cover

    @overload
    async def call_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_BaseAsyncStreamT]],
        ],
    ) -> _BaseAsyncStreamT:
        ...  # pragma: no cover

    @overload
    async def call_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[_ResponseModelT]],
        ],
    ) -> _ResponseModelT:
        ...  # pragma: no cover

    @overload
    async def call_async(
        self,
        decorator: Callable[
            [Callable[..., Awaitable[BaseFunctionReturn]]],
            Callable[..., Awaitable[AsyncIterable[_ResponseModelT]]],
        ],
    ) -> AsyncIterable[_ResponseModelT]:
        ...  # pragma: no cover

    async def call_async(
        self,
        decorator: Callable[
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
        | _BaseAsyncStreamT
        | _ResponseModelT
        | AsyncIterable[_ResponseModelT]
    ):
        """Returns the response of async calling the API of the provided decorator."""

        @decorator
        async def _call_async() -> BaseFunctionReturn:
            return {"messages": self.message_params()}

        return await _call_async()


BasePromptT = TypeVar("BasePromptT", bound=BasePrompt)


def tags(args: list[str]) -> Callable[[type[BasePromptT]], type[BasePromptT]]:
    """A decorator for adding tags to a `BasePrompt`.

    Adding this decorator to a `BasePrompt` updates the `tags` class attribute to the
    given value. This is useful for adding metadata to a `BasePrompt` that can be used
    for logging or filtering.

    Example:

    ```python
    from mirascope.core import BasePrompt, tags

    @tags(["version:0001", "books"])
    class BookRecommendationPrompt(BasePrompt):
        prompt_template = "Recommend a {genre} book."

        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")

    print(prompt.tags)
    #> ["version:0001", "books"]

    print(prompt.dump()["tags"])
    #> ["version:0001", "books"]
    ```

    Returns:
        The decorated class with `tags` class attribute set.
    """

    def wrapper(model_class: type[BasePromptT]) -> type[BasePromptT]:
        """Updates the `tags` class attribute to the given value."""
        setattr(model_class, "tags", args)
        return model_class

    return wrapper
