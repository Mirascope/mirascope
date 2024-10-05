# HyperDX

Mirascope provides out-of-the-box integration with [HyperDX](https://www.hyperdx.io/).

You can install the necessary packages directly or using the `hyperdx` extras flag:

```python
pip install "mirascope[hyperdx]"
```

You can then use the `with_hyperdx` decorator to automatically log calls:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="2 5"
            --8<-- "examples/integrations/hyperdx/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

This decorator is a simple wrapper on top of our [OpenTelemetry integration](./otel.md)
