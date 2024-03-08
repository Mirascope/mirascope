"""A class for better prompting."""

from __future__ import annotations

import pickle
import re
from string import Formatter
from textwrap import dedent
from typing import Any, Callable, ClassVar, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from .types import (
    AssistantMessage,
    BaseCallParams,
    Message,
    SystemMessage,
    ToolMessage,
    UserMessage,
)


def format_template(prompt: BasePrompt, template: str) -> str:
    """Formats the template with the prompt's attributes."""
    template_vars = [
        var for _, var, _, _ in Formatter().parse(template) if var is not None
    ]
    return template.format(**{var: getattr(prompt, var) for var in template_vars})


class BasePrompt(BaseModel):
    '''A Pydantic model for prompts.

    Example:

    ```python
    from mirascope import BasePrompt, BaseCallParams


    class BookRecommendationPrompt(BasePrompt):
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

    @classmethod
    def template(cls) -> str:
        """Custom parsing functionality for docstring prompt.

        This function is the first step in formatting the prompt template docstring.
        For the default `BasePrompt`, this function dedents the docstring and replaces
        all repeated sequences of newlines with one fewer newline character. This
        enables writing blocks of text instead of really long single lines. To include
        any number of newline characters, simply include one extra.

        Raises:
            ValueError: If the class docstring is empty.
        """
        if cls.__doc__ is None:
            raise ValueError("`BasePrompt` must have a prompt template docstring.")

        return re.sub(
            "(\n+)",
            lambda x: x.group(0)[:-1] if len(x.group(0)) > 1 else " ",
            dedent(cls.__doc__).strip("\n"),
        )

    def __str__(self) -> str:
        """Returns the docstring prompt template formatted with template variables."""
        return format_template(self, self.template())

    @property
    def messages(self) -> Union[list[Message], Any]:
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
    def load(cls, filepath: str) -> BasePrompt:
        """Loads the prompt from the given filepath."""
        with open(filepath, "rb") as f:
            return pickle.load(f)


BasePromptT = TypeVar("BasePromptT", bound=BasePrompt)


def tags(args: list[str]) -> Callable[[Type[BasePromptT]], Type[BasePromptT]]:
    '''A decorator for adding tags to a `BasePrompt`.

    Adding this decorator to a `BasePrompt` updates the `_tags` class attribute to the given
    value. This is useful for adding metadata to a `BasePrompt` that can be used for logging
    or filtering.

    Example:

    ```python
    from mirascope import BasePrompt, tags


    @tags(["book_recommendation", "entertainment"])
    class BookRecommendationPrompt(BasePrompt):
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

    def tags_fn(model_class: Type[BasePromptT]) -> Type[BasePromptT]:
        """Updates the `_tags` class attribute to the given value."""
        setattr(model_class, "tags", args)
        return model_class

    return tags_fn
