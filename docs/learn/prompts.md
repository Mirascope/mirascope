# Prompts

Prompts are the foundation of effective communication with Large Language Models (LLMs). Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions. This guide will walk you through the features and best practices for prompt engineering using Mirascope.

## Prompt Templates

??? api "API Documentation"

    [`mirascope.core.base.prompt.prompt_template`](../api/core/base/prompt.md#mirascope.core.base.prompt.prompt_template)

The primary means of writing prompts in Mirascope is through prompt templates, which are formatted strings with additional conveniences. This allows you to define prompts that are dynamic and reusable.

Prompt templates in Mirascope work similarly to f-strings in Python, but with added functionality specifically designed for LLM interactions. The `@prompt_template` decorator automatically injects variables from your class or function into the template.

Let's look at a basic example:

```python hl_lines="1 5"
@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str

prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# Output: Recommend a fantasy book
```

In this example:
1. The `@prompt_template` decorator defines the template string.
2. The `{genre}` placeholder in the template corresponds to the `genre` attribute of the class.
3. When you create an instance of `BookRecommendationPrompt` with `genre="fantasy"`, the `genre` value is automatically injected into the template.

This approach allows for flexible and reusable prompt creation, making it easy to generate variations of prompts by changing the input parameters.


For more complex use cases, we'll use:

- `@prompt_template`: a decorator for attaching a prompt template to a function or class
- `BasePrompt`: a base class for writing provider-agnostic prompts.

We'll cover `BasePrompt` in more detail later. For now, let's focus on how template variables are injected and how to view the resulting prompt:

```python hl_lines="9"
from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a fantasy book
```

In this example, the `@prompt_template` decorator defines the template string `"Recommend a {genre} book"`. The genre attribute of the `BookRecommendationPrompt` class corresponds to the `{genre}` placeholder in the template. When you create an instance of the class with `genre="fantasy"`, this value is automatically injected into the template.

We've implemented the `__str__` method in `BasePrompt` for easy verification of how variables are templated.

For your convenience, we automatically dedent and strip the prompt template. This makes writing multi-line prompts a breeze:

```python hl_lines="5-8 11"
from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    """
    Recommend a book.
    It should be a {genre} book.
    """
)
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a book.
#   It should be a fantasy book.
```

### Format Specifiers

Since Mirascope prompt templates are just formatted strings, standard Python format specifiers work as expected:

```python hl_lines="4 6 9"
from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a book cheaper than ${price:.2f}")
class BookRecommendationPrompt(BasePrompt):
    price: float


prompt = BookRecommendationPrompt(price=12.3456)
print(prompt)
# > Recommend a book cheaper than $12.34
```

In this example, we use the `.2f` format specifier to limit the price to two decimal places.

We also provide additional specifiers we've found useful in our own prompt engineering:

- `list`: formats an input list as a newline-separated string
- `lists`: formats an input list of lists as newline-separated strings separated by double newlines

Here's an example demonstrating these custom specifiers:

```python hl_lines="7 10 19-23"
from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    """
    Recommend a book from one of the following genres:
    {genres:list}

    Examples:
    {examples:lists}
    """
)
class BookRecommendationPrompt(BasePrompt):
    genres: list[str]
    examples: list[tuple[str, str]]


prompt = BookRecommendationPrompt(
    genres=["fantasy", "scifi", "mystery"],
    examples=[
        ("Title: The Name of the Wind", "Author: Patrick Rothfuss"),
        ("Title: Mistborn: The Final Empire", "Author: Brandon Sanderson"),
    ]
)
print(prompt)
# > Recommend a book from one of the following genres:
#   fantasy
#   scifi
#   mystery
#
#   Examples:
#   Title: The Name of the Wind
#   Author: Patrick Rothfuss
#
#   Title: Mistborn: The Final Empire
#   Author: Brandon Sanderson
```

This example showcases how the `list` and `lists` specifiers can be used to format complex data structures within your prompts.

If there are any other such specifiers you would find useful, let us know!

### Message Roles

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

By default, Mirascope treats the entire prompt as a single user message. However, you can use the `SYSTEM`, `USER`, and `ASSISTANT` keywords to specify different message roles, which we will parse into `BaseMessageParam` instances:

```python hl_lines="6 7 16 17"
from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    """
    SYSTEM: You are the world's greatest librarian
    USER: Recommend a {genre} book
    """
)
class RecommendBookPrompt(BasePrompt):
    genre: str


prompt = RecommendBookPrompt(genre="fantasy")
print(prompt)
# > SYSTEM: You are the world's greatest librarian
#   USER: Recommend a fantasy book
print(prompt.message_params())
# > [BaseMessageParam(role='system', content="You are the world's greatest librarian"), BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

In this example, we use the `SYSTEM` and `USER` keywords to specify different roles for parts of the prompt. The `message_params()` method returns a list of BaseMessageParam instances, each representing a different role and its content.

!!! note "Order Of Operations"

    When parsing prompt templates, we first parse each message parameter and then format the content of each parameter individually. We have implemented this specifically to prevent injecting new message parameters through a template variable.

Make sure when writing multi-line prompts with message roles that you start the prompt on the following line so it is properly dedented:

```python
# BAD
@prompt_template(
    """
    USER: First line
    Second line
    """
)

# GOOD
@prompt_template(
    """
    USER:
    First line
    Second line
    """
)
```

This ensures that the content for each role is properly formatted and aligned.


### `MESSAGES` Keyword

Often you'll want to inject messages (such as previous chat messages) into the prompt. We provide a `MESSAGES` keyword for this injection, which you can add in whatever position and as many times as you'd like:

```python hl_lines="7 18-22"
from mirascope.core import BaseMessageParam, BasePrompt, prompt_template


@prompt_template(
    """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {history}
    USER: {query}
    """
)
class BookRecommendationPrompt(BasePrompt):
    history: list[BaseMessageParam]
    query: str


prompt = BookRecommendationPrompt(
    history=[
        BaseMessageParam(role="user", content="What should I read next?"),
        BaseMessageParam(
            role="assistant",
            content="I recommend 'The Name of the Wind' by Patrick Rothfuss",
        ),
    ],
    query="Anything similar you would recommend?",
)
print(prompt.message_params())
# > [
#     BaseMessageParam(role='system', content="You are the world's greatest librarian."),
#     BaseMessageParam(role='user', content='What should I read next?'),
#     BaseMessageParam(role='assistant', content="I recommend 'The Name of the Wind' by Patrick Rothfuss"),
#     BaseMessageParam(role='user', content='Anything similar you would recommend?')
#   ]
```

This example demonstrates how to include a conversation history in your prompt, allowing for more context-aware responses from the LLM.

### Inject Accessed Attributes

When the fields of your class or arguments of your function are more complex objects with attributes, you can access and use these attributes directly in the prompt template:

```python hl_lines="11 12 18 19"
from mirascope.core import BasePrompt, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str

@prompt_template(
    """
    I just read {book.title} by {book.author}.
    What should I read next?
    """
)
class MyPrompt(BasePrompt):
    book: Book

book = Book(title="The Great Gatsby", author="F. Scott Fitzgerald")
my_prompt = MyPrompt(book=book)
print(my_prompt.message_params())
# > [BaseMessageParam(role="user", content="I just read The Great Gatsby by F. Scott Fitzgerald.\nWhat should I read next?")]
```

This feature allows you to work with more complex data structures in your prompts, improving flexibility and readability.

### Empty Messages

When a template variable is set to `None` it will be injected as the empty string.

If the content of a message is empty, that message will be excluded from the final list of message parameters:

```python hl_lines="7 11 14 16"
from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    """
    SYSTEM: You are the world's greatest librarian.
    USER: {query}
    """
)
class BookRecommendationPrompt(BasePrompt):
    query: str | None


