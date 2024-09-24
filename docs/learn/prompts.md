# Prompts

Prompts are the foundation of effective communication with Large Language Models (LLMs). Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions. This guide will walk you through the features and best practices for prompt engineering using Mirascope.

## What Are Prompts?

When working with Large Language Model (LLMs) APIs, the "prompt" is generally a list of messages where each message has a particular role.

First, let's take a look at a call to the OpenAI API for reference:

```python hl_lines="9"
--8<-- "examples/learn/prompts/what_are_prompts/single_user_message.py"
```

Here, the prompt is the messages array with a single user message. You can also specify multiple messages with different roles. For example, we can provide what is called a "system message" by first including a message with the system role:

```python hl_lines="9-12"
--8<-- "examples/learn/prompts/what_are_prompts/multiple_messages.py"
```

In these examples, we're only showing how to use the OpenAI API. One of the core values of Mirascope is that we offer tooling to make your prompts more reusable and work across the various different LLM providers.

Let's take a look at how we can write these same prompts in a provider-agnostic way.

!!! info "Calls will come later"

    For the following explanations we will be talking *only* about the messages aspect of prompt engineering and will discuss calling the API later in the [Calls](./calls.md) documentation.
    
    In that section we will show how to use these provider-agnostic prompts to actually call a provider's API as well as how to engineer and tie a prompt to a specific call.

