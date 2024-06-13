"""
This example shows how to use Mirascope to call tools and append the tool call to history.
"""
import os
from typing import Literal

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
):
    """Get the current weather in a given location."""
    if "tokyo" in location.lower():
        return f"It is 10 degrees {unit} in Tokyo, Japan"
    elif "san francisco" in location.lower():
        return f"It is 72 degrees {unit} in San Francisco, CA"
    elif "paris" in location.lower():
        return f"It is 22 degress {unit} in Paris, France"
    else:
        return f"I'm not sure what the weather is like in {location}"


class Forecast(OpenAICall):
    prompt_template = """
    MESSAGES: {history}
    USER: {question}
    """

    question: str
    history: list[ChatCompletionMessageParam] = []
    call_params = OpenAICallParams(tools=[get_current_weather])


# Make the first call to the LLM
forecast = Forecast(question="What's the weather in Tokyo Japan?")
response = forecast.call()
forecast.history += [
    {"role": "user", "content": forecast.question},
    response.message.model_dump(),  # type: ignore
]

tool = response.tool
if tool:
    print("Tool arguments:", tool.args)
    # > {'location': 'Tokyo, Japan', 'unit': 'fahrenheit'}
    output = tool.fn(**tool.args)
    print("Tool output:", output)
    # > It is 10 degrees fahrenheit in Tokyo, Japan

    # reinsert the tool call into the chat messages through history
    # NOTE: this should be more convenient, e.g. `tool.message_param`
    forecast.history += [
        {
            "role": "tool",
            "content": output,
            "tool_call_id": tool.tool_call.id,
            "name": tool.__class__.__name__,
        },  # type: ignore
    ]
    # Set no question so there isn't a user message
    forecast.question = ""
else:
    print(response.content)  # if no tool, print the content of the response

# Call the LLM again with the history including the tool call
response = forecast.call()
print("After Tools Response:", response.content)
