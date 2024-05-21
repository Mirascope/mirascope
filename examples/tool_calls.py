from typing import Literal

from openai.types.chat import ChatCompletionMessageParam

from mirascope.openai import OpenAICall, OpenAICallParams


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
    call_params = OpenAICallParams(model="gpt-4-turbo", tools=[get_current_weather])


# do the first call to get assistant to call the tool
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

    # this should just be `tool.message_param` or something, need to implement
    forecast.history += [
        {
            "role": "tool",
            "content": output,
            "tool_call_id": tool.tool_call.id,
            "name": tool.__class__.__name__,
        },  # type: ignore
    ]

# do the second call to get assistant response
forecast.question = "Is that cold or hot?"
response = forecast.call()
print("After Tools Response:", response.content)
