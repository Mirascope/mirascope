# Tools

Tools are defined functions that a Large Language Model (LLM) can invoke to extend its capabilities. This greatly enhances the capabilities of LLMs by allowing them to perform specific tasks, access external data, interact with other systems, and more. This feature enables the create of more dynamic and interactic LLM applications.

!!! info "How Tools Are Called"

    When an LLM decides to use a tool, it indicates the tool name and argument values in its response. It's important to note that the LLM doesn't actually execute the function; instead, you are responsible for calling the tool and (optionally) providing the output back to the LLM in a subsequent interaction. For more details on such iterative tool-use flows, checkout our [Agents](./agents.md) documentation.

Mirascope provides a provider-agnostic way to define tools, which can be used across all supported LLM providers without modification.

## Defining Tools

### The `BaseTool` Class

??? api "API Documentation"

    [`mirascope.core.base.tool`](../api/core/base/tool.md)

The `BaseTool` class, built on Pydantic's `BaseModel`, offers a flexible way to define tools:

```python hl_lines="4-6"
from mirascope.core import BaseTool


class FormatBook(BaseTool):
    title: str
    author: str

    def call(self) -> str:
        return f"{self.title} by {self.author}"
```

Key points for class-based tool definitions:

- Tools are defined as subclasses of `BaseTool`.
- Tool arguments are defined as class attributes with type hints.
- The `call` method must be defined and returns the tool's output.
- Tools require a description. If provided, we will use the class docstring. Otherwise, we will use our default template, which we have found to work well in our own usage of tools.
- Use Pydantic's `Field` for additional argument information:

```python hl_lines="4-6 8 9"
from mirascope.core import BaseTool
from pydantic import Field

class FormatBook(BaseTool):
    title: str = Field(..., description="Book title in ALL CAPS")
    author: str = Field(..., description="Author as 'Last, First'")

    def call(self) -> str:
        return f"{self.title} by {self.author}"
```

### Using Functions as Tools

Functions can also be used directly as tools:

```python
def format_book(title: str, author: str) -> str:
    """Format a book's title and author."""
    return f"{title} by {author}"
```

Function-based tools require type hints for arguments and must return a string. They are converted to `BaseTool` types internally and can be used anywhere you can use a `BaseTool` definition.

## Comparison with Official SDKs

To illustrate the simplicity and power of Mirascope's tool implementation, let's compare it with the OpenAI SDK:

### OpenAI SDK
```python hl_lines="5-12 16-35 40 43 44"
from openai import OpenAI

client = OpenAI()

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)

messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
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

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)
arguments = response.choices[0].message.tool_calls[0].function.arguments
result = get_current_weather(**json.loads(arguments))
print(result)
```

### Mirascope
```python hl_lines="3-15 17 25"
from mirascope.core import BaseTool, openai, prompt_template

class GetCurrentWeather(BaseTool):
    """Get the current weather in a given location"""
    location: str
    unit: str = "fahrenheit"

    def call(self) -> str:
        weather_info = {
            "location": self.location,
            "temperature": "72",
            "unit": self.unit,
            "forecast": ["sunny", "windy"],
        }
        return json.dumps(weather_info)

@openai.call("gpt-4o-mini", tools=[GetCurrentWeather])
@prompt_template("What's the weather like in {location}?")
def get_weather(location: str):
    ...

response = get_weather("Boston")
print(response.content)
if tool := response.tool:
    print(tool.call())
```

As you can see, Mirascope's implementation is more concise and intuitive, while still providing all the necessary functionality.

## Using Tools with Standard Calls

Incorporate tools in your LLM calls by passing them to the `call` decorator:

```python hl_lines="12 18"
from mirascope.core import BaseTool, openai, prompt_template


class FormatBook(BaseTool):
    title: str
    author: str

    def call(self) -> str:
        return f"{self.title} by {self.author}"


@openai.call("gpt-4o-mini", tools=[FormatBook])  # OR `tools=[format_book]`
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

response = recommend_book("fantasy")
if tools := response.tools:
    for tool in tools:
        print(tool.call())
else:
    print(response.content)
```

