"""A class for better prompting."""

from __future__ import annotations

import pickle
import re
import warnings
from string import Formatter
from textwrap import dedent
from typing import Any, ClassVar, Optional, Type, TypeVar

from .base.prompt import BasePrompt
from .base.types import (
    AssistantMessage,
    BaseCallParams,
    Message,
    SystemMessage,
    ToolMessage,
    UserMessage,
)


def format_template(prompt: Prompt, template: str) -> str:
    """Formats the template with the prompt's attributes."""
    template_vars = [
        var for _, var, _, _ in Formatter().parse(template) if var is not None
    ]
    return template.format(**{var: getattr(prompt, var) for var in template_vars})


class Prompt(BasePrompt):
    '''(DEPRECATED): Use `BasePrompt` or specific prompt (e.g. `OpenAIPrompt`) instead.

    A Pydantic model for prompts.

    Example:

    ```python
    from mirascope import Prompt, BaseCallParams


    class BookRecommendationPrompt(Prompt):
        """
        I've recently read the following books: {titles_in_quotes}.
        What should I read next?
        """

        book_titles: list[str]

        call_params = BaseCallParams(model="gpt-3.5-turbo-0125")

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

    call_params: ClassVar[BaseCallParams] = BaseCallParams(model="gpt-3.5-turbo-0125")
    tags: ClassVar[list[str]] = []

    def __init__(self, **data: Any):
        """Initializes the prompt with the given data."""
        warnings.warn(
            "The `Prompt` class is deprecated. Instead use either `BasePrompt` or a "
            "specific prompt (e.g. `OpenAIPrompt`) instead; version>=0.3.0",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(**data)

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
        return format_template(self, self.template())

    @property
    def messages(self) -> list[Message]:
        """Returns the docstring as a list of messages."""
        message_param_map = {
            "system": SystemMessage,
            "user": UserMessage,
            "assistant": AssistantMessage,
            "tool": ToolMessage,
        }
        messages = []
        for match in re.finditer(
            r"(SYSTEM|USER|ASSISTANT|TOOL): "
            r"((.|\n)+?)(?=\n(SYSTEM|USER|ASSISTANT|TOOL):|\Z)",
            self.template(),
        ):
            role = match.group(1).lower()
            content = format_template(self, match.group(2))
            messages.append(message_param_map[role](role=role, content=content))
        if len(messages) == 0:
            messages.append(UserMessage(role="user", content=str(self)))
        return messages

    def dump(self, completion: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Dumps the prompt template to a dictionary."""
        prompt_dict: dict[str, Any] = {
            "template": self.template(),
            "inputs": self.model_dump(),
            "tags": self.tags,
            "call_params": {
                key: value
                for key, value in self.call_params.model_dump().items()
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
    warnings.warn(
        "The `messages` decorator is deprecated and no longer necessary. You can write "
        "a `messages` style docstring without the decorator; version>=0.3.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return cls
