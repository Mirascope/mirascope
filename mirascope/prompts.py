"""A class for better prompting."""
from __future__ import annotations

import warnings
from typing import Any, ClassVar, Type, TypeVar

from .base.prompt import BasePrompt
from .base.types import (
    BaseCallParams,
)


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
