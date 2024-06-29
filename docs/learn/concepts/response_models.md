# Response Model

Mirascope uses Pydantic’s `BaseModel` for defining extraction schemas, so check out their docs[link] for anything related to the `BaseModel` itself.

To extract structured data with Mirascope, define your `BaseModel` schema and set the `response_model` to the class in the decorator. 

```python
from typing import Literal
from pydantic import BaseModel
from mirascope.core import openai

class BookDetails(BaseModel):
    title: str
    author: str

@openai.call(model="gpt-4o", response_model=BookDetails)
def extract_book_details(book: str):
    """
    Extract the book details from the following book:
    {book}
    """

book = "The Name of the Wind by Patrick Rothfuss."
book_details = extract_book_details(book=book)
assert isinstance(book_details, BookDetails)
print(book_details)
# > title='The Name of the Wind' author='Patrick Rothfuss'
```

Mirascope extractions return an instance of the response model itself. However, you can still access the original provider response with the `._response` property.

## JSON Mode

Most providers natively support extraction via a JSON mode, which paired together with standard extractions improve consistency and accuracy. To activate JSON mode with Mirascope, set `json_mode=True` in the decorator:

```python
@openai.call(
		model="gpt-4o",
		response_model=BookDetails,
		json_mode=True,
)
def extract_book_details(book: str):
    """{book}"""

book = "The Name of the Wind by Patrick Rothfuss."
book_details = extract_book_details(book=book)
print(book_details)
# > title='The Name of the Wind' author='Patrick Rothfuss'
```

Of course, you are free to use `json_mode=True` on its own to call a model on JSON mode:

```python
import json

from mirascope.core import openai

@openai.call(model="gpt-4o", json_mode=True)
def extract_book_details(book: str):
		"""
		Extract book details in json using the following schema:
		
		title: str
		author: str
		
		Book: {book}
		"""
		
response = extract_book_details("The Name of the Wind by Patrick Rothfuss.")
json_obj = json.loads(response.content)
print(json_obj)
# > {'title': 'The Name of the Wind', 'author': 'Patrick Rothfuss'}
```

## Structured Streaming

You can stream partial instances of the `response_model` by setting `stream=True`. The partial models returned will have `None` for fields that have not yet been streamed, and it will parse partial objects (like strings) so you can see the progression of the stream for individual fields. The final model returned by the structured stream will be a true instance of `response_model` as if you had just run a standard extraction.

```python
class BookDetails(BaseModel):
    title: str
    author: str

@openai.call(model="gpt-4o", response_model=BookDetails)
def extract_book_details(book: str):
    """
    Extract the book details from the following book:
    {book}
    """

book = "The Name of the Wind by Patrick Rothfuss."
book_details = extract_book_details(book=book)
for partial_model in book_details:
    print(partial_model)
# > title=None author=None
#   title='The' author=None
#   title='The Name' author=None
#   title='The Name of' author=None
#   ...
#   title='The Name of the Wind' author='Patrick Rothfuss'
```

!!! Note Structured streaming is only supported by OpenAI and Anthropic. For other model providers, you must set `json_mode=True`.

## Async

If you want concurrency, use `call_async` to extract:

```python
import asyncio

class BookDetails(BaseModel):
    title: str
    author: str

@openai.call_async(model="gpt-4o", response_model=BookDetails)
async def book_details_extractor(book: str):
    """
    Extract the book details from the following book:
    {book}
    """

book = "The Name of the Wind by Patrick Rothfuss."

async def run():
    book_details = await book_details_extractor(book=book)
    assert isinstance(book_details, BookDetails)
    print(book_details)

asyncio.run(run())
```

## Generating Structured Data

You can also use `response_model` to generate structured data. The only difference between generating structured data and extracting it is the prompt, and being explicit often helps produce desired results (e.g. using words like “generate” or “extract” explicitly).

```python
class Book(BaseModel):
    title: str
    author: str

@openai.call(model="gpt-4o",response_model=Book)
def recommend_book(genre: str):
    """
    Generate a {genre} book recommendation.
    """

response = recommend_book(genre="fantasy")
print(response)
# > title='Mistborn: The Final Empire' author='Brandon Sanderson'
```

## Few Shot Examples

Extractions can often fail, and one technique to achieve higher success rates is through few shot examples. When setting up your extraction schema, use the `examples` argument of Pydantic’s `Field` to set examples for individual attributes or the `model_config` to set up examples of the entire model:

```python
from pydantic import BaseModel, ConfigDict

class Book(BaseModel):
    title: str = Field(..., examples=["The Name of the Wind"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "The Name of the Wind", "author": "Rothfuss, Patrick"}
            ]
        }
    )
```

## Validate Output and Retry

Model outputs do not always adhere to the correct structure or typing, and inserting validation errors back into your prompt and running it again often resolves any problems.

We provide a tenacity integration[link] for collecting validation errors on each retry to make it easy for you to insert the errors back into your call. This includes any additional validation you add to your schema.

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel
from tenacity import retry, stop_after_attempt

from mirascope.core import openai
from mirascope.integrations.tenacity import collect_validation_errors

def is_all_caps(s: str) -> bool:
    assert s.isupper(), "Value is not all caps uppercase."
    return s

class Book(BaseModel):
    title: Annotated[str, AfterValidator(is_all_caps)]
    author: Annotated[str, AfterValidator(is_all_caps)]

@retry(stop=stop_after_attempt(3), after=collect_validation_errors)
@openai.call(model="gpt-4o", response_model=Book)
def recommend_book(genre: str, *, validation_errors: list[str] | None = None):
    """
    {previous_errors}
    Recommend a {genre} book.
    """
    return {
        "computed_fields": {
            "previous_errors": f"Previous errors: {validation_errors}"
            if validation_errors
            else ""
        }
    }

book = recommend_book("fantasy")
assert isinstance(book, Book)
print(book)
#> title='THE NAME OF THE WIND' author='PATRICK ROTHFUSS'

```

### Validate and Retry Structured Streams

When streaming structured responses, you’ll need to wrap the stream in a function if you want to use the `retry` decorator with `collect_validation_errors`:

```python
@retry(stop=stop_after_attempt(3), after=collect_validation_errors)
def stream_book(*, validation_errors: list[str] | None = None) -> Book:
    book_stream = recommend_book("fantasy", validation_errors=validation_errors)
    for partial_book in book_stream:
        book = partial_book
        # do something with book
    return book
```
