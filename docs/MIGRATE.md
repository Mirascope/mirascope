# Migration Guide: v0 → v1

!!! warning "This Guide May Not Cover Everything"

    We have tried our best to cover everything that may be involved in a migration from v0 to v1, but there is always a possibility that we missed something. Please bear with us as we work with you to help you get migrated.
    
    If there is anything missing from this guide or anything that leaves you confused, let us know!
    
    We're here to help make sure your migration can progress smoothly :)
    
    We're extremely excited about the changes in v1 and want to make sure that you are set up to be equally excited.

## Introduction

Mirascope v1 introduces significant changes to improve developer experience, enhance flexibility, and provide more powerful features for working with Large Language Models (LLMs). This guide will help you migrate your existing Mirascope v0 code to v1, highlighting key differences and new features.

## Core Changes

### From Classes to Decorators

The most significant change in v1 is the shift from class-based to decorator-based calls.

Before (v0):

```python
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
print(response.content)
```

After (v1):

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("fantasy")
print(response.content)
```

### Async Calls

Before (v0):

```python
import asyncio

from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str


recommender = BookRecommender(genre="fantasy")
response = asyncio.run(recommender.call_async())
print(response.content)
```

After (v1):

```python
import asyncio

from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str):
    ...


response = asyncio.run(recommend_book("fantasy"))
print(response.content)
```

### Streaming

Before (v0):

```python
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str


recommender = BookRecommender(genre="fantasy")
stream = recommender.stream()
for chunk in stream:
    print(chunk.content, end="", flush=True)
```

After (v1):

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


stream = recommend_book("fantasy")
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

### Tools (Function Calling)

Before (v0):

```python
from mirascope.openai import OpenAICall, OpenAICallParams, OpenAITool


class FormatBook(OpenAITool):
    title: str
    author: str

    def call(self):
        return f"{self.title} by {self.author}"


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str

    call_params = OpenAICallParams(tools=[FormatBook], tool_choice="required")


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
if tool := response.tool:
    print(tool.call())
else:
    print(response.content)

```

After (v1):

```python
from mirascope.core import BaseTool, openai, prompt_template


class FormatBook(BaseTool):
    title: str
    author: str

    def call(self):
        return f"{self.title} by {self.author}"


