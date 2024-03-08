# Defining tools (function calls)

Tools are extremely useful when you want the model to intelligently choose to output the arguments to call one or more functions. With Mirascope it is extremely easy to use tools.

## Using tools in Mirascope

Mirascope will automatically convert any function properly documented with a docstring into a tool. This means that you can use any such function as a tool with no additional work. Create a function call, this one is taken from [OpenAI documentation](https://platform.openai.com/docs/guides/function-calling) with Google style python docstrings:

```python
import json

from typing import Literal


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
```

You can also define your own `OpenAITool` class. This is necessary when the function you want to use as a tool does not have a docstring. Additionally, the `OpenAITool` class makes it easy to further update the descriptions, which is useful when you want to further engineer your prompt:

```python
from typing import Literal

from pydantic import Field

from mirascope import tool_fn
from mirascope.openai import OpenAITool


def get_current_weather(location, unit="fahrenheit"):
		# Assume this function does not have a docstring
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


@tool_fn(get_current_weather)
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
```

Using the [tool_fn](../api/base/tools.md#mirascope.base.tools.tool_fn) decorator will attach the function defined by the tool to the tool for easier calling of the function. This happens automatically when using the function directly.

## Tools with OpenAI API only

Using the same OpenAI docs, the function call is defined as such:

```python
import json


def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})
```

OpenAI uses JSON Schema to define the tool call:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]
```

You can quickly see how bloated OpenAI tools become when defining multiple tools:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
]
```

With Mirascope, it will look like this:

```python
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"


class GetNDayWeatherForecast(GetCurrentWeather):
    """Get an N-day weather forecast"""

    num_days: int = Field(..., description="The number of days to forecast")
```

We can take advantage of class inheritance and reduce repetition. 

## Other Providers

If you are using a function property documented with a docstring, **you do not need to make any code changes** when using other providers. Mirascope will automatically convert these functions to their proper format for you under the hood.

For classes, simply replace `OpenAITool` with your provider of choice e.g. `GeminiTool` to match your choice of prompt.