## Prompt Templates (Messages)

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

    [`mirascope.core.base.prompt.prompt_template`](../api/core/base/prompt.md#mirascope.core.base.prompt.prompt_template)

The core concept to understand here is [`BaseMessageParam`](../api/core/base/message_param.md#basemessageparam). This class operates as the base class for message parameters that Mirascope can handle and use across all supported providers.

In Mirascope, we use the `@prompt_template` decorator to write prompt templates as reusable methods. Let's look at a basic example:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="4-6 10"
        --8<-- "examples/learn/prompts/prompt_templates/single_user_message/shorthand.py"
        ```

    === "Messages"

        ```python hl_lines="4-6 10"
        --8<-- "examples/learn/prompts/prompt_templates/single_user_message/messages.py"
        ```

    === "String Template"

        ```python hl_lines="4-5 9"
        --8<-- "examples/learn/prompts/prompt_templates/single_user_message/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="4-6 10"
        --8<-- "examples/learn/prompts/prompt_templates/single_user_message/base_message_param.py"
        ```

In this example:

1. The `recommend_book_prompt` method's signature defines the prompt's template variables.
2. Calling the method with `genre="fantasy"` returns a list with the corresponding `BaseMessageParam` instance with role `user` and content "Recommend a fantasy book".

As before, we can also define additional messages with different roles:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="7-8 14-15"
        --8<-- "examples/learn/prompts/prompt_templates/multiple_messages/shorthand.py"
        ```

    === "Messages"

        ```python hl_lines="7-8 14-15"
        --8<-- "examples/learn/prompts/prompt_templates/multiple_messages/messages.py"
        ```

    === "String Template"

        ```python hl_lines="6-7 15-16"
        --8<-- "examples/learn/prompts/prompt_templates/multiple_messages/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="7-8 14-15"
        --8<-- "examples/learn/prompts/prompt_templates/multiple_messages/base_message_param.py"
        ```

And that's it! Prompts written in this functional way are provider-agnostic, reusable, and properly typed, making them easier to write and maintain.

!!! note "`Messages.Type`"

    The return type `Messages.Type` accepts all shorthand methods as well as `BaseMessageParam` types. Since the message methods (e.g. `Messages.User`) return `BaseMessageParam` instances, we generally recommend always typing your prompt templates with the `Messages.Type` return type since it covers all prompt template writing methods.

!!! info "Supported Roles"

    Mirascope prompt templates currently support the `system`, `user`, and `assistant` roles. When using string templates, the roles are parsed by their corresponding all caps keyword (e.g. SYSTEM).

    For messages with the `tool` role, see how Mirascope automatically generates these messages for you in the [Tools](./tools.md) and [Agents](./agents.md) sections.

## Multi-Line Prompts

When writing prompts that span multiple lines, it's important to ensure you don't accidentally include additional, unnecessary tokens (namely `\t` tokens):

!!! mira ""

    === "Shorthand"

        ```python hl_lines="8-13 17"
        --8<-- "examples/learn/prompts/prompt_templates/multi_line/shorthand.py"
        ```

    === "Messages"

        ```python hl_lines="9-14 19"
        --8<-- "examples/learn/prompts/prompt_templates/multi_line/messages.py"
        ```

    === "String Template"

        ```python hl_lines="6-7 14"
        --8<-- "examples/learn/prompts/prompt_templates/multi_line/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="11-16 22"
        --8<-- "examples/learn/prompts/prompt_templates/multi_line/base_message_param.py"
        ```

In this example, we use `inspect.cleandoc` to remove unnecessary tokens while maintaining proper formatting in our codebase.

??? warning "Multi-Line String Templates"

    When using string templates, the template is automatically cleaned for you, so there is no need to use `inspect.cleandoc` in that case. However, it's extremely important to note that you must start messages with the same indentation in order to properly remove the unnecessary tokens. For example:

    ```python
    # BAD
    @prompt_template(
        """
        USER: First line
        Second line
        """
    )

    # GOOD
    @prompt_template(
        """
        USER:
        First line
        Second line
        """
    )
    ```

## Multi-Modal Inputs

Recent advancements in Large Language Model architecture has enabled many model providers to support multi-modal inputs (text, images, audio, etc.) for a single endpoint. Mirascope treats these input types as first-class and supports them natively.

While Mirascope provides a consistent interface, support varies among providers:

| Type          | Anthropic | Cohere | Gemini | Groq | Mistral | OpenAI |
|---------------|-----------|--------|--------|------|---------|--------|
| text          | ✓         | ✓      | ✓      | ✓    | ✓       | ✓      |
| image         | ✓         | -      | ✓      | ✓    | ✓       | ✓      |
| audio         | -         | -      | ✓      | -    | -       | -      |
| video         | -         | -      | ✓      | -    | -       | -      |

Legend: ✓ (Supported), - (Not Supported)

### Image Inputs

!!! mira ""

    === "Shorthand"

        ```python hl_lines="7 16-18"
        --8<-- "examples/learn/prompts/prompt_templates/multi_modal/image/shorthand.py"
        ```

    === "Messages"

        ```python hl_lines="8 18-20"
        --8<-- "examples/learn/prompts/prompt_templates/multi_modal/image/messages.py"
        ```

    === "String Template"

        ```python hl_lines="5 15-17"
        --8<-- "examples/learn/prompts/prompt_templates/multi_modal/image/string_template.py"
        ```

    === "BaseMessageParam"
    
        ```python hl_lines="10-17 28-30"
        --8<-- "examples/learn/prompts/prompt_templates/multi_modal/image/base_message_param.py"
        ```

??? info "Additional String Template Image Functionality"

    When using string templates, you can also specify `:images` to inject multiple image inputs through a single template variable.

    The `:image` and `:images` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

    You can also specify additional options as arguments of the tags, e.g. `{url:image(detail=low)}`

### Audio Inputs

!!! mira ""

    === "Shorthand"

        ```python
        # Coming soon
        ```

    === "Messages"

        ```python
        # Coming soon
        ```

    === "String Template"

        ```python hl_lines="4 13-15"
        --8<-- "examples/learn/prompts/prompt_templates/multi_modal/audio/string_template.py"
        ```

    === "BaseMessageParam"
    
        ```python hl_lines="10-16 27-29"
        --8<-- "examples/learn/prompts/prompt_templates/multi_modal/audio/base_message_param.py"
        ```

??? info "Additional String Template Audio Functionality"

    When using string templates, you can also specify `:audios` to inject multiple audio inputs through a single template variable.

    The `:audio` and `:audios` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

## Chat History

Often you'll want to inject messages (such as previous chat messages) into the prompt. Generally you can just unroll the messages into the return value of your prompt template. When using string templates, we provide a `MESSAGES` keyword for this injection, which you can add in whatever position and as many times as you'd like:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="6 10-11 15-18"
        --8<-- "examples/learn/prompts/prompt_templates/chat_history/shorthand.py"
        ```
    
    === "Messages"

        ```python hl_lines="6 10-11 15-18"
        --8<-- "examples/learn/prompts/prompt_templates/chat_history/messages.py"
        ```

    === "String Template"

        ```python hl_lines="6-8 15-16 20-23"
        --8<-- "examples/learn/prompts/prompt_templates/chat_history/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="7-9 14-15 19-22"
        --8<-- "examples/learn/prompts/prompt_templates/chat_history/base_message_param.py"
        ```

## Object Attribute Access

When using template variables that have attributes, you can easily inject these attributes directly even when using string templates:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="12 17"
        --8<-- "examples/learn/prompts/prompt_templates/object_attribute_access/shorthand.py"
        ```
    
    === "Messages"

        ```python hl_lines="13 19"
        --8<-- "examples/learn/prompts/prompt_templates/object_attribute_access/messages.py"
        ```

    === "String Template"

        ```python hl_lines="10 16"
        --8<-- "examples/learn/prompts/prompt_templates/object_attribute_access/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="15 22"
        --8<-- "examples/learn/prompts/prompt_templates/object_attribute_access/base_message_param.py"
        ```

It's worth noting that this also works with `self` when using prompt templates inside of a class, which is particularly important when building [Agents](./agents.md).

## Format Specifiers

Since Mirascope prompt templates are just formatted strings, standard Python format specifiers work as expected:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="6 10"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/float_format/shorthand.py"
        ```
    
    === "Messages"

        ```python hl_lines="6 10"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/float_format/messages.py"
        ```

    === "String Template"

        ```python hl_lines="4 9"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/float_format/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="8 14"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/float_format/base_message_param.py"
        ```

When writing string templates, we also offer additional `list` and `lists` format specifiers for convenience around formatting lists:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="8-9 13 16 32 38-48"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/lists_format/shorthand.py"
        ```
    
    === "Messages"

        ```python hl_lines="10-11 16 19 36 42-52"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/lists_format/messages.py"
        ```

    === "String Template"

        ```python hl_lines="7 10 27 33-43"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/lists_format/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="10-11 18 21 39 45-55"
        --8<-- "examples/learn/prompts/prompt_templates/format_specifiers/lists_format/base_message_param.py"
        ```

## Computed Fields (Dynamic Configuration)

In Mirascope, we write prompt templates as functions, which enables dynamically configuring our prompts at runtime depending on the values of the template variables. We use the term "computed fields" to talk about variables that are computed and formatted at runtime.

In the following examples, we demonstrate using computed fields and dynamic configuration across all prompt templating methods. Of course, this is only actually necessary for string templates. For other methods you can simply format the computed fields directly and return `Messages.Type` as before.

However, there is value in always dynamically configuring computed fields for any and all prompt templating methods. While we cover this in more detail in the [Calls](./calls.md) and [Chaining](./chaining.md) sections, the short of it is that it enables proper tracing even across nested calls and chains.

!!! mira ""

    === "Shorthand"

        ```python hl_lines="6-7 9-10 16-17"
        --8<-- "examples/learn/prompts/prompt_templates/computed_fields/shorthand.py"
        ```
    
    === "Messages"

        ```python hl_lines="6-7 9-10 16-17"
        --8<-- "examples/learn/prompts/prompt_templates/computed_fields/messages.py"
        ```

    === "String Template"

        ```python hl_lines="4 6 8 13"
        --8<-- "examples/learn/prompts/prompt_templates/computed_fields/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="6 8 11-12 19-20"
        --8<-- "examples/learn/prompts/prompt_templates/computed_fields/base_message_param.py"
        ```

There are various other parts of an LLM API call that we may want to configure dynamically as well, such as call parameters, tools, and more. We cover such cases in each of their respective sections.

## Next Steps

By mastering prompts in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend taking a look at the [Calls](./calls.md) documentation, which shows you how to use your prompt templates to actually call LLM APIs and generate a response.