@openai.call(
    "gpt-4o-mini",
    tools=[FormatBook],
    call_params={"tool_choice": "required"},
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("fantasy")
if tool := response.tool:
    print(tool.call())
else:
    print(response.content)
```

!!! note "Function Tools"

    If you were using functions as tools, these can still be used as tools in the same way. The only difference is how you supply the tools, which is through the `tools` argument of the `call` decorator in v1.

### Streaming Tools

Before (v0):

```python
from mirascope.openai import OpenAICall, OpenAICallParams, OpenAIToolStream


def format_book(title: str, author: str):
    """Returns a formatted book string."""
    return f"{title} by {author}"


class BookRecommender(OpenAICall):
    prompt_template = "Recommend two (2) {genre} books."
    genre: str

    call_params = OpenAICallParams(tools=[format_book], tool_choice="required")


recommender = BookRecommender(genre="fantasy")
tool_stream = OpenAIToolStream.from_stream(recommender.stream())
for tool in tool_stream:
    print(tool.call())
```

After (v1):

```python
from mirascope.core import openai, prompt_template


def format_book(title: str, author: str):
    # docstring no longer required, but still used if supplied
    return f"{title} by {author}"


@openai.call(
    "gpt-4o-mini",
    stream=True,
    tools=[format_book],
    call_params={"tool_choice": "required"},
)
@prompt_template("Recommend two (2) {genre} books")
def recommend_book(genre: str):
    ...


stream = recommend_book("fantasy")
for chunk, tool in stream:
    if tool:
        print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
```

### Extracting Structured Information

Before (v0):

```python
from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class BookExtractor(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Recommend a {genre} book."

    genre: str


extractor = BookExtractor(genre="fantasy")
book = extractor.extract()
assert isinstance(book, Book)
print(book)

```

After (v1):

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@openai.call("gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


book = recommend_book("fantasy")
assert isinstance(book, Book)
print(book)
```

### JSON Mode

Before (v0):

```python
from mirascope.openai import OpenAICallParams, OpenAIExtractor
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class BookExtractor(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Recommend a {genre} book."

    genre: str

    call_params = OpenAICallParams(response_format={"type": "json_object"})


extractor = BookExtractor(genre="fantasy")
book = extractor.extract()
print(book)

```

After (v1):

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@openai.call("gpt-4o-mini", response_model=Book, json_mode=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


book = recommend_book("fantasy")
print(book)
```

### Streaming Structured Information

Before (v0)

```python
from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class BookExtractor(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Recommend a {genre} book."
    genre: str


extractor = BookExtractor(genre="fantasy")
book_stream = extractor.stream()
for partial_book in book_stream:
    print(partial_book)
```

After (v1)

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@openai.call("gpt-4o-mini", stream=True, response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


book_stream = recommend_book("fantasy")
for partial_book in book_stream:
    print(partial_book)
```

### Dynamic Variables and Chaining

Before (v0):

```python
from mirascope.openai import OpenAICall
from pydantic import computed_field


class AuthorRecommender(OpenAICall):
    prompt_template = """
    Recommend an author that writes the best {genre} books.
    Give me just their name.
    """

    genre: str


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book written by {author}"
    
    genre: str

    @computed_field
    @property
    def author(self) -> str:
        return AuthorRecommender(genre=self.genre).call().content


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
print(response.content)
```

After (v1):

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template(
    """
    Recommend an author that writes the best {genre} books.
    Give me just their name.
    """
)
def recommend_author(genre: str):
    ...


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book written by {author}")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {"computed_fields": {"author": recommend_author(genre)}}


response = recommend_book("fantasy")
print(response.content)
print(response.fn_args["author"])
```

### Dumping Call Information

Before (v0):

```python
from mirascope.openai import OpenAICall


class BookRecommender(OpenAICall):
    prompt_template = "Recommend a {genre} book."
    genre: str


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
print(response.dump())
```

After (v1):

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("fantasy")
print(response.model_dump())
```

### Multimodal Capabilities

Before (v0):

```python
from mirascope.openai import OpenAICall
from openai.types.chat import ChatCompletionMessageParam


class ImageDetection(OpenAICall):
    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "I just read this book: "},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/en/4/44/Mistborn-cover.jpg",
                        },
                    },
                    {"type": "text", "text": "What should I read next?"},
                ],
            },
        ]


response = ImageDetection().call()
print(response.content)
```

After (v1):

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template(
    """
    I just read this book: {previous_book:image}.
    What should I read next?
    """
)
def recommend_book(previous_book: str): ...


response = recommend_book(
    "https://upload.wikimedia.org/wikipedia/en/4/44/Mistborn-cover.jpg"
)
print(response.content)
```

### FastAPI Integration

Before (v0):

```python
from fastapi import FastAPI
from mirascope.openai import OpenAIExtractor
from pydantic import BaseModel

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Recommend a {genre} book."

    genre: str


@app.get("/recommend_book")
def recommend_book(genre: str):
    recommender = BookRecommender(genre=genre)
    return recommender.extract()
```

After (v1):

```python
from fastapi import FastAPI
from mirascope.core import openai, prompt_template
from pydantic import BaseModel

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


@app.get("/recommend_book")
@openai.call("gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...
```

Migrating to Mirascope v1 offers a more streamlined and flexible approach to working with LLMs. The new decorator-based syntax simplifies code structure and makes it easier to implement advanced features like streaming, tools, and structured information extraction. 

Remember to update your import statements to use `from mirascope.core import ...` instead of the provider-specific imports used in v0. Also, be sure to familiarize yourself with the updated [`BasePrompt`](./learn/prompts.md#the-baseprompt-class) class for provider-agnostic prompt definitions.

If you encounter any issues during migration or have questions about the new features, please refer to the [Learn](./learn/index.md) documentation or reach out to the Mirascope community for support.
