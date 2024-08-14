# Tenacity

Making an API call to a provider can fail due to various reasons, such as rate limits, internal server errors, validation errors, and more. Mirascope combined with [Tenacity](https://tenacity.readthedocs.io/en/latest/) increases the chance for these requests to succeed or provides transparency to end users.

## Using Tenacity with Mirascope

A Mirascope call with Tenacity exponential back-off when service is temporarily unavailable:

```python
from anthropic import InternalServerError
from tenacity import retry, stop_after_attempt, wait_exponential

from mirascope.core import anthropic, prompt_template


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@anthropic.call(model="claude-3-5-sonnet-20240620")
@prompt_template("What is your purpose?")
def run(): ...


print(run())
```

The most common situation is that the call goes through and runs like normal. In the chance that Anthropic is down or rate limit occurs, we will make the request again, after waiting for some time. After 3 attempts, we will get a `RetryError` that can further be handled.

## Error Reinsertion

Let us take a look at a more common use-case for using Tenacity `retry`.
Extracting structured information is not guaranteed and often time will lead to Pydantic a `ValidationError`. We can collect the list of `ValidationError` and feed it back into the LLM call to give better context for the next try:

```python
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
    author: str = Field(description="Author of the book")


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
    return {"computed_fields": {"previous_errors": errors}}


book = "the name of the wind by patrick rothfuss"
book_details = book_extractor(book=book)
print(book_details)
```

For demonstrative purposes, we first prompt engineer the result to return a lower case title and author. We then feed the `ValidationError` "Title must be in all caps." back to the prompt, which is then used in the subsequent call, returning an all caps title and author.  
