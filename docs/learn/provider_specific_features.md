# Provider-Specific Features

While Mirascope provides a provider-agnostic interface for as many features as possible, there are inevitably features that not all providers support.

Often these provider-specific features are powerful and worth using, so we try our best to provide support for such features, which we have documented here.

If there are any features in particular that you want to use that are not currently supported, let us know!

## OpenAI

### Structured Outputs

OpenAI's newest models (starting with `gpt-4o-2024-08-06`) support strict structured outputs that reliably adhere to developer-supplied JSON Schemas, achieving 100% reliability in their evals, perfectly matching the desired output schemas.

This feature can be extremely useful when extracting structured information or using tools, and you can access this feature when using tools or response models with Mirascope.

#### Tools

To use structured outputs with tools, use the `OpenAIToolConfig` and set `strict=True`. You can then use the tool just like you normally would:

```python hl_lines="9"
from mirascope.core import BaseTool, openai, prompt_template
from mirascope.core.openai import OpenAIToolConfig


class FormatBook(BaseTool):
    title: str
    author: str

    tool_config = OpenAIToolConfig(strict=True)

    def call(self) -> str:
        return f"{self.title} by {self.author}"


@openai.call(
    "gpt-4o-2024-08-06", tools=[FormatBook], call_params={"tool_choice": "required"}
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("fantasy")
if tool := response.tool:
    print(tool.call())
# > The Name of the Wind by Patrick Rothfuss
```

Under the hood, Mirascope generates a JSON Schema for the `FormatBook` tool based on its attributes and the `OpenAIToolConfig`. This schema is then used by OpenAI's API to ensure the model's output strictly adheres to the defined structure.

For comparison, here's how you might implement this using the official OpenAI SDK:

```python
from openai import OpenAI
import json

client = OpenAI()

def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"

function_json = {
    "name": "format_book",
    "description": "Format a book's title and author",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "The title of the book"},
            "author": {"type": "string", "description": "The author of the book"}
        },
        "required": ["title", "author"]
    }
}

response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[{"role": "user", "content": "Recommend a fantasy book"}],
    functions=[function_json],
    function_call={"name": "format_book"}
)

function_args = json.loads(response.choices[0].message.function_call.arguments)
result = format_book(**function_args)
print(result)
# > The Name of the Wind by Patrick Rothfuss
```

As you can see, Mirascope significantly simplifies the process of defining and using tools with OpenAI's API, while still providing the same level of control and strictness.

#### Response Models

Similarly, you can use structured outputs with response models by setting `strict=True` in the response model's `ResponseModelConfigDict`, which is just a subclass of Pydantic's `ConfigDict` with the addition of the `strict` key. You will also need to set `json_mode=True`:

```python hl_lines="9"
from mirascope.core import ResponseModelConfigDict, openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str

    model_config = ResponseModelConfigDict(strict=True)


@openai.call("gpt-4o-2024-08-06", response_model=Book, json_mode=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


book = recommend_book("fantasy")
print(book)
# > title='The Name of the Wind' author='Patrick Rothfuss'
```

## Anthropic

### Prompt Caching

Anthropic's prompt caching feature can help save a lot of tokens by caching parts of your prompt. For full details, we recommend reading [their documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).

To access this feature in Mirascope, simply add a `:cache_control` tagged breakpoint to your prompt:

```python hl_lines="9"
@prompt_template(
    """
    SYSTEM:
    You are an AI assistant tasked with analyzing literary works.
    Your goal is to provide insightful commentary on themes, characters, and writing style.

    Here is the book in it's entirety: {book}

    {:cache_control}

    USER: {query}
    """
)
```

You can also specify the cache control type the same way we support additional options for multimodal parts (although currently `"ephemeral"` is the only supported type):

```python
@prompt_template("... {:cache_control(type=ephemeral)}")
```

It is also possible to cache tools by using the `AnthropicToolConfig` and setting the cache control:

```python hl_lines="8"
from mirascope.core import BaseTool, anthropic
from mirascope.core.anthropic import AnthropicToolConfig


class CachedTool(BaseTool):
    ...

    tool_config = AnthropicToolConfig(cache_control={"type": "ephemeral"})

    def call(self) -> str: ...
```

