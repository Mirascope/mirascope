from typing import Annotated

from mirascope import Messages, llm
from pydantic import AfterValidator, ValidationError


def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v


def get_book_author(title: Annotated[str, AfterValidator(is_upper)]) -> str:
    """Returns the author of the book with the given title

    Args:
        title: The title of the book.
    """
    if title == "THE NAME OF THE WIND":
        return "Patrick Rothfuss"
    elif title == "MISTBORN: THE FINAL EMPIRE":
        return "Brandon Sanderson"
    else:
        return "Unknown"


@llm.call(provider="openai", model="gpt-4o-mini", tools=[get_book_author])
def identify_author(book: str) -> Messages.Type:
    return Messages.User(f"Who wrote {book}?")


response = identify_author("The Name of the Wind")
try:
    if tool := response.tool:
        print(tool.call())
    else:
        print(response.content)
except ValidationError as e:
    print(e)
    # > 1 validation error for GetBookAuthor
    #   title
    #     Assertion failed, Must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.8/v/assertion_error
