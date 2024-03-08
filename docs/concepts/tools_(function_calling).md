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

## Tools in Mirascope

Mirascope provides a clean and intuitive way to incorporate tools into your LLM workflows. The simplest form-factor we offer is to extract a single tool automatically generated from a function. We can then call that function with the extracted arguments:

```python
from mirascope.openai import OpenAIPrompt


def get_weather(location: str) -> str:
    """Get's the weather for `location` and prints it.

    Args:
        location: The "City, State" or "City, Country" for which to get the weather.
    """
    print(location)
    if location == "Tokyo, Japan":
        return f"The weather in {location} is 72 degrees and sunny."
    elif location == "San Francisco, CA":
        return f"The weather in {location} is 45 degrees and cloudy."
    else:
        return f"I'm sorry, I don't have the weather for {location}."


class Weather(OpenAIPrompt):
    """What's the weather in Tokyo?"""


weather_tool = Weather().extract(get_weather)
print(weather_tool.fn(**weather_tool.args))
#> The weather in Tokyo, Japan is 72 degrees and sunny.
```

!!! note

    While it may not be clear from the above example, `tool.fn` is an extremely powerful simplification. When using multiple tools, having the function attached to the tool makes it immediately accessible and callable with a single line of code.

In the following pages, we’ll go into greater detail around how to define and use tools effectively.
