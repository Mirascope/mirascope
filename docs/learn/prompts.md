# Prompts

Prompts are the foundation of effective communication with Large Language Models (LLMs). Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions. This guide will walk you through the features and best practices for prompt engineering using Mirascope.

## What Are "Prompts"

When working with Large Language Model (LLMs) APIs, the "prompt" is generally a list of messages where each message has a particular role. First, let's take a look at a call to the OpenAI API for reference:

```python hl_lines="8"
from openai import OpenAI

client = OpenAI()

def recommend_book(genre: str) -> str | None:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"recommend a {genre} book"}]
    )
    return completion.choices[0].message.content
```

Here, the prompt is the messages array with a single user message. You can also specify multiple messages with different roles. For example, we can provide what is called a "system prompt" by first including a message with the system role:

```python hl_lines="8-11"
from openai import OpenAI

client = OpenAI()

def recommend_book(genre: str) -> str | None:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a librarian"},
            {"role": "user", "content": f"recommend a {genre} book"},
        ]
    )
    return completion.choices[0].message.content
```

In these examples, we're only showing how to use the OpenAI API. One of the core values of Mirascope is that we offer tooling to make your prompts more reusable and work across the various different LLM providers.

Let's take a look at how we can write these same prompts in a provider-agnostic way.

!!! note "Calls Will Come Later"

    For the following explanations we will be talking *only* about the messages aspect and will discuss calling the API later in the [Calls](./calls.md) documentation, which will show how to use these provider-agnostic prompts to actually call a provider's API.

## Messages

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

The core concept to understand here is [`BaseMessageParam`](../api/core/base/message_param.md#basemessageparam). This class operates as the base class for message parameters that Mirascope can handle and use across all supported providers.

Let's look at a basic example:

```python hl_lines="5"
from mirascope.core import BaseMessageParam

def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(role="user", content=f"recommend a {genre} book")
    ]
```

In this example:

1. The `recommend_book_prompt` method's signature defines the prompt's template variables.
2. We define and return a list with a single `BaseMessageParam` with role `user`.

As before, we can also define additional messages with different roles:

```python hl_lines="5-6"
from mirascope.core import BaseMessageParam

def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(role="system", content="You are a librarian"),
        BaseMessageParam(role="user", content=f"Recommend a {genre} book"),
    ]
```

And that's it! Prompts written in this functional way are provider-agnostic, reusable, and properly typed, making them easier to write and maintain.

The `BaseMessageParam` class currently supports the `system`, `user`, `assistant`, and `tool` roles.

### Message Writing Convenience

We understand that writing the full `BaseMessageParam` class can often feel like a lot of unnecessary boilerplate, and we strive to reduce the amount of boilerplate code you need to write as much as possible.

To this end, we've implemented shorthand methods of writing messages to make writing them simpler. All you need to do is add the `@prompt_template` decorator to your method to access these shorthand forms.

#### Single User Message

When writing a single message with the `user` role, you can simply return the string content of the message:

```python hl_lines="5 8"
from mirascope.core import Messages, prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> Messages.Type:
    return f"Recommend a {genre} book"

print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

In this example:

1. We decorate our method with the `@prompt_template` decorator
2. We specify the `Messages.Type` return type that the decorator expects
3. We return the single user message as a formatted string
4. Calling the method automatically converts the output into the corresponding `BaseMessageParam` with role `user` and content equal to the returned string.

#### Single User Message With Multiple Parts

Many providers also support writing messages with multiple content parts. For such providers, you can return a list containing each content part:

```python hl_lines="5 11"
from mirascope.core import Messages, prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> Messages.Type:
    return ["Hi!", f"Recommend a {genre} book"]

print(recommend_book_prompt("fantasy"))
# Output: [
#   BaseMessageParam(
#       role='user',
#       content=[{"type": "text", "text": "Hi!"}, {"type": "text", "text": 'Recommend a fantasy book'}],
#   )
# ]
```

!!! warning "Not All Providers Support Multiple Parts"

    Only certain providers support writing messages where the content can be written as multiple parts. To our knowledge, this includes OpenAI, Anthropic, Gemini, Groq, and any other provider that hosts models from those providers. Using multiple content parts with any other provider will not work.

    If there are any providers that support multiple parts that we've missed, let us know so we can support them!

#### Multiple Messages With Roles

The prompt templates in the above examples results in a single user message. To use the same shorthand with other message roles, you can use the `Messages.{Role}` class, which accepts the same shorthand as described above for writing content:

```python hl_lines="6-7 12-13"
from mirascope.core import Messages, prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> Messages.Type:
    return [
        Messages.System("You are a librarian"),
        Messages.User(f"Recommend a {genre} book"),
    ]

print(recommend_book_prompt("fantasy"))
# Output: [
#   BaseMessageParam(role='system', content='You are a librarian'),
#   BaseMessageParam(role='user', content='Recommend a fantasy book'),
# ]
```

### Multi-Modal Inputs

Recent advancements in Large Language Model architecture has enabled many model providers to support multi-modal inputs (text, images, audio, etc.) for a single endpoint. The `BaseMessageParam` class supports these types:

```python hl_lines="9-16"
from mirascope.core import BaseMessageParam
from mirascope.core.base import ImagePart, TextPart

def recommend_book_prompt(previous_book_jpeg: bytes) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="I just read this book:"),
                ImagePart(
                    type="image",
                    media_type="image/jpeg",
                    image=previous_book_jpeg,
                    detail=None,
                ),
                TextPart(type="text", text="What should I read next?"),
            ],
        )
    ]
