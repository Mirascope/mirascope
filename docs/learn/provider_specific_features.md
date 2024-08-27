# Provider-Specific Features

While Mirascope provides a provider-agnostic interface for as many features as possible, there are inevitably features that not all providers support.

Often these provider-specific features are powerful and worth using, so we try our best to provide support for such features, which we have documented here.

If there are any features in particular that you want to use that that are not currently supported, let us know!

## OpenAI

### Structured Outputs

OpenAI's newest models (starting with `gpt-4o-2024-08-06`) support strict structured outputs that reliably adhere to developer-supplied JSON Schemas, achieving 100% reliability in their evals, perfectly matching the desired output schemas.

This feature can be extremely useful when extracting structured information or using tools, and you can access this feature when using tools or response models with Mirascope.

#### Tools

To use structured outputs with tools, use the `OpenAIToolConfig` and set `strict=True`. You can then use the tool just like you normally would:

```python
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

#### Response Models

Similarly, you can use structured outputs with response models by setting `strict=True` in the response model's `ResponseModelConfigDict`, which is just a subclass of Pydantic's `ConfigDict` with the addition of the `strict` key. You will also need to set `json_mode=True`:

```python
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

To access this feature in Mirascope, simple add a `:cache_control` tagged breakpoint to your prompt:

```python
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

```python
from mirascope.core import BaseTool, anthropic
from mirascope.core.anthropic import AnthropicToolConfig


class CachedTool(BaseTool):
    ...

    tool_config = AnthropicToolConfig(cache_control={"type": "ephemeral"})

    def call(self) -> str: ...
```

Remember only to include the cache control on the last tool in your list of tools that you want to cache (as all tools up to the tool with a cache control breakpoint will be cached).

!!! warning "This Feature Is In Beta"

    While we've added support for prompt caching with Anthropic, this feature is still in beta and requires setting extra headers. You can set this header as an additional call parameter, e.g.

    ```python
    @anthropic.call(
        "claude-3-5-sonnet-20240620",
        call_params={
            "max_tokens": 1024,
            "extra_headers": {"anthropic-beta": "prompt-caching-2024-07-31"},
        },
    )
    ```

    As this feature is in beta, there may be changes made by Anthropic that may result in changes in our own handling of this feature.