prompt = BookRecommendationPrompt(query=None)
print(prompt.message_params())
# >[BaseMessageParam(role='system', content="You are the world's greatest librarian.")]
```

!!! note "Why exclude them?"

    While it might not be immediately clear yet, this exclusion of empty messages can be extremely useful, particularly when calling an LLM where you may want to exclude the final user message as the model iteratively calls tools.

### Multi-Modal Inputs

Recent advancements in Large Language Model architecture has enabled many model providers to support multi-modal inputs (text, images, audio, etc.) for a single endpoint. For all multi-modal inputs, we handle URLs, local filepaths, and raw bytes.

To inject multimodal inputs into your prompt template, simply tag the input with the multimodal type:

- `image` / `images`: injects a (list of) image(s) into the message parameter
- `audio` / `audios`: injects a (list of) audio file(s) into the message parameter

We find that this method of templating multi-modal inputs enables writing prompts in a far more natural, readable format:

```python hl_lines="4"
from mirascope.core import BasePrompt, prompt_template


@prompt_template("I just read this book: {book:image}. What should I read next?")
class BookRecommendationPrompt(BasePrompt):
    book: str | bytes


url = "https://upload.wikimedia.org/wikipedia/en/5/56/TheNameoftheWind_cover.jpg"
prompt = BookRecommendationPrompt(book=url)
print(prompt.message_params())
# > [BaseMessageParam(
#       role='user',
#       content=[
#           TextPart(type='text', text='I just read this book:'),
#           ImagePart(
#               type='image',
#               media_type='image/jpeg',
#               image=b'...',
#               detail=None
#           ),
#           TextPart(type='text', text='. What should I read next?')
#       ]
#   )]
```

This example shows how to include an image in your prompt, which can be particularly useful for tasks like visual question answering or image captioning.

Some providers (e.g. OpenAI) offer additional options for multi-modal inputs such as image detail. You can specify additional options as though you are initializing the image format spec with keyword arguments for the options:

```python hl_lines="10"
from mirascope.core import BasePrompt, prompt_template


