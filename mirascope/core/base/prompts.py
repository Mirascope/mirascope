"""The `BasePrompt` class for better prompt engineering."""

from textwrap import dedent
from typing import Any, Callable, ClassVar, TypeVar

from pydantic import BaseModel

from .._internal import utils
from .types import BaseMessageParam


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
        return utils.format_prompt_template(self.prompt_template, self.model_dump())

    def message_params(self) -> list[BaseMessageParam]:
        """Returns the template as a formatted list of `Message` instances."""
        return utils.parse_prompt_messages(
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
