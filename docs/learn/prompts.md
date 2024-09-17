# Prompts

Prompts are the foundation of effective communication with Large Language Models (LLMs). Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions. This guide will walk you through the features and best practices for prompt engineering using Mirascope.

## Prompt Templates

??? api "API Documentation"

    [`mirascope.core.base.prompt.prompt_template`](../api/core/base/prompt.md#mirascope.core.base.prompt.prompt_template)

The primary means of writing prompts in Mirascope is through prompt templates, which are just formatted strings (as they should be) with a few additional conveniences. This allows you to define prompts such that they are dynamic and reusable.

Prompt templates in Mirascope work similarly to f-strings in Python, but with added functionality specifically designed for LLM interactions. The `@prompt_template` decorator automatically injects variables from your class or function into the template.

If you prefer to write prompts using formatted strings directly instead of prompt templates, see the [Messages](#messages) section below.

Let's look at a basic example:

```python hl_lines="3 6"
from mirascope.core import prompt_template

@prompt_template("Recommend a {genre} book")
def book_recommendation_prompt(genre: str): ...

print(book_recommendation_prompt("fantasy"))
# > [BaseMessageParam(role='user', content='Recommend a fantasy book')]
```

In this example:
1. The `@prompt_template` decorator defines the template string.
2. The `{genre}` placeholder in the template is replaced with the argument passed to the function.
3. The resulting prompt is a list containing a single `BaseMessageParam` object with the role 'user' and the content "Recommend a fantasy book".

This structure allows LLMs to understand the context and role of each part of the prompt, enabling more sophisticated interactions.

### Format Specifiers

Since Mirascope prompt templates are just formatted strings, standard Python format specifiers work as expected:

```python hl_lines="1 4"
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

```python hl_lines="4 7 13-17"
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

### Message Roles

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

By default, Mirascope treats the entire prompt as a single user message. However, you can use the `SYSTEM`, `USER`, and `ASSISTANT` keywords to specify different message roles, which we will parse into `BaseMessageParam` instances:

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

This example demonstrates how to use different roles (SYSTEM and USER) within a single prompt template.

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

```python hl_lines="6 13-19"
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

### Multi-Modal Inputs

Recent advancements in Large Language Model architecture has enabled many model providers to support multi-modal inputs (text, images, audio, etc.) for a single endpoint. For all multi-modal inputs, we handle URLs, local filepaths, and raw bytes.

To inject multimodal inputs into your prompt template, simply tag the input with the multimodal type:

- `image` / `images`: injects a (list of) image(s) into the message parameter
- `audio` / `audios`: injects a (list of) audio file(s) into the message parameter

We find that this method of templating multi-modal inputs enables writing prompts in a far more natural, readable format:

```python hl_lines="1"
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

```python hl_lines="1"
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

Computed fields allow you to dynamically generate or modify template variables used in your prompt. Here's an example:

```python
from mirascope.core import openai, prompt_template

@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book with a reading level of {reading_level}")
def recommend_book(genre: str, age: int) -> openai.OpenAIDynamicConfig:
    reading_level = "adult"
    if age < 12:
        reading_level = "elementary"
    elif age < 18:
        reading_level = "young adult"
    return {"computed_fields": {"reading_level": reading_level}}

response = recommend_book("fantasy", 15)
print(response.content)
```

In this example, the `reading_level` is computed based on the `age` input, allowing for dynamic customization of the prompt.

## Messages

Mirascope allows you to write prompts using formatted strings directly, providing flexibility in how you structure your prompts. When combined with the `@prompt_template()` decorator, you can leverage both the convenience of direct string formatting and the power of Mirascope's prompt template system.

Here are various ways to use `Messages` with `@prompt_template()`:

### String Return Type

```python
from mirascope.core import Messages, prompt_template

@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    return f"recommend a {genre} book"

print(recommend_book("fantasy"))
# > [BaseMessageParam(role='user', content='recommend a fantasy book')]
```

### List of Strings Return Type

```python
from mirascope.core import Messages, prompt_template

@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    return ["hello!", f"recommend a {genre} book"]

print(recommend_book("fantasy"))
# > [BaseMessageParam(role='user', content=[TextPart(type='text', text='hello!'), TextPart(type='text', text='recommend a fantasy book')])]
```

### List of Role-Specific Messages

```python
from mirascope.core import Messages, prompt_template

@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    return [Messages.System("You are a librarian"), Messages.User(f"recommend a {genre} book")]

print(recommend_book("fantasy"))
# > [BaseMessageParam(role='system', content='You are a librarian'), BaseMessageParam(role='user', content='recommend a fantasy book')]
```

### Using BaseMessageParam Directly

```python
from mirascope.core import Messages, BaseMessageParam, prompt_template

@prompt_template()
def recommend_book(genre: str) -> Messages.Type:
    # You can wrap in a list or return directly - both are valid
    return BaseMessageParam(role='user', content=["hello!", f"recommend a {genre} book"])

print(recommend_book("fantasy"))
# > [BaseMessageParam(role='user', content=[TextPart(type='text', text='hello!'), TextPart(type='text', text='recommend a fantasy book')])]
```

### Multi-Modal Input

```python
from mirascope.core import Messages, prompt_template
from PIL import Image

@prompt_template()
def recommend_book(previous_book: Image.Image) -> Messages.Type:
    return ["I just read this book:", previous_book, "What should I read next?"]
    # Alternatively:
    # return BaseMessageParam(role='user', content=["I just read this book:", previous_book, "What should I read next?"])

# Usage (assuming you have an image loaded)
image = Image.open("book_cover.jpg")
print(recommend_book(image))
# > [BaseMessageParam(role='user', content=[TextPart(type='text', text='I just read this book:'), ImagePart(...), TextPart(type='text', text='What should I read next?')])]
```

These examples demonstrate how to use the `Messages` type in Mirascope with the `@prompt_template()` decorator. This combination allows for flexible prompt writing while still taking advantage of Mirascope's prompt template system. You can mix and match these approaches based on your specific needs, creating prompts that are both natural to write and powerful in their capabilities.

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

For more advanced features, see the respective sections in our documentation:

- [Calls](./calls.md)
- [Response Models](./response_models.md)

By mastering prompts in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.