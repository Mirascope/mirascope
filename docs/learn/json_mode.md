---
search:
  boost: 2
---

# JSON Mode

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

JSON Mode is a feature in Mirascope that allows you to request structured JSON output from Large Language Models (LLMs). This mode is particularly useful when you need to extract structured information from the model's responses, making it easier to parse and use the data in your applications.

??? warning "Not all providers have an official JSON Mode"

    For providers with explicit support, Mirascope uses the native JSON Mode feature of the API. For providers without explicit support (e.g. Anthropic), Mirascope implements a pseudo JSON Mode by instructing the model in the prompt to output JSON.

    | Provider  | Support Type | Implementation      |
    |-----------|--------------|---------------------|
    | Anthropic | Pseudo       | Prompt engineering  |
    | Azure     | Explicit     | Native API feature  |
    | Bedrock   | Pseudo       | Prompt engineering  |
    | Cohere    | Pseudo       | Prompt engineering  |
    | Google    | Explicit     | Native API feature  |
    | Groq      | Explicit     | Native API feature  |
    | LiteLLM   | Explicit     | Native API feature  |
    | Mistral   | Explicit     | Native API feature  |
    | OpenAI    | Explicit     | Native API feature  |

    If you'd prefer not to have any internal updates made to your prompt, you can always set JSON mode yourself through `call_params` rather than using the `json_mode` argument, which provides provider-agnostic support but is certainly not required to use JSON mode.

## Basic Usage and Syntax

Let's take a look at a basic example using JSON Mode:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "base_message_param" %}
            ```python hl_lines="6 10 17"
            {% elif method == "string_template" %}
            ```python hl_lines="6 7 13"
            {% else %}
            ```python hl_lines="6 8 13"
            {% endif %}
            --8<-- "build/snippets/learn/json_mode/basic_usage/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

In this example we

1. Enable JSON Mode with `json_mode=True` in the `call` decorator
2. Instruct the model what fields to include in our prompt
3. Load the JSON string response into a Python object and print it

## Error Handling and Validation

While JSON Mode can signifanctly improve the structure of model outputs, it's important to note that it's far from infallible. LLMs often produce invalid JSON or deviate from the expected structure, so it's crucial to implement proper error handling and validation in your code:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "base_message_param" %}
            ```python hl_lines="15 18"
            {% else %}
            ```python hl_lines="11 14"
            {% endif %}
            --8<-- "build/snippets/learn/json_mode/error_handling/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

!!! warning "Beyond JSON Validation"

    While this example catches errors for invalid JSON, there's always a chance that the LLM returns valid JSON that doesn't conform to your expected schema (such as missing fields or incorrect types).

    For more robust validation, we recommend using [Response Models](./response_models.md) for easier structuring and validation of LLM outputs.

## Next Steps

By leveraging JSON Mode, you can create more robust and data-driven applications that efficiently process and utilize LLM outputs. This approach allows for easy integration with databases, APIs, or user interfaces, demonstrating the power of JSON Mode in creating robust, data-driven applications.

Next, we recommend reading the section on [Output Parsers](./output_parsers.md) to see how to engineer prompts with specific output structures and parse the outputs automatically on every call.