Remember only to include the cache control on the last tool in your list of tools that you want to cache (as all tools up to the tool with a cache control breakpoint will be cached).

Under the hood, Mirascope adds the appropriate cache control headers to the API request, ensuring that the specified parts of your prompt are cached by Anthropic's servers. This can significantly reduce token usage and improve response times for subsequent calls with similar prompts.

For comparison, here's how you might implement prompt caching using the official Anthropic SDK:

```python
from anthropic import Anthropic

client = Anthropic()

book_content = "This is where the full text of the book would go, but for copyright reasons, we're not including it here."
query = "Analyze the major themes in this book."

response = client.beta.prompt_caching.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    system=[
        {
            "type": "text", 
            "text": "You are an AI assistant tasked with analyzing literary works. "
                    "Your goal is to provide insightful commentary on themes, characters, and writing style.\n"
        },
        {
            "type": "text", 
            "text": f"Here is the book in its entirety: {book_content}",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[
        {"role": "user", "content": query}
    ],
)

print(response.content)
```

As you can see, Mirascope significantly simplifies the process of using prompt caching with Anthropic's API, while still providing the same functionality.

!!! warning "This Feature Is In Beta"

    While we've added support for prompt caching with Anthropic, this feature is still in beta and requires setting extra headers. You can set this header as an additional call parameter, e.g.

    ```python hl_lines="5"
    @anthropic.call(
        "claude-3-5-sonnet-20240620",
        call_params={
            "max_tokens": 1024,
            "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"},
        },
    )
    ```

    As this feature is in beta, there may be changes made by Anthropic that may result in changes in our own handling of this feature.


## Real-World Examples of Using Provider-Specific Features

### 1. Product Catalog Management System Using OpenAI's Structured Output

In a large e-commerce platform, there's often a need to automatically generate product descriptions and store them in a structured format in the database. OpenAI's structured output feature can streamline this process.

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel

class ProductDescription(BaseModel):
    name: str
    category: str
    features: list[str]
    specifications: dict[str, str]

@openai.call("gpt-4o-2024-08-06", response_model=ProductDescription, json_mode=True)
@prompt_template("Generate a structured product description for: {product_info}")
def generate_product_description(product_info: str):
    ...

raw_info = "Latest smartphone model XYZ, 6.1-inch display, 5G capable, 128GB storage, available in black and white"
product = generate_product_description(raw_info)

# Save the result to the database
save_to_database(product)
```

In this example, we're automatically generating a structured product description from unstructured text information. This allows for efficient processing of large volumes of product information and maintenance of an organized catalog.

### 2. Legal Document Analysis System Using Anthropic's Prompt Caching

Law firms often need to analyze large volumes of legal documents and extract important information. Anthropic's prompt caching feature can be used to streamline the processing of long legal documents.

```python
from mirascope.core import anthropic, prompt_template

@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template(
    """
    SYSTEM: You are a legal document analyzer. Analyze the following legal document 
    and extract key information such as parties involved, main clauses, and any potential risks.

    Document: {document}
    
    {:cache_control}

    USER: {query}
    """
)
def analyze_legal_document(document: str, query: str):
    ...

long_legal_document = "... (content of a long legal document) ..."

# Cache the entire document while performing different analyses
parties = analyze_legal_document(long_legal_document, "List all parties mentioned in the document.")
clauses = analyze_legal_document(long_legal_document, "Summarize the main clauses of the agreement.")
risks = analyze_legal_document(long_legal_document, "Identify any potential legal risks or ambiguities.")

# Compile the results into a report
compile_legal_report(parties, clauses, risks)
```

In this example, we cache a long legal document once and then efficiently execute multiple different analysis queries. This allows for detailed analysis while avoiding the need to resend the lengthy document that would consume a large number of tokens.

For more information on how to effectively use these provider-specific features in your projects, please refer to our [cookbook recipes](../cookbook/index.md) and [advanced usage guides](../learn/index.md).