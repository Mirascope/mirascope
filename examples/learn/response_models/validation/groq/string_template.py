from typing import Annotated, cast

from mirascope.core import groq, prompt_template
from pydantic import AfterValidator, BaseModel, ValidationError


def validate_upper(v: str) -> str:
    assert v.isupper(), "Field must be uppercase"
    return v


class Book(BaseModel):
    """An extracted book."""

    title: Annotated[str, AfterValidator(validate_upper)]
    author: Annotated[str, AfterValidator(validate_upper)]


@groq.call("llama-3.1-70b-versatile", response_model=Book)
@prompt_template("Extract {text}")
def extract_book(text: str): ...


try:
    book = extract_book("The Name of the Wind by Patrick Rothfuss")
    print(book)
    # Output: title='The Name of the Wind' author='Patrick Rothfuss'
except ValidationError as e:
    print(f"Error: {str(e)}")
    # Error: 2 validation errors for Book
    # title
    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
    # author
    #   Assertion failed, Field must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
    #     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error
    response = cast(groq.GroqCallResponse, e._response)  # pyright: ignore[reportAttributeAccessIssue]
    print(response.model_dump())
    # > {'metadata': {}, 'response': {'id': ...}, ...}
