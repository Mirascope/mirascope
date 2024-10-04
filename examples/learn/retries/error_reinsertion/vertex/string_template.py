from typing import Annotated

from mirascope.core import BaseDynamicConfig, prompt_template, vertex
from mirascope.retries.tenacity import collect_errors
from pydantic import AfterValidator, ValidationError
from tenacity import retry, stop_after_attempt


def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v


@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
@vertex.call(
    "gemini-1.5-flash",
    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
)
@prompt_template(
    """
    {previous_errors}

    Who wrote {book}?
    """
)
def identify_author(
    book: str, *, errors: list[ValidationError] | None = None
) -> BaseDynamicConfig:
    previous_errors = None
    if errors:
        previous_errors = f"Previous Errors: {errors}"
        print(previous_errors)
    return {"computed_fields": {"previous_errors": previous_errors}}


author = identify_author("The Name of the Wind")
print(author)
# Previous Errors: [1 validation error for str
# value
#   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
#     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
# PATRICK ROTHFUSS
