# Why Use Mirascope?

## The Problem with Existing LLM Tools

When building applications with Large Language Models (LLMs), developers often face a common set of challenges:

- **Overly Complex Abstractions**: Many LLM libraries introduce layers of abstraction that, while well-intentioned, often obscure the underlying API calls and make it difficult to understand what's really happening under the hood.
- **Lack of Flexibility**: As projects grow and requirements evolve, developers frequently find themselves fighting against the constraints of their chosen framework, spending more time trying to work around limitations than building their actual application.
- **Poor Developer Experience**: Inadequate type hinting, unclear documentation, and magical behaviors lead to frustrating debugging sessions and reduced productivity.
- **Lock-in**: Some frameworks are so opinionated that they make it challenging to integrate with other tools or migrate away if needed.
- **Rapid Evolution**: The field of AI and LLMs is advancing at breakneck speed. Rigid, all-encompassing frameworks often struggle to keep pace with new developments and model capabilities.

## Mirascope's Solution

Mirascope addresses these pain points with a philosophy centered on transparency, modularity, and developer experience. Here's why Mirascope stands out:

- **Low-Level Abstractions with Maximum Control**: Mirascope provides convenient abstractions for common tasks without hiding the underlying mechanics. This approach gives you the best of both worlds: productivity gains where it matters, and the ability to drop down to lower levels of abstraction when needed.
- **Uncompromising Transparency**:
    - **Clear Documentation**: Our documentation is always up-to-date, drawn directly from the source code.
    - **No Magic**: Every convenience we offer has a clear, documented alternative for manual implementation.
- **Modular Design**: Mirascope is designed to work seamlessly with other tools in the AI ecosystem. It's not an all-or-nothing framework, but a set of powerful, flexible building blocks that you can use as much of or as little of as you need.
- **Provider-Agnostic Approach**: While Mirascope supports multiple LLM providers out of the box, it also makes it easy to implement custom providers. This flexibility ensures you're never locked into a single ecosystem.
- **Emphasis on Colocation**: Mirascope encourages keeping all the factors that impact your LLM calls in one place. This design principle makes it easier to reason about, iterate on, and maintain your LLM-powered features.
- **Focus On Developer Experience**:
    - **Excellent Editor Support**: Benefit from detailed autocomplete suggestions and inline documentation.
    - **Type Safety**: Catch errors before runtime with our comprehensive type annotations.
    - **Intuitive API**: Our API is designed to be predictable and easy to learn, following Python best practices.

## Comparison with Official SDKs

Mirascope offers advantages over official SDKs like OpenAI's, particularly in terms of simplicity and developer experience. Let's compare the two:

1. **Simplified Syntax**:

Mirascope's approach streamlines the process using decorators, making it more concise and easier to manage. This is particularly evident in handling complex scenarios like streaming, tools, and agents.

Basic Usage:

OpenAI's official SDK:

```python
from openai import OpenAI

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello world"}
    ]
)
print(completion.choices[0].message.content)
```

Mirascope:

```python
from mirascope.core import openai, prompt_template

@openai.call("gpt-3.5-turbo")
@prompt_template("Hello world")
def hello_world():
   ...

response = hello_world()
print(response.content)
```

Streaming Example:

OpenAI's official SDK:

```python
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': 'Count to 5.'}
    ],
    temperature=0,
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

Mirascope:

```python
@openai.call("gpt-3.5-turbo", stream=True)
@prompt_template("Count to 5.")
def count_to_five():
   ...

for chunk, _ in count_to_five():
    print(chunk.content, end="", flush=True)
```

Tools Example:

OpenAI's official SDK:

```python
import json

def get_current_weather(location, unit="fahrenheit"):
    # Mock weather data
    weather_info = f"The current weather in {location} is 72°F."
    return weather_info

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)
if tool_call := response.choices[0].message.tool_calls[0]:
    function_arguments = json.loads(tool_call.function.arguments)
    print(get_current_weather(**function_arguments))
else:
    print(response.choices[0].message.content)