@prompt_template("I just read this book: {book:image(detail=high)}. What should I read next?")
class BookRecommendationPrompt(BasePrompt):
    book: str | bytes


url = "https://upload.wikimedia.org/wikipedia/en/5/56/TheNameoftheWind_cover.jpg"
prompt = BookRecommendationPrompt(book=url)
print(prompt.message_params())
# > [BaseMessageParam(
#       role='user',
#       content=[
#           ...
#           ImagePart(
#               ...
#               detail='high'
#           ),
#           ...
#       ]
#   )]
```

## The `BasePrompt` Class

??? api "API Documentation"

    [`mirascope.core.base.prompt.BasePrompt`](../api/core/base/prompt.md#mirascope.core.base.prompt.BasePrompt)

So far we've only used `BasePrompt` to demonstrate the functionality of Mirascope prompt templates; however, the class has much more to offer as a provider-agnostic base class for creating reusable prompts.

It leverages Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/concepts/models/) for easy validation and serialization of prompt data as well as additional convenience around writing more complex template variables.

To recap, you can create a prompt using `BasePrompt` by defining a class that inherits from it:

```python hl_lines="4-7"
from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a {genre} book for a {age_group} reader")
class BookRecommendationPrompt(BasePrompt):
    genre: str
    age_group: str

prompt = BookRecommendationPrompt(genre="fantasy", age_group="young adult")
print(prompt)
# > Recommend a fantasy book for a young adult reader
print(prompt.message_params())
# > [BaseMessageParam(role="user", content="Recommend a fantasy book for a young adult reader")]
```

Again, note that we've implemented the `__str__` and `message_param` methods for easy verification of how variables are templated.

### Computed Fields

You can use Pydantic's `@computed_field` decorator to inject more complex template variables into your prompt. These computed fields can be written just like any other function of the class and can thus compute their value using other fields:

```python hl_lines="10-18 23"
from mirascope.core import BasePrompt, prompt_template
from pydantic import computed_field


@prompt_template("Recommend a {genre} {book_type} for a {age_group} reader.")
class BookRecommendationPrompt(BasePrompt):
    genre: str
    age_group: str

    @computed_field
    @property
    def book_type(self) -> str:
        if self.age_group == "child":
            return "picture book"
        elif self.age_group == "young adult":
            return "novel"
        else:
            return "book"


