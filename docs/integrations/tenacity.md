# Tenacity

Making an API call to a provider can fail due to various reasons, such as rate limits, internal server errors, validation errors, and more. Mirascope combined with [Tenacity](https://tenacity.readthedocs.io/en/latest/) increases the chance for these requests to succeed or provides transparency to end users.

You can install the necessary packages directly or using the `tenacity` extras flag:

```python
pip install "mirascope[tenacity]"
```

## Usage with Mirascope

### Calls

A Mirascope call with Tenacity exponential back-off when service is temporarily unavailable:

```python
from mirascope.core import anthropic, prompt_template
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("fantasy")
print(response.content)
```

The most common situation is that the call goes through and runs like normal. In the chance that Anthropic is down or rate limit occurs, we will make the request again, after waiting for some time. After 3 attempts, we will get a `RetryError` that can further be handled.

### Streams

When streaming, the generator is not actually run until you start iterating. This means that the initial API call may be successful but fail during the actual iteration through the stream. In such a case, adding `retry` to your call will not run (since the call succeeded), so instead you need to wrap your call and add retries to this new function:

```python
from mirascope.core import anthropic, prompt_template
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@anthropic.call("claude-3-5-sonnet-20240620", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


def stream():
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)


stream()
```

### Tools

When using tools, you need to handle your retries similarly to how we handle streams above. This is because errors such as `ValidationError` won't happen until we attempt to construct the tool (either when calling `response.tools` or iterating through the stream).

```python
from mirascope.core import anthropic, prompt_template
from tenacity import retry, stop_after_attempt, wait_exponential


def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"


@anthropic.call("claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def run():
    response = recommend_book("fantasy")
    if tool := response.tool:
        print(tool.call())
    else:
        print(response.content)


run()
```

### Response Model

When using `response_model`, we attempt to construct the model before the end of the call in order to return it as the final output of the function. This means that you can safely add retries to the original call like we did for the basic call above.

```python
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential


class Book(BaseModel):
    title: str
    author: str


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@anthropic.call("claude-3-5-sonnet-20240620", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


book = recommend_book("fantasy")
print(book)
```

## Error Reinsertion

Every example above simply retries after a failed attempt without making any updates to the call. This approach can be sufficient for some use-cases where we can safely expect the call to succeed on subsequent attempts (e.g. rate limits).

However, there are some cases where the LLM is likely to make the same mistake over and over again. For example, when using tools or response models, the LLM may return incorrect or missing arguments where it's highly likely the LLM will continuously make the same mistake on subsequent calls. In these cases, it's important that we update subsequent calls bsaed on resulting errors to improve the chance of success on the next call.

To make it easier to make such updates, we provide a `collect_errors` handler that can collect any errors of your choice and insert them into subsequent calls through an `errors` keyword argument.

```python
from typing import Annotated

from mirascope.core import openai, prompt_template
from mirascope.integrations.tenacity import collect_errors
from pydantic import AfterValidator, BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt


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
```

We can see from the above example that the first attempt fails because the title and author are in all lowercase. The `ValidationError`s are then reinserted into the subsequent call, which enables the model to learn from it's mistake and correct it on the subsequent call.

Of course, we could always prompt engineer the prompt template and response model to ask for all caps from the beginning, but even prompt engineering isn't perfect. The purpose of this example is to demonstrate the power of reinserting errors to improve results.  
