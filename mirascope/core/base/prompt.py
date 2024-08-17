"""The `BasePrompt` class for better prompt engineering."""

from functools import reduce
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

from ._utils import (
    BaseType,
    format_template,
    get_metadata,
    get_prompt_template,
    parse_prompt_messages,
)
from .call_response import BaseCallResponse
from .dynamic_config import BaseDynamicConfig
from .message_param import BaseMessageParam
from .metadata import Metadata
from .stream import BaseStream

_P = ParamSpec("_P")
_R = TypeVar("_R")
_T = TypeVar("_T", bound=Callable)
_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)


class BasePrompt(BaseModel):
    """The base class for engineering prompts.

    usage docs: learn/prompts.md#the-baseprompt-class

    This class is implemented as the base for all prompting needs. It is intended to
    work across various providers by providing a common prompt interface.

    Example:

    ```python
    from mirascope.core import BasePrompt, metadata, prompt_template

    @prompt_template("Recommend a {genre} book")
    @metadata({"tags": {"version:0001", "books"}})
    class BookRecommendationPrompt(BasePrompt):
        genre: str

    prompt = BookRecommendationPrompt(genre="fantasy")

    print(prompt)
    # > Recommend a fantasy book

    print(prompt.message_params())
    # > [BaseMessageParam(role="user", content="Recommend a fantasy book")]

    print(prompt.dump()["metadata"])
    # > {"metadata": {"version:0001", "books"}}
    ```
    """

    def __str__(self) -> str:
        """Returns the formatted template."""
        prompt_template = get_prompt_template(self)
        prompt_template = (
            prompt_template.replace(":images}", "}")
            .replace(":image}", "}")
            .replace(":audios", "}")
            .replace(":audio}", "}")
        )
        return format_template(prompt_template, self.model_dump())

    def message_params(self) -> list[BaseMessageParam]:
        """Returns the list of parsed message parameters."""
        return parse_prompt_messages(
            roles=["system", "user", "assistant"],
            template=get_prompt_template(self),
            attrs={field: getattr(self, field) for field in self.model_fields},
        )

    def dynamic_config(self) -> BaseDynamicConfig:
        """Returns the dynamic config of the prompt."""
        return None

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
        call_decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _BaseCallResponseT]
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> _BaseCallResponseT: ...  # pragma: no cover

    @overload
    def run(
        self,
        call_decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _BaseStreamT]
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> _BaseStreamT: ...  # pragma: no cover

    @overload
    def run(  # type: ignore
        self,
        call_decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _ResponseModelT]
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> _ResponseModelT: ...  # pragma: no cover

    @overload
    def run(
        self,
        call_decorator: Callable[
            [Callable[..., BaseDynamicConfig]],
            Callable[..., Iterable[_ResponseModelT]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Iterable[_ResponseModelT]: ...  # pragma: no cover

    def run(
        self,
        call_decorator: Callable[
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
        *additional_decorators: Callable[[_T], _T],
    ) -> (
        _BaseCallResponseT | _BaseStreamT | _ResponseModelT | Iterable[_ResponseModelT]
    ):
        """Returns the response of calling the API of the provided decorator.

        usage docs: learn/prompts.md#running-prompts

        Example:

        ```python
        from mirascope.core import BasePrompt, openai, prompt_template


        @prompt_template("Recommend a {genre} book")
        class BookRecommendationPrompt(BasePrompt):
            genre: str


        prompt = BookRecommendationPrompt(genre="fantasy")
        response = prompt.run(openai.call("gpt-4o-mini"))
        print(response.content)
        ```
        """
        kwargs = self.model_dump()
        args_str = ", ".join(kwargs.keys())
        namespace, fn_name = {}, self.__class__.__name__
        exec(f"def {fn_name}({args_str}): ...", namespace)
        return reduce(
            lambda res, f: f(res),  # type: ignore
            [
                metadata(get_metadata(self, self.dynamic_config())),
                prompt_template(get_prompt_template(self)),
                call_decorator,
                *additional_decorators,
            ],
            namespace[fn_name],
        )(**kwargs)

    @overload
    def run_async(
        self,
        call_decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_BaseCallResponseT]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Awaitable[_BaseCallResponseT]: ...  # pragma: no cover

    @overload
    def run_async(
        self,
        call_decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_BaseStreamT]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Awaitable[_BaseStreamT]: ...  # pragma: no cover

    @overload
    def run_async(
        self,
        call_decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_ResponseModelT]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Awaitable[_ResponseModelT]: ...  # pragma: no cover

    @overload
    def run_async(
        self,
        call_decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[AsyncIterable[_ResponseModelT]]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Awaitable[AsyncIterable[_ResponseModelT]]: ...  # pragma: no cover

    def run_async(
        self,
        call_decorator: Callable[
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
        *additional_decorators: Callable[[_T], _T],
    ) -> (
        Awaitable[_BaseCallResponseT]
        | Awaitable[_BaseStreamT]
        | Awaitable[_ResponseModelT]
        | Awaitable[AsyncIterable[_ResponseModelT]]
    ):
        """Returns the response of calling the API of the provided decorator.

        usage docs: learn/prompts.md#running-prompts

        Example:

        ```python
        import asyncio

        from mirascope.core import BasePrompt, openai, prompt_template


        @prompt_template("Recommend a {genre} book")
        class BookRecommendationPrompt(BasePrompt):
            genre: str


        async def run():
            prompt = BookRecommendationPrompt(genre="fantasy")
            response = await prompt.run_async(openai.call("gpt-4o-mini"))
            print(response.content)


        asyncio.run(run())
        ```
        """
        kwargs = self.model_dump()
        args_str = ", ".join(kwargs.keys())
        namespace, fn_name = {}, self.__class__.__name__
        exec(f"async def {fn_name}({args_str}): ...", namespace)
        return reduce(
            lambda res, f: f(res),  # type: ignore
            [
                metadata(get_metadata(self, self.dynamic_config())),
                prompt_template(get_prompt_template(self)),
                call_decorator,
                *additional_decorators,
            ],
            namespace[fn_name],
        )(**kwargs)


_BasePromptT = TypeVar("_BasePromptT", bound=BasePrompt)


def prompt_template(template: str):
    """A decorator for setting the `prompt_template` of a `BasePrompt` or `call`.

    usage docs: learn/prompts.md#prompt-templates

    Example:

    ```python
    from mirascope.core import openai, prompt_template


    @openai.call("gpt-4o-mini")
    @prompt_template("Recommend a {genre} book")
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")
    print(response.prompt_template)
    print(response.fn_args)
    ```

    Returns:
        decorator (Callable): The decorator function that updates the `_prompt_template`
            attribute of the decorated input prompt or call.
    """

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

    usage docs: learn/prompts.md#metadata

    Adding this decorator to a `BasePrompt` or `call` updates the `metadata` annotation
    to the given value. This is useful for adding metadata to a `BasePrompt` or `call`
    that can be used for logging or filtering.

    Example:

    ```python
    from mirascope.core import metadata, openai, prompt_template


    @openai.call("gpt-4o-mini")
    @prompt_template("Recommend a {genre} book")
    @metadata({"tags": {"version:0001", "books"}})
    def recommend_book(genre: str):
        ...


    response = recommend_book("fantasy")
    print(response.metadata)
    ```

    Returns:
        decorator (Callable): The decorator function that updates the `_metadata`
            attribute of the decorated input prompt or call.
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
