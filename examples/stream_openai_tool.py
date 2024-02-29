"""An example demonstrating how to stream `OpenAITool`s tools."""
import os
from typing import Callable, Literal, Type, Union

from pydantic import Field

from mirascope import (
    OpenAICallParams,
    OpenAIChat,
    OpenAITool,
    OpenAIToolStreamParser,
    Prompt,
)

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> str:
    """Returns the current weather in a given location."""
    return f"{location} is 65 degrees {unit}."


class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"


tools: list[Union[Callable, Type[OpenAITool]]] = [GetCurrentWeather]


class CurrentWeatherPrompt(Prompt):
    """What's the weather like in San Francisco, Tokyo, and Paris?"""

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo-1106",
        tools=tools,  # pass in function itself for automatic conversion
    )


chat = OpenAIChat()
prompt = CurrentWeatherPrompt()
stream_completion = chat.stream(prompt)
parser = OpenAIToolStreamParser(tools=tools)
for tool in parser.from_stream(stream_completion):
    print(tool)
