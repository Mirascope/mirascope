# Attaching tool functions to Mirascope Calls

## Using Mirascope OpenAI Tool

Create your call and pass in your `OpenAITool`:

```python
from typing import Literal

from pydantic import Field

from mirascope import tool_fn
from mirascope.openai import OpenAICall, OpenAITool

@tool_fn(get_current_weather)
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"

class TodaysForecast(OpenAICall):
    prompt_template = "What's the weather like in San Francisco, Tokyo, and Paris?"

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo-1106", tools=[GetCurrentWeather]
    )
```

The tools are attached to the `call_params` attribute in a Mirascope Call. For more information check out Learn why colocation is so important and how combining it with the [Mirascope CLI](using_the_mirascope_cli.md) makes engineering better prompts and calls easy.

## Using a function properly documented with a docstring

Create your call and pass in your function:

```python
import json

from typing import Literal

from mirascope.openai import OpenAICall


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


class TodaysForecast(OpenAICall):
    prompt_template = "What's the weather like in San Francisco, Tokyo, and Paris?"

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo-1106", tools=[get_current_weather]
    )
```

## Calling Tools

Generate content by calling the `call` method:

```python
# using same code as above
forecast = TodaysForecast()
response = forecast.call()
if tools := response.tools:
    for tool in tools:
        print(tool.fn(**tool.args))

#> {"location": "San Francisco", "temperature": "72", "unit": "celsius"}
#> {"location": "Tokyo", "temperature": "10", "unit": "celsius"}
#> {"location": "Paris", "temperature": "22", "unit": "celsius"}
```

The `response.tools` property returns an actual instance of the tool.

## Async

All of the examples above also work with `async` by replacing `call` with `call_async` or `stream` with `stream_async`.
