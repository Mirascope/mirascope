from typing import Annotated

from mirascope import BaseMessageParam, llm
from mirascope.retries.tenacity import collect_errors
from pydantic import AfterValidator, ValidationError
from tenacity import retry, stop_after_attempt


def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v


@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=Annotated[str, AfterValidator(is_upper)],  # pyright: ignore [reportArgumentType, reportCallIssue]
)
def identify_author(
    book: str, *, errors: list[ValidationError] | None = None
) -> list[BaseMessageParam]:
    previous_errors = None
    if errors:
        print(previous_errors)
        content = f"Previous Error: {errors}\n\nWho wrote {book}?"
    else:
        content = f"Who wrote {book}?"
    return [BaseMessageParam(role="user", content=content)]


author = identify_author("The Name of the Wind")
print(author)
# Previous Errors: [1 validation error for str
# value
#   Assertion failed, Must be uppercase [type=assertion_error, input_value='Patrick Rothfuss', input_type=str]
#     For further information visit https://errors.pydantic.dev/2.7/v/assertion_error]
# PATRICK ROTHFUSS
