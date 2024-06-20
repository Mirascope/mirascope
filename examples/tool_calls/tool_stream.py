"""Streaming tool calls with @openai_stream"""

import os
from typing import Literal

from mirascope.core.openai import openai_stream

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


@openai_stream(model="gpt-4o", tools=[get_current_weather])
def forecast(location: str):
    """What's the weather in {location}"""


for chunk, tool in forecast(location="Tokyo?"):
    if tool:
        tool.call()
        # > It is 10 degrees fahrenheit in Tokyo, Japan
    else:
        print(chunk.content, end="", flush=True)
