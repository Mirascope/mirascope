# Dynamic Configuration

Dynamic Configuration is a powerful feature in Mirascope that allows you to modify the behavior of LLM calls at runtime. By returning a provider-specific dynamic configuration dictionary from the decorated function, you can flexibly adjust various aspects of the LLM call based on input arguments or other runtime conditions.

## How It Works

When you use a Mirascope LLM function decorator (e.g., `openai.call`), the decorated function is executed before the actual LLM call. The function's return value, if it's a dynamic configuration dictionary, is used to update the call's configuration. This allows for dynamic adjustment of the call based on the function's input or any computation performed within the function.

### Order of Operations

1. The decorated function is called with the provided arguments.
2. If the function returns a dynamic configuration dictionary, it's used to update the call configuration.
3. Dynamic configuration options take precedence over static options defined in the decorator.
4. The LLM call is made using the final, dynamically updated configuration.

## Dynamic Configuration Options

??? api "API Documentation"

    [`mirascope.core.base.dynamic_config`](../api/core/base/dynamic_config.md)

    [`mirascope.core.anthropic.dynamic_config`](../api/core/anthropic/dynamic_config.md)
    
    [`mirascope.core.cohere.dynamic_config`](../api/core/cohere/dynamic_config.md)
    
    [`mirascope.core.gemini.dynamic_config`](../api/core/gemini/dynamic_config.md)
    
    [`mirascope.core.groq.dynamic_config`](../api/core/groq/dynamic_config.md)
    
    [`mirascope.core.mistral.dynamic_config`](../api/core/mistral/dynamic_config.md)
    
    [`mirascope.core.openai.dynamic_config`](../api/core/openai/dynamic_config.md)

Each provider has its own dynamic configuration type (e.g., `openai.OpenAIDynamicConfig`). Here are the common options available across providers:

### Computed Fields

Computed fields allow you to dynamically generate or modify template variables used in your prompt.

```python
from mirascope.core import openai, prompt_template

@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book with a reading level of {reading_level}")
def recommend_book(genre: str, age: int) -> openai.OpenAIDynamicConfig:
    reading_level = "adult"
    if age < 12:
        reading_level = "elementary"
    elif age < 18:
        reading_level = "young adult"
    return {"computed_fields": {"reading_level": reading_level}}

response = recommend_book("fantasy", 15)
print(response.content)
```

In this example, the `reading_level` is computed based on the `age` input, allowing for dynamic customization of the prompt.

### Tools

??? api "API Documentation"

    [`mirascope.core.base.tool`](../api/core/base/tool.md)

    [`mirascope.core.base.toolkit`](../api/core/base/toolkit.md)

You can dynamically configure which tools are available to the LLM based on runtime conditions.

```python
from mirascope.core import BaseToolKit, openai, prompt_template, toolkit_tool


class BookToolkit(BaseToolKit):
    genre: str

    @toolkit_tool
    def format_book(self, title: str, author: str) -> str:
        """Format a {self.genre} book recommendation."""
        return f"{title} by {author} ({self.genre})"


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    toolkit = BookToolkit(genre=genre)
    return {"tools": toolkit.create_tools()}


response = recommend_book("mystery")
if response.tool:
    print(response.tool.call())
```

This example demonstrates how to dynamically create and configure tools based on the input `genre`. This feature can also be particularly useful when you want to limit which tools you provide to the LLM based on input arguments, reducing the potential behavior paths the LLM can take.

### Custom Messages

You can completely override the default messages generated from the prompt template by providing custom messages.

```python
from mirascope.core import openai

@openai.call("gpt-4o-mini")
def recommend_book(genre: str, style: str) -> openai.OpenAIDynamicConfig:
    return {
        "messages": [
            {"role": "system", "content": "You are a helpful book recommender."},
            {"role": "user", "content": f"Recommend a {genre} book in the style of {style}."},
        ]
    }

response = recommend_book("science fiction", "cyberpunk")
print(response.content)
```

When using custom messages, the prompt template is ignored and not required.

!!! warning "No Longer Provider-Agnostic"

    When writing your own custom messages, these messages must be written specifically for the provider you are using. This makes switching providers more of a hassle; however, there may be new features that our prompt template parsing does not currently support, which you will always be able to access through custom messages.

### Metadata

??? api "API Documentation"

    [`mirascope.core.base.medata`](../api/core/base/metadata.md)

You can dynamically add metadata to your LLM calls, which can be useful for logging, tracking, or categorizing responses.

```python
from mirascope.core import openai, prompt_template

@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {
        "metadata": {
            "tags": {f"genre:{genre}", "type:recommendation"}
        }
    }

response = recommend_book("horror")
print(response.metadata)
```

This example shows how to add dynamic tags based on the input genre.

### Call Parameters

??? api "API Documentation"

    [`mirascope.core.anthropic.call_params`](../api/core/anthropic/call_params.md)

    [`mirascope.core.cohere.call_params`](../api/core/cohere/call_params.md)

    [`mirascope.core.gemini.call_params`](../api/core/gemini/call_params.md)

    [`mirascope.core.groq.call_params`](../api/core/groq/call_params.md)

    [`mirascope.core.mistral.call_params`](../api/core/mistral/call_params.md)

    [`mirascope.core.openai.call_params`](../api/core/openai/call_params.md)

You can adjust call parameters dynamically, allowing for fine-tuned control over the LLM's behavior.

```python
from mirascope.core import openai, prompt_template

@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str, creativity: float) -> openai.OpenAIDynamicConfig:
    return {
        "call_params": {
            "temperature": creativity
        }
    }

response = recommend_book("mystery", 0.8)
print(response.content)
```

This example demonstrates how to dynamically set the temperature based on a `creativity` input.

## Best Practices

- Use dynamic configuration when you need runtime flexibility in your LLM calls.
- Be mindful of performance implications when performing complex computations in the function body.
- Leverage dynamic configuration to create more adaptive and context-aware LLM interactions.
- Consider using dynamic configuration for A/B testing different prompt strategies or model parameters.

Dynamic configuration is currently limited to the options available in the provider-specific configuration dictionaries. If you find that you need configuration options not currently available in the dynamic configuration dictionaries, please let us know. We're always looking to expand and improve our features based on user needs.
