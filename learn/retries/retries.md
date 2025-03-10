---
search:
  boost: 2
---

# Retries

Making an API call to a provider can fail due to various reasons, such as rate limits, internal server errors, validation errors, and more. This makes retrying calls extremely important when building robust systems.

Mirascope combined with [Tenacity](https://tenacity.readthedocs.io/en/latest/) increases the chance for these requests to succeed while maintaining end user transparency.

You can install the necessary packages directly or use the `tenacity` extras flag:

```python
pip install "mirascope[tenacity]"
```

## Tenacity `retry` Decorator

### Calls

Let's take a look at a basic Mirascope call that retries with exponential back-off:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="2 5-8"
            --8<-- "build/snippets/learn/retries/calls/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

Ideally the call to `recommend_book` will succeed on the first attempt, but now the API call will be made again after waiting should it fail.

The call will then throw a `RetryError` after 3 attempts if unsuccessful. This error should be caught and handled.

### Streams

When streaming, the generator is not actually run until you start iterating. This means the initial API call may be successful but fail during the actual iteration through the stream.

Instead, you need to wrap your call and add retries to this wrapper:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="10-14"
            --8<-- "build/snippets/learn/retries/streams/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

### Tools

When using tools, `ValidationError` errors won't happen until you attempt to construct the tool (either when calling `response.tools` or iterating through a stream with tools).

You need to handle retries in this case the same way as streams:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="19-23"
            --8<-- "build/snippets/learn/retries/tools/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

### Error Reinsertion

Every example above simply retries after a failed attempt without making any updates to the call. This approach can be sufficient for some use-cases where we can safely expect the call to succeed on subsequent attempts (e.g. rate limits).

However, there are some cases where the LLM is likely to make the same mistake over and over again. For example, when using tools or response models, the LLM may return incorrect or missing arguments where it's highly likely the LLM will continuously make the same mistake on subsequent calls. In these cases, it's important that we update subsequent calls based on resulting errors to improve the chance of success on the next call.

To make it easier to make such updates, Mirascope provides a `collect_errors` handler that can collect any errors of your choice and insert them into subsequent calls through an `errors` keyword argument.

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="4 14 28 43"
            {% elif method == "shorthand" %}
            ```python hl_lines="4 14 20 34"
            {% else %}
            ```python hl_lines="4 14 21 38" 
            {% endif %}
            --8<-- "build/snippets/learn/retries/error_reinsertion/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

In this example the first attempt fails because the identified author is not all uppercase. The `ValidationError` is then reinserted into the subsequent call, which enables the model to learn from it's mistake and correct its error.

Of course, we could always engineer a better prompt (i.e. ask for all caps), but even prompt engineering does not guarantee perfect results. The purpose of this example is to demonstrate the power of a feedback loop by reinserting errors to build more robust systems.

## Fallback

When using the provider-agnostic `llm.call` decorator, you can use the `fallback` decorator to automatically catch certain errors and use a backup provider/model to attempt the call again.

For example, we may want to attempt the call with Anthropic in the event that we get a `RateLimitError` from OpenAI:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        ```python hl_lines="7-16 24 28"
        --8<-- "examples/learn/retries/fallback/{{ method }}.py"
        ```

    {% endfor %}

Here, we first attempt to call OpenAI (the default setting). If we catch the `OpenAIRateLimitError`, then we'll attempt to call Anthropic. If we catch the `AnthropicRateLimitError`, then we'll receive a `FallbackError` since all attempts failed.

You can provide an `Exception` or tuple of multiple to catch, and you can stack the `fallback` decorator to handle different errors differently if desired.

### Fallback With Retries

The decorator also works well with Tenacity's `retry` decorator. For example, we may want to first attempt to call OpenAI multiple times with exponential backoff, but if we fail 3 times fall back to Anthropic, which we'll also attempt to call 3 times:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        ```python hl_lines="14-28"
        --8<-- "examples/learn/retries/fallback_retries/{{ method }}.py"
        ```

    {% endfor %}
