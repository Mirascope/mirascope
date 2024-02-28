"""An example demonstrating how to stream `OpenAITool`s tools asynchronously."""
import asyncio
import os
from typing import Callable, Literal, Type, Union

from pydantic import Field

from mirascope import (
    AsyncOpenAIChat,
    AsyncOpenAIToolStreamParser,
    OpenAICallParams,
    OpenAITool,
    Prompt,
    openai_tool_fn,
)

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> str:
    """Returns the current weather in a given location."""
    return f"{location} is 65 degrees {unit}."


@openai_tool_fn(get_current_weather)
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"


class CurrentWeatherPrompt(Prompt):
    """What's the weather like in San Francisco, Tokyo, and Paris?"""

    call_params: OpenAICallParams = OpenAICallParams(
        model="gpt-3.5-turbo-1106",
        tools=[GetCurrentWeather],  # pass in function itself for automatic conversion
    )


tools: list[Union[Callable, Type[OpenAITool]]] = [GetCurrentWeather]


async def stream_openai_tool():
    chat = AsyncOpenAIChat()
    prompt = CurrentWeatherPrompt()
    stream_completion = chat.stream(prompt)
    parser = AsyncOpenAIToolStreamParser(tools=prompt.call_params.tools)
    async for partial_tool in parser.from_stream(stream_completion):
        print("data: ", partial_tool.__dict__, "\n\n")


asyncio.run(stream_openai_tool())
