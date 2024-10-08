# Retries

Making an API call to a provider can fail due to various reasons, such as rate limits, internal server errors, validation errors, and more. This makes retrying calls extremely important when building robust systems.

Mirascope combined with [Tenacity](https://tenacity.readthedocs.io/en/latest/) increases the chance for these requests to succeed while maintaining end user transparency.

You can install the necessary packages directly or use the `tenacity` extras flag:

```python
pip install "mirascope[tenacity]"
```

## Calls

Let's take a look at a basic Mirascope call that retries with exponential back-off:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="2 5-8"
            --8<-- "examples/learn/retries/calls/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

Ideally the call to `recommend_book` will succeed on the first attempt, but now the API call will be made again after waiting should it fail.

The call will then throw a `RetryError` after 3 attempts if unsuccessful. This error should be caught and handled.

## Streams

When streaming, the generator is not actually run until you start iterating. This means the initial API call may be successful but fail during the actual iteration through the stream.

Instead, you need to wrap your call and add retries to this wrapper:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="10-14"
            --8<-- "examples/learn/retries/streams/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Tools

When using tools, `ValidationError` errors won't happen until you attempt to construct the tool (either when calling `response.tools` or iterating through a stream with tools).

You need to handle retries in this case the same way as streams:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="19-23"
            --8<-- "examples/learn/retries/tools/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Error Reinsertion

Every example above simply retries after a failed attempt without making any updates to the call. This approach can be sufficient for some use-cases where we can safely expect the call to succeed on subsequent attempts (e.g. rate limits).

However, there are some cases where the LLM is likely to make the same mistake over and over again. For example, when using tools or response models, the LLM may return incorrect or missing arguments where it's highly likely the LLM will continuously make the same mistake on subsequent calls. In these cases, it's important that we update subsequent calls based on resulting errors to improve the chance of success on the next call.

To make it easier to make such updates, Mirascope provides a `collect_errors` handler that can collect any errors of your choice and insert them into subsequent calls through an `errors` keyword argument.

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="4 14 27 42"
            {% elif method == "shorthand" %}
            ```python hl_lines="4 14 19 33"
            {% else %}
            ```python hl_lines="4 14 20 37"
            {% endif %}
            --8<-- "examples/learn/retries/error_reinsertion/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

In this example the first attempt fails because the identified author is not all uppercase. The `ValidationError` is then reinserted into the subsequent call, which enables the model to learn from it's mistake and correct its error.

Of course, we could always engineer a better prompt (i.e. ask for all caps), but even prompt engineering does not guarantee perfect results. The purpose of this example is to demonstrate the power of a feedback loop by reinserting errors to build more robust systems.
