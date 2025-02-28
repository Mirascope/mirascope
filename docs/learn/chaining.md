---
search:
  boost: 2
---

# Chaining

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Chaining in Mirascope allows you to combine multiple LLM calls or operations in a sequence to solve complex tasks. This approach is particularly useful for breaking down complex problems into smaller, manageable steps.

Before diving into Mirascope's implementation, let's understand what chaining means in the context of LLM applications:

1. **Problem Decomposition**: Breaking a complex task into smaller, manageable steps.
2. **Sequential Processing**: Executing these steps in a specific order, where the output of one step becomes the input for the next.
3. **Data Flow**: Passing information between steps to build up a final result.

## Basic Usage and Syntax

### Function Chaining

Mirascope is designed to be Pythonic. Since calls are defined as functions, chaining them together is as simple as chaining the function calls as you would normally:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="6 11 14-15"
            {% elif method == "base_message_param" %}
            ```python hl_lines="5 10 19-20"
            {% else %}
            ```python hl_lines="5 10 14-15"
            {% endif %}
            --8<-- "build/snippets/learn/chaining/function_chaining/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}
    {% endfor %}

One benefit of this approach is that you can chain your calls together any which way since they are just functions. You can then always wrap these functional chains in a parent function that operates as the single call to the chain.

### Nested Chains

In some cases you'll want to prompt engineer an entire chain rather than just chaining together individual calls. You can do this simply by calling the subchain inside the function body of the parent:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="6 10 12 15"
            {% elif method == "base_message_param" %}
            ```python hl_lines="5 11 15 20"
            {% else %}
            ```python hl_lines="5 11-12 15"
            {% endif %}
            --8<-- "build/snippets/learn/chaining/nested_chains/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}
    {% endfor %}

We recommend using nested chains for better observability when using tracing tools or applications.

??? tip "Improved tracing through computed fields"

    If you use computed fields in your nested chains, you can always access the computed field in the response. This provides improved tracing for your chains from a single call. 

    !!! mira ""

        {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
        === "{{ method_title }}"

            {% for provider in supported_llm_providers %}
            === "{{ provider }}"

                {% if method == "string_template" %}
                ```python hl_lines="12 18-19"
                {% elif method == "base_message_param" %}
                ```python hl_lines="19 26-27"
                {% else %}
                ```python hl_lines="16 23-24"
                {% endif %}
                --8<-- "build/snippets/learn/chaining/computed_fields/{{ provider | provider_dir }}/{{ method }}.py"
                ```
            {% endfor %}
        {% endfor %}

## Advanced Chaining Techniques

There are many different ways to chain calls together, often resulting in breakdowns and flows that are specific to your task.

Here are a few examples:

!!! mira ""

    === "Conditional"

        ```python
        --8<-- "examples/learn/chaining/advanced_techniques/conditional_chaining.py"
        ```

    === "Parallel"

        ```python
        --8<-- "examples/learn/chaining/advanced_techniques/parallel_chaining.py"
        ```

    === "Iterative"

        ```python
        --8<-- "examples/learn/chaining/advanced_techniques/iterative_chaining.py"
        ```

[Response Models](./response_models.md) are a great way to add more structure to your chains, and [parallel async calls](./async.md#parallel-async-calls) can be particularly powerful for making your chains more efficient.

For inspiration on even more ways you can chain calls together, check out our tutorial section on [chaining-based prompt engineering](../tutorials/prompt_engineering/chaining_based/self_refine.ipynb), which covers many advanced chaining techniques used to apply prompt engineering concepts.

## Next Steps

By mastering Mirascope's chaining techniques, you can create sophisticated LLM-powered applications that tackle complex, multi-step problems with greater accuracy, control, and observability.

Next, we recommend taking a look at the [Response Models](./response_models.md) documentation, which shows you how to generate structured outputs.
