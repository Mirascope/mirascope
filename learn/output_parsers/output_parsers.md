---
search:
  boost: 2
---

# Output Parsers

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Output Parsers in Mirascope provide a flexible way to process and structure the raw output from Large Language Models (LLMs). They allow you to transform the LLM's response into a more usable format, enabling easier integration with your application logic and improving the overall reliability of your LLM-powered features.

## Basic Usage and Syntax

??? api "API Documentation"

    {% for provider in supported_llm_providers %}
    [`mirascope.core.{{ provider | provider_dir }}.call.output_parser`](../api/core/{{ provider | provider_dir }}/call.md?h=output_parser)
    {% endfor %}

Output Parsers are functions that take the call response object as input and return an output of a specified type. When you supply an output parser to a `call` decorator, it modifies the return type of the decorated function to match the output type of the parser.

Let's take a look at a basic example:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"
            {% if method == "base_message_param" %}
            {% if provider == "Bedrock" %}
            ```python hl_lines="10 22"
            {% else %}
            ```python hl_lines="9 20"
            {% endif %}
            {% else %}
            {% if provider == "Bedrock" %} 
            ```python hl_lines="10 17"
            {% else %}
            ```python hl_lines="9 15"
            {% endif %}
            {% endif %}
            --8<-- "build/snippets/learn/output_parsers/basic_usage/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Additional Examples

There are many different ways to structure and parse LLM outputs, ranging from XML parsing to using regular expressions.

Here are a few examples:

!!! mira ""

    === "Regular Expression"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="7 14 17 18"
            --8<-- "build/snippets/learn/output_parsers/additional_examples/{{ provider | provider_dir }}/regex.py"
            ```

        {% endfor %}


    === "XML"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="14-28 31 35-40"
            --8<-- "build/snippets/learn/output_parsers/additional_examples/{{ provider | provider_dir }}/xml.py"
            ```

        {% endfor %}

    === "JSON Mode"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="7-9 12-14"
            --8<-- "build/snippets/learn/output_parsers/additional_examples/{{ provider | provider_dir }}/json_mode.py"
            ```

        {% endfor %}

## Next Steps

By leveraging Output Parsers effectively, you can create more robust and reliable LLM-powered applications, ensuring that the raw model outputs are transformed into structured data that's easy to work with in your application logic.

Next, we recommend taking a look at the section on [Tools](./tools.md) to learn how to extend the capabilities of LLMs with custom functions.