prompt = BookRecommendationPrompt(genre="fantasy", age_group="child")
print(prompt)
# > Recommend a fantasy picture book for a child reader.
```

This example demonstrates how computed fields can be used to dynamically determine parts of the prompt based on other input parameters.

!!! tip "Retrieving External Data"

    Computed fields can be particularly useful when you want to inject information you retrieve from an external source. For example, perhaps you want to retrieve context from a document store to augment the generation with relevant information (RAG).

### Metadata

??? api "API Documentation"

    [`mirascope.core.base.prompt.metadata`](../api/core/base/prompt.md#mirascope.core.base.prompt.metadata)

You can add metadata to your prompts using the `@metadata` decorator. This will attach a `Metadata` object, which is a simple `TypedDict` with a single typed key `tags: set[str]`.

This can be useful for tracking versions, categories, or any other relevant information.

```python hl_lines="4 12 13"
from mirascope.core import BasePrompt, prompt_template, metadata


@metadata({"tags": {"version:0001", "category:books"}})
@prompt_template("Recommend a {genre} book for a {age_group} reader.")
class BookRecommendationPrompt(BasePrompt):
    genre: str
    age_group: str


prompt = BookRecommendationPrompt(genre="fantasy", age_group="adult")
print(prompt.dump()['metadata'])
# > {'tags': {'version:0001', 'category:books'}}
```

This feature allows you to add structured metadata to your prompts, which can be useful for versioning, categorization, or tracking.

!!! note "Adding Additional Fields"

    Although `Metadata` is a `TypedDict` with only the `tags` key, there is nothing stopping you from adding additional keys. The only issue is that this will throw a type error, which you can ignore. We recommend ignoring the specific error. For example, if you're using pyright you should add `# pyright: ignore [reportArgumentType]`.
    
    If there are particular keys you find yourself using frequently, let us know so we can add them!

### Running Prompts

