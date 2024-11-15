---
title: A Guide to Function Calling in OpenAI
description: >
  OpenAI function calling extends the capabilities of large language models by providing them with tools for calling external APIs and applications.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-07-12
slug: openai-function-calling
---

# A Guide to Function Calling in OpenAI

In OpenAI function calling (or _tools_ as it’s now known), you send descriptions of functions to the LLM in order for it to format these as structured outputs in valid JSON format—which is aligned to a particular schema. You then use these outputs in your calls to an application’s function, or to an API endpoint.

What makes these structured outputs useful is they can be a part of an automated workflow that integrates multiple systems and services.

**With tools, LLMs become agents with greater scope to act on your behalf, autonomously choosing which functions or external services to use** , for example, use cases like generating calls for the application to search on Bing or book a flight as part of a travel chatbot.

<!-- more -->

In addition, tools:

- Enable the AI model to delegate tasks to a specific function by getting it to focus on understanding and generating requests for other parts of the system to execute.
  ‍
- Make it easy to add new capabilities by just defining new functions, without having to modify the core logic of the language model itself.
  ‍
- Improve your application’s overall functionality and interoperability, also with frameworks like LangChain.

But function calling as a term is often misunderstood: many believe the model is actually executing the function call, when in fact it’s only providing the parameters.

As for OpenAI’s tool capabilities, some have found these to be overly verbose and complex for what they deliver (i.e., formatting of outputs). Plus hand coding function descriptions in JSON isn’t fun.

