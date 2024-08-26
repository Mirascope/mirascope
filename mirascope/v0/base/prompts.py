from collections.abc import Callable
from typing import TypeVar

from .calls import BaseCall

_BaseCallT = TypeVar("_BaseCallT", bound=BaseCall)


def tags(args: list[str]) -> Callable[[type[_BaseCallT]], type[_BaseCallT]]:
    '''A decorator for adding tags to a `BasePrompt`.

    Adding this decorator to a `BasePrompt` updates the `_tags` class attribute to the
    given value. This is useful for adding metadata to a `BasePrompt` that can be used
    for logging or filtering.

    Example:

    ```python
    from mirascope import BasePrompt, tags


    @tags(["book_recommendation", "entertainment"])
    class BookRecommendationPrompt(BasePrompt):
        prompt_template = """
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

    def tags_fn(model_class: type[_BaseCallT]) -> type[_BaseCallT]:
        """Updates the `tags` class attribute to the given value."""
        model_class.tags = args
        return model_class

    return tags_fn
