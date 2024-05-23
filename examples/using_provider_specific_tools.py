"""
We automatically convert functions into their proper tool; however, there are often
functions that are not well documents that we would still like to use as tools. In these
cases we can define a model provider specific tool, such as `OpenAITool` or `GeminiTool`
for use with that specific model provider. This example uses `OpenAITool`, but you can
just as easily use `GeminiTool` with no additional change.
"""

from typing import Literal

from pydantic import Field

from mirascope.base import tool_fn
from mirascope.openai import OpenAICall, OpenAICallParams, OpenAITool


def get_current_weather(location, unit):
    if "tokyo" in location.lower():
        print(f"It is 10 degrees {unit} in Tokyo, Japan")
    elif "san francisco" in location.lower():
        print(f"It is 72 degrees {unit} in San Francisco, CA")
    elif "paris" in location.lower():
        print(f"It is 22 degress {unit} in Paris, France")
    else:
        print("I'm not sure what the weather is like in {location}")


@tool_fn(get_current_weather)
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(
        ..., description="The location in City, State or City, Country format."
    )
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"


class Forecast(OpenAICall):
    prompt_template = "What's the weather like in Tokyo, San Francisco, and Paris?"

    call_params = OpenAICallParams(tools=[GetCurrentWeather])


if tools := Forecast().call().tools:
    for tool in tools:
        tool.fn(**tool.args)
# > It is 10 degrees celsius in Tokyo, Japan
# > It is 72 degrees fahrenheit in San Francisco, CA
# > It is 22 degrees celsius in Paris, France
