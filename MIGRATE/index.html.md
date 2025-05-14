# Migration Guide: v0 → v1

!!! warning "This Guide May Not Cover Everything"

    We have tried our best to cover everything that may be involved in a migration from v0 to v1, but there is always a possibility that we missed something. Please bear with us as we work with you to help you get migrated.
    
    If there is anything missing from this guide or anything that leaves you confused, let us know!
    
    We're here to help make sure your migration can progress smoothly :)
    
    We're extremely excited about the changes in v1 and want to make sure that you are set up to be equally excited.

Mirascope v1 introduces significant changes to improve developer experience, enhance flexibility, and provide more powerful features for working with Large Language Models (LLMs). This guide will help you migrate your existing Mirascope v0 code to v1, highlighting key differences and new features.

## Understanding the Shift from v0 to v1

### Why Decorators Instead of Classes?

The transition from a class-based approach in v0 to a decorator-based approach in v1 represents a fundamental shift in how Mirascope handles LLM API calls. This change was driven by several key considerations:

1. **Stateless Nature of LLM API Calls**:
   LLM API calls are inherently stateless. The class-based approach in v0, which introduced fields as state, didn't align well with this stateless nature. Decorators better represent the functional, stateless character of these API interactions.

2. **Performance Improvements**:
   Creating a class instance for every call introduced unnecessary overhead. Functions, modified by decorators at runtime, provide a more lightweight and faster execution model.

3. **Functional Programming Paradigm**:
   The move to a more functional approach allows for greater flexibility and composability. It enables features like dynamic configuration, which were challenging to implement with the class-based model.

4. **Easier Integration with Other Libraries**:
   Many Python libraries use decorators. By adopting a decorator-based approach, Mirascope v1 seamlessly integrates with these libraries. For example, you can now use libraries like `tenacity` for retry logic without any explicit integration – it just works.

### Benefits of the New Approach

1. **Simplified Code**:
   Instead of defining a class for each LLM call, you can now use a simple function with a decorator. This results in more concise and readable code.

2. **Enhanced Flexibility**:
   The decorator approach allows for more dynamic behavior, such as easily changing call parameters or prompt templates at runtime.

3. **Improved Performance**:
   By eliminating the need to construct class instances, the new approach offers better performance, especially for applications making frequent LLM calls.

4. **Better Alignment with Python Ecosystem**:
   The decorator pattern is widely used in Python, making Mirascope v1 feel more native to experienced Python developers.

The v1 approach is more concise, directly represents the stateless nature of the API call, and allows for easier dynamic usage and integration with other Python libraries.

By embracing this new paradigm, Mirascope v1 offers a more pythonic, flexible, and powerful way to interact with LLMs, setting the stage for more advanced features and integrations in the future.

## Core Changes

The most significant change in v1 is the shift from class-based to decorator-based calls. To illustrate the difference, let's take a look at various comparison examples between the two versions.

### From Classes to Decorators

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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


response = recommend_book("fantasy")
print(response.content)
```

#### `BasePrompt`

The `BasePrompt` class still operates in the same way as v0 calls (e.g. `OpenAICall`). The primary difference is that you run the prompt using the `run` method instead of using the `call` or `stream` methods. This method can be run against any provider's call decorator:

```python
from mirascope.core import BasePrompt, openai, prompt_template


@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
response = prompt.run(openai.call("gpt-4o-mini"))
print(response.content)
```

Of course, there's nothing stopping you from replicating the original v0 functionality of `OpenAICall` by writing your own `call` method (or whatever you'd like to name it):

```python
from mirascope.core import BasePrompt, openai, prompt_template


@prompt_template("Recommend a {genre} book")
class BookRecommender(BasePrompt):
    genre: str

    def call(self) -> openai.OpenAICallResponse:
        return self.run(openai.call("gpt-4o-mini"))

    def stream(self) -> openai.OpenAIStream:
        return self.run(openai.call("gpt-4o-mini", stream=True))


recommender = BookRecommender(genre="fantasy")
response = recommender.call()
print(response.content)

stream = recommender.stream()
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)
```

#### Statefulness

Some people may feel that "statelessness" is actually an inherent problem with LLM API calls. We agree with this sentiment, and it's the reason for the original design in v0. However, as we've continued to build we've come to believe that adding such state to the abstraction for making the LLM call itself is the wrong place for that state to live. Instead, the state should live in a class that wraps the call, and the call should have easy access to said state.

This provides a far clearer sense of what is "state" and what is an "argument" of the call. Consider the following example:

```python
from mirascope.core import BaseMessageParam, openai, prompt_template
from pydantic import BaseModel, computed_field


class Librarian(BaseModel):
    genre: str

    @openai.call("gpt-4o-mini")
    @prompt_template(
        """
        SYSTEM: You are a librarian. You specialize in the {self.genre} genre
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def call(self, query: str): ...

    @computed_field
    @property
    def history(self) -> list[BaseMessageParam | openai.OpenAIMessageParam]:
        """Returns dummy history for demonstration purposes"""
        return [
            {"role": "user", "content": "What book should I read?"},
            {
                "role": "assistant",
                "content": "Do you like fantasy books?",
            },
        ]


fantasy_librarian = Librarian(genre="fantasy")
response = fantasy_librarian.call("I do like fantasy books!")
print(response.content)
```

It's evident that `genre` and `history` are state of the `Librarian` class, and the call method uses this state for every call. However, we've also introduced the `query` argument of the call, which is clearly not state and should be provided for every call.

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
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


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
def recommend_book(genre: str) -> str:
    return f"Recommend two (2) {genre} books"


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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


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
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
```

Migrating to Mirascope v1 offers a more streamlined and flexible approach to working with LLMs. The new decorator-based syntax simplifies code structure and makes it easier to implement advanced features like streaming, tools, and structured information extraction. 

Remember to update your import statements to use `from mirascope.core import ...` instead of the provider-specific imports used in v0. Also, be sure to familiarize yourself with the updated recommendations for writing [prompts](./learn/prompts.md) in the more functional form we now recommend.

If you encounter any issues during migration or have questions about the new features, please refer to the [Learn](./learn/index.md) documentation or reach out to the Mirascope community for support.
