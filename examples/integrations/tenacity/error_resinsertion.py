from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt

from mirascope.core import openai, prompt_template
from mirascope.integrations.tenacity import collect_errors


def check_if_caps(value: str) -> str:
    if not value.isupper():
        raise ValueError("Title must be in all caps.")
    return value


class Book(BaseModel):
    title: Annotated[str, AfterValidator(check_if_caps)] = Field(
        description="Title of the book"
    )
    author: Annotated[str, AfterValidator(check_if_caps)] = Field(
        description="Author of the book"
    )


@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
@openai.call(
    model="gpt-4o-mini",
    response_model=Book,
)
@prompt_template(
    """
    {previous_errors}

    Extract the following Book details lowercased:
    {book}
    """
)
def book_extractor(
    book: str, *, errors: list[ValidationError] | None = None
) -> openai.OpenAIDynamicConfig:
    previous_errors = None
    if errors:
        previous_errors = f"Previous Errors: {errors}"
        print(previous_errors)
    return {"computed_fields": {"previous_errors": previous_errors}}


book = "the name of the wind by patrick rothfuss"
book_details = book_extractor(book=book)
print(book_details)
# Previous Errors: [2 validation errors for Book
# title
#   Value error, Title must be in all caps. [type=value_error, input_value='the name of the wind', input_type=str]
#     For further information visit https://errors.pydantic.dev/2.8/v/value_error
# author
#   Value error, Title must be in all caps. [type=value_error, input_value='patrick rothfuss', input_type=str]
#     For further information visit https://errors.pydantic.dev/2.8/v/value_error]
# title='THE NAME OF THE WIND' author='PATRICK ROTHFUSS'
