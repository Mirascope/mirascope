# Langfuse

Mirascope provides out-of-the-box integration with [Langfuse](https://langfuse.com/).

You can install the necessary packages directly or using the `langfuse` extras flag:

```python
pip install "mirascope[langfuse]"
```

You can then use the `with_langfuse` decorator to automatically log calls:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="2 5"
            --8<-- "examples/integrations/langfuse/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

This will give you:

* A trace around the `recommend_book` function that captures items like the prompt template, and input/output attributes and more.
* Human-readable display of the conversation with the agent
* Details of the response, including the number of tokens used

??? info "Example trace"

    ![logfire-call](../assets/langfuse-call.png)

??? note "Handling streams"

    When logging streams, the span will not be logged until the stream has been exhausted. This is a function of how streaming works.

    You will also need to set certain `call_params` for usage to be tracked for certain providers (such as OpenAI).
