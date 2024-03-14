"""A base class for writing prompts."""
import re
from string import Formatter
from textwrap import dedent
from typing import Any, Callable, ClassVar, Type, TypeVar, Union

from pydantic import BaseModel

from .types import (
    AssistantMessage,
    Message,
    ModelMessage,
    SystemMessage,
    ToolMessage,
    UserMessage,
)


class BasePrompt(BaseModel):
    '''The base class for working with prompts.

    This class is implemented as the base for all prompting needs across various model
    providers.

    Example:

    ```python
    from mirascope import BasePrompt


    class BookRecommendationPrompt(BasePrompt):
        """A prompt for recommending a book."""

        template = """\\
            SYSTEM: You are the world's greatest librarian.
            USER: Please recommend a {genre} book.
        """

        genre: str


    prompt = BookRecommendationPrompt(genre="fantasy")
    print(prompt.messages)
    #> [{"role": "user", "content": "Please recommend a fantasy book."}]

    print(prompt)
    #> Please recommend a fantasy book.
    ```
    '''

    tags: ClassVar[list[str]] = []
    template: ClassVar[str] = ""

    def __str__(self) -> str:
        """Returns the formatted template."""
        return self._format_template(self.template)

    def messages(self) -> Union[list[Message], Any]:
        """Returns the template as a formatted list of messages."""
        message_type_by_role = {
            "system": SystemMessage,
            "user": UserMessage,
            "assistant": AssistantMessage,
            "model": ModelMessage,
            "tool": ToolMessage,
        }
        return [
            message_type_by_role[message["role"]](
                role=message["role"], content=message["content"]
            )
            for message in self._parse_messages(list(message_type_by_role.keys()))
        ]

    def dump(
        self,
    ) -> dict[str, Any]:
        """Dumps the contents of the prompt into a dictionary."""
        return {
            "tags": self.tags,
            "template": dedent(self.template).strip("\n"),
            "inputs": self.model_dump(),
        }

    ############################## PRIVATE METHODS ###################################

    def _format_template(self, template: str):
        """Formats the given `template` with attributes matching template variables."""
        template = dedent(template).strip("\n")
        template_vars = [
            var for _, var, _, _ in Formatter().parse(template) if var is not None
        ]
        return template.format(**{var: getattr(self, var) for var in template_vars})

    def _parse_messages(self, roles: list[str]) -> list[dict[str, str]]:
        """Returns messages parsed from the `template` ClassVar.

        Raises:
            ValueError: if the template contains an unknown role.
        """
        messages = []
        re_roles = "|".join([role.upper() for role in roles] + ["[A-Z]*"])
        for match in re.finditer(
            rf"({re_roles}):((.|\n)+?)(?=({re_roles}):|\Z)",
            self.template,
        ):
            role = match.group(1).lower()
            if role not in roles:
                raise ValueError(f"Invalid role: {role}")
            content = self._format_template(match.group(2))
            messages.append({"role": role, "content": content})
        if len(messages) == 0:
            messages.append({"role": "user", "content": self.template})
        return messages


BasePromptT = TypeVar("BasePromptT", bound=BasePrompt)


def tags(args: list[str]) -> Callable[[Type[BasePromptT]], Type[BasePromptT]]:
    '''A decorator for adding tags to a `BasePrompt`.

    Adding this decorator to a `BasePrompt` updates the `_tags` class attribute to the
    given value. This is useful for adding metadata to a `BasePrompt` that can be used
    for logging or filtering.

    Example:

    ```python
    from mirascope import BasePrompt, tags


    @tags(["book_recommendation", "entertainment"])
    class BookRecommendationPrompt(BasePrompt):
        template = """
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
        The decorated class with `tags` class attribute set.
    '''

    def tags_fn(model_class: Type[BasePromptT]) -> Type[BasePromptT]:
        """Updates the `tags` class attribute to the given value."""
        setattr(model_class, "tags", args)
        return model_class

    return tags_fn