The `response.tools` property returns a list of provider-specific tool instances (e.g. `OpenAITool`). Use `response.tool` to access just the first tool call.

??? api "API Documentation"

    [`mirascope.core.anthropic.tool`](../api/core/anthropic/tool.md)

    [`mirascope.core.azure.tool`](../api/core/azure/tool.md)

    [`mirascope.core.cohere.tool`](../api/core/cohere/tool.md)

    [`mirascope.core.gemini.tool`](../api/core/gemini/tool.md)

    [`mirascope.core.groq.tool`](../api/core/groq/tool.md)

    [`mirascope.core.litellm.tool`](../api/core/openai/tool.md)

    [`mirascope.core.mistral.tool`](../api/core/mistral/tool.md)

    [`mirascope.core.openai.tool`](../api/core/openai/tool.md)

    [`mirascope.core.vertex.tool`](../api/core/vertex/tool.md)

### Accessing Original Tool Calls

All provider-specific `BaseTool` instances have a `tool_call` property for accessing the original LLM tool call.

!!! note "Reasoning For Provider-Specific `BaseTool` Objects"

    The reason that we have provider-specific tools (e.g. `OpenAITool`) is to provide proper type hints and safety when accessing the original tool call.

## Streaming Tools

Mirascope supports streaming responses with tools, useful for long-running tasks or real-time updates:

```python hl_lines="9 14-16"
from mirascope.core import openai, prompt_template


def format_book(title: str, author: str) -> str:
    """Format a book's title and author."""
    return f"{title} by {author}"


@openai.call(model="gpt-4", tools=[format_book], stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

for chunk, tool in recommend_book("fantasy"):
    if tool:
        print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
```

!!! note "When Are Tools Returned?"

    When we identify that a tool is being streamed, we will internally reconstruct the tool from the streamed response. This means that the tool won't be returned until the full tool has been streamed and reconstructed on your behalf.

??? info "Providers That Support Streaming Tools"

    We support streaming tools for the following providers. If you think we're missing any, let us know!

    - OpenAI
    - Anthropic
    - Groq
    - Mistral

## Validation

As `BaseTool` instances are `BaseModel` instances, they are validated on construction. Handle potential `ValidationError`s for robust applications:

```python hl_lines="7-9 12-17 20"
from typing import Annotated

from mirascope.core import BaseTool, openai, prompt_template
from pydantic import AfterValidator, ValidationError


def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v


class FormatBook(BaseTool):
    title: Annotated[str, AfterValidator(is_upper)]
    author: str

    def call(self) -> str:
        return f"{self.title} by {self.author}"


@openai.call(model="gpt-4", tools=[FormatBook])
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


try:
    response = recommend_book("fantasy")
    if tool := response.tool:
        print(tool.call())
    else:
        print(response.content)
except ValidationError as e:
    print(e)
    # > 1 validation error for FormatBook
    #   title
    #     Assertion failed, Must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.8/v/assertion_error
```

You can also use `Annotated` to add custom validation when using functions as tools -- simply annotate the type hint of the function argument you want to validate.

!!! tip "Reinserting Errors"

    For enhanced robustness, consider using our [tenacity integration](../integrations/tenacity.md) to catch and reinsert `ValidationError`s into subsequent retries.

## Few Shot Examples

Improve tool response accuracy by adding few shot examples:

```python hl_lines="9-15"
from pydantic import ConfigDict, Field

class FormatBook(BaseTool):
    """Format a book's title and author."""
    
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

For function-based tools, add JSON examples in the docstring:

```python hl_lines="4-9"
def format_book(title: str, author: str) -> str:
    """Format a book recommendation.

    Example:
        {"title": "THE HOBBIT", "author": "J.R.R. Tolkien"}

    Example:
        {"title": "THE NAME OF THE WIND", "author": "Patrick Rothfuss"}
    """
    return f"I recommend {title} by {author}."
