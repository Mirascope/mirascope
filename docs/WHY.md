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

### Simplified Syntax

Mirascope's approach streamlines the process using decorators, making it more concise and easier to manage. This is particularly evident when working with various LLM providers or more ecomplex use-cases like tools and agents.

#### Basic Usage

!!! note "OpenAI's Official SDK"

    ```python
    from openai import OpenAI

    client = OpenAI()

    def hello_world() -> str | None:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello world"}
            ]
        )
        return completion.choices[0].message.content

    print(hello_world())
    ```

!!! tip "Mirascope"

    ```python
    from mirascope.core import openai, prompt_template

    @openai.call("gpt-3.5-turbo")
    @prompt_template("Hello world")
    def hello_world():
        ...

    response = hello_world()
    print(response.content)
    ```

#### Streaming

!!! note "OpenAI's Official SDK"

    ```python
    from openai import OpenAI

    client = OpenAI()

    def count_to_five() -> Generator[str, None, None]:
        stream = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Count to 5.'}],
            stream=True
        )
        for chunk in stream:
            if (content := chunk.choices[0].delta.content) is not None:
                yield content

    for content in count_to_five():
        print(content, end="", flush=True)
    ```

!!! tip "Mirascope"

    ```python
    @openai.call("gpt-3.5-turbo", stream=True)
    @prompt_template("Count to 5.")
    def count_to_five():
        ...

    for chunk, _ in count_to_five():
        print(chunk.content, end="", flush=True)
    ```

#### Tools

!!! note "OpenAI's Official SDK"

    ```python
    import json
    from typing import Literal

    from openai import OpenAI

    client = OpenAI()


    def get_current_weather(
        location: str, unit: Literal["fahrenheit", "celsius"] = "fahrenheit"
    ):
        # Mock weather data
        return f"The current weather in {location} is 72°F"


    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]


    available_tools = {"get_current_weather": get_current_weather}
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"What's the weather like in {location}"}
        ],
        tools=tools,
        tool_choice="auto",
    )
    if tool_calls := response.choices[0].message.tool_calls:
        tool_call = tool_calls[0]
        tool = available_tools[tool_call.function.name]
        arguments = json.loads(tool_calls[0].function.arguments)
        print(tool(**arguments))
    else:
        print(response.choices[0].message.content)
    ```

!!! tip "Mirascope"

    ```python
    from typing import Literal

    from mirascope.core import openai, prompt_template


    def get_current_weather(location: str, unit: Literal["fahrenheit", "celsius"]) -> str:
        """Get the current weather in a given location

        Args:
            location: The city and state, e.g. San Francisco, CA
            unit: The temperature unit commonly used in `location`.
        """
        # Mock weather data
        return f"The current weather in {location} is 72°F"


    @openai.call("gpt-4o-mini", tools=[get_current_weather])
    @prompt_template("What's the weather like in {location}?")
    def weather(location: str):
        ...


    response = weather("Boston")
    if tool := response.tool:
        print(tool.call())
    else:
        print(response.content)
    ```

As you can see, Mirascope significantly reduces the amount of boilerplate code, making your LLM interactions more concise and easier to understand at a glance.

### Provider Agnostic

Mirascope allows you to easily switch between providers without changing your core logic. This is not possible with official SDKs, which are tied to specific providers.

!!! note "Using Multiple Providers' Official SDKs"

    ```python
    from anthropic import Anthropic
    from openai import OpenAI

    anthropic_client = Anthropic()
    openai_client = OpenAI()


    def openai_translate(text: str) -> str | None:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Translate '{text}' to French"}],
        )
        return completion.choices[0].message.content


    def anthropic_translate(text: str) -> str:
        message = anthropic_client.messages.create(
            model="claude-3.5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"Translate '{text}' to French"}],
        )
        block = message.content[0]
        return block.text if block.type == "text" else ""


    openai_translation = openai_translate("Hello, World!")
    print("OpenAI translation:", openai_translation)

    anthropic_translation = anthropic_translate("Hello, World!")
    print("Anthropic translation:", anthropic_translation)
    ```

!!! tip "Using Multiple Providers With Mirascope"

    ```python
    from mirascope.core import openai, anthropic, prompt_template

    @prompt_template("Translate '{text}' to French")
    def translate_prompt(text: str):
        ...

    openai_translate = openai.call("gpt-4o-mini")(translate_propmt)
    anthropic_translate = anthropic.call("claude-3-5-sonnet-20240620")(translate_propmt)

    openai_translation = openai_translate("Hello, world!")
    print("OpenAI translation:", openai_translation.content)

    anthropic_translation = anthropic_translate("Hello, world!")
    print("Anthropic translation:", anthropic_translation.content)
    ```

With Mirascope, you can easily switch between providers or use multiple providers while keeping your prompt template consistent. This approach provides more flexibility compared to using provider-specific SDKs, allowing for easier experimentation and provider comparisons.

By choosing Mirascope, you'll significantly enhance the efficiency and flexibility of your LLM application development. With its intuitive interface, consistency across providers, and powerful prompt management features, developers can focus on implementing core functionality and not boilerplate.

Mirascope also extends the capabilities of official SDKs, offering a more productive and maintainable development experience with features such as `response_model`. We recommend adopting Mirascope for new projects or improving existing codebases.

<video src="https://github.com/user-attachments/assets/174acc23-a026-4754-afd3-c4ca570a9dde" controls="controls" style="max-width: 730px;"></video>

## Who Should Use Mirascope?

Mirascope is ideal for:

- **Professional Developers**: Who need fine-grained control and transparency in their LLM interactions.
- **AI Application Builders**: Looking for a tool that can grow with their project from prototype to production.
- **Teams**: Who value clean, maintainable code and want to avoid the "black box" problem of many AI frameworks.
- **Researchers and Experimenters**: Who need the flexibility to quickly try out new ideas without fighting their tools.

## Getting Started

If you haven't already, check out our [Getting Started](./index.md) guide. If you're ready to dive deeper, we recommend reading through our [Learn](./learn/index.md) documentation to learn how to build cleaner, more maintainable LLM applications today.

By choosing Mirascope, you're opting for a tool that respects your expertise as a developer while providing the conveniences you need to work efficiently with LLMs. We believe that the best tools get out of your way and let you focus on building great applications.
