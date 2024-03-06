"""An example demonstrating how to use functions as tools."""
import os
from typing import Literal

from mirascope.openai import OpenAICallParams, OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


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


class CurrentWeatherPrompt(OpenAIPrompt):
    """What's the weather like in San Francisco, Tokyo, and Paris?"""

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo-1106", tools=[get_current_weather]
    )


completion = CurrentWeatherPrompt().create()

if tools := completion.tools:
    for tool in tools:
        if tool.fn:
            print(tool.fn(**tool.model_dump(exclude={"tool_call"})))
        else:
            print("No function found.")
