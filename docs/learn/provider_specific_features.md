# Provider-Specific Features

While Mirascope provides a provider-agnostic interface for as many features as possible, there are inevitably features that not all providers support.

Often these provider-specific features are powerful and worth using, so we try our best to provide support for such features, which we have documented here.

If there are any features in particular that you want to use that that are not currently supported, let us know!

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
)
```

You can also specify the cache control type the same way we support additional options for multimodal parts (although currently `"ephemeral"` is the only supported type):

```python
@prompt_template("... {:cache_control(type=ephemeral)}")
```

It is also possible to cache tools by setting the cache control on the tool's `ConfigDict`:

```python
from mirascope.core import BaseTool, ToolConfig

class CachedTool(BaseTool):
    ...

    tool_config = ToolConfig(cache_control={"type": "ephemeral"})

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