```

## `BaseToolKit`

??? api "API Documentation"

    [`mirascope.core.base.toolkit`](../api/core/base/toolkit.md)

The `BaseToolKit` class allows organization of tools under a single namespace as well as dynamic updating of tool schemas:

```python hl_lines="7 8 10 22"
from typing import Literal

from mirascope.core import BaseToolKit, openai, prompt_template, toolkit_tool


class BookTools(BaseToolKit):
    __namespace__ = "book_tools"
    reading_level: Literal["beginner", "intermediate", "advanced"]

    @toolkit_tool
    def recommend_book_by_level(self, title: str, author: str) -> str:
        """Recommend a book based on reading level.

        Reading Level: {self.reading_level}
        """
        return f"{title} by {author}"


toolkit = BookTools(reading_level="beginner")


@openai.call("gpt-4o-mini", tools=toolkit.create_tools())
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("science")
print(response.content)
# > Astrophysics for Young People in a Hurry by Neil deGrasse Tyson
```

The `create_tools` method generates tools with the specified `reading_level` injected into their schemas. The tools' names are also updated to reflect the toolkit's namespace (e.g. `book_tools_recommend_book_by_level`).

## Type Support Across Providers

While Mirascope provides a consistent interface, type support varies among providers:

| Type          | Anthropic | Cohere | Gemini | Groq | Mistral | OpenAI |
|---------------|-----------|--------|--------|------|---------|--------|
| str           | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| int           | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| float         | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| bool          | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| bytes         | ✓         | ✓      | -      | ✓    | ✓       | ✓      |
| list          | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| set           | ✓         | ✓      | -      | ✓    | ✓       | ✓      |
| tuple         | ✓         | ✓      | -      | ✓    | ✓       | -      |
| dict          | ✓         | ✓      | ✓      | ✓    | ✓       | -      |
| Literal/Enum  | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| BaseModel     | ✓         | -      | ✓      | ✓    | ✓       | ✓      |
| Nested ($def) | ✓         | -      | -      | ✓    | ✓       | ✓      |

Legend: ✓ (Supported), - (Not Supported)

Consider provider-specific capabilities when working with advanced type structures. Even for supported types, LLM outputs may sometimes be incorrect or of the wrong type. In such cases, prompt engineering or error handling (like reinserting validation errors) may be necessary.

## Common Use Cases

Tools can enhance LLM applications in various ways:

- Data retrieval (e.g., weather, stock prices)
- Complex calculations
- External API interactions
- Database queries
- Text processing (analysis, summarization, translation)

## Best Practices

When working with tools in Mirascope:

1. **Provide clear, concise tool descriptions**: 
     - Use docstrings to describe the purpose and functionality of your tools.
     - Be specific about what the tool does and what kind of input it expects.
     Example:
     ```python hl_lines="2-6"
     class WeatherTool(BaseTool):
         """Get the current weather for a given location.
       
         This tool fetches real-time weather data from a weather API.
         It requires a valid location name and returns temperature and conditions.
         """
         location: str = Field(..., description="Name of the city or location")
   
         def call(self) -> str:
             # Implementation details...
             return f"The weather in {self.location} is 72°F and sunny."
     ```

2. **Implement robust error handling**:
     - Use try-except blocks to catch and handle potential errors.
     - Consider using our [tenacity integration](../integrations/tenacity.md) for automatic retries.
     Example:
     ```python hl_lines="10-24"
     from mirascope.integrations.tenacity import collect_errors
     from tenacity import retry, stop_after_attempt
     
     @retry(stop=stop_after_attempt(3), after=collect_errors(ValueError))
     @openai.call("gpt-4", tools=[WeatherTool])
     @prompt_template("What's the weather like in {location}?")
     def get_weather(location: str):
      ...
     
     try:
      response = get_weather("New York")
      print(response.content)
     except Exception as e:
      print(f"An error occurred: {e}")
     ```

3. **Use proper type annotations for safety and clarity**:
     - Leverage Python's type hinting system to make your tool interfaces clear.
     - Use Pydantic's `Field` for additional metadata and validation.
     Example:
     ```python hl_lines="5-7"
     from typing import Literal
     from pydantic import Field
     
     class TemperatureConverter(BaseTool):
         value: float = Field(..., description="Temperature value to convert")
         from_unit: Literal["C", "F"] = Field(..., description="Original temperature unit")
         to_unit: Literal["C", "F"] = Field(..., description="Target temperature unit")
     
         def call(self) -> str:
             if self.from_unit == self.to_unit:
                 return f"{self.value}{self.from_unit}"
             if self.from_unit == "C" and self.to_unit == "F":
                 return f"{(self.value * 9/5) + 32}F"
             return f"{(self.value - 32) * 5/9}C"
     ```

4. **Optimize performance for resource-intensive operations**:
     - If a tool performs heavy computations, consider caching results or implementing lazy evaluation.
     Example:
     ```python hl_lines="9 21"
     from mirascope.core import BaseTool, anthropic, prompt_template
     from mirascope.core.anthropic import AnthropicToolConfig
     
     # Define a tool that utilizes Anthropic's prompt caching feature
     class LiteraryAnalysisTool(BaseTool):
         book_title: str
         analysis_type: str
     
         tool_config = AnthropicToolConfig(cache_control={"type": "ephemeral"})
     
         def call(self) -> str:
             # Simulated analysis (in a real scenario, this would be more complex)
             analysis_results = {
                 "themes": "The book explores themes of love, loss, and redemption.",
                 "characters": "The protagonist undergoes significant character development.",
                 "style": "The author employs a unique narrative style with non-linear storytelling."
             }
             return analysis_results.get(self.analysis_type, "Analysis type not supported.")
     
     # Define a prompt that uses the tool and Anthropic's prompt caching
     @anthropic.call("claude-3-5-sonnet-20240620", tools=[LiteraryAnalysisTool])
     @prompt_template(
         """
         SYSTEM:
         You are an AI assistant specialized in literary analysis.
         Your task is to provide in-depth analysis of books based on user queries.
     
         Here's a summary of the book "{book_title}":
     
         {:cache_control}
     
         USER: Can you analyze the {analysis_type} of the book?
         """
     )
     def analyze_book(book_title: str, analysis_type: str):
         ...
     
     # Example usage
     response = analyze_book("To Kill a Mockingbird", "themes")
     print(response.content)
     
     # Another example with a different analysis type
     response = analyze_book("To Kill a Mockingbird", "style")
     print(response.content)
     ```

5. **Consider provider-specific limitations and features**:
     - Be aware of the type support differences across providers.
     - Tailor your tool implementations to work across all providers you intend to support.
     Example:
     ```python hl_lines="7 8 10 22"
     class ProviderAgnosticTool(BaseTool):
         data: dict  # Use dict instead of more specific types for better compatibility
     
         def call(self) -> str:
             # Implement in a way that works across providers
             return json.dumps(self.data)  # Return JSON string for maximum compatibility
     
     @openai.call("gpt-4", tools=[ProviderAgnosticTool])
     @anthropic.call("claude-3-5-sonnet-20240620", tools=[ProviderAgnosticTool])
     @prompt_template("Process this data: {data}")
     def process_data(data: dict):
         ...
     ```

6. **Test your tools thoroughly**:
     - Write unit tests for your tool implementations.
     - Test with different LLM providers to ensure consistent behavior.
     Example:
     ```python hl_lines="6 7 27 28"
     from mirascope.core import openai, anthropic
     
     def test_weather_tool():
         tool = WeatherTool(location="London")
         result = tool.call()
         assert "London" in result
         assert "°F" in result
     
     def test_weather_tool_with_providers():
         @openai.call("gpt-4", tools=[WeatherTool])
         @prompt_template("What's the weather in {location}?")
         def get_weather_openai(location: str):
             ...
 
         @anthropic.call("claude-3-5-sonnet-20240620", tools=[WeatherTool])
         @prompt_template("What's the weather in {location}?")
         def get_weather_anthropic(location: str):
             ...
         response = get_weather_openai("New York")
         assert response.tool is not None
         openai_result = response.tool.call()

         response = get_weather_anthropic("New York")
         assert response.tool is not None
         anthropic_result = response.tool.call()

         assert "New York", openai_result
         assert "New York", anthropic_result
     ```

7. **Keep tools modular and reusable**:
     - Design tools that can be easily composed and reused across different contexts.
     Example:
     ```python hl_lines="4-14 16-23 26 31 36"
     from mirascope.core import BaseTool, openai, prompt_template
     
     # Reusable tools
     class CurrencyConverter(BaseTool):
         amount: float
         from_currency: str
         to_currency: str
     
         def call(self) -> str:
             # Simplified conversion logic
             conversion_rates = {"USD_EUR": 0.92, "EUR_USD": 1.09, "GBP_USD": 1.27, "USD_GBP": 0.79}
             rate = conversion_rates.get(f"{self.from_currency}_{self.to_currency}", 1)
             converted = self.amount * rate
             return f"{self.amount} {self.from_currency} is equivalent to {converted:.2f} {self.to_currency}"
     
     class StockPriceFetcher(BaseTool):
         symbol: str
     
         def call(self) -> str:
             # Simplified stock price fetching logic
             prices = {"AAPL": 150.25, "GOOGL": 2750.50, "MSFT": 305.75}
             price = prices.get(self.symbol, 0)
             return f"The current price of {self.symbol} is ${price:.2f}"
     
     # Multiple prompts using the same tools
     @openai.call("gpt-4", tools=[CurrencyConverter, StockPriceFetcher])
     @prompt_template("What's the value of {amount} {currency} worth of {stock} stock?")
     def get_stock_value(amount: float, currency: str, stock: str):
         ...
     
     @openai.call("gpt-4", tools=[CurrencyConverter, StockPriceFetcher])
     @prompt_template("Compare the prices of {stock1} and {stock2} in {currency}.")
     def compare_stocks(stock1: str, stock2: str, currency: str):
         ...
     
     @openai.call("gpt-4", tools=[CurrencyConverter])
     @prompt_template("Convert {amount} {from_currency} to {to_currency}.")
     def currency_conversion(amount: float, from_currency: str, to_currency: str):
         ...
     
     # Example usage
     print(get_stock_value(1000, "EUR", "AAPL"))
     print(compare_stocks("AAPL", "GOOGL", "GBP"))
     print(currency_conversion(100, "USD", "EUR"))
     ```

8. **Use `BaseToolKit` for organizing related tools**:
     - Group related tools under a single namespace for better organization.
     - Leverage dynamic schema updates for more flexible tool configurations. 
     Example:
     ```python hl_lines="2 11 19"
     class FinanceTools(BaseToolKit):
         __namespace__ = "finance"
         base_currency: str = "USD"
     
         @toolkit_tool
         def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> str:
             """Convert currency based on the base currency."""
             # Implementation details...
             return f"{amount} {from_currency} is X {to_currency}"
     
         @toolkit_tool
         def get_stock_price(self, symbol: str) -> str:
             """Get the current stock price in the base currency."""
             # Implementation details...
             return f"The current price of {symbol} is {self.base_currency} X"
     
     finance_toolkit = FinanceTools(base_currency="EUR")
     
     @openai.call("gpt-4", tools=finance_toolkit.create_tools())
     @prompt_template("Analyze the value of {amount} {currency} worth of {stock} stock.")
     def analyze_stock_value(amount: float, currency: str, stock: str):
         ...
     ```

These examples demonstrate how to implement each best practice in your Mirascope tools. Remember to adapt these examples to your specific use case and requirements.

Tools in Mirascope significantly extend LLM capabilities, enabling more interactive and dynamic applications. By mastering tool definition, usage, and optimization across different providers, you can create sophisticated LLM-powered solutions that leverage external data and functionality.

We encourage you to explore and experiment with tools to enhance your projects and find the best fit for your specific needs. As LLM technology evolves, tools will continue to play a crucial role in building advanced AI applications.
