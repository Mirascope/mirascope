# Prompts

When working with LLMs, a surprising amount of work can go into determining the final text which gets passed into the model. Let's take a look at some of the tools Mirascope provides to make formatting your prompts as seamless as possible.

## BasePrompt

`BasePrompt` is a base class which works across all model providers. To create a prompt using `BasePrompt`:

- Define a class which inherits `BasePrompt`
- Set the prompt via the docstring and denote any template variable with curly braces
- Type your template variables (and type them correctly! `BasePrompt` is built on Pydantic's `BaseModel` so incorrect typing will result in a `ValidationError`).

```python
from mirascope.core import BasePrompt

class BookRecommendationPrompt(BasePrompt):
    """Recommend a {genre} book."""
    
    genre: str
```

You can also set the prompt via the `prompt_template` decorator, which allows you to use a standard docstring for your class if you prefer:

```python
from mirascope.core import prompt_template

@prompt_template("Recommend a {genre} book.")
class BookRecommendationPrompt(BasePrompt):
    """Now this is a normal docstring."""
    
    genre: str
```

To call the model with a `BasePrompt`, create an instance of your class and invoke the `run()` method with the appropriate provider’s configuration decorator. The `run()` function will create a decorated function covered in more detail in the next section[link to calls].

For the configuration decorator, you are required to set the `model` argument. You can also set  `stream` for streams[link] `response_model` for extractions[link], and `tools` for function calling/tools[link]. All other functionality is supported in the provider’s native API, and the original parameters can be passed directly as keyword arguments into the decorator.

```python
from mirascope.core import openai, anthropic

prompt = BookRecommendationPrompt(genre="fantasy")

# Sync Call
response = prompt.run(
	openai.call(model="gpt-4o", temperature=1.0) # OpenAI takes a temperature flag
)

# Async Stream
response = prompt.run(
	anthropic.call_async(model="claude-3-5-sonnet-20240620", stream=True)
)
```

`BasePrompt` supports every way to call a model that you would via a function decorator. For a full list of the functionalities, check out the `BasePrompt` section of the API reference[link].

## Message Types

By default, Mirascope treats the prompt template as a single user message. If you want to specify a list of messages, simply use the message keywords (`SYSTEM`, `USER`, `ASSISTANT`). Make sure to capitalize the keyword and follow it with a colon.

```python
class BookRecommendationPrompt(BasePrompt):
  """
  SYSTEM: You are a librarian.
	USER: Recommend a {genre} book.
  """

  genre: str
```

When writing messages that span multiple lines, the message must start on a new line for the tabs to get properly dedented:

```python
class BookRecommendationPrompt(BasePrompt):
    """
    SYSTEM:
    You are the world's greatest librarian.
    When recommending books, also describe the book's writing style and content.
  
	  USER: Recommend a {genre} book.
    """

	  genre: str
```

Note that any additional space between messages will not be included in the final messages array as each message is parsed and formatted individually.

## Keyword: Messages

Mirascope supports a special message keyword `MESSAGES`, which injects a list of messages into the conversation. To use `MESSAGES`, follow up the keyword with solely a template variable. This template variable must be a list of messages with keys that correspond to the provider's API.

```python
from mirascope.core.base import BaseMessageParam

class BookRecommendationPrompt(BasePrompt):
  """
  SYSTEM
  You are the world's greatest librarian.
  When making recommendations, take user preferences into account.

  MESSAGES: {messages}
  USER: Recommend a {genre} book.
  """

  genre: str
  messages: list[BaseMessageParam]
  
messages = [
  {"role": "user", "content": "My favorite books are the Lord of the Rings series."},
  {"role": "assistant", "content": "Ok! I'll recommend books with similar writing styles."}
]

prompt = BookRecommendationPrompt(genre="fantasy", messages=messages)
response = prompt.run(openai.call("gpt-4o"))
print(response.content)
# > Sure! If you liked the Lord of the Rings, you might like ...
```

## `__str__` overload

`BasePrompt`'s `__str__()` is overloaded so that it returns the formatted prompt with template variables.

```python
class BookRecommendationPrompt(BasePrompt):
	"""
	SYSTEM: You are a librarian.
	USER: Recommend a {genre} book.
	"""	
  genre: str

prompt = Librarian(genre="fantasy")
print(prompt)
# > SYSTEM: You are a librarian.
#   USER: Recommend a fantasy book.
```

## `dump()`

The `dump()` method shows you some important information about your prompt: its tags, the formatted prompt, the prompt template, and inputs.

```python
class BookRecommendationPrompt(BasePrompt):
	"""
	SYSTEM: You are a librarian.
	USER: Recommend a {genre} book.
	"""	
  genre: str

prompt = Librarian(genre="fantasy")
print(prompt.dump())
# > {
#     'tags': [],
#     'prompt': 'SYSTEM: You are a librarian.\nUSER: Recommend a fantasy book.',
#     'template': 'SYSTEM: You are a librarian.\nUSER: Recommend a {genre} book.',
#     'inputs': {'genre': 'fantasy'}
#   }
```

## Complex Template Variables

When using `BasePrompt`, you can take advantage of the fact that it inherits Pydantic’s `BaseModel` to define template variables with more complex logic.

The most common instance will be using Pydantic’s `computed_field` to define a variable:

```python
from pydantic import computed_field

class BookRecommendationPrompt(BasePrompt):
	"""Recommend a {genre} {book_type}."""
		
  genre: str
  
  @computed_field
  def book_type(self) -> str:
	  if self.genre in ["science", "history", "math"]:
		  return "textbook"
		return "book"
		
prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a fantasy book.

prompt = BookRecommendationPrompt(genre="science")
print(prompt)
# > Recommend a science textbook.
```

Using a `computed_field` will include the computed field in the dump, which is useful for seeing what affects your prompts.

```python
prompt = BookRecommendationPrompt(genre="science")
print(prompt.dump())
# > {
#     ...
#     'inputs': {'genre': 'fantasy', , 'book_type': 'textbook'}
#   }
```

You should note that this is just one example, and you can use all Pydantic functionalities to improve your prompts. Check out their docs here[link].

## Tags

You may have noticed that the `dump()` method contains the key `tags`. Use the `tags` decorator to tag your prompts, useful for organization when logging your results.

```python
from mirascope.core import tags

@tags(["version:0001"])
class BookRecommendationPrompt(BasePrompt):
    """Recommend a {genre} book."""
		
    genre: str
  
prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt.dump())
# > {
#     'tags': ['version:0001'],
#     ...
#   }
```
