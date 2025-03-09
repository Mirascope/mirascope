---
search:
  boost: 2
---

# Response Models

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Response Models in Mirascope provide a powerful way to structure and validate the output from Large Language Models (LLMs). By leveraging Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), Response Models offer type safety, automatic validation, and easier data manipulation for your LLM responses. While we cover some details in this documentation, we highly recommend reading through Pydantic's documentation for a deeper, comprehensive dive into everything you can do with Pydantic's `BaseModel`.

## Why Use Response Models?

1. **Structured Output**: Define exactly what you expect from the LLM, ensuring consistency in responses.
2. **Automatic Validation**: Pydantic handles type checking and validation, reducing errors in your application.
3. **Improved Type Hinting**: Better IDE support and clearer code structure.
4. **Easier Data Manipulation**: Work with Python objects instead of raw strings or dictionaries.

## Basic Usage and Syntax

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="12 19"
            --8<-- "build/snippets/learn/response_models/basic_usage/{{ provider | provider_dir }}/{{ method }}.py:3:21"
            ```
        {% endfor %}

    {% endfor %}

??? note "Official SDK"

    {% for provider in supported_llm_providers %}
    === "{{ provider }}"

        {% if provider == "Anthropic" %}
        ```python hl_lines="19-38 43"
        {% elif provider == "Mistral" %}
        ```python hl_lines="21-46 51"
        {% elif provider == "Google" %}
        ```python hl_lines="21-60 65"
        {% elif provider == "Cohere" %}
        ```python hl_lines="19-36 41"
        {% elif provider == "LiteLLM" %}
        ```python hl_lines="16-37 42"
        {% elif provider == "Azure AI" %}
        ```python hl_lines="26-46 51"
        {% elif provider == "Bedrock" %}
        ```python hl_lines="16-48 53"
        {% else %}
        ```python hl_lines="18-39 44"
        {% endif %}
        --8<-- "examples/learn/response_models/basic_usage/official_sdk/{{ provider | provider_dir }}_sdk.py"
        ```

    {% endfor %}

Notice how Mirascope makes generating structured outputs significantly simpler than the official SDKs. It also greatly reduces boilerplate and standardizes the interaction across all supported LLM providers.