That’s why we’ve designed [Mirascope](https://github.com/mirascope/mirascope), our own toolkit for building LLM applications, to make function calling as pain free as possible. For instance, we generate these function definitions for you based on your application’s functions in Python.

In this article, we explain how OpenAI tools work, and provide examples of this. We also describe how Mirascope implements these. Finally, we highlight the major differences between the two libraries when it comes to function calling.

## How OpenAI Function Calling Works

The `tools` parameter of OpenAI’s [Chat Completion API](https://platform.openai.com/docs/guides/text-generation/chat-completions-api) is an array that defines a list of tools (functions) that the model may call if and when it needs to. You define a function by specifying its list of parameters: `name`, `description`, and `parameters`.

```python
"tools": [
    {
        "type": "function",
        "function": {
            "name": "get_current_stock_price",
            "description": "Get the current stock price",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the company, eg. Apple Inc.",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["USD", "EUR", "JPY"],
                    },
                    "required": ["company", "currency"],
                },
            },
        },
    }
]
```

The `tools` array takes multiple functions that you define. The more detailed your `description` above is in terms of the situations in which it can and should call the function, the better. Note, however, that function descriptions are part of the [prompt](https://mirascope.com/blog/langchain-prompt-template) and so consume tokens all the same.

The `parameters` field above describe the parameters your function takes and must conform to the [JSON specification](https://json-schema.org/understanding-json-schema).

After specifying your function call signature(s), you send the prompt to the LLM (using your `openai_api_key`) for the function(s) to be part of its context window and for the model to decide the appropriate function a future response should refer to.

If and when the natural language model wants you to call a function you’ve provided, it returns a JSON object similar to this:

```python
{
    "index": 0,
    "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
            {
                "name": "get_current_stock_price",
                "arguments": '{\n  "company": "Apple Inc.",\n  "format": "USD"\n}',
            }
        ],
    },
    "finish_reason": "tool_calls",
}
```

`tool_calls` above contains the name of the function and its arguments. If the LLM in this example had called no function, then the value of this field would be `null` and `content` would rather contain the model’s response. (Each tool call has a `tool_call_id`.)

Your application should parse this response to use as part of its actual call to the function.

By default, `tool_choice=auto` which means the model decides which function to select from a choice of functions. You can, however, [change this](https://platform.openai.com/docs/api-reference/chat/create#chat-create-tool_choice) by setting `tool_choice` to the following:

- `none` to not call any tool
- `auto` to let the model decide for itself which function to call
- `required` to require the LLM to use a tool, but if you provide more than one tool it can choose between which tool to call
- `{"type": "function", "function": {"name": "my_function"}}` to require a specific tool (even if you have more than one tool definition in the call)

You then include this response when you call the actual function. After the function responds, you send its response together with the system message history back to the LLM for the final response, as shown below:

![Functions > Application > API > LLM diagram](../../assets/blog/openai-function-calling/function_calling_diagram.png)

## How Mirascope Function Calling Works

Mirascope generates the OpenAI function description in JSON for you, so you can continue to use the Python you normally use.

Rather than getting your hands dirty with manual coding in JSON, Mirascope extracts function descriptions in two ways:

### Define Tools from Docstrings

One way is to extract function descriptions from docstrings: this lets you use any function as a tool without additional effort.

For example, we designate `tools=[get_current_stock_price]` below in the `openai.call` decorator. You then execute the function by calling the tool's `call` method, which calls the original function with the arguments provided by the LLM.

```python
from mirascope.core import openai, prompt_template


def get_current_stock_price(company: str) -> str:
    """Get the current stock price for `company` and prints it.

    Args:
        company: The name of the company, e.g., Apple Inc.
    """
    if company == "Apple, Inc.":
        return f"The current stock price of {company} is $200."
    elif company == "Google LLC":
        return f"The current stock price of {company} is $180."
    else:
        return f"I'm sorry, I don't have the stock price for {company}."


@openai.call("gpt-4o-mini", tools=[get_current_stock_price])
@prompt_template("What's the stock price of {company}")
def stock_price(company: str): ...


response = stock_price("Apple, Inc.")
if tool := response.tool:
    print(tool.call())
# > The current stock price of Apple Inc. is $200.
```

### Using the BaseTool Class

If your function doesn’t have a docstring or can’t be modified for some reason (like if it’s third-party code) you can alternatively use Mirascope’s `BaseTool` class and call the original function in the tools `call` method, which makes it more easily callable. You can also write the function you want to call directly in the `call` method for colocation.

```python
from mirascope.core import BaseTool, openai, prompt_template
from pydantic import Field


def get_current_stock_price(company: str) -> str:
    # Assume this function does not have a docstring
    if company == "Apple, Inc.":
        return f"The current stock price of {company} is $200."
    elif company == "Google LLC":
        return f"The current stock price of {company} is $180."
    else:
        return f"I'm sorry, I don't have the stock price for {company}."


class GetCurrentStockPrice(BaseTool):
    """Get the current stock price for a given company."""

    company: str = Field(
        ...,
        description="The name of the company, e.g., Apple Inc.",
    )

    def call(self):
        return get_current_stock_price(self.company)


@openai.call("gpt-4o", tools=[GetCurrentStockPrice])
@prompt_template("What's the stock price of {company}")
def stock_price(company: str): ...


response = stock_price("Apple, Inc.")
if tool := response.tool:
    print(tool.call())
# > The current stock price of Apple, Inc. is $200.
```

**Note:** Both the functional and `BaseTool` definitions of tools work across all providers that Mirascope supports, making it easy to test your tool usage with other providers such as Anthropic's Claude, Google's Gemini, and more.

### Provide Examples for Tool Definitions

Large language models often provide better outputs when you use examples, and Mirascope lets you add these to your tool definitions. In the code below, we add examples directly in the `title` and `author` fields in `FormatMovie`, as well as for the JSON schema:

```python
from mirascope.core import BaseTool
from pydantic import ConfigDict, Field


class FormatMovie(BaseTool):
    """Returns the title and director of a movie nicely formatted."""

    title: str = Field(..., examples=["Inception"])
    director: str = Field(..., examples=["Nolan, Christopher"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Inception", "director": "Nolan, Christopher"}
            ]
        }
    )

    def call(self) -> str:
        return f"{self.title} directed by {self.director}"
```

### Reinsert Function Calls Back into Messages

To retain context and allow the model to continue the conversation with knowledge of previous interactions, you can reinsert the tool call into chat messages, using the call’s result as the basis for further responses and allowing it to handle multi-step tasks and complex queries.

Below, the result of the first tool call is reinserted into the chat using the `response.tool_message_params` convenience method, ensuring that the context of the tool's output is preserved for future interactions.

```python
from typing import Literal

from openai.types.chat import ChatCompletionMessageParam

from mirascope.core import openai, prompt_template


def get_current_stock_price(company: str, format: Literal["USD", "EUR", "JPY"] = "USD"):
    """Get the current stock price of a company."""
    if "apple" in company.lower():
        return f"The current stock price of {company} is 200 {format}"
    elif "microsoft" in company.lower():
        return f"The current stock price of {company} is 250 {format}"
    elif "google" in company.lower():
        return f"The current stock price of {company} is 2800 {format}"
    else:
        return f"I'm not sure what the stock price of {company} is."


@openai.call("gpt-4o-mini", tools=[get_current_stock_price])
@prompt_template(
    """
    MESSAGES: {history}
    USER: {question}
    """
)
def check_stock_price(question: str, history: list[ChatCompletionMessageParam]): ...


# Make the first call to the LLM
history = []
response = check_stock_price("What's the stock price of Apple Inc?", history)
if response.user_message_param:
    history.append(response.user_message_param)
history.append(response.message_param)

if tool := response.tool:
    print("Tool arguments:", tool.model_dump())
    # > {'company': 'Apple Inc', 'format': 'USD'}
    output = tool.call()
    print("Tool output:", output)
    # > The current stock price of Apple Inc is 200 USD

    # Reinsert the tool call into the chat messages through history
    history += response.tool_message_params([(tool, output)])
else:
    print(response.content)  # if no tool, print the content of the response

# Make an API call to the LLM again with the history including the tool call and no new user message
response = check_stock_price("", history)
print("After Tools Response:", response.content)
```

### Use Other Model Providers—Not Just OpenAI

As long as your functions are documented with docstrings, you can work with [other providers](https://mirascope.com/learn/calls) without needing to make many code changes, as Mirascope reformats the code in the background.

As well, you can define tools in Mirascope using `BaseTool`, which works across all providers by default so you don’t have to change anything when switching providers.

## Function Calling with Mirascope vs OpenAI

As you’ve already seen, Mirascope offers conveniences when working with function calls, and the main advantage is that you can let our library write the JSON for you rather than code this yourself.

Looking at our earlier example, here’s how Mirascope would define a function call:

```python
def get_current_stock_price(company: str) -> str:
    # Assume this function does not have a docstring
    if company == "Apple Inc.":
        return f"The current stock price of {company} is $200."
    elif company == "Google LLC":
        return f"The current stock price of {company} is $180."
    else:
        return f"I'm sorry, I don't have the stock price for {company}."
```

Whereas with the OpenAI API, you’d need to hand code this definition in JSON:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_stock_price",
            "description": "Get the current stock price of a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the company, e.g., 'Apple Inc.' or 'Google LLC'",
                    },
                },
                "required": ["company"],
            },
        },
    }
]
```

When we define multiple definitions at the same time, our code starts getting verbose:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_stock_price",
            "description": "Get the current stock price of a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the company, e.g., 'Apple Inc.' or 'Google LLC'",
                    },
                },
                "required": ["company"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price_in_currency",
            "description": "Get the current stock price of a company in a specific currency",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the company, e.g., 'Apple Inc.' or 'Google LLC'",
                    },
                    "currency": {
                        "type": "string",
                        "description": "The currency to get the stock price in, e.g., 'USD', 'EUR', 'JPY'",
                    },
                },
                "required": ["company", "currency"],
            },
        },
    }
]
```