```

!!! warning "Not All Providers Support Multi-Modal Inputs"

    Unfortunately, not all providers support multi-modal inputs. To our knowledge, only OpenAI, Anthropic, Gemini, and Groq support multimodal LLMs. If there are any providers that we've missed, let us know so we can add support!

We recognize that writing these message parameters directly contains a lot of boilerplate code, so we've implemented similar convenience here for passing multi-modal types in more directly and succinctly:

```python hl_lines="6-8"
from mirascope.core import Messages, prompt_template
from PIL import Image

def recommend_book_prompt(previous_book: Image.Image) -> Messages.Type:
    return [
        "I just read this book:",
        previous_book,
        "What should I read next?",
    ]
```

!!! tip "Multi-Modal Works With All Shorthands"

    You can also use this shorthand when using the shorthand methods for writing messages with specific roles (e.g. `Messages.User`)

!!! info "Shorthand Audio Support Coming Soon"

    We are working on providing similar convenience for handling audio inputs. If this is of particular interest to you, let us know and we can work to prioritize it!

### Writing Messages With Dynamic Configuration

Certain features in Mirascope offer dynamic configuration, which we cover in more detail in each applicable section. However, it's worth noting here that using dynamic configuration also relies on the return value of your prompt method and thus changes how to return your messages.

When using dynamic configuration, you just need to include your messages as part of the dynamic config through the `messages` key:

```python hl_lines="6-8"
from mirascope.core import BaseDynamicConfig, BaseMessageParam, prompt_template

@prompt_template()
def recommend_book_prompt(genre: str) -> BaseDynamicConfig:
    return {
        "messages": [
            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
        ],
    }
```

!!! tip "Using Shorthand"

    Even when using dynamic configuration you can still use the shorthand method of writing messages as described above (e.g. `Messages.User`)

## Prompt Templates

??? api "API Documentation"

    [`mirascope.core.base.prompt.prompt_template`](../api/core/base/prompt.md#mirascope.core.base.prompt.prompt_template)

For even more convenience and readability, Mirascope offers full support for writing prompts as templates. These prompt templates are just formatted strings (as they should be) but with added functionality designed specifically for LLM interactions.

This allows you to define and write prompts in a more readable way while ensuring prompts remain dynamic, reusable, and properly typed.

Let's look at a basic example:

```python hl_lines="3 7"
from mirascope.core import prompt_template

@prompt_template("Recommend a {genre} book")
def book_recommendation_prompt(genre: str): ...

print(book_recommendation_prompt("fantasy"))
# > [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

In this example:

1. The `@prompt_template` decorator defines the template string.
2. The `{genre}` placeholder in the template is replaced with the argument passed to the function.
3. The resulting prompt is a list containing a single `BaseMessageParam` object with the role `user` and the content `"Recommend a fantasy book"`.

### Format Specifiers

Since Mirascope prompt templates are just formatted strings, standard Python format specifiers work as expected:

```python hl_lines="1 5"
@prompt_template("Recommend a book cheaper than ${price:.2f}")
def book_recommendation_prompt(price: float): ...

print(book_recommendation_prompt(12.3456))
# > [BaseMessageParam(role='user', content='Recommend a book cheaper than $12.34')]
```

In this example, we use the `.2f` format specifier to limit the price to two decimal places.

We also provide additional specifiers we've found useful in our own prompt engineering:

- `list`: formats an input list as a newline-separated string
- `lists`: formats an input list of lists as newline-separated strings separated by double newlines

Here's an example demonstrating these custom specifiers:

```python hl_lines="4 7 13-17 21-23 26-30"
@prompt_template(
    """
    Recommend a book from one of the following genres:
    {genres:list}

    Examples:
    {examples:lists}
    """
)
def book_recommendation_prompt(genres: list[str], examples: list[tuple[str, str]]): ...

prompt = book_recommendation_prompt(
    genres=["fantasy", "scifi", "mystery"],
    examples=[
        ("Title: The Name of the Wind", "Author: Patrick Rothfuss"),
        ("Title: Mistborn: The Final Empire", "Author: Brandon Sanderson"),
    ]
)
print(prompt[0].content)
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

### Specifying Message Roles

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

By default, Mirascope treats the entire prompt template as a single user message. However, you can use the `SYSTEM`, `USER`, and `ASSISTANT` keywords to specify different message roles, which we will parse into `BaseMessageParam` instances:

```python hl_lines="3 4 11 12"
@prompt_template(
    """
    SYSTEM: You are the world's greatest librarian
    USER: Recommend a {genre} book
    """
)
def book_recommendation_prompt(genre: str): ...