!!! info "Tools By Default"

    By default, `response_model` will use [Tools](./tools.md) under the hood, forcing to the LLM to call that specific tool and constructing the response model from the tool's arguments.

    We default to using tools because all supported providers support tools. You can also optionally set `json_mode=True` to use [JSON Mode](./json_mode.md) instead, which we cover in [more detail below](#json-mode).

### Accessing Original Call Response

Every `response_model` that uses a Pydantic `BaseModel` will automatically have the original `BaseCallResponse` instance accessible through the `_response` property:

!!! mira "Mirascope"

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="1 23-25"
            --8<-- "build/snippets/learn/response_models/basic_usage/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

### Built-In Types

For cases where you want to extract just a single built-in type, Mirascope provides a shorthand:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="4 16"
            --8<-- "build/snippets/learn/response_models/builtin_types/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

Here, we are using `list[str]` as the `response_model`, which Mirascope handles without needing to define a full `BaseModel`. You could of course set `response_model=list[Book]` as well.

Note that we have no way of attaching `BaseCallResponse` to built-in types, so using a Pydantic `BaseModel` is recommended if you anticipate needing access to the original call response.

## Supported Field Types

While Mirascope provides a consistent interface, type support varies among providers:

|     Type      | OpenAI | Anthropic | Google | Groq | xAI | Mistral | Cohere |
|---------------|--------|-----------|--------|------|-----|---------|--------|
|     str       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     int       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|    float      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bool      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bytes     |✓✓|✓✓|-✓|✓✓|✓✓|✓✓|✓✓|
|     list      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     set       |✓✓|✓✓|--|✓✓|✓✓|✓✓|✓✓|
|     tuple     |-✓|✓✓|-✓|✓✓|-✓|✓✓|✓✓|
|     dict      |-✓|✓✓|✓✓|✓✓|-✓|✓✓|✓✓|
|  Literal/Enum |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|   BaseModel   |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|-✓|
| Nested ($def) |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|--|

✓✓ : Fully Supported, -✓: Only JSON Mode Support, -- : Not supported

## Validation and Error Handling

While `response_model` significantly improves output structure and validation, it's important to handle potential errors.

Let's take a look at an example where we want to validate that all fields are uppercase:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="1 4 7-9 15-16 24 28"
            --8<-- "build/snippets/learn/response_models/validation/{{ provider | provider_dir }}/{{ method }}.py::36"
            ```
        {% endfor %}

    {% endfor %}

Without additional prompt engineering, this call will fail every single time. It's important to engineer your prompts to reduce errors, but LLMs are far from perfect, so always remember to catch and handle validation errors gracefully.

We highly recommend taking a look at our section on [retries](./retries.md) to learn more about automatically retrying and re-inserting validation errors, which enables retrying the call such that the LLM can learn from its previous mistakes.

### Accessing Original Call Response On Error

In case of a `ValidationError`, you can access the original response for debugging:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="28-31"
            --8<-- "build/snippets/learn/response_models/validation/{{ provider | provider_dir }}/{{ method }}.py::28"
            --8<-- "build/snippets/learn/response_models/validation/{{ provider | provider_dir }}/{{ method }}.py:37:39"
            ```
        {% endfor %}

    {% endfor %}

This allows you to gracefully handle errors as well as inspect the original LLM response when validation fails.

## JSON Mode

By default, `response_model` uses [Tools](./tools.md) under the hood. You can instead use [JSON Mode](./json_mode.md) in conjunction with `response_model` by setting `json_mode=True`:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"
            ```python hl_lines="12"
            --8<-- "build/snippets/learn/response_models/json_mode/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Few-Shot Examples

Adding few-shot examples to your response model can improve results by demonstrating exactly how to adhere to your desired output.

We take advantage of Pydantic's [`Field`](https://docs.pydantic.dev/latest/concepts/fields/) and [`ConfigDict`](https://docs.pydantic.dev/latest/concepts/config/) to add these examples to response models:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"
            {% if method == "messages" %}
            ```python hl_lines="6-7 11-13 27"
            {% elif method == "base_message_param" %}
            ```python hl_lines="6-7 11-13 30"
            {% else %}
            ```python hl_lines="6-7 11-13 25"
            {% endif %}
            --8<-- "build/snippets/learn/response_models/few_shot_examples/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Streaming Response Models

If you set `stream=True` when `response_model` is set, your LLM call will return an `Iterable` where each item will be a partial version of your response model representing the current state of the streamed information. The final model returned by the iterator will be the full response model.

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"
            {% if provider == "Bedrock" %}
            ```python hl_lines="11 18-19"
            {% else %}
            ```python hl_lines="10 16-17"
            {% endif %}
            --8<-- "build/snippets/learn/response_models/streaming/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

Once exhausted, you can access the final, full response model through the `constructed_response_model` property of the structured stream. Note that this will also give you access to the [`._response` property](#accessing-original-call-response) that every `BaseModel` receives.

You can also use the `stream` property to access the `BaseStream` instance and [all of it's properties](./streams.md#common-stream-properties-and-methods).

## FromCallArgs

Fields annotated with `FromCallArgs` will be populated with the corresponding argument from the function call rather than expecting it from the LLM's response. This enables seamless validation of LLM outputs against function inputs:

!!! mira "Mirascope"

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="15 27"
            {% else %}
            ```python hl_lines="15 26"
            {% endif %}
            --8<-- "build/snippets/learn/response_models/from_call_args/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Next Steps

By following these best practices and leveraging Response Models effectively, you can create more robust, type-safe, and maintainable LLM-powered applications with Mirascope.

Next, we recommend taking a lookg at one of:

- [JSON Mode](./json_mode.md) to see an alternate way to generate structured outputs where using Pydantic to validate outputs is optional.
- [Evals](./evals.md) to see how to use `response_model` to evaluate your prompts.
