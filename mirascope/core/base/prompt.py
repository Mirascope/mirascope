"""The `BasePrompt` class for better prompt engineering."""

from collections.abc import AsyncIterable, Awaitable, Callable, Iterable
from functools import reduce, wraps
from textwrap import dedent
from typing import (
    Any,
    ClassVar,
    ParamSpec,
    Protocol,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ._utils import (
    BaseType,
    MessagesDecorator,
    fn_is_async,
    format_template,
    get_fn_args,
    get_metadata,
    get_prompt_template,
    messages_decorator,
    parse_prompt_messages,
)
from .call_response import BaseCallResponse
from .dynamic_config import BaseDynamicConfig
from .message_param import BaseMessageParam
from .metadata import Metadata

_P = ParamSpec("_P")
_R = TypeVar("_R")
_T = TypeVar("_T", bound=Callable)
_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseStreamT = TypeVar("_BaseStreamT")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | BaseType)

SUPPORTED_MESSAGE_ROLES = ["system", "user", "assistant"]


class BasePrompt(BaseModel):
    """The base class for engineering prompts.

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

    prompt_template: ClassVar[str]

    def __str__(self) -> str:
        """Returns the formatted template."""
        prompt_template = get_prompt_template(self)
        prompt_template = (
            prompt_template.replace(":images}", "}")
            .replace(":image}", "}")
            .replace(":audios}", "}")
            .replace(":audio}", "}")
            .replace(":documents}", "}")
            .replace(":document}", "}")
            .replace(":texts}", "}")
            .replace(":text", "")
        )
        return format_template(prompt_template, self.model_dump())

    def message_params(self) -> list[BaseMessageParam]:
        """Returns the list of parsed message parameters."""
        return parse_prompt_messages(
            roles=SUPPORTED_MESSAGE_ROLES,
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
    ) -> _BaseCallResponseT: ...

    @overload
    def run(
        self,
        call_decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _BaseStreamT]
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> _BaseStreamT: ...

    @overload
    def run(
        self,
        call_decorator: Callable[
            [Callable[..., BaseDynamicConfig]], Callable[..., _ResponseModelT]
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> _ResponseModelT: ...

    @overload
    def run(
        self,
        call_decorator: Callable[
            [Callable[..., BaseDynamicConfig]],
            Callable[..., Iterable[_ResponseModelT]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Iterable[_ResponseModelT]: ...

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
        kwargs = {field: getattr(self, field) for field in self.model_fields}
        args_str = ", ".join(kwargs.keys())
        namespace, fn_name = {}, self.__class__.__name__
        exec(f"def {fn_name}({args_str}): ...", namespace)
        return reduce(
            lambda res, f: f(res),  # pyright: ignore [reportArgumentType, reportCallIssue]
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
    ) -> Awaitable[_BaseCallResponseT]: ...

    @overload
    def run_async(
        self,
        call_decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_BaseStreamT]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Awaitable[_BaseStreamT]: ...

    @overload
    def run_async(
        self,
        call_decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[_ResponseModelT]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Awaitable[_ResponseModelT]: ...

    @overload
    def run_async(
        self,
        call_decorator: Callable[
            [Callable[..., Awaitable[BaseDynamicConfig]]],
            Callable[..., Awaitable[AsyncIterable[_ResponseModelT]]],
        ],
        *additional_decorators: Callable[[_T], _T],
    ) -> Awaitable[AsyncIterable[_ResponseModelT]]: ...

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
        kwargs = {field: getattr(self, field) for field in self.model_fields}
        args_str = ", ".join(kwargs.keys())
        namespace, fn_name = {}, self.__class__.__name__
        exec(f"async def {fn_name}({args_str}): ...", namespace)
        return reduce(
            lambda res, f: f(res),  # pyright: ignore [reportArgumentType, reportCallIssue]
            [
                metadata(get_metadata(self, self.dynamic_config())),
                prompt_template(get_prompt_template(self)),
                call_decorator,
                *additional_decorators,
            ],
            namespace[fn_name],
        )(**kwargs)


_BasePromptT = TypeVar("_BasePromptT", bound=BasePrompt)


class PromptDecorator(Protocol):
    @overload
    def __call__(
        self, prompt: Callable[_P, BaseDynamicConfig]
    ) -> Callable[_P, list[BaseMessageParam]]: ...

    @overload
    def __call__(
        self, prompt: Callable[_P, Awaitable[BaseDynamicConfig]]
    ) -> Callable[_P, Awaitable[list[BaseMessageParam]]]: ...

    @overload
    def __call__(self, prompt: type[_BasePromptT]) -> type[_BasePromptT]: ...

    def __call__(
        self,
        prompt: type[_BasePromptT]
        | Callable[_P, BaseDynamicConfig]
        | Callable[_P, Awaitable[BaseDynamicConfig]],
    ) -> (
        Callable[_P, list[BaseMessageParam]]
        | Callable[_P, Awaitable[list[BaseMessageParam]]]
        | type[_BasePromptT]
    ): ...


@overload
def prompt_template(template: str) -> PromptDecorator: ...


@overload
def prompt_template(template: None = None) -> MessagesDecorator: ...


def prompt_template(
    template: str | None = None,
) -> PromptDecorator | MessagesDecorator:
    """A decorator for setting the `prompt_template` of a `BasePrompt` or `call`.

    usage docs: learn/prompts.md#prompt-templates-messages

    Example:

    ```python
    from mirascope.core import openai, prompt_template


    @prompt_template()
    def recommend_book(genre: str) -> str:
        return f"Recommend a {genre} book"


    print(recommend_book("fantasy"))
    # Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
    ```

    Returns:
        decorator (Callable): The decorator function that turns the decorated function
            into a prompt template.
    """

    if template is None:
        # For @prompt_template() case
        decorator = messages_decorator()
        decorator.__mirascope_prompt_template__ = True  # pyright: ignore [reportAttributeAccessIssue]
        return decorator
    template = dedent(template).strip()

    @overload
    def inner(
        prompt: Callable[_P, BaseDynamicConfig],
    ) -> Callable[_P, list[BaseMessageParam]]: ...

    @overload
    def inner(
        prompt: Callable[_P, Awaitable[BaseDynamicConfig]],
    ) -> Callable[_P, Awaitable[list[BaseMessageParam]]]: ...

    @overload
    def inner(prompt: type[_BasePromptT]) -> type[_BasePromptT]: ...

    def inner(
        prompt: type[_BasePromptT]
        | Callable[_P, BaseDynamicConfig]
        | Callable[_P, Awaitable[BaseDynamicConfig]],
    ) -> (
        Callable[_P, list[BaseMessageParam]]
        | Callable[_P, Awaitable[list[BaseMessageParam]]]
        | type[_BasePromptT]
    ):
        """Updates the `prompt_template` class attribute to the given value."""
        prompt._prompt_template = template  # pyright: ignore [reportAttributeAccessIssue,reportFunctionMemberAccess]

        if isinstance(prompt, type):
            return prompt

        if fn_is_async(prompt):

            @wraps(prompt)
            async def get_base_message_params_async(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> list[BaseMessageParam]:
                return parse_prompt_messages(
                    roles=SUPPORTED_MESSAGE_ROLES,
                    template=template,
                    attrs=get_fn_args(prompt, args, kwargs),
                    dynamic_config=await prompt(*args, **kwargs),
                )

            get_base_message_params_async._original_fn = prompt  # pyright: ignore [reportAttributeAccessIssue,reportFunctionMemberAccess]
            return get_base_message_params_async

        else:

            @wraps(prompt)
            def get_base_message_params(
                *args: _P.args, **kwargs: _P.kwargs
            ) -> list[BaseMessageParam]:
                return parse_prompt_messages(
                    roles=SUPPORTED_MESSAGE_ROLES,
                    template=template,
                    attrs=get_fn_args(prompt, args, kwargs),
                    dynamic_config=prompt(*args, **kwargs),
                )

            get_base_message_params._original_fn = prompt  # pyright: ignore [reportAttributeAccessIssue,reportFunctionMemberAccess]
            return get_base_message_params

    inner.__mirascope_prompt_template__ = True  # pyright: ignore [reportFunctionMemberAccess]
    return inner


class MetadataDecorator(Protocol):
    @overload
    def __call__(self, prompt: type[_BasePromptT]) -> type[_BasePromptT]: ...

    @overload
    def __call__(self, prompt: Callable[_P, _R]) -> Callable[_P, _R]: ...

    def __call__(
        self,
        prompt: type[_BasePromptT] | Callable[_P, _R],
    ) -> type[_BasePromptT] | Callable[_P, _R]: ...


def metadata(metadata: Metadata) -> MetadataDecorator:
    """A decorator for adding metadata to a `BasePrompt` or `call`.

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
    def inner(prompt: type[_BasePromptT]) -> type[_BasePromptT]: ...

    @overload
    def inner(prompt: Callable[_P, _R]) -> Callable[_P, _R]: ...

    def inner(
        prompt: type[_BasePromptT] | Callable[_P, _R],
    ) -> type[_BasePromptT] | Callable[_P, _R]:
        """Updates the `metadata` class attribute to the given value."""
        prompt._metadata = metadata  # pyright: ignore [reportAttributeAccessIssue,reportFunctionMemberAccess]
        return prompt

    return inner
