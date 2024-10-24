# Anthropic-Specific Features

## Prompt Caching

Anthropic's prompt caching feature can help save a lot of tokens by caching parts of your prompt. For full details, we recommend reading [their documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).

!!! warning "This Feature Is In Beta"

    While we've added support for prompt caching with Anthropic, this feature is still in beta and requires setting extra headers. You can set this header as an additional call parameter.

    As this feature is in beta, there may be changes made by Anthropic that may result in changes in our own handling of this feature.

### Message Caching

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

### Tool Caching

It is also possible to cache tools by using the `AnthropicToolConfig` and setting the cache control:

!!! mira ""

    ```python hl_lines="8 16 19"
    --8<-- "examples/learn/provider_specific_features/anthropic/caching/tools.py"
    ```

Remember only to include the cache control on the last tool in your list of tools that you want to cache (as all tools up to the tool with a cache control breakpoint will be cached).