```

Mirascope:

```python
from mirascope.core import BaseTool

class WeatherTool(BaseTool):
    location: str
    unit: str = "fahrenheit"

    def call(self) -> str:
        return f"The current weather in {self.location} is 72°F."

@openai.call("gpt-3.5-turbo", tools=[WeatherTool])
@prompt_template("What's the weather like in {location}?")
def get_weather(location: str): ...

response = get_weather("Boston")
if tool := response.tool:
    print(tool.call())
else:
    print(response.content)
```

As you can see, Mirascope significantly reduces the amount of boilerplate code, making your LLM interactions more concise and easier to understand at a glance.

2. **Prompt Management**:

Mirascope's `@prompt_template` decorator provides a clean way to manage prompts separately from logic. Official SDKs often mix prompts with API calls.

OpenAI's official SDK:

```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Translate the following English text to French: '{text}'"}
    ]
)
```

Mirascope:

```python
@openai.call("gpt-3.5-turbo")
@prompt_template("""
    SYSTEM: You are a helpful assistant.
    USER: Translate the following English text to French: '{text}'
""")
def translate_to_french(text: str):
    ...
```

This separation of concerns makes it easier to manage and update prompts without touching the core logic of your application.

3. **Provider Agnostic**:

Mirascope allows you to easily switch between providers without changing your core logic. This is not possible with official SDKs, which are tied to specific providers.

Using multiple providers with official SDKs:

OpenAI's official SDK:

```python
from openai import OpenAI

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Translate 'Hello, world!' to French"}
    ]
)
print(completion.choices[0].message.content)
```

Anthropic's official SDK:

```python
from anthropic import Anthropic

client = Anthropic()
message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Translate 'Hello, world!' to French",
        }
    ],
    model="claude-3-5-sonnet-20240620",
)
print(message.content)
```

Using multiple providers with Mirascope:

```python
from mirascope.core import openai, anthropic, prompt_template

# Using OpenAI
@openai.call("gpt-3.5-turbo")
@prompt_template("Translate '{text}' to French")
def openai_translate(text: str):
    ...

# Using Anthropic
@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Translate '{text}' to French")
def anthropic_translate(text: str):
    ...

openai_translation = openai_translate("Hello, world!")
anthropic_translation = anthropic_translate("Hello, world!")

print("OpenAI translation:", openai_translation.content)
print("Anthropic translation:", anthropic_translation.content)
```

With Mirascope, you can easily switch between providers or use multiple providers while keeping your core logic (the `translate_to_french` function) unchanged. This approach provides more flexibility compared to using provider-specific SDKs, allowing for easier experimentation and provider comparisons.

By choosing Mirascope, you'll significantly enhance the efficiency and flexibility of your LLM application development. With its intuitive interface, consistency across providers, and powerful prompt management features, developers can focus on implementing core functionality. Mirascope extends the capabilities of official SDKs, offering a more productive and maintainable development experience. We recommend adopting Mirascope for new projects or improving existing codebases.

This video is just one example of the many benefits Mirascope provides developers:

<video src="https://github.com/user-attachments/assets/174acc23-a026-4754-afd3-c4ca570a9dde" controls="controls" style="max-width: 730px;"></video>

## Who Should Use Mirascope?

Mirascope is ideal for:

- **Professional Developers**: Who need fine-grained control and transparency in their LLM interactions.
- **AI Application Builders**: Looking for a tool that can grow with their project from prototype to production.
- **Teams**: Who value clean, maintainable code and want to avoid the "black box" problem of many AI frameworks.
- **Researchers and Experimenters**: Who need the flexibility to quickly try out new ideas without fighting their tools.

## Getting Started

Ready to experience the Mirascope difference? Check out our [Learn](./learn/index.md) documentation to begin learning how to build cleaner, more maintainable LLM applications today.

By choosing Mirascope, you're opting for a tool that respects your expertise as a developer while providing the conveniences you need to work efficiently with LLMs. We believe that the best tools get out of your way and let you focus on building great applications.
