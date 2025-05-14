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

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="8 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="7 12"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/basic_usage/bedrock/base_message_param.py

            ```


In this example we:

1. Define `recommend_book` as an asynchronous function.
2. Create a `main` function that calls `recommend_book` and awaits it.
3. Use `asyncio.run(main())` to start the asynchronous event loop and run the main function.

## Parallel Async Calls

One of the main benefits of asynchronous programming is the ability to run multiple operations concurrently. Here's an example of making parallel async calls:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="8 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="7 13-14"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/parallel/bedrock/base_message_param.py

            ```


We are using `asyncio.gather` to run and await multiple asynchronous tasks concurrently, printing the results for each task one all are completed.

## Async Streaming

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Streams](./streams.md)
    </div>

Streaming with async works similarly to synchronous streaming, but you use `async for` instead of a regular `for` loop:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="6 8 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="6 7 12-13"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/streams/bedrock/base_message_param.py

            ```


## Async Tools

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Tools](./tools.md)
    </div>

When using tools asynchronously, you can make the `call` method of a tool async:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/openai/shorthand.py

            ```
        === "Anthropic"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/anthropic/shorthand.py

            ```
        === "Google"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/google/shorthand.py

            ```
        === "Groq"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/groq/shorthand.py

            ```
        === "xAI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/xai/shorthand.py

            ```
        === "Mistral"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/mistral/shorthand.py

            ```
        === "Cohere"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/cohere/shorthand.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/litellm/shorthand.py

            ```
        === "Azure AI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/azure/shorthand.py

            ```
        === "Bedrock"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/bedrock/shorthand.py

            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/openai/messages.py

            ```
        === "Anthropic"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/anthropic/messages.py

            ```
        === "Google"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/google/messages.py

            ```
        === "Groq"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/groq/messages.py

            ```
        === "xAI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/xai/messages.py

            ```
        === "Mistral"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/mistral/messages.py

            ```
        === "Cohere"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/cohere/messages.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/litellm/messages.py

            ```
        === "Azure AI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/azure/messages.py

            ```
        === "Bedrock"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/bedrock/messages.py

            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/openai/string_template.py

            ```
        === "Anthropic"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/anthropic/string_template.py

            ```
        === "Google"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/google/string_template.py

            ```
        === "Groq"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/groq/string_template.py

            ```
        === "xAI"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/xai/string_template.py

            ```
        === "Mistral"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/mistral/string_template.py

            ```
        === "Cohere"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/cohere/string_template.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/litellm/string_template.py

            ```
        === "Azure AI"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/azure/string_template.py

            ```
        === "Bedrock"

            ```python hl_lines="10 16 18 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/bedrock/string_template.py

            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/openai/base_message_param.py

            ```
        === "Anthropic"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/anthropic/base_message_param.py

            ```
        === "Google"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/google/base_message_param.py

            ```
        === "Groq"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/groq/base_message_param.py

            ```
        === "xAI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/xai/base_message_param.py

            ```
        === "Mistral"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/mistral/base_message_param.py

            ```
        === "Cohere"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/cohere/base_message_param.py

            ```
        === "LiteLLM"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/litellm/base_message_param.py

            ```
        === "Azure AI"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/azure/base_message_param.py

            ```
        === "Bedrock"

            ```python hl_lines="10 16 17 24-25"
                # Code file not found: /home/runner/work/mirascope/mirascope/build/snippets/learn/async/tools/bedrock/base_message_param.py

            ```


It's important to note that in this example we use `isinstance(tool, FormatBook)` to ensure the `call` method can be awaited safely. This also gives us proper type hints and editor support.

## Custom Client

When using custom clients with async calls, it's crucial to use the asynchronous version of the client. You can provide the async client either through the decorator or dynamic configuration:

__Decorator Parameter:__

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Google"

            ```python hl_lines="1 5"
                from mirascope.core import google


                @google.call("gemini-1.5-flash")
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import groq


                @groq.call("llama-3.3-70b-versatile", client=AsyncGroq())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "xAI"

            ```python hl_lines="2 7"
                from mirascope.core import xai
                from openai import AsyncOpenAI


                @xai.call(
                    "grok-3-mini",
                    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"),
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import cohere


                @cohere.call("command-r-plus", client=AsyncClient())
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                async def recommend_book_async(genre: str) -> str:
                    return f"Recommend a {genre} book"
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import Messages, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Google"

            ```python hl_lines="1 5"
                from mirascope.core import Messages, google


                @google.call("gemini-1.5-flash")
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.3-70b-versatile", client=AsyncGroq())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "xAI"

            ```python hl_lines="2 7"
                from mirascope.core import Messages, xai
                from openai import AsyncOpenAI


                @xai.call(
                    "grok-3-mini",
                    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"),
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import Messages, mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", client=AsyncClient())
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import Messages, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import Messages, bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                async def recommend_book_async(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import openai, prompt_template
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Google"

            ```python hl_lines="1 5"
                from mirascope.core import google, prompt_template


                @google.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.3-70b-versatile", client=AsyncGroq())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "xAI"

            ```python hl_lines="2 7"
                from mirascope.core import prompt_template, xai
                from openai import AsyncOpenAI


                @xai.call(
                    "grok-3-mini",
                    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"),
                )
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import mistral, prompt_template
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                )
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", client=AsyncClient())
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, prompt_template


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import bedrock, prompt_template
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                @prompt_template("Recommend a {genre} book")
                async def recommend_book_async(genre: str): ...
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="2 5"
                from mirascope.core import BaseMessageParam, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini", client=AsyncOpenAI())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Anthropic"

            ```python hl_lines="1 5"
                from anthropic import AsyncAnthropic
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", client=AsyncAnthropic())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Google"

            ```python hl_lines="1 5"
                from mirascope.core import BaseMessageParam, google


                @google.call("gemini-1.5-flash")
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Groq"

            ```python hl_lines="1 5"
                from groq import AsyncGroq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.3-70b-versatile", client=AsyncGroq())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "xAI"

            ```python hl_lines="2 7"
                from mirascope.core import BaseMessageParam, xai
                from openai import AsyncOpenAI


                @xai.call(
                    "grok-3-mini",
                    client=AsyncOpenAI(base_url="https://api.xai.com/v1", api_key="YOUR_API_KEY"),
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Mistral"

            ```python hl_lines="4 8"
                import os

                from mirascope.core import BaseMessageParam, mistral
                from mistralai import Mistral


                @mistral.call(
                    "mistral-large-latest", client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Cohere"

            ```python hl_lines="1 5"
                from cohere import AsyncClient
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", client=AsyncClient())
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 8-10"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import BaseMessageParam, azure


                @azure.call(
                    "gpt-4o-mini",
                    client=AsyncChatCompletionsClient(
                        endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                    ),
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```

        === "Bedrock"

            ```python hl_lines="7-10 14"
                import asyncio

                from mirascope.core import BaseMessageParam, bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call(
                    "anthropic.claude-3-haiku-20240307-v1:0", client=asyncio.run(get_async_client())
                )
                async def recommend_book_async(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]
            ```


__Dynamic Configuration:__

!!! mira ""

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="2 9"
                from mirascope.core import openai, Messages
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic, Messages


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 9"
                from google.genai import Client
                from mirascope.core import google, Messages


                @google.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Client(),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import AsyncGroq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.3-70b-versatile")
                async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncGroq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="1 9"
                from mirascope.core import Messages, xai
                from openai import AsyncOpenAI


                @xai.call("grok-3-mini")
                async def recommend_book(genre: str) -> xai.AsyncXAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"  
                import os

                from mirascope.core import mistral, Messages
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import AsyncClient
                from mirascope.core import cohere, Messages


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, Messages


                @azure.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="5-8 15"
                from mirascope.core import bedrock, Messages
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": await get_async_client(),
                    }
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="2 9"
                from mirascope.core import Messages, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import AsyncAnthropic
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 9"
                from google.genai import Client
                from mirascope.core import Messages, google


                @google.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Client(),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import AsyncGroq
                from mirascope.core import Messages, groq


                @groq.call("llama-3.3-70b-versatile")
                async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncGroq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="1 9"
                from mirascope.core import Messages, xai
                from openai import AsyncOpenAI


                @xai.call("grok-3-mini")
                async def recommend_book(genre: str) -> xai.AsyncXAIDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"  
                import os

                from mirascope.core import Messages, mistral
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import AsyncClient
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": AsyncChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="5-8 15"
                from mirascope.core import bedrock, Messages
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "messages": [Messages.User(f"Recommend a {genre} book")],
                        "client": await get_async_client(),
                    }
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="2 9"
                from mirascope.core import openai, prompt_template
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 9"
                from anthropic import AsyncAnthropic
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 9"
                from google.genai import Client
                from mirascope.core import google, prompt_template


                @google.call("gemini-1.5-flash")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "client": Client(),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 9"
                from groq import AsyncGroq
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.3-70b-versatile")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "client": AsyncGroq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="1 9"
                from mirascope.core import prompt_template, xai
                from openai import AsyncOpenAI


                @xai.call("grok-3-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> xai.AsyncXAIDynamicConfig:
                    return {
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 11"  
                import os

                from mirascope.core import mistral, prompt_template
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 9"
                from cohere import AsyncClient
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 10-12"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "client": AsyncChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="5-8 15"
                from mirascope.core import bedrock, prompt_template
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                @prompt_template("Recommend a {genre} book")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "client": await get_async_client(),
                    }
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="2 11"
                from mirascope.core import BaseMessageParam, openai
                from openai import AsyncOpenAI


                @openai.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> openai.AsyncOpenAIDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Anthropic"

            ```python hl_lines="1 11"
                from anthropic import AsyncAnthropic
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620")
                async def recommend_book(genre: str) -> anthropic.AsyncAnthropicDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncAnthropic(),
                    }
            ```

        === "Google"

            ```python hl_lines="1 11"
                from google.genai import Client
                from mirascope.core import BaseMessageParam, google


                @google.call("gemini-1.5-flash")
                async def recommend_book(genre: str) -> google.GoogleDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Client(),
                    }
            ```

        === "Groq"

            ```python hl_lines="1 11"
                from groq import AsyncGroq
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.3-70b-versatile")
                def recommend_book(genre: str) -> groq.AsyncGroqDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncGroq(),
                    }
            ```

        === "xAI"

            ```python hl_lines="1 11"
                from mirascope.core import BaseMessageParam, xai
                from openai import AsyncOpenAI


                @xai.call("grok-3-mini")
                async def recommend_book(genre: str) -> xai.AsyncXAIDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncOpenAI(),
                    }
            ```

        === "Mistral"

            ```python hl_lines="4 15"
                import os

                from mirascope.core import BaseMessageParam, mistral
                from mistralai import Mistral


                @mistral.call("mistral-large-latest")
                async def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": Mistral(api_key=os.environ["MISTRAL_API_KEY"]),
                    }
            ```

        === "Cohere"

            ```python hl_lines="1 11"
                from cohere import AsyncClient
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus")
                async def recommend_book(genre: str) -> cohere.AsyncCohereDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncClient(),
                    }
            ```

        === "LiteLLM"

            ```python
                # Not Supported
            ```

        === "Azure AI"

            ```python hl_lines="1-2 12-14"
                from azure.ai.inference.aio import ChatCompletionsClient as AsyncChatCompletionsClient
                from azure.core.credentials import AzureKeyCredential
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini")
                async def recommend_book(genre: str) -> azure.AsyncAzureDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": AsyncChatCompletionsClient(
                            endpoint="your-endpoint", credential=AzureKeyCredential("your-credentials")
                        ),
                    }
            ```

        === "Bedrock"

            ```python hl_lines="5-8 17"
                from mirascope.core import BaseMessageParam, bedrock
                from aiobotocore.session import get_session


                async def get_async_client():
                    session = get_session()
                    async with session.create_client("bedrock-runtime") as client:
                        return client


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
                async def recommend_book(genre: str) -> bedrock.AsyncBedrockDynamicConfig:
                    return {
                        "messages": [
                            BaseMessageParam(role="user", content=f"Recommend a {genre} book")
                        ],
                        "client": await get_async_client(),
                    }
            ```


!!! warning "Synchronous vs Asynchronous Clients"
    Make sure to use the appropriate asynchronous client class (e.g., `AsyncOpenAI` instead of `OpenAI`) when working with async functions. Using a synchronous client in an async context can lead to blocking operations that defeat the purpose of async programming.

## Next Steps

By leveraging these async features in Mirascope, you can build more efficient and responsive applications, especially when working with multiple LLM calls or other I/O-bound operations.

This section concludes the core functionality Mirascope supports. If you haven't already, we recommend taking a look at any previous sections you've missed to learn about what you can do with Mirascope.

You can also check out the section on [Provider-Specific Features](./provider_specific_features/openai.md) to learn about how to use features that only certain providers support, such as OpenAI's structured outputs.
