"""
We’ve made implementing and using tools (function calling) intuitive:
"""
from typing import Literal

from mirascope.openai import OpenAICall, OpenAICallParams


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

    call_params = OpenAICallParams(model="gpt-4", tools=[get_current_weather])


tool = Forecast().call().tool
if tool:
    tool.fn(**tool.args)
# > It is 10 degrees fahrenheit in Tokyo, Japan
