---
search:
  boost: 2
---

# Async

Asynchronous programming is a crucial concept when building applications with LLMs (Large Language Models) using Mirascope. This feature allows for efficient handling of I/O-bound operations (e.g., API calls), improving application responsiveness and scalability. Mirascope utilizes the [asyncio](https://docs.python.org/3/library/asyncio.html) library to implement asynchronous processing.

!!! tip "Best Practices"

    - **Use asyncio for I/O-bound tasks**: Async is most beneficial for I/O-bound operations like API calls. It may not provide significant benefits for CPU-bound tasks.
    - **Avoid blocking operations**: Ensure that you're not using blocking operations within async functions, as this can negate the benefits of asynchronous programming.
    - **Consider using connection pools**: When making many async requests, consider using connection pools to manage and reuse connections efficiently.
    - **Be mindful of rate limits**: While async allows for concurrent requests, be aware of API rate limits and implement appropriate throttling if necessary.
    - **Use appropriate timeouts**: Implement timeouts for async operations to prevent hanging in case of network issues or unresponsive services.
    - **Test thoroughly**: Async code can introduce subtle bugs. Ensure comprehensive testing of your async implementations.
    - **Leverage async context managers**: Use async context managers (async with) for managing resources that require setup and cleanup in async contexts.

??? info "Diagram illustrating the flow of asynchronous processing"

    ```mermaid
    sequenceDiagram
        participant Main as Main Process
        participant API1 as API Call 1
        participant API2 as API Call 2
        participant API3 as API Call 3

        Main->>+API1: Send Request
        Main->>+API2: Send Request
        Main->>+API3: Send Request
        API1-->>-Main: Response
        API2-->>-Main: Response
        API3-->>-Main: Response
        Main->>Main: Process All Responses
    ```

## Key Terms

- `async`: Keyword used to define a function as asynchronous
- `await`: Keyword used to wait for the completion of an asynchronous operation
- `asyncio`: Python library that supports asynchronous programming

## Basic Usage and Syntax

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

To use async in Mirascope, simply define the function as async and use the `await` keyword when calling it. Here's a basic example:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="8 12"
            {% else %}
            ```python hl_lines="7 12"
            {% endif %}
            --8<-- "build/snippets/learn/async/basic_usage/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

In this example we:

1. Define `recommend_book` as an asynchronous function.
2. Create a `main` function that calls `recommend_book` and awaits it.
3. Use `asyncio.run(main())` to start the asynchronous event loop and run the main function.

## Parallel Async Calls

One of the main benefits of asynchronous programming is the ability to run multiple operations concurrently. Here's an example of making parallel async calls:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="8 13-14"
            {% else %}
            ```python hl_lines="7 13-14"
            {% endif %}
            --8<-- "build/snippets/learn/async/parallel/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

We are using `asyncio.gather` to run and await multiple asynchronous tasks concurrently, printing the results for each task one all are completed.

## Async Streaming

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Streams](./streams.md)
    </div>

Streaming with async works similarly to synchronous streaming, but you use `async for` instead of a regular `for` loop:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="6 8 12-13"
            {% else %}
            ```python hl_lines="6 7 12-13"
            {% endif %}
            --8<-- "build/snippets/learn/async/streams/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Async Tools

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Tools](./tools.md)
    </div>

When using tools asynchronously, you can make the `call` method of a tool async:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="10 16 18 24-25"
            {% else %}
            ```python hl_lines="10 16 17 24-25"
            {% endif %}
            --8<-- "build/snippets/learn/async/tools/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

It's important to note that in this example we use `isinstance(tool, FormatBook)` to ensure the `call` method can be awaited safely. This also gives us proper type hints and editor support.

## Custom Client

When using custom clients with async calls, it's crucial to use the asynchronous version of the client. You can provide the async client either through the decorator or dynamic configuration:

__Decorator Parameter:__

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider == "LiteLLM" %}
            ```python
            {% elif provider in ["OpenAI"] %}
            ```python hl_lines="2 5"
            {% elif provider == "Azure AI" %}
            ```python hl_lines="1-2 8-10"
            {% elif provider == "Bedrock" %}
            ```python hl_lines="7-10 14"
            {% elif provider == "Mistral" %}
            ```python hl_lines="4 8"
            {% elif provider == "xAI" %}
            ```python hl_lines="2 7"
            {% else %}
            ```python hl_lines="1 5"
            {% endif %}
            --8<-- "examples/learn/async/custom_client/decorator/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}
    {% endfor %}

__Dynamic Configuration:__

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"
        {% if method == "base_message_param" %}
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider == "LiteLLM" %}
            ```python
            {% elif provider in ["OpenAI"] %}
            ```python hl_lines="2 11"
            {% elif provider == "Azure AI" %}
            ```python hl_lines="1-2 12-14"
            {% elif provider == "Bedrock" %}
            ```python hl_lines="5-8 17"
            {% elif provider == "Mistral" %}
            ```python hl_lines="4 15"
            {% else %}
            ```python hl_lines="1 11"
            {% endif %}
            --8<-- "examples/learn/async/custom_client/dynamic_configuration/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}
        {% else %}
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider == "LiteLLM" %}
            ```python
            {% elif provider in ["OpenAI"] %}
            ```python hl_lines="2 9"
            {% elif provider == "Azure AI" %}
            ```python hl_lines="1-2 10-12"
            {% elif provider == "Bedrock" %}
            ```python hl_lines="5-8 15"
            {% elif provider == "Mistral" %}
            ```python hl_lines="4 11"  
            {% else %}
            ```python hl_lines="1 9"
            {% endif %}
            --8<-- "examples/learn/async/custom_client/dynamic_configuration/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}
        {% endif %}
    {% endfor %}

!!! warning "Synchronous vs Asynchronous Clients"
    Make sure to use the appropriate asynchronous client class (e.g., `AsyncOpenAI` instead of `OpenAI`) when working with async functions. Using a synchronous client in an async context can lead to blocking operations that defeat the purpose of async programming.

## Next Steps

By leveraging these async features in Mirascope, you can build more efficient and responsive applications, especially when working with multiple LLM calls or other I/O-bound operations.

This section concludes the core functionality Mirascope supports. If you haven't already, we recommend taking a look at any previous sections you've missed to learn about what you can do with Mirascope.

You can also check out the section on [Provider-Specific Features](./provider_specific_features/openai.md) to learn about how to use features that only certain providers support, such as OpenAI's structured outputs.
