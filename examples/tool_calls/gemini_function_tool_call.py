"""
We’ve made implementing and using tools (function calling) intuitive:
"""

import os
from typing import Literal

from dotenv import load_dotenv
from google.generativeai import configure  # type: ignore

from mirascope.core import gemini

load_dotenv()

configure(api_key=os.getenv("GEMINI_API_KEY"))


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


@gemini.call(model="gpt-4o", tools=[get_current_weather])
def forecast():
    """What's the weather in Tokyo?"""


tool = forecast().tool
if tool:
    tool.call()
    # > It is 10 degrees celsius in Tokyo, Japan
