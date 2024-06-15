# Tools (Function Calling)

Large Language Models (LLMs) are incredibly powerful at generating human-like text, but their capabilities extend far beyond mere text generation. With the help of tools (often called function calling), LLMs can perform a wide range of tasks, from mathematical calculations to code execution and information retrieval.

## What are Tools?

Tools, in the context of LLMs, are essentially functions or APIs that the model can call upon to perform specific tasks. These tools can range from simple arithmetic operations to complex web APIs or custom-built functions. By leveraging tools, LLMs can augment their capabilities and provide more accurate and useful outputs.

## Why are Tools Important?

Traditionally, LLMs have been limited to generating text based solely on their training data and the provided prompt. While this approach can produce impressive results, it also has inherent limitations. Tools allow LLMs to break free from these constraints by accessing external data sources, performing calculations, and executing code, among other capabilities.

Incorporating tools into LLM workflows opens up a wide range of possibilities, including:

1. **Improved Accuracy**: By leveraging external data sources and APIs, LLMs can provide more accurate and up-to-date information, reducing the risk of hallucinations or factual errors.
2. **Enhanced Capabilities**: Tools allow LLMs to perform tasks that would be challenging or impossible with text generation alone, such as mathematical computations, code execution, and data manipulation.
3. **Contextualized Responses**: By incorporating external data and contextual information, LLMs can provide more relevant and personalized responses, tailored to the user's specific needs and context.

## Defining and Using Tools in Mirascope