??? api "API Documentation"

    [`mirascope.core.base.prompt.BasePrompt.run`](../api/core/base/prompt.md#mirascope.core.base.prompt.BasePrompt.run)

    [`mirascope.core.base.prompt.BasePrompt.run_async`](../api/core/base/prompt.md#mirascope.core.base.prompt.BasePrompt.run_async)

One of the key benefits of `BasePrompt` is that it is provider-agnostic. You can use the same prompt with different LLM providers, making it easy to compare performance or switch providers.

You can do this with the `run` and `run_async` methods that run the prompt using the configuration of a call decorator. For now, just know that the decorator is configuring a call to the LLM, and the return value of the `run` and `run_async` methods match that of the decorator:

```python hl_lines="12"
from mirascope.core import BasePrompt, anthropic, openai, prompt_template


@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")

# Running the prompt with OpenAI
print(prompt.run(openai.call(model="gpt-4o-mini")))
# > Sure! If you're looking for a captivating fantasy novel, I recommend...

# Running the prompt with Anthropic
print(prompt.run(anthropic.call(model="claude-3-5-sonnet-20240620")))
# > There are many great fantasy books to choose from, but...
```

This example demonstrates how you can use the same prompt with different LLM providers, allowing for easy comparison and flexibility in your applications.

We will begin covering these decorators in more detail in the [following section](./calls.md).

!!! note "Agnostic Assuming Support"

    While `BasePrompt` is provider-agnostic, some features (like multi-modal inputs) may not be supported by all providers. We try to maximize support across providers, but you should always check the provider's capabilities when using more advanced features.

### Additional Decorators

When you want to run additional decorators on top of the `call` decorator, simply supply the decorators as additional arguments to the run function. They will then be applied in the order in which they are provided. This is most commonly used in conjunction with [tenacity](../integrations/tenacity.md), [custom middleware](../integrations/middleware.md) and other [integrations](../integrations/index.md).

```python hl_lines="2 14-17"
from mirascope.core import BasePrompt, openai, prompt_template
from tenacity import retry, stop_after_attempt, wait_exponential


@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(
    prompt.run(
        openai.call(model="gpt-4o-mini"),
        retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10),
        ),
    ),
)
```

This example demonstrates how to add retry logic to your prompt execution, making your application more resilient to temporary failures.

## Docstring Prompt Templates

While the `@prompt_template` decorator is the recommended way to define prompt templates, Mirascope also supports using class and function docstrings as prompt templates. This feature is disabled by default to prevent unintended use of docstrings as templates. To enable this feature, you need to set the `MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE` environment variable to `"ENABLED"`.

Once enabled, you can use the class or function's docstring as the prompt template:

```python hl_lines="5 9 21"
import os
from mirascope.core import BasePrompt, openai

# Enable docstring prompt templates
os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "ENABLED"


class BookRecommendationPrompt(BasePrompt):
    """Recommend a {genre} book"""

    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a fantasy book


@openai.call(model="gpt-4o-mini")
def recommend_book(genre: str):
    """Recommend a {genre} book"""
    ...


response = recommend_book("mystery")
print(response.content)
# > Here's a recommendation for a fantasy book: ...
```

This feature allows you to use docstrings as prompt templates, which can be useful in certain scenarios where you want to keep the prompt close to the function or class definition.

!!! warning

    Using docstrings as prompt templates can make your code less explicit and harder to maintain. It's generally recommended to use the `@prompt_template` decorator for clarity and separation of concerns. Enable this feature at your own risk.

## Best Practices

To make the most of Mirascope's prompt features, consider the following best practices:

- **Provider Comparison**: Use `BasePrompt` to easily test the same prompt across different providers to compare performance and output quality.
   ```python
   prompt = MyPrompt(...)
   openai_response = prompt.run(openai.call(...))
   anthropic_response = prompt.run(anthropic.call(...))
   ```

- **Prompt Versioning**: Utilize the metadata decorator to keep track of different versions of your prompts as you refine them.
   ```python
   @metadata({"tags": {"version:0002", "purpose:book_recommendation"}})
   class BookRecommendationPromptV2(BasePrompt):
       ...
   ```

- **Dynamic Content**: Leverage `@computed_field` for injecting dynamic content or API calls into your prompts.
   ```python
   class ContextAwarePrompt(BasePrompt):
       @computed_field
       def current_weather(self) -> str:
           return get_weather_api_data()
   ```

- **Cached Properties**: Use `@functools.cached_property` to cache frequently used properties that you only want to compute once.
   ```python
   from functools import cached_property

   class ExpensiveComputationPrompt(BasePrompt):
       @cached_property
       def expensive_data(self) -> str:
           return perform_expensive_computation()
   ```

- **Prompt Libraries**: Build libraries of commonly used prompts that can be easily shared across projects or teams.
   ```python
   # prompts/book_recommendations.py
   class GenreBasedRecommendation(BasePrompt):
       ...

   class AuthorBasedRecommendation(BasePrompt):
       ...

   # In your main code
   from prompts.book_recommendations import GenreBasedRecommendation
   ```

- **Multi-Modal Prompts**: When working with image or audio inputs, use the appropriate format specifiers to seamlessly integrate these into your prompts.
   ```python
   @prompt_template("Describe this image: {image:image}")
   class ImageDescriptionPrompt(BasePrompt):
       image: str  # URL or file path
   ```

- **Error Handling**: Implement robust error handling, especially when working with external data sources or complex computed fields.
   ```python
   @computed_field
   def external_data(self) -> str:
       try:
           return fetch_external_data()
       except ExternalAPIError:
           return "Data unavailable"
   ```

- **Testing**: Create unit tests for your prompts, especially for complex templates or those with computed fields.
   ```python
   def test_book_recommendation_prompt():
       prompt = BookRecommendationPrompt(genre="mystery", age_group="adult")
       assert "mystery book for an adult reader" in str(prompt)
   ```

Mastering `BasePrompt` is the first step towards building robust LLM applications with Mirascope that are flexible, reusable, and provider-agnostic. By following these best practices, you can create more maintainable, efficient, and powerful prompts for your LLM-powered applications.