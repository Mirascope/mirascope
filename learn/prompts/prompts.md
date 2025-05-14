---
search:
  boost: 3
---

# Prompts

When working with Large Language Model (LLM) APIs, the "prompt" is generally a list of messages where each message has a particular role. These prompts are the foundation of effectively working with LLMs, so Mirascope provides powerful tools to help you create, manage, and optimize your prompts for various LLM interactions.

Let's look at how we can write prompts using Mirascope in a reusable, modular, and provider-agnostic way.

!!! info "Calls will come later"

    For the following explanations we will be talking *only* about the messages aspect of prompt engineering and will discuss calling the API later in the [Calls](./calls.md) documentation.
    
    In that section we will show how to use these provider-agnostic prompts to actually call a provider's API as well as how to engineer and tie a prompt to a specific call.

## Prompt Templates (Messages)

??? api "API Documentation"

    [`mirascope.core.base.message_param`](../api/core/base/message_param.md)

    [`mirascope.core.base.prompt.prompt_template`](../api/core/base/prompt.md#mirascope.core.base.prompt.prompt_template)

First, let's look at a basic example:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="4-5 9"
        {% else %}
        ```python hl_lines="4-6 10"
        {% endif %}
        --8<-- "examples/learn/prompts/single_user_message/{{ method }}.py"
        ```
    {% endfor %}

In this example:

1. The `recommend_book_prompt` method's signature defines the prompt's template variables.
2. Calling the method with `genre="fantasy"` returns a list with the corresponding `BaseMessageParam` instance with role `user` and content "Recommend a fantasy book".

The core concept to understand here is [`BaseMessageParam`](../api/core/base/message_param.md#basemessageparam). This class operates as the base class for message parameters that Mirascope can handle and use across all supported providers.

In Mirascope, we use the `@prompt_template` decorator to write prompt templates as reusable methods that return the corresponding list of `BaseMessageParam` instances.

There are four methods of writing prompts:

1. _(Shorthand)_ Returning the `str` or `list` content for a single user message.
2. _(Messages)_ Using `Messages.{Role}` methods, which accept the full or shorthand content and output a `BaseMessageParam` instance.
3. _(String Template)_ Passing a string template to `@prompt_template` that gets parsed and then formatted like a normal Python formatted string.
4. _(BaseMessageParam)_ Directly writing `BaseMessageParam` instances.

Which method you use is mostly up to your preference, so feel free to select which one you prefer in the following sections.

## Message Roles

We can also define additional messages with different roles, such as a system message:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="6-7 15-16"
        {% else %}
        ```python hl_lines="7-8 14-15"
        {% endif %}
        --8<-- "examples/learn/prompts/multiple_messages/{{ method }}.py"
        ```
    {% endfor %}

!!! note "`Messages.Type`"

    The return type `Messages.Type` accepts all shorthand methods as well as `BaseMessageParam` types. Since the message methods (e.g. `Messages.User`) return `BaseMessageParam` instances, we generally recommend always typing your prompt templates with the `Messages.Type` return type since it covers all prompt template writing methods.

!!! info "Supported Roles"

    Mirascope prompt templates currently support the `system`, `user`, and `assistant` roles. When using string templates, the roles are parsed by their corresponding all caps keyword (e.g. SYSTEM).

    For messages with the `tool` role, see how Mirascope automatically generates these messages for you in the [Tools](./tools.md) and [Agents](./agents.md) sections.

## Multi-Line Prompts

When writing prompts that span multiple lines, it's important to ensure you don't accidentally include additional, unnecessary tokens (namely `\t` tokens):

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "shorthand" %}
        ```python hl_lines="8-13 17"
        {% elif method == "messages" %}
        ```python hl_lines="9-14 19"
        {% elif method == "string_template" %}
        ```python hl_lines="6-7 14"
        {% else %}
        ```python hl_lines="11-16 22"
        {% endif %}
        --8<-- "examples/learn/prompts/multi_line/{{ method }}.py"
        ```
    {% endfor %}

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

| Type          | Anthropic | Cohere | Google Gemini | Groq | Mistral | OpenAI |
|---------------|-----------|--------|---------------|------|---------|--------|
| text          | ✓         | ✓      | ✓             | ✓    | ✓       | ✓      |
| image         | ✓         | -      | ✓             | ✓    | ✓       | ✓      |
| audio         | -         | -      | ✓             | -    | -       | ✓      |
| video         | -         | -      | ✓             | -    | -       | -      |
| document      | ✓         | -      | -             | -    | -       | -      |

Legend: ✓ (Supported), - (Not Supported)

### Image Inputs

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "shorthand" %}
        ```python hl_lines="7 16-18"
        {% elif method == "messages" %}
        ```python hl_lines="8 18-20"
        {% elif method == "string_template" %}
        ```python hl_lines="5 15-17"
        {% else %}
        ```python hl_lines="9-16 27-29"
        {% endif %}
        --8<-- "examples/learn/prompts/multi_modal/image/{{ method }}.py"
        ```
    {% endfor %}

??? info "Additional String Template Image Functionality"

    When using string templates, you can also specify `:images` to inject multiple image inputs through a single template variable.

    The `:image` and `:images` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

    You can also specify additional options as arguments of the tags, e.g. `{url:image(detail=low)}`

### Audio Inputs

!!! mira ""

    {% for audio_pkg in ["pydub", "wave"] %}
    === "{{ audio_pkg }}"
        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"
            {% if method == "string_template" %}
            ```python hl_lines="4 13-15"
            {% elif method == "base_message_param" %}
            ```python hl_lines="9-15 26-28"
            {% elif method == "messages" %}
            ```python hl_lines="9 19-21"
            {% else %}
            ```python hl_lines="8 17-19"
            {% endif %}
            --8<-- "examples/learn/prompts/multi_modal/audio/{{ audio_pkg }}/{{ method }}.py"
            ```
        {% endfor %}
    {% endfor %}

??? info "Additional String Template Audio Functionality"

    When using string templates, you can also specify `:audios` to inject multiple audio inputs through a single template variable.

    The `:audio` and `:audios` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

### Document Inputs

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="5 15-17"
        {% elif method == "base_message_param" %}
        ```python hl_lines="9-15 26-28"
        {% else %}
        ```python hl_lines="8-14 24-26"
        {% endif %}
        --8<-- "examples/learn/prompts/multi_modal/document/{{ method }}.py"
        ```
    {% endfor %}

!!! warning "Support Document Types"

    Currently, only Anthropic supports the `:document` specifier, and only PDF documents are supported.

??? info "Additional String Template Document Functionality"

    When using string templates, you can also specify `:documents` to inject multiple document inputs through a single template variable.

    The `:document` and `:documents` tags support the `bytes | str` and `list[bytes] | list[str]` types, respectively. When passing in a `str`, the string template assumes it indicates a url or local filepath and will attempt to load the bytes from the source.

## Chat History

Often you'll want to inject messages (such as previous chat messages) into the prompt. Generally you can just unroll the messages into the return value of your prompt template. When using string templates, we provide a `MESSAGES` keyword for this injection, which you can add in whatever position and as many times as you'd like:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="6-8 15-16 20-23"
        {% elif method == "base_message_param" %}
        ```python hl_lines="7-9 14-15 19-22"
        {% else %}
        ```python hl_lines="6 10-11 15-18"
        {% endif %}
        --8<-- "examples/learn/prompts/chat_history/{{ method }}.py"
        ```
    {% endfor %}

## Object Attribute Access

When using template variables that have attributes, you can easily inject these attributes directly even when using string templates:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "shorthand" %}
        ```python hl_lines="12 17"
        {% elif method == "messages" %}
        ```python hl_lines="13 19"
        {% elif method == "string_template" %}
        ```python hl_lines="10 16"
        {% else %}
        ```python hl_lines="15 22"
        {% endif %}
        --8<-- "examples/learn/prompts/object_attribute_access/{{ method }}.py"
        ```
    {% endfor %}

It's worth noting that this also works with `self` when using prompt templates inside of a class, which is particularly important when building [Agents](./agents.md).

## Format Specifiers

Since Mirascope prompt templates are just formatted strings, standard Python format specifiers work as expected:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="4 9"
        {% elif method == "base_message_param" %}
        ```python hl_lines="8 14"
        {% else %}
        ```python hl_lines="6 10"
        {% endif %}
        --8<-- "examples/learn/prompts/format_specifiers/float_format/{{ method }}.py"
        ```
    {% endfor %}

When writing string templates, we also offer additional format specifiers for convenience around formatting more dynamic content:

!!! mira ""

    {% for title, filename in [("List(s)", "lists"), ("Text(s)", "texts"), ("Part(s)", "parts")] %}
    === "{{ title }}"

        {% if filename == "lists" %}
        ```python hl_lines="7 10 17-21 26-36"
        {% elif filename == "texts" %}
        ```python hl_lines="7 10 17-21 26-32"
        {% else %}
        ```python hl_lines="7 10 17-21 26-32"
        {% endif %}
        --8<-- "examples/learn/prompts/format_specifiers/{{ filename }}.py"
        ```
    {% endfor %}

## Computed Fields (Dynamic Configuration)

In Mirascope, we write prompt templates as functions, which enables dynamically configuring our prompts at runtime depending on the values of the template variables. We use the term "computed fields" to talk about variables that are computed and formatted at runtime.

In the following examples, we demonstrate using computed fields and dynamic configuration across all prompt templating methods. Of course, this is only actually necessary for string templates. For other methods you can simply format the computed fields directly and return `Messages.Type` as before.

However, there is value in always dynamically configuring computed fields for any and all prompt templating methods. While we cover this in more detail in the [Calls](./calls.md) and [Chaining](./chaining.md) sections, the short of it is that it enables proper tracing even across nested calls and chains.

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="4 6 8 13"
        {% elif method == "base_message_param" %}
        ```python hl_lines="6 8 11-12 19-20"
        {% else %}
        ```python hl_lines="6-7 9-10 16-17"
        {% endif %}
        --8<-- "examples/learn/prompts/computed_fields/{{ method }}.py"
        ```
    {% endfor %}

There are various other parts of an LLM API call that we may want to configure dynamically as well, such as call parameters, tools, and more. We cover such cases in each of their respective sections.

## Next Steps

By mastering prompts in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend taking a look at the [Calls](./calls.md) documentation, which shows you how to use your prompt templates to actually call LLM APIs and generate a response.
