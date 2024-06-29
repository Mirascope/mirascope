# Calls

Mirascope lets you succinctly call a model while maintaining flexibility for complex workflows. 

## Decorators

Mirascope’s function decorators offer a more compact way to call a model than with `BasePrompt`. Every provider we support has a corresponding decorator. Here’s how to use them:

- Import the module for the provider you want to use (or the specific decorator)
- Configure the decorator with the settings with which to make the call
- Define a function with a docstring prompt template (or the prompt template decorator)
- Use input arguments as template variables using curly braces for string templating
- Invoke the decorated function to call the provider’s API

```python
from mirascope.core import openai
# Alternatively:
# from mirascope.core.openai import openai_call

@openai.call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book"""

# call OpenAI's chat completion API
response = recommend_book("fantasy") 

# print the string content of the call
print(response.content)
# > Sure! "The Name of the Wind" by Patrick Rothfuss is a book about...
```

You can alternatively use the `prompt_template` decorator to define the prompt template and retain standard docstring functionality if you prefer.

```python
@openai.call("gpt-4o")
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    """This is now a standard docstring."""
```

### Call Parameters

To configure call parameters inside the decorator, you are required to set the `model` argument. You can also set  `stream` for streams[link], `response_model` for extractions[link], and `tools` for function calling/tools[link]. All other functionality is supported in the provider’s native API, and the original parameters can be passed directly as keyword arguments into the decorator.

```python
@openai.call(model="gpt-4o", temperature=0.7)
def recommend_book(genre: str):
    "Recommend a {genre} book."
```

## Call Responses

When you make a Mirascope call, it returns a provider-specific subclass of `BaseCallResponse`. In the snippet above, it’s an `OpenAICallResponse`.

`BaseCallResponse` serves as an abstract interface for Mirascope’s various convenience wrappers which allow you to easily access important properties relevant to your call. In addition, the model-specific subclasses implement these properties via the model’s original API, so you can easily see everything that’s going on under the hood if you wish.

Here are some important convenience wrappers you might use often:

```python
# String content of the call
print(response.content)
# > Certainly! If you're looking for a fantasy book...

# Original response object from provider's API 
print(response.response)
# > ChatCompletion(id='chatcmpl-9ePlrujRgozswiat7nBIAjQN28Ps7', ...

# Most recent user message in message param form
print(response.user_message_param)
# > {'content': 'Recommend a fantasy book.', 'role': 'user'} 

# Provider message in message param form
print(response.message_param)
# > {'content': 'Certainly! ..., `role`: `assistant`, `tool_calls`: None}

# Usage statistics in provider's API
print(response.usage)
# > CompletionUsage(completion_tokens=102, prompt_tokens=12, total_tokens=114)
```

For the full list of convenience wrappers, check out the API reference[link].

## Async

If you want concurrency, make an asynchronous call with `call_async`.

```python
import asyncio
from mirascope.core import openai

@openai.call_async(model="gpt-4o")
async def recommend_book(genre: str):
    """Recommend a {genre} book"""

async def run():
    print(await recommend_book("fantasy"))

asyncio.run(run())
# > Certainly! If you're looking for a fantasy book...
```

## Message Types

Calls support parsing message types and message injections like `BasePrompt` does. For an in depth explanation, check out the Message Types section in Prompts[link].

```python
from openai.types.chat import ChatCompletionMessageParam

@openai.call(model="gpt-4o")
def recommend_book(
	genre: str, messages = list[ChatCompletionMessageParam]
):
    """
    SYSTEM:
    You are a librarian. When making a recommendation, you take into
    account the user's preferences, inferenced from past dialogue.
    
    MESSAGES: {messages}
    
    USER: Recommend a {genre} book.
    """
    
messages = [
  {"role": "user", "content": "My favorite books are the Lord of the Rings series."},
  {"role": "assistant", "content": "Ok! I'll recommend books with similar writing styles."}
]

response = recommend_book(genre="fantasy", messages=messages)
print(response.content)
# > Of course! If you liked the Lord of the Rings, you might like ...
```

## Dynamic Configurations

Mirascope’s function decorators expect to wrap a function that returns a provider specific `BaseDynamicConfig` instance, which is just a `TypedDict` or `None`. The decorator will first call the original function to retrieve the dynamic configuration, which it will use with the highest priority to configure your call. Keys set in the dynamic configuration will take precedence over any matching configuration options in the decorator.

!!! note

This means that you can execute arbitrary code before making the final call. The returned dynamic config is optional, and it can be configured using said arbitrary code. This enables dynamically configure your calls using the arguments of the function.

### Call Parameters

For any call parameters native to your provider’s API other than the model and streaming, you can define them via the key `call_params`:

```python
@openai.call(model="gpt-4o")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    """Recommend a {genre}."""
    temperature = 0.75 if genre == "mystery" else 0.25
    return {"call_params": {"temperature": temperature}}
```

### Computed Fields

To define a template variable that is dependent on the function’s arguments, set it with the key `computed_fields`. The computed field must have a `str()` method:

```python
@openai.call(model="gpt-4o", temperature=0.7)
def recommend_author(genre: str) -> openai.OpenAIDynamicConfig:
  """Recommend an author for {genre}. Just the name."""

@openai.call(model="gpt-4o", temperature=0.7)
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
  """Recommend a {genre} book by {author}."""
  author = recommend_author(genre)
  return {"computed_fields": {"author": author}}
```

Computed fields become included in the response’s serialization with `model_dump()`, which is useful for colocating metadata when chaining calls[link].

### Custom Messages

If you want to define messages via the provider’s original API (or need access to features not yet supported by our prompt template parser), set the `messages` key with your custom messages. Note that this turns the docstring into a normal docstring and the function will ignore any prompt template or `computed_fields`.

```python
@openai.call(model="gpt-4o")
def recommend_book(genre: str):
    """Now just a normal docstring."""
    messages = [
        {"role": "system", "content": "You are a librarian."},
        {"role": "user", "content": f"Recommend a {genre} book."},
    ]
    return {"messages": messages]  
    
response = recommend_book("fantasy")
print(response.content)
# > Certainly! If you're looking for a fantasy book...
```

### Tools

You can also configure tools dynamically, which we cover in the tools section[link].

## Output Parsers

To run custom output parsers, set the argument `output_parser` in the decorator to a function that handles the response:

```python
@openai.call("gpt-4o", output_parser=str)  # runs `str(response)`
def recommend_book(genre: str):
    """Recommend a {genre} book."""
    
recommendation = recommend_book("fantasy")
assert isinstance(recommendation, str)
print(recommendation)
# > Certainly! If you're looking for a great fantasy book...
```

## Instance Methods as Calls

Instance methods can also be decorated and used as calls. The class’s attributes accessed via `self` will be parsed and incorporated into the prompt.

```python
from typing import Literal

from mirascope.core import openai
from pydantic import BaseModel

class BookCalls(BaseModel):
    user_reading_level: Literal["beginner", "intermediate", "advanced"]

    @openai.call("gpt-4o")
    def recommend_book(self, genre: str):
        """Recommend a {genre} book.

        Reading level: {self.user_reading_level}
        """

beginner_book_calls = BookCalls(user_reading_level="beginner")
response = beginner_book_calls.recommend_book("fantasy")
print(response.content)
```

With prompts dependent on state, you can easily build agents[link].
