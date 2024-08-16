# Prompts

Prompts are the foundation of effective communication with Large Language Models (LLMs). Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions. This guide will walk you through the features and best practices for prompt engineering using Mirascope.

## Prompt Templates

??? api "API Documentation"

    [`mirascope.core.base.prompt.prompt_template`](../api/core/base/prompt.md#mirascope.core.base.prompt.prompt_template)

The primary means of writing prompts in Mirascope is through prompt templates, which are just formatted strings (as they should be) with a few additional conveniences. This allows you to define prompts such that they are dynamic and reusable.

For the purposes of explaining how prompt templates work, we will use:

- `@prompt_template`: a decorator for attaching a prompt template to a function or class
- `BasePrompt`: a base class for writing provider-agnostic prompts.

We will cover `BasePrompt` in more detail later. For now, all you need to know is that we inject fields with names that match template variables and that we've implemented the `__str__` method for easily viewing how template variables get injected:

```python
from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a fantasy book
```

For your convenience, we will also automatically dedent and strip the prompt template. This makes writing multi-line prompts a breeze:

```python
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

Since Mirascope prompt templates are just formatted strings, standard specifiers will work as expected:

```python
from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a book cheaper than ${price:.2f}")
class BookRecommendationPrompt(BasePrompt):
    price: float


prompt = BookRecommendationPrompt(price=12.3456)
print(prompt)
# > Recommend a book cheaper than $12.34
```

We also provide additional specifiers we've found useful in our own prompt engineering:

- `list`: formats an input list as a newline-separated string
- `lists`: formats an input list of lists as newline-separated strings separated by double newlines

```python
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

If there are any other such specifiers you would find useful, let us know!

### Message Roles

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

By default, Mirascope treats the entire prompt as a single user message. However, you can use the `SYSTEM`, `USER`, and `ASSISTANT` keywords to specify different message roles, which we will parse into `BaseMessageParam` instances:

```python
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

### `MESSAGES` Keyword

Often you'll want to inject messages (such as previous chat messages) into the prompt. We provide a `MESSAGES` keyword for this injection, which you can add in whatever position and as many times as you'd like:

```python
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

### Inject Accessed Attributes

When the fields of your class or arguments of your function are more complex objects with attributes, you can access and use these attributes directly in the prompt template:

```python
from mirascope.core import openai, prompt_template
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

### Empty Messages

When a template variable is set to `None` it will be injected as the empty string.

If the content of a message is empty, that message will be excluded from the final list of message parameters:

```python
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

```python
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

Some providers (e.g. OpenAI) offer additional options for multi-modal inputs such as image detail. You can specify additional options as though you are initializing the image format spec with keyword arguments for the options:

```python
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

```python
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

```python
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

!!! tip "Retrieving External Data"

    Computed fields can be particularly useful when you want to inject information you retrieve from an external source. For example, perhaps you want to retrieve context from a document store to augment the generation with relevant information (RAG).

### Metadata

??? api "API Documentation"

    [`mirascope.core.base.prompt.metadata`](../api/core/base/prompt.md#mirascope.core.base.prompt.metadata)

You can add metadata to your prompts using the `@metadata` decorator. This will attach a `Metadata` object, which is a simple `TypedDict` with a single typed key `tags: set[str]`.

This can be useful for tracking versions, categories, or any other relevant information.

```python
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

!!! note "Adding Additional Fields"

    Although `Metadata` is a `TypedDict` with only the `tags` key, there is nothing stopping you from adding additional keys. The only issue is that this will throw a type error, which you can ignore. We recommend ignoring the specific error. For example, if you're using pyright you should add `# pyright: ignore [reportArgumentType]`.
    
    If there are particular keys you find yourself using frequently, let us know so we can add them!

### Running Prompts

??? api "API Documentation"

    [`mirascope.core.base.prompt.BasePrompt.run`](../api/core/base/prompt.md#mirascope.core.base.prompt.BasePrompt.run)

    [`mirascope.core.base.prompt.BasePrompt.run_async`](../api/core/base/prompt.md#mirascope.core.base.prompt.BasePrompt.run_async)

One of the key benefits of `BasePrompt` is that it is provider-agnostic. You can use the same prompt with different LLM providers, making it easy to compare performance or switch providers.

You can do this with the `run` and `run_async` methods that run the prompt using the configuration of a call decorator. For now, just know that the decorator is configuring a call to the LLM, and the return value of the `run` and `run_async` methods match that of the decorator:

```python
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

We will begin covering these decorators in more detail in the [following section](./calls.md).

!!! note "Agnostic Assuming Support"

    While `BasePrompt` is provider-agnostic, some features (like multi-modal inputs) may not be supported by all providers. We try to maximize support across providers, but you should always check the provider's capabilities when using more advanced features.

### Additional Decorators

When you want to run additional decorators on top of the `call` decorator, simply supply the decorators as additional arguments to the run function. They will then be applied in the order in which they are provided. This is most commonly used in conjunction with [tenacity](../integrations/tenacity.md), [custom middleware](../integrations/middleware.md) and other [integrations](../integrations/index.md).

```python
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

## Docstring Prompt Templates

While the `@prompt_template` decorator is the recommended way to define prompt templates, Mirascope also supports using class and function docstrings as prompt templates. This feature is disabled by default to prevent unintended use of docstrings as templates. To enable this feature, you need to set the `MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE` environment variable to `"ENABLED"`.

Once enabled, you can use the class or function's docstring as the prompt template:

```python
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

!!! warning

    Using docstrings as prompt templates can make your code less explicit and harder to maintain. It's generally recommended to use the `@prompt_template` decorator for clarity and separation of concerns. Enable this feature at your own risk.

## Best Practices

- Provider Comparison: Use `BasePrompt` to easily test the same prompt across different providers to compare performance and output quality.
- Prompt Versioning: Utilize the metadata decorator to keep track of different versions of your prompts as you refine them.
- Dynamic Content: Leverage `@computed_field` for injecting dynamic content or API calls into your prompts.
- Cached Properties: Use `@functools.cached_property` to cache frequently used properties that you only want to compute once.
- Prompt Libraries: Build libraries of commonly used prompts that can be easily shared across projects or teams.

Mastering `BasePrompt` is the first step towards building robust LLM applications with Mirascope that are flexible, reusable, and provider-agnostic.
