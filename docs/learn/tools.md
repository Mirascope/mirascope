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

```python
from mirascope.core import BaseTool


class FormatBook(BaseTool):
    title: str
    author: str

    def call(self) -> str:
        return f"{self.title} by {self.author}"
```

Key points for class-based tool definitions:

- Tools require a description. If provided, we will use the class docstring. Otherwise, we will use our default template, which we have found to work well in our own usage of tools.
- The `call` method must be defined.
- Use Pydantic's `Field` for additional argument information:

```python
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

## Using Tools with Standard Calls

Incorporate tools in your LLM calls by passing them to the `call` decorator:

```python
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

    [`mirascope.core.cohere.tool`](../api/core/cohere/tool.md)
    
    [`mirascope.core.gemini.tool`](../api/core/gemini/tool.md)
    
    [`mirascope.core.groq.tool`](../api/core/groq/tool.md)
    
    [`mirascope.core.mistral.tool`](../api/core/mistral/tool.md)
    
    [`mirascope.core.openai.tool`](../api/core/openai/tool.md)

### Accessing Original Tool Calls

All provider-specific `BaseTool` instances have a `tool_call` property for accessing the original LLM tool call.

!!! note "Reasoning For Provider-Specific `BaseTool` Objects"

    The reason that we have provider-specific tools (e.g. `OpenAITool`) is to provide proper type hints and safety when accessing the original tool call.

## Streaming Tools

Mirascope supports streaming responses with tools, useful for long-running tasks or real-time updates:

```python
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

```python
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

```python
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

```python
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

```python
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

- Provide clear, concise tool descriptions.
- Implement robust error handling.
- Use proper type annotations for safety and clarity.
- Optimize performance for resource-intensive operations.
- Consider provider-specific limitations and features.

Tools in Mirascope can significantly extend LLM capabilities, enabling more interactive and dynamic applications. By mastering tool definition, usage, and optimization across different providers, you can create sophisticated LLM-powered solutions that leverage external data and functionality.

We encourage you to explore and experiment with tools to enhance your projects and find the best fit for your specific needs. As LLM technology evolves, tools will continue to play a crucial role in building advanced AI applications.
