# Logfire

[Logfire](https://docs.pydantic.dev/logfire/), a new tool from Pydantic, is built on OpenTelemetry. Since Pydantic powers many of Mirascope's features, it's appropriate for us to ensure seamless integration with them.

You can install the necessary packages directly or using the `logfire` extras flag:

```python
pip install "mirascope[logfire]"
```

You can then use the `with_logfire` decorator to automatically log calls:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="1 3 6 14"
            --8<-- "examples/integrations/logfire/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

This will give you:

* A span called `recommend_book` that captures items like the prompt template, templating properties and fields, and input/output attributes
* Human-readable display of the conversation with the agent
* Details of the response, including the number of tokens used

??? info "Example log"

    ![logfire-call](../assets/logfire-response-model.png)

??? note "Handling streams"

    When logging streams, the span will not be logged until the stream has been exhausted. This is a function of how streaming works.

    You will also need to set certain `call_params` for usage to be tracked for certain providers (such as OpenAI).
