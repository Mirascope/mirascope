# Provider-Specific Features

While Mirascope provides a provider-agnostic interface for as many features as possible, there are inevitably features that not all providers support.

Often these provider-specific features are powerful and worth using, so we try our best to provide support for such features, which we have documented here.

If there are any features in particular that you want to use that are not currently supported, let us know!

## OpenAI

### Structured Outputs

OpenAI's newest models (starting with `gpt-4o-2024-08-06`) support [strict structured outputs](https://platform.openai.com/docs/guides/structured-outputs) that reliably adhere to developer-supplied JSON Schemas, achieving 100% reliability in their evals, perfectly matching the desired output schemas.

This feature can be extremely useful when extracting structured information or using tools, and you can access this feature when using tools or response models with Mirascope.

#### Tools

To use structured outputs with tools, use the `OpenAIToolConfig` and set `strict=True`. You can then use the tool as described in our [Tools documentation](./tools.md):

!!! mira ""

    ```python hl_lines="9"
    --8<-- "examples/learn/provider_specific_features/openai/structured_outputs/tools.py"
    ```

Under the hood, Mirascope generates a JSON Schema for the `FormatBook` tool based on its attributes and the `OpenAIToolConfig`. This schema is then used by OpenAI's API to ensure the model's output strictly adheres to the defined structure.

#### Response Models

Similarly, you can use structured outputs with response models by setting `strict=True` in the response model's `ResponseModelConfigDict`, which is just a subclass of Pydantic's `ConfigDict` with the addition of the `strict` key. You will also need to set `json_mode=True`:

!!! mira ""

    ```python hl_lines="9"
    --8<-- "examples/learn/provider_specific_features/openai/structured_outputs/response_model.py"
    ```

## Anthropic

### Prompt Caching

Anthropic's prompt caching feature can help save a lot of tokens by caching parts of your prompt. For full details, we recommend reading [their documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).

!!! warning "This Feature Is In Beta"

    While we've added support for prompt caching with Anthropic, this feature is still in beta and requires setting extra headers. You can set this header as an additional call parameter.

    As this feature is in beta, there may be changes made by Anthropic that may result in changes in our own handling of this feature.

#### Message Caching

To cache messages, simply add a `:cache_control` tagged breakpoint to your prompt:

!!! mira ""

    ```python hl_lines="8 19"
    --8<-- "examples/learn/provider_specific_features/anthropic/caching/messages.py"
    ```

??? info "Additional options"

    You can also specify the cache control type the same way we support additional options for multimodal parts (although currently `"ephemeral"` is the only supported type):

    ```python
    @prompt_template("... {:cache_control(type=ephemeral)}")
    ```

#### Tool Caching

It is also possible to cache tools by using the `AnthropicToolConfig` and setting the cache control:

!!! mira ""

    ```python hl_lines="8 16 19"
    --8<-- "examples/learn/provider_specific_features/anthropic/caching/tools.py"
    ```

Remember only to include the cache control on the last tool in your list of tools that you want to cache (as all tools up to the tool with a cache control breakpoint will be cached).
