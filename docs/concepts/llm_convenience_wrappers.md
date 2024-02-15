# LLM Convenience Wrappers

Mirascope provides convenience wrappers around the OpenAI client to make writing the code even more enjoyable. We purposefully pass `**kwargs` through our calls so that you always have direct access to their arguments.

## Why should you care?

- Easy to learn
    - There's no magic here -- it's just python
    - Chaining is no different from writing basic python functions
- Convenient
    - You could do it yourself -- and you still can -- but there's just something nice about calling `str(res)` to get the response content
    - You only need to pass in a [`Prompt`](../api/prompts.md) and we'll handle the rest

## OpenAIChat

### Create

You can initialize an [`OpenAIChat`](../api/chat/models/openai_chat.md#mirascope.chat.models.OpenAIChat) instance and call [`create`](../api/chat/models/openai_chat.md#mirascope.chat.models.OpenAIChat.create) to generate an [`OpenAIChatCompletion`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletion):

```python
from mirascope import OpenAIChat, Prompt

class RecipePrompt(Prompt):
	"""
	Recommend recipes that use {ingredient} as an ingredient
	"""

	ingredient: str

chat = OpenAIChat(api_key="YOUR_OPENAI_API_KEY")
completion = chat.create(RecipePrompt(ingredient="apples"))
print(completion)  # prints the string content of the completion
```

You can also pass a `str` in directly as your prompt if you'd prefer to use your own prompt tooling:

```python
from mirascope import OpenAIChat

chat = OpenAIChat(api_key="YOUR_OPENAI_API_KEY")
completion = chat.create("Recommend recipes that use apples.")
print(completion)
```

#### Completion

The `create` method returns an [`OpenAIChatCompletion`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletion) class instance, which is a simple wrapper around the [`ChatCompletion`](https://platform.openai.com/docs/api-reference/chat/object) class in `openai`. In fact, you can access everything from the original chunk as desired. The primary purpose of the class is to provide convenience.

```python
from mirascope.chat.types import OpenAIChatCompletion

completion = OpenAIChatCompletion(...)

completion.completion  # ChatCompletion(...)
str(completion)        # original.choices[0].delta.content
completion.choices     # original.choices
completion.choice      # original.choices[0]
completion.message     # original.choices[0].message
completion.content     # original.choices[0].message.content
completion.tool_calls  # original.choices[0].message.tool_calls
```

### Chaining

Adding a chain of calls is as simple as writing a function:

```python
from mirascope import OpenAIChat, Prompt

class ChefPrompt(Prompt):
    """
    Name the best chef in the world at cooking {food_type} food
    """

    food_type: str


class RecipePrompt(Prompt):
    """
    Recommend a recipe that uses {ingredient} as an ingredient
    that chef {chef} would serve in their restuarant
    """

    ingredient: str
    chef: str


def recipe_by_chef_using(ingredient: str, food_type: str) -> str:
    """Returns a recipe using `ingredient`.

    The recipe will be generated based on what dish using `ingredient`
    the best chef in the world at cooking `food_type` might serve in
    their restaurant
    """
    chat = OpenAIChat(api_key="YOUR_OPENAI_API_KEY")
    chef_prompt = ChefPrompt(food_type=food_type)
    chef = str(chat.create(chef_prompt))
    recipe_prompt = RecipePrompt(ingredient=ingredient, chef=chef)
    return str(chat.create(recipe_prompt))


recipe = recipe_by_chef_using("apples", "japanese")
```

### Streaming

You can use the [`stream`](../api/chat/models/openai_chat.md#mirascope.chat.models.OpenAIChat.stream) method to stream a response. All this is doing is setting `stream=True` and providing the [`OpenAIChatCompletionChunk`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletionChunk) convenience wrappers around the response chunks.

```python
chat = OpenAIChat()
stream = chat.stream(prompt)
for chunk in stream:
	print(str(chunk), end="")
```

#### OpenAIChatCompletionChunk

The `stream` method returns an [`OpenAIChatCompletionChunk`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletionChunk) instance, which is a convenience wrapper around the [`ChatCompletionChunk`](https://platform.openai.com/docs/api-reference/chat/streaming) class in `openai`

```python
from mirascope.chat.types import OpenAIChatCompletionChunk

chunk = OpenAIChatCompletionChunk(...)

chunk.chunk    # ChatCompletionChunk(...)
str(chunk)     # original.choices[0].delta.content
chunk.choices  # original.choices
chunk.choice   # original.choices[0]
chunk.delta    # original.choices[0].delta
chunk.content  # original.choices[0].delta.content
```

### Extraction

Often you want to extract structured information into a format like JSON. The [`extract`](../api/chat/models/openai_chat.md#mirascope.chat.models.OpenAIChat.extract) method makes this extremely easy by extracting the information into a Pydantic `BaseModel` schema that you define:

```python
from mirascope import OpenAIChat
from pydantic import BaseModel

class BookInfo(BaseModel):
    """Information about a book."""

    title: str
    author: str

book_info = chat.extract(BookInfo, "The Name of the Wind is by Patrick Rothfuss.")
assert isinstance(book_info, BookInfo)
assert book_info.model_dump() == {
    "title": "The Name of the Wind",
    "author": "Patrick Rothfuss",
}
```

#### Retries

Often you will want to retry your query in the event of a `ValidationError` when `extract` fails to convert the model response into the Pydantic model you've provided. Set the number of retries and `extract` will automatically retry up to that many times (by default `retries` is `0`):

```python
book_info = chat.extract(
    BookInfo,
    "The Name of the Wind is by Patrick Rothfuss.",
    retries=5,  # this will result in 6 total creation attempts if it never succeeds
)
```

### Tools

Tools are extremely useful when you want the model to intelligently choose to output the arguments to call one or more functions. With mirascope it is extremely easy to use tools. Any function properly documented with a docstring will be automatically converted into a tool. This means that you can use any such function as a tool with no additional work:

```python
from typing import Literal

from mirascope import OpenAIChat, Prompt

class CurrentWeatherPrompt(Prompt):
    """What's the weather like in Los Angeles?"""

def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> str:
    """Get the current weather in a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA.
        unit: The unit for the temperature.

    Returns:
        A JSON string containing the location, temperature, and unit.
    """
    return f"{location} is 65 degrees {unit}."

chat = OpenAIChat(model="gpt-3.5-turbo-1106")
completion = chat.create(
    CurrentWeatherPrompt(),
    tools=[get_current_weather],  # pass in the function itself
)

for tool in completion.tools or []:
    print(tool)                      # this is a `GetCurrentWeather` instance
    print(tool.fn(**tool.__dict__))  # this will call `get_current_weather`
```

This works by automatically converting the given function into an [`OpenAITool`](../api/chat/tools.md#mirascope.chat.tools.OpenAITool) class. The `completion.tools` property then returns an actual instance of the tool.

You can also define your own `OpenAITool` class. This is necessary when the function you want to use as a tool does not have a docstring. Additionally, the `OpenAITool` class makes it easy to further update the descriptions, which is useful when you want to further engineer your prompt:

```python
from typing import Literal

from mirascope import OpenAIChat, OpenAITool, Prompt, openai_tool_fn
from pydantic import Field

class CurrentWeatherPrompt(Prompt):
    """What's the weather like in Los Angeles?"""

def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> str:
    """Get the current weather in a given location."""
    return f"{location} is 65 degrees {unit}."

@openai_tool_fn(get_current_weather)
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"

chat = OpenAIChat(model="gpt-3.5-turbo-1106")
completion = chat.create(
    CurrentWeatherPrompt(),
    tools=[GetCurrentWeather],  # pass in the tool class
)

for tool in completion.tools or []:
    print(tool)                      # this is a `GetCurrentWeather` instance
    print(tool.fn(**tool.__dict__))  # this will call `get_current_weather`
```

Notice that using the [`openai_tool_fn`](../api/chat/tools.md#mirascope.chat.tools.openai_tool_fn) decorator will attach the function defined by the tool to the tool for easier calling of the function. This happens automatically when using the function directly.

However, attaching the function is not necessary. In fact, often there are times where the intention of using a tool is not to call a function but to extract information from text. In these cases there is no need to attach the function at all. Simply define the `OpenAITool` class without the attached function and access the extracted information through the arguments of the `completion.tools` instances:

```python
from typing import Literal

from mirascope import OpenAIChat, OpenAITool, Prompt
from pydantic import Field

class CurrentWeatherPrompt(Prompt):
    """What's the weather like in Los Angeles?"""

class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"

chat = OpenAIChat(model="gpt-3.5-turbo-1106")
completion = chat.create(
    CurrentWeatherPrompt(),
    tools=[GetCurrentWeather],  # pass in the tool class
)

for tool in completion.tools or []:
    print(tool)                      # this is a `GetCurrentWeather` instance
```
### Streaming Tools

We also support streaming of tools using our `OpenAIToolStreamParser` class. Simply replace the `chat.create` with `chat.stream` and call `from_stream`, like so:

```python
from typing import Callable, Literal, Type, Union

from mirascope import OpenAIChat, OpenAITool, OpenAIToolStreamParser, Prompt

# Using same OpenAITool and Prompt defined in Tool example

tools: list[Union[Callable, Type[OpenAITool]]] = [GetCurrentWeather]
completion = chat.stream(
    CurrentWeatherPrompt(),
    tools=tools,  # pass in the tool class
)

parser = OpenAIToolStreamParser(tools=tools) # pass in the same tool class
for tool in parser.from_stream(completion):
    print(tool)
```

### Async

All of the examples above also work with `async` by updating the import from `OpenAIChat` to `AsyncOpenAIChat`.

## Future updates

There is a lot more to be added to the Mirascope models. Here is a list in no order of things we are thinking about adding next: 

* data extraction streaming - extract information from text into a Partial Pydantic model
* additional models - support models beyond OpenAI, particularly OSS models

If you want some of these features implemented or if you think something is useful but not on this list, let us know!