print(book_recommendation_prompt("fantasy"))
# > [
#     BaseMessageParam(role='system', content="You are the world's greatest librarian"),
#     BaseMessageParam(role='user', content='Recommend a fantasy book')
#   ]
```

This example demonstrates how to use different roles (`SYSTEM` and `USER`) within a single prompt template.

!!! note "Order Of Operations"

    When parsing prompt templates, we first parse each message parameter and then format the content of each parameter individually. We have implemented this specifically to prevent injecting new message parameters through a template variable.

When writing multi-line prompts with message roles, start the prompt on the following line to ensure proper dedenting:

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

This ensures that the content for each role is properly formatted and aligned without unintended indentation.

### `MESSAGES` Keyword

Often you'll want to inject messages (such as previous chat messages) into the prompt. We provide a `MESSAGES` keyword for this injection, which you can add in whatever position and as many times as you'd like:

```python hl_lines="6 13-19 25-26"
from mirascope.core import BaseMessageParam, prompt_template

@prompt_template(
    """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {history}
    USER: {query}
    """
)
def book_recommendation_prompt(history: list[BaseMessageParam], query: str): ...

prompt = book_recommendation_prompt(
    history=[
        BaseMessageParam(role="user", content="What should I read next?"),
        BaseMessageParam(
            role="assistant",
            content="I recommend 'The Name of the Wind' by Patrick Rothfuss",
        ),
    ],
    query="Anything similar you would recommend?",
)
print(prompt)
# > [
#     BaseMessageParam(role='system', content="You are the world's greatest librarian."),
#     BaseMessageParam(role='user', content='What should I read next?'),
#     BaseMessageParam(role='assistant', content="I recommend 'The Name of the Wind' by Patrick Rothfuss"),
#     BaseMessageParam(role='user', content='Anything similar you would recommend?')
#   ]
```

### Multi-Modal Templates

To inject multimodal inputs into your prompt template, simply tag the input with the multimodal type:

- `image` / `images`: injects a (list of) image(s) into the message parameter
- `audio` / `audios`: injects a (list of) audio file(s) into the message parameter

For inputs in prompt templates tagged as multi-modal, we handle URLs, local filepaths, and raw bytes.

We find that this method of templating multi-modal inputs enables writing prompts in a far more natural, readable format:

```python hl_lines="1 10-17"
@prompt_template("I just read this book: {book:image}. What should I read next?")
def book_recommendation_prompt(book: str | bytes): ...

url = "https://upload.wikimedia.org/wikipedia/en/5/56/TheNameoftheWind_cover.jpg"
prompt = book_recommendation_prompt(book=url)
print(prompt)
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

```python hl_lines="1 13"
@prompt_template("I just read this book: {book:image(detail=high)}. What should I read next?")
def book_recommendation_prompt(book: str | bytes): ...

url = "https://upload.wikimedia.org/wikipedia/en/5/56/TheNameoftheWind_cover.jpg"
prompt = book_recommendation_prompt(book=url)
print(prompt)
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

### Computed Fields

When writing messages directly, it's easy to inject variables that are generated dynamically based on the original input arguments to your prompt method. When using prompt templates, computed fields allow you to similarly inject dynamically generated variables.

Here is an example:

```python hl_lines="10 13"
from mirascope.core import BaseDynamicConfig, prompt_template

@prompt_template("Recommend a {reading_level} {genre} book")
def recommend_book(genre: str, age: int) -> BaseDynamicConfig:
    reading_level = "adult"
    if age < 12:
        reading_level = "elementary"
    elif age < 18:
        reading_level = "young adult"
    return {"computed_fields": {"reading_level": reading_level}}

print(recommend_book_prompt("fantasy", 15))
# Output: [BaseMessageParam(role='user', content='Recommend a young adult fantasy book')]
```

In this example, the `reading_level` template variable is computed dynamically based on the `age` input, allowing for dynamic customization of the prompt.

## Best Practices

To make the most of Mirascope's prompt features, consider the following best practices:

- **Prompt Libraries**: Build libraries of commonly used prompts that can be easily shared across projects or teams.

   ```python
   # prompts/book_recommendations.py
   @prompt_template("Recommend a {genre} book by {author}")
   def book_recommendation_prompt(genre: str, author: str): ...

   # In your main code
   from prompts.book_recommendations import book_recommendation_prompt
   ```

- **Testing Your Prompts**: Create unit tests for your prompts to ensure they generate the expected output.

   ```python
   def test_book_recommendation_prompt():
       prompt = book_recommendation_prompt("mystery")
       assert "Recommend a mystery book" in prompt[0].content
   ```

By mastering prompts in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend taking a look at the [Calls](./calls.md) documentation, which shows you how to use your prompt templates to actually call LLM APIs and generate a response.
