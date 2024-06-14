"""
Streaming tool calls with OpenAIToolStream
"""

import os
from typing import Literal

from mirascope.openai import OpenAICall, OpenAICallParams, OpenAIStream

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
):
    """Get the current weather in a given location."""
    if "tokyo" in location.lower():
        print(f"It is 10 degrees {unit} in Tokyo, Japan")
    elif "san francisco" in location.lower():
        print(f"It is 72 degrees {unit} in San Francisco, CA")
    elif "paris" in location.lower():
        print(f"It is 22 degress {unit} in Paris, France")
    else:
        print("I'm not sure what the weather is like in {location}")


class Forecast(OpenAICall):
    prompt_template = "What's the weather in Tokyo?"

    call_params = OpenAICallParams(tools=[get_current_weather])


stream = OpenAIStream(Forecast().stream())
for chunk, tool in stream:
    if tool:
        tool.fn(**tool.args)
        # > It is 10 degrees fahrenheit in Tokyo, Japan
    else:
        print(chunk.content, end="", flush=True)
