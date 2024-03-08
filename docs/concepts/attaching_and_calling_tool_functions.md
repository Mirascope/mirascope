# Attaching tool functions to Mirascope Prompts

## Using Mirascope OpenAI Tool

Create your prompt and pass in your `OpenAITool`:

```python
from typing import Literal

from pydantic import Field

from mirascope import tool_fn
from mirascope.openai import OpenAIPrompt, OpenAITool

@tool_fn(get_current_weather)
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"

class CurrentWeather(OpenAIPrompt):
    """What's the weather like in San Francisco, Tokyo, and Paris?"""

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo-1106", tools=[GetCurrentWeather]
    )
```

The tools are attached to the `call_params` attribute in a Mirascope Prompt. For more information check out Learn why colocation is so important and how combining it with the [Mirascope CLI](using_the_mirascope_cli.md) makes engineering better prompts easy.

## Using a function properly documented with a docstring

Create your prompt and pass in your function:

```python
import json

from typing import Literal

from mirascope.openai import OpenAIPrompt


def get_current_weather(
		location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> str:
	"""Get the current weather in a given location.

	Args:
		location: The city and state, e.g. San Francisco, CA.
		unit: The unit for the temperature.
	
	Returns:
		A JSON object containing the location, temperature, and unit.
	"""
	if "tokyo" in location.lower():
		return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
	elif "san francisco" in location.lower():
		return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
	elif "paris" in location.lower():
		return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
	else:
		return json.dumps({"location": location, "temperature": "unknown"})


class CurrentWeather(OpenAIPrompt):
    """What's the weather like in San Francisco, Tokyo, and Paris?"""

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo-1106", tools=[get_current_weather]
    )
```

## Calling Tools

Generate content by calling the `create` method:

```python
# using same code as above
current_weather = CurrentWeather()
completion = current_weather.create()
if tools := completion.tools:
    for tool in tools:
        print(tool.fn(**tool.args))

#> {"location": "San Francisco", "temperature": "72", "unit": "celsius"}
#> {"location": "Tokyo", "temperature": "10", "unit": "celsius"}
#> {"location": "Paris", "temperature": "22", "unit": "celsius"}
```

The `completion.tools` property returns an actual instance of the tool.

## Streaming Tools

We also support streaming of tools using our `OpenAIToolStreamParser` class. Simply replace `create` with `stream` and call `from_stream`, like so:

```python
from mirascope.openai import OpenAIToolStreamParser

# using same code as above
current_weather = CurrentWeather()
completion = current_weather.stream()
parser = OpenAIToolStreamParser(tools=current_weather.call_params.tools)  # pass in the same tools
for tool in parser.from_stream(completion):
    print(tool.fn(**tool.args))

#> {"location": "San Francisco", "temperature": "72", "unit": "celsius"}
#> {"location": "Tokyo", "temperature": "10", "unit": "celsius"}
#> {"location": "Paris", "temperature": "22", "unit": "celsius"}
```

Note, this will stream complete tools, not partial tools.

## Async

All of the examples above also work with `async` by replacing `create` with `async_create` or `stream` with `async_stream` .

If streaming, you will also need to replace `OpenAIToolStreamParser` with `AsyncOpenAIToolStreamParser` and change the `Generator` to an `AsyncGenerator`

```python
from mirascope.openai import AsyncOpenAIToolStreamParser

completion = current_weather.async_stream()
parser = AsyncOpenAIToolStreamParser(tools=current_weather.call_params.tools)
async for tool in parser.from_stream(completion):
    print(tool.fn(**tool.args))
```