Mirascope provides a clean and intuitive way to incorporate tools into your LLM workflows. The simplest form-factor we offer is to extract a single tool automatically generated from a function with a docstring. We can then call that function with the extracted arguments. This means that you can use any such function as a tool with no additional work. The function below is taken from [OpenAI documentation](https://platform.openai.com/docs/guides/function-calling) with Google style python docstrings:

!!! note

    We support Google, ReST, Numpydoc, and Epydoc style docstrings.

```python
from mirascope.openai import OpenAICall, OpenAICallParams


def get_weather(location: str) -> str:
    """Get's the weather for `location` and prints it.

    Args:
        location: The "City, State" or "City, Country" for which to get the weather.
    """
    if location == "Tokyo, Japan":
        return f"The weather in {location} is 72 degrees and sunny."
    elif location == "San Francisco, CA":
        return f"The weather in {location} is 45 degrees and cloudy."
    else:
        return f"I'm sorry, I don't have the weather for {location}."


class Forecast(OpenAICall):
    prompt_template = "What's the weather in Tokyo?"

    call_params = OpenAICallParams(tools=[get_weather])


response = Forecast().call()
weather_tool = response.tool
print(weather_tool.fn(**weather_tool.args))
#> The weather in Tokyo, Japan is 72 degrees and sunny.
```

!!! note

    While it may not be clear from the above example, `tool.fn` is an extremely powerful simplification. When using multiple tools, having the function attached to the tool makes it immediately accessible and callable with a single line of code.

You can also define your own `OpenAITool` class. This is necessary when the function you want to use as a tool cannot be modified (e.g. another library) and does not have a docstring. Additionally, the `OpenAITool` class makes it easy to further update the descriptions, which is useful when you want to further engineer your prompt:

```python
from mirascope.base import tool_fn
from mirascope.openai import OpenAICall, OpenAICallParams, OpenAITool
from pydantic import Field


def get_weather(location: str) -> str:
    # Assume this function does not have a docstring
    if location == "Tokyo, Japan":
        return f"The weather in {location} is 72 degrees and sunny."
    elif location == "San Francisco, CA":
        return f"The weather in {location} is 45 degrees and cloudy."
    else:
        return f"I'm sorry, I don't have the weather for {location}."


@tool_fn(get_weather)
class GetWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(
        ...,
        description="The 'City, State' or 'City, Country' for which to get the weather.",
    )


class Forecast(OpenAICall):
    prompt_template = "What's the weather in Tokyo?"

    call_params = OpenAICallParams(tools=[GetWeather])


response = Forecast().call()
weather_tool = response.tool
print(weather_tool.fn(**weather_tool.args))
#> The weather in Tokyo, Japan is 72 degrees and sunny.
```

Using the [tool_fn](../api/base/tools.md#mirascope.base.tools.tool_fn) decorator will attach the function defined by the tool to the tool for easier calling of the function. This happens automatically when using the function directly as mentioned above.

## Adding Examples To Your Tool Definitions

Mirascope makes it easy to add examples to tool definitions, which can help the model better understand how you want it to call the tool. You can add examples both for individual fields as well as for the entire tool.

```python
class FormatBook(OpenAITool):
    """Returns the title and author of a book nicely formatted."""

    title: str = Field(..., examples=["The Name of the Wind"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "The Name of the Wind", "author": "Rothfuss, Patrick"}
            ]
        }
    )

    def call(self) -> str:
        return f"{self.title} by {self.author}"
```

## Inserting Tools Back Into The Chat Messages

Often you will want to reinsert the tool call into the messages for a future call so that the LLM can respond given the actual output of the tool call. This is necessary for agentic behavior.

We are currently working on improving this flow with additional convenience, but for now you can do the following:

```python
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


# Make the first call to the LLM
forecast = Forecast(question="What's the weather in Tokyo Japan?")
response = forecast.call()
if response.user_message_param:
    forecast.history.append(response.user_message_param)
forecast.history.append(response.message_param)

tool = response.tool
if tool:
    print("Tool arguments:", tool.args)
    # > {'location': 'Tokyo, Japan', 'unit': 'fahrenheit'}
    output = tool.fn(**tool.args)
    print("Tool output:", output)
    # > It is 10 degrees fahrenheit in Tokyo, Japan

    # reinsert the tool call into the chat messages through history
    forecast.history += response.tool_message_params([(tool, output)])
    # Set no question so there isn't a user message
    forecast.question = ""
else:
    print(response.content)  # if no tool, print the content of the response

# Call the LLM again with the history including the tool call
response = forecast.call()
print("After Tools Response:", response.content)
```

!!! note

    For providers that support streaming tools (e.g. OpenAI), their respective stream classes (e.g. `OpenAIStream`) also have a `tool_message_params` function with the same signature as that of the response class.

## Using Tools with Supported Providers

If you are using a function property documented with a docstring, **you do not need to make any code changes** when using other [supported providers](./supported_llm_providers.md). Mirascope will automatically convert these functions to their proper format for you under the hood.

For classes, simply replace `OpenAITool` with your provider of choice e.g. `GeminiTool` to match your choice of call.

## What tools look like without Mirascope (OpenAI API only)

Using the same OpenAI docs, the function call is defined as such:

```python
def get_weather(location: str) -> str:
    if location == "Tokyo, Japan":
        return f"The weather in {location} is 72 degrees and sunny."
    elif location == "San Francisco, CA":
        return f"The weather in {location} is 45 degrees and cloudy."
    else:
        return f"I'm sorry, I don't have the weather for {location}."
```

OpenAI uses JSON Schema to define the tool call:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The 'City, State' or 'City, Country' for which to get the weather.",
                    },
                },
                "required": ["location"],
            },
        },
    }
]
```

You can quickly see how bloated OpenAI tools become when defining multiple tools:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The 'City, State' or 'City, Country' for which to get the weather.",
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The 'City, State' or 'City, Country' for which to get the weather.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    },
                },
                "required": ["location", "num_days"],
            },
        },
    },
]
```

With Mirascope, we can take advantage of class inheritance to reduce repetition:

```python
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(
        ...,
        description="The 'City, State' or 'City, Country' for which to get the weather.",
    )


class GetNDayWeatherForecast(GetCurrentWeather):
    """Get an N-day weather forecast"""

    num_days: int = Field(..., description="The number of days to forecast")
```