Whereas generating the function definitions above is more cleanly done with class inheritance:

```python
class GetCurrentStockPrice(BaseTool):
    """Get the current stock price of a company."""

    company: str = Field(
        ...,
        description="The name of the company, e.g., 'Apple Inc.' or 'Google LLC'"
    )

class GetStockPriceInCurrency(BaseTool):
    """Get the current stock price of a company in a specific currency"""

    currency: Literal["USD", "EUR", "JPY"] = Field(
        ...,
        description="The currency to get the stock price in, e.g., 'USD', 'EUR', 'JPY'"
    )
```

Mirascope lets you write the schema in a pythonic way that’s easier to write and read compared with coding the JSON yourself. Under the hood, the underlying JSON is reliably generated using [Pydantic](https://docs.pydantic.dev/). Our prompt classes also extend Pydantic’s `BaseModel` class, saving you from having to write your own error-checking boilerplate.

Generating tool definitions as part of function calling (or even parallel function calling) is thus rolled up into your [prompt engineering workflow](https://mirascope.com/blog/prompt-engineering-best-practices), allowing you to focus on building your application rather than painstakingly formatting tool definitions so they conform to the JSON specification.

## Simplify Function Calling with Mirascope’s Advanced Tools

Mirascope offers other advantages as well: it’s a lightweight, extensible toolkit that takes a building block over a framework approach to [LLM prompting](https://mirascope.com/blog/engineers-should-handle-prompting-llms), letting you write clean code thanks to best practices like colocation, built-in Pydantic type safety, and full editor support. Our toolkit was designed with software developer best practices in mind so you can focus on getting the most out of OpenAI models like GPT-4 or external APIs rather than on chasing errors due to overly complex abstractions.

Want to learn more? You can find more Mirascope code samples, docs, and a tutorial on both our [documentation site](https://mirascope.com) and on [GitHub](https://github.com/mirascope/mirascope/).
