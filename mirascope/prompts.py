"""A class for better prompting."""

from __future__ import annotations

import pickle
import re
from string import Formatter
from textwrap import dedent
from typing import Type, TypeVar

from pydantic import BaseModel


class Prompt(BaseModel):
    """A Pydantic model for prompts."""

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
        template = self.template()
        template_vars = [
            var for _, var, _, _ in Formatter().parse(template) if var is not None
        ]
        return template.format(**{var: getattr(self, var) for var in template_vars})

    @property
    def messages(self) -> list[tuple[str, str]]:
        """Returns the docstring as a list of messages."""
        return [("user", str(self))]

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
    """A decorator for updating the `messages` class attribute of a `Prompt`.

    Adding this decorator to a `Prompt` updates the `messages` class attribute
    to parse the docstring as a list of messages. Each message is a tuple containing
    the role and the content. The docstring should have the following format:

        <role>:
        <content>

    For example, you might want to first include a system prompt followed by a user
    prompt, which you can structure as follows:

        SYSTEM:
        This would be the system message content.

        USER:
        This would be the user message content.

    This decorator currently supports the SYSTEM, USER, and ASSISTANT roles.

    Returns:
        The decorated class.

    Raises:
        ValueError: If the docstring is empty.
    """

    def messages_fn(self) -> list[tuple[str, str]]:
        """Returns the docstring as a list of messages."""
        if self.__doc__ is None:
            raise ValueError("`Prompt` must have a prompt template docstring.")

        return [
            (match.group(1).lower(), match.group(2))
            for match in re.finditer(
                r"(SYSTEM|USER|ASSISTANT|TOOL): "
                r"((.|\n)+?)(?=\n(SYSTEM|USER|ASSISTANT|TOOL):|\Z)",
                str(self),
            )
        ]

    setattr(cls, "messages", property(messages_fn))
    return cls
