"""
We’ve made implementing and using tools (function calling) intuitive (Gemini):
"""

from typing import Literal

from google.generativeai import configure  # type: ignore

from mirascope.core import gemini

configure(api_key="YOUR_GEMINI_API_KEY")


def get_current_weather(location: str, unit: Literal["celsius", "fahrenheit"]):
    """Get the current weather in a given location."""
    if "tokyo" in location.lower():
        print(f"It is 10 degrees {unit} in Tokyo, Japan")
    elif "san francisco" in location.lower():
        print(f"It is 72 degrees {unit} in San Francisco, CA")
    elif "paris" in location.lower():
        print(f"It is 22 degress {unit} in Paris, France")
    else:
        print("I'm not sure what the weather is like in {location}")


@gemini.call(model="gemini-1.0-pro", tools=[get_current_weather])
def get_forecast():
    """What's the weather in Tokyo in celsius?"""


forecast = get_forecast()
tool = forecast.tool
if tool:
    tool.call()
    # > It is 10 degrees celsius in Tokyo, Japan
