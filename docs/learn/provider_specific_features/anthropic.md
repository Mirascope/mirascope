# Anthropic-Specific Features

## Prompt Caching

Anthropic's prompt caching feature can help save a lot of tokens by caching parts of your prompt. For full details, we recommend reading [their documentation](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).

!!! warning "This Feature Is In Beta"

    While we've added support for prompt caching with Anthropic, this feature is still in beta and requires setting extra headers. You can set this header as an additional call parameter.

    As this feature is in beta, there may be changes made by Anthropic that may result in changes in our own handling of this feature.

### Message Caching

To cache messages, simply add a `:cache_control` tagged breakpoint to your prompt:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="9 20"
        {% elif method == "base_message_param" %}
        ```python hl_lines="11 28"
        {% else %}
        ```python hl_lines="11 24"
        {% endif %}
        --8<-- "examples/learn/provider_specific_features/anthropic/caching/messages/{{ method }}.py"
        ```
    {% endfor %}

??? info "Additional options with string templates"

    When using string templates, you can also specify the cache control type the same way we support additional options for multimodal parts (although currently `"ephemeral"` is the only supported type):

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
