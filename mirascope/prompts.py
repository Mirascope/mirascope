"""A class for better prompting."""

from __future__ import annotations

import pickle
import re
from string import Formatter
from textwrap import dedent
from typing import Any, Callable, Optional, Type, TypeVar, Union

from httpx import Timeout
from openai._types import Body, Headers, Query
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.completion_create_params import ResponseFormat
from pydantic import BaseModel, ConfigDict

from .chat.tools import OpenAITool


def _format_template(prompt: Prompt, template: str) -> str:
    """Formats the template with the prompt's attributes."""
    template_vars = [
        var for _, var, _, _ in Formatter().parse(template) if var is not None
    ]
    return template.format(**{var: getattr(prompt, var) for var in template_vars})


class OpenAICallParams(BaseModel):
    """The parameters to use when calling the OpenAI Chat API with a prompt."""

    model: str
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_tokens: Optional[int] = None
    n: Optional[int] = None
    presence_penalty: Optional[float] = None
    response_format: Optional[ResponseFormat] = None
    seed: Optional[int] = None
    stop: Union[Optional[str], list[str]] = None
    temperature: Optional[float] = None
    tool_choice: Optional[ChatCompletionToolChoiceOptionParam] = None
    tools: Optional[list[Union[Callable, Type[OpenAITool]]]] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: Optional[str] = None
    # Values defined below take precedence over values defined elsewhere. Use these
    # params to pass additional parameters to the API if necessary that aren't already
    # available as params.
    extra_headers: Optional[Headers] = None
    extra_query: Optional[Query] = None
    extra_body: Optional[Body] = None
    timeout: Optional[Union[float, Timeout]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Prompt(BaseModel):
    '''A Pydantic model for prompts.

    Example:

    ```python
    from mirascope import Prompt


    class BookRecommendationPrompt(Prompt):
        """
        I've recently read the following books: {titles_in_quotes}.
        What should I read next?
        """

        book_titles: list[str]

        @property
        def titles_in_quotes(self) -> str:
            """Returns a comma separated list of book titles each in quotes."""
            return ", ".join([f'"{title}"' for title in self.book_titles])


    prompt = BookRecommendationPrompt(
        book_titles=["The Name of the Wind", "The Lord of the Rings"]
    )

    print(BookRecommendationPrompt.template())
    #> I've recently read the following books: {titles_in_quotes}. What should I read
    #  next?

    print(str(prompt))
    #> I've recently read the following books: "The Name of the Wind", "The Lord of the
    #  Rings". What should I read next?

    print(prompt.messages)
    #> [{
    #     'role': 'user',
    #     'content': 'I\'ve recently read the following books: "The Name of the Wind",
    #                "The Lord of the Rings". What should I read next?',
    #  }]
    ```
    '''

    _call_params: OpenAICallParams = OpenAICallParams(model="gpt-3.5-turbo-16k")
    _tags: list[str] = []

    @classmethod
    def call_params(cls) -> OpenAICallParams:
        """Returns the default value set for `call_params`."""
        return cls._call_params.default  # type: ignore

    @classmethod
    def tags(cls) -> list[str]:
        """Returns the default value set for `_tags`."""
        if isinstance(cls._tags, list):
            return cls._tags
        else:
            return cls._tags.default

    @classmethod
    def template(cls) -> str:
        """Custom parsing functionality for docstring prompt.

        This function is the first step in formatting the prompt template docstring.
        For the default `Prompt`, this function dedents the docstring and replaces all
        repeated sequences of newlines with one fewer newline character. This enables
        writing blocks of text instead of really long single lines. To include any
        number of newline characters, simply include one extra.

        Raises:
            ValueError: If the class docstring is empty.
        """
        if cls.__doc__ is None:
            raise ValueError("`Prompt` must have a prompt template docstring.")

        return re.sub(
            "(\n+)",
            lambda x: x.group(0)[:-1] if len(x.group(0)) > 1 else " ",
            dedent(cls.__doc__).strip("\n"),
        )

    def __str__(self) -> str:
        """Returns the docstring prompt template formatted with template variables."""
        return _format_template(self, self.template())

    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        """Returns the docstring as a list of messages."""
        return [ChatCompletionUserMessageParam(role="user", content=str(self))]

    def dump(self, completion: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Dumps the prompt template to a dictionary."""
        prompt_dict: dict[str, Any] = {
            "template": self.template(),
            "inputs": self.model_dump(),
            "tags": self._tags,
            "call_params": {
                key: value
                for key, value in self.call_params().model_dump().items()
                if value is not None
            },
        }
        if completion is not None:
            return prompt_dict | completion
        return prompt_dict

    def save(self, filepath: str):
        """Saves the prompt to the given filepath."""
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str) -> Prompt:
        """Loads the prompt from the given filepath."""
        with open(filepath, "rb") as f:
            return pickle.load(f)


T = TypeVar("T", bound=Prompt)


def messages(cls: Type[T]) -> Type[T]:
    '''A decorator for updating the `messages` class attribute of a `Prompt`.

    Adding this decorator to a `Prompt` updates the `messages` class attribute
    to parse the docstring as a list of messages. Each message is a tuple containing
    the role and the content. The docstring should have the following format:

        <role>:
        <content>

    Example:

    ```python
    from mirascope import Prompt, messages


    @messages
    class BookRecommendationPrompt(Prompt):
        """
        SYSTEM:
        You are the world's greatest librarian.

        USER:
        I recently read {book_title}. What should I read next?
        """

        book_title: [str]


    prompt = BookRecommendationPrompt(book_title="The Name of the Wind")

    print(prompt.messages)
    #> [
    #    {
    #      'role': 'system',
    #      'content': "You are the world's greatest librarian."
    #    },
    #    {
    #      'role': 'user',
    #      'content': "I recently read The Name of the  Wind. What should I read next?'
    #    },
    #  ]
    ```

    This decorator currently supports the SYSTEM, USER, ASSISTANT, and TOOL roles.

    Returns:
        The decorated class.

    Raises:
        ValueError: If the docstring is empty.
    '''

    def messages_fn(self: Prompt) -> list[ChatCompletionMessageParam]:
        """Returns the docstring as a list of messages."""
        message_param_map = {
            "system": ChatCompletionSystemMessageParam,
            "user": ChatCompletionUserMessageParam,
            "assistant": ChatCompletionAssistantMessageParam,
            "tool": ChatCompletionToolMessageParam,
        }
        messages = []
        for match in re.finditer(
            r"(SYSTEM|USER|ASSISTANT|TOOL): "
            r"((.|\n)+?)(?=\n(SYSTEM|USER|ASSISTANT|TOOL):|\Z)",
            self.template(),
        ):
            role = match.group(1).lower()
            content = _format_template(self, match.group(2))
            messages.append(message_param_map[role](role=role, content=content))
        return messages

    setattr(cls, "messages", property(messages_fn))
    return cls


def tags(args: list[str]) -> Callable[[Type[T]], Type[T]]:
    '''A decorator for adding tags to a `Prompt`.

    Adding this decorator to a `Prompt` updates the `_tags` class attribute to the given
    value. This is useful for adding metadata to a `Prompt` that can be used for logging
    or filtering.

    Example:

    ```python
    from mirascope import Prompt, tags


    @tags(["book_recommendation", "entertainment"])
    class BookRecommendationPrompt(Prompt):
        """
        SYSTEM:
        You are the world's greatest librarian.

        USER:
        I've recently read this book: {book_title}.
        What should I read next?
        """

        book_title: [str]

    print(BookRecommendationPrompt.dump()["tags"])
    #> ['book_recommendation', 'entertainment']
    ```

    Returns:
        The decorated class with `_tags` class attribute set.
    '''

    def tags_fn(model_class: Type[T]) -> Type[T]:
        """Updates the `_tags` class attribute to the given value."""
        setattr(model_class, "_tags", args)
        return model_class

    return tags_fn
