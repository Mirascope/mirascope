---
search:
  boost: 2 
---

# Streams

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Calls](./calls.md)
    </div>

Streaming is a powerful feature when using LLMs that allows you to process chunks of an LLM response in real-time as they are generated. This can be particularly useful for long-running tasks, providing immediate feedback to users, or implementing more responsive applications.

??? info "Diagram illustrating standard vs. streaming responses"

    ```mermaid
    sequenceDiagram
        participant User
        participant App
        participant LLM

        User->>App: Request
        App->>LLM: Query
        Note right of LLM: Standard Response
        LLM-->>App: Complete Response
        App-->>User: Display Result

        User->>App: Request
        App->>LLM: Query (Stream)
        Note right of LLM: Streaming Response
        loop For each chunk
            LLM-->>App: Response Chunk
            App-->>User: Display Chunk
        end
    ```

This approach offers several benefits:

1. **Immediate feedback**: Users can see responses as they're being generated, creating a more interactive experience.
2. **Reduced latency**: For long responses, users don't have to wait for the entire generation to complete before seeing results.
3. **Incremental processing**: Applications can process and act on partial results as they arrive.
4. **Efficient resource use**: Memory usage can be optimized by processing chunks instead of storing the entire response.
5. **Early termination**: If the desired information is found early in the response, processing can be stopped without waiting for the full generation.

??? api "API Documentation"

    [`mirascope.core.base.stream`](../api/core/base/stream.md)
    [`mirascope.core.openai.stream`](../api/core/openai/stream.md)
    [`mirascope.core.anthropic.stream`](../api/core/anthropic/stream.md)
    [`mirascope.core.mistral.stream`](../api/core/mistral/stream.md)
    [`mirascope.core.gemini.stream`](../api/core/gemini/stream.md)
    [`mirascope.core.groq.stream`](../api/core/groq/stream.md)
    [`mirascope.core.cohere.stream`](../api/core/cohere/stream.md)
    [`mirascope.core.litellm.stream`](../api/core/openai/stream.md)
    [`mirascope.core.azure.stream`](../api/core/azure/stream.md)
    [`mirascope.core.vertex.stream`](../api/core/vertex/stream.md)
    [`mirascope.core.bedrock.stream`](../api/core/bedrock/stream.md)

## Basic Usage and Syntax

To use streaming, simply set the `stream` parameter to `True` in your [`call`](calls.md) decorator:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 9-11"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="4 9-11"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="4 9-11"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="4 9-11"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="4 9-11"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="4 9-11"
                from mirascope.core import cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="4 9-11"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="4 9-11"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```


    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="4 9-11"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```


    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 9-11"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="4 9-11"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="4 9-11"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="4 9-11"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="4 9-11"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="4 9-11"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="4 9-11"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="4 9-11"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```


    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="4 9-11"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)
            ```



In this example:

1. We use the `call` decorator with `stream=True` to enable streaming.
2. The `recommend_book` function now returns a generator that yields `(chunk, tool)` tuples of the response.
3. We iterate over the chunks, printing each one as it's received.
4. We use `end=""` and `flush=True` parameters in the print function to ensure that the output is displayed in real-time without line breaks.

## Handling Streamed Responses

??? api "API Documentation"

    [`mirascope.core.base.call_response_chunk`](../api/core/base/call_response_chunk.md)
    [`mirascope.core.openai.call_response_chunk`](../api/core/openai/call_response_chunk.md)
    [`mirascope.core.anthropic.call_response_chunk`](../api/core/anthropic/call_response_chunk.md)
    [`mirascope.core.mistral.call_response_chunk`](../api/core/mistral/call_response_chunk.md)
    [`mirascope.core.gemini.call_response_chunk`](../api/core/gemini/call_response_chunk.md)
    [`mirascope.core.groq.call_response_chunk`](../api/core/groq/call_response_chunk.md)
    [`mirascope.core.cohere.call_response_chunk`](../api/core/cohere/call_response_chunk.md)
    [`mirascope.core.litellm.call_response_chunk`](../api/core/openai/call_response_chunk.md)
    [`mirascope.core.azure.call_response_chunk`](../api/core/azure/call_response_chunk.md)
    [`mirascope.core.vertex.call_response_chunk`](../api/core/vertex/call_response_chunk.md)
    [`mirascope.core.bedrock.call_response_chunk`](../api/core/bedrock/call_response_chunk.md)
 

When streaming, the initial response will be a provider-specific [`BaseStream`](../api/core/base/stream.md#mirascopecorebasestream) instance (e.g. `OpenAIStream`), which is a generator that yields tuples `(chunk, tool)` where `chunk` is a provider-specific [`BaseCallResponseChunk`](../api/core/base/call_response_chunk.md) (e.g. `OpenAICallResponseChunk`) that wraps the original chunk in the provider's response. These objects provide a consistent interface across providers while still allowing access to provider-specific details.

!!! note "Streaming Tools"

    You'll notice in the above example that we ignore the `tool` in each tuple. If no tools are set in the call, then `tool` will always be `None` and can be safely ignored. For more details, check out the documentation on [streaming tools](./tools.md#streaming-tools)

### Common Chunk Properties and Methods

All `BaseCallResponseChunk` objects share these common properties:

- `content`: The main text content of the response. If no content is present, this will be the empty string.
- `finish_reasons`: A list of reasons why the generation finished (e.g., "stop", "length"). These will be typed specifically for the provider used. If no finish reasons are present, this will be `None`.
- `model`: The name of the model used for generation.
- `id`: A unique identifier for the response if available. Otherwise this will be `None`.
- `usage`: Information about token usage for the call if available. Otherwise this will be `None`.
- `input_tokens`: The number of input tokens used if available. Otherwise this will be `None`.
- `output_tokens`: The number of output tokens generated if available. Otherwise this will be `None`.

### Common Stream Properties and Methods

!!! info "Must Exhaust Stream"

    To access these properties, you must first exhaust the stream by iterating through it.

Once exhausted, all `BaseStream` objects share the [same common properties and methods as `BaseCallResponse`](./calls.md#common-response-properties-and-methods), except for `usage`, `tools`, `tool`, and `__str__`.

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="13"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Anthropic"

            ```python hl_lines="13"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Mistral"

            ```python hl_lines="13"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Gemini"

            ```python hl_lines="13"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Groq"

            ```python hl_lines="13"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Cohere"

            ```python hl_lines="13"
                from mirascope.core import cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "LiteLLM"

            ```python hl_lines="13"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Azure AI"

            ```python hl_lines="13"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Vertex AI"

            ```python hl_lines="13"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Bedrock"

            ```python hl_lines="13"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```


    === "Messages"

        === "OpenAI"

            ```python hl_lines="13"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Anthropic"

            ```python hl_lines="13"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Mistral"

            ```python hl_lines="13"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Gemini"

            ```python hl_lines="13"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Groq"

            ```python hl_lines="13"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Cohere"

            ```python hl_lines="13"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "LiteLLM"

            ```python hl_lines="13"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Azure AI"

            ```python hl_lines="13"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Vertex AI"

            ```python hl_lines="13"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Bedrock"

            ```python hl_lines="13"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```


    === "String Template"

        === "OpenAI"

            ```python hl_lines="13"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Anthropic"

            ```python hl_lines="13"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Mistral"

            ```python hl_lines="13"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Gemini"

            ```python hl_lines="13"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Groq"

            ```python hl_lines="13"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Cohere"

            ```python hl_lines="13"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "LiteLLM"

            ```python hl_lines="13"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Azure AI"

            ```python hl_lines="13"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Vertex AI"

            ```python hl_lines="13"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Bedrock"

            ```python hl_lines="13"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```


    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Anthropic"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Mistral"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Gemini"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Groq"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Cohere"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "LiteLLM"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Azure AI"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Vertex AI"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```

        === "Bedrock"

            ```python hl_lines="13"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")
            ```



You can access the additional missing properties by using the method `construct_call_response` to reconstruct a provider-specific `BaseCallResponse` instance:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="15-16"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Anthropic"

            ```python hl_lines="15-16"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Mistral"

            ```python hl_lines="15-16"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Gemini"

            ```python hl_lines="15-16"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Groq"

            ```python hl_lines="15-16"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Cohere"

            ```python hl_lines="15-16"
                from mirascope.core import cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "LiteLLM"

            ```python hl_lines="15-16"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Azure AI"

            ```python hl_lines="15-16"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Vertex AI"

            ```python hl_lines="15-16"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Bedrock"

            ```python hl_lines="15-16"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```


    === "Messages"

        === "OpenAI"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Anthropic"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Mistral"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Gemini"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Groq"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Cohere"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "LiteLLM"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Azure AI"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Vertex AI"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Bedrock"

            ```python hl_lines="15-16"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```


    === "String Template"

        === "OpenAI"

            ```python hl_lines="15-16"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Anthropic"

            ```python hl_lines="15-16"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Mistral"

            ```python hl_lines="15-16"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Gemini"

            ```python hl_lines="15-16"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Groq"

            ```python hl_lines="15-16"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Cohere"

            ```python hl_lines="15-16"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "LiteLLM"

            ```python hl_lines="15-16"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Azure AI"

            ```python hl_lines="15-16"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Vertex AI"

            ```python hl_lines="15-16"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Bedrock"

            ```python hl_lines="15-16"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```


    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Anthropic"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Mistral"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Gemini"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Groq"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Cohere"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "LiteLLM"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Azure AI"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Vertex AI"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```

        === "Bedrock"

            ```python hl_lines="15-16"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    print(chunk.content, end="", flush=True)

                print(f"Content: {stream.content}")

                call_response = stream.construct_call_response()
                print(f"Usage: {call_response.usage}")
            ```



!!! warning "Reconstructed Response Limitations"

    While we try our best to reconstruct the `BaseCallResponse` instance from the stream, there's always a chance that some information present in a standard call might be missing from the stream.

### Provider-Specific Response Details

While Mirascope provides a consistent interface, you can always access the full, provider-specific response object if needed. This is available through the `chunk` property of the `BaseCallResponseChunk` object:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="11"
                from mirascope.core import openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="11"
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="11"
                from mirascope.core import mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="11"
                from mirascope.core import gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="11"
                from mirascope.core import groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="11"
                from mirascope.core import cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="11"
                from mirascope.core import litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="11"
                from mirascope.core import azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="11"
                from mirascope.core import vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="11"
                from mirascope.core import bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```


    === "Messages"

        === "OpenAI"

            ```python hl_lines="11"
                from mirascope.core import Messages, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="11"
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="11"
                from mirascope.core import Messages, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="11"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="11"
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="11"
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="11"
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="11"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="11"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="11"
                from mirascope.core import Messages, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```


    === "String Template"

        === "OpenAI"

            ```python hl_lines="11"
                from mirascope.core import openai, prompt_template


                @openai.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="11"
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="11"
                from mirascope.core import mistral, prompt_template


                @mistral.call("mistral-large-latest", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="11"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="11"
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="11"
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="11"
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="11"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="11"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="11"
                from mirascope.core import bedrock, prompt_template


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```


    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, openai


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Anthropic"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Mistral"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, mistral


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Gemini"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Groq"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Cohere"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "LiteLLM"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Azure AI"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Vertex AI"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```

        === "Bedrock"

            ```python hl_lines="11"
                from mirascope.core import BaseMessageParam, bedrock


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                print(f"Original chunk: {chunk.chunk}")
                    print(chunk.content, end="", flush=True)
            ```



!!! note "Reasoning For Provider-Specific `BaseCallResponseChunk` Objects"

    The reason that we have provider-specific response objects (e.g. `OpenAICallResponseChunk`) is to provide proper type hints and safety when accessing the original response chunk.


## Multi-Modal Outputs

While most LLM providers focus on text streaming, some providers support streaming additional output modalities like audio. The availability of multi-modal streaming varies among providers:

| Provider    | Text | Audio | Image |
|------------|------|-------|-------|
| OpenAI     | ✓    | ✓     | -     |
| Anthropic  | ✓    | -     | -     |
| Mistral    | ✓    | -     | -     |
| Gemini     | ✓    | -     | -     |
| Groq       | ✓    | -     | -     |
| Cohere     | ✓    | -     | -     |
| LiteLLM    | ✓    | -     | -     |
| Azure AI   | ✓    | -     | -     |
| Vertex AI  | ✓    | -     | -     |

Legend: ✓ (Supported), - (Not Supported)

### Audio Streaming

For providers that support audio outputs, you can stream both text and audio responses simultaneously:

!!! mira "" 

    === "Shorthand"
        === "OpenAI"

            ```python hl_lines="17 18 20 31-34"
                import io


                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai

                SAMPLE_WIDTH = 2
                FRAME_RATE = 24000
                CHANNELS = 1


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "pcm16"},
                        "modalities": ["text", "audio"],
                    },
                    stream=True,
                )
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                audio_chunk = b""
                audio_transcript_chunk = ""

                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    if chunk.audio:
                        audio_chunk += chunk.audio
                    if chunk.audio_transcript:
                        audio_transcript_chunk += chunk.audio_transcript

                print(audio_transcript_chunk)


                audio_segment = AudioSegment.from_raw(
                    io.BytesIO(audio_chunk),
                    sample_width=SAMPLE_WIDTH,
                    frame_rate=FRAME_RATE,
                    channels=CHANNELS,
                )
                play(audio_segment)
            ```

        === "Anthropic"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

    === "Messages"
        === "OpenAI"

            ```python hl_lines="17 18 20 31-34"
                import io


                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai, Messages

                SAMPLE_WIDTH = 2
                FRAME_RATE = 24000
                CHANNELS = 1


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "pcm16"},
                        "modalities": ["text", "audio"],
                    },
                    stream=True,
                )
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                audio_chunk = b""
                audio_transcript_chunk = ""

                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    if chunk.audio:
                        audio_chunk += chunk.audio
                    if chunk.audio_transcript:
                        audio_transcript_chunk += chunk.audio_transcript

                print(audio_transcript_chunk)


                audio_segment = AudioSegment.from_raw(
                    io.BytesIO(audio_chunk),
                    sample_width=SAMPLE_WIDTH,
                    frame_rate=FRAME_RATE,
                    channels=CHANNELS,
                )
                play(audio_segment)
            ```

        === "Anthropic"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

    === "String Template"
        === "OpenAI"

            ```python hl_lines="17 18 20 31-34"
                import io


                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai, prompt_template

                SAMPLE_WIDTH = 2
                FRAME_RATE = 24000
                CHANNELS = 1


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "pcm16"},
                        "modalities": ["text", "audio"],
                    },
                    stream=True,
                )
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                audio_chunk = b""
                audio_transcript_chunk = ""

                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    if chunk.audio:
                        audio_chunk += chunk.audio
                    if chunk.audio_transcript:
                        audio_transcript_chunk += chunk.audio_transcript

                print(audio_transcript_chunk)


                audio_segment = AudioSegment.from_raw(
                    io.BytesIO(audio_chunk),
                    sample_width=SAMPLE_WIDTH,
                    frame_rate=FRAME_RATE,
                    channels=CHANNELS,
                )
                play(audio_segment)
            ```

        === "Anthropic"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

    === "BaseMessageParam"
        === "OpenAI"

            ```python hl_lines="17 18 20 31-34"
                import io


                from pydub.playback import play
                from pydub import AudioSegment

                from mirascope.core import openai, BaseMessageParam

                SAMPLE_WIDTH = 2
                FRAME_RATE = 24000
                CHANNELS = 1


                @openai.call(
                    "gpt-4o-audio-preview",
                    call_params={
                        "audio": {"voice": "alloy", "format": "pcm16"},
                        "modalities": ["text", "audio"],
                    },
                    stream=True,
                )
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                audio_chunk = b""
                audio_transcript_chunk = ""

                stream = recommend_book("fantasy")
                for chunk, _ in stream:
                    if chunk.audio:
                        audio_chunk += chunk.audio
                    if chunk.audio_transcript:
                        audio_transcript_chunk += chunk.audio_transcript

                print(audio_transcript_chunk)


                audio_segment = AudioSegment.from_raw(
                    io.BytesIO(audio_chunk),
                    sample_width=SAMPLE_WIDTH,
                    frame_rate=FRAME_RATE,
                    channels=CHANNELS,
                )
                play(audio_segment)
            ```

        === "Anthropic"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Mistral"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Gemini"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Groq"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Cohere"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "LiteLLM"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Azure AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Vertex AI"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```

        === "Bedrock"

            ```python hl_lines="17 18 20 31-34"
                # Not supported
            ```



Each stream chunk provides access to:

- `chunk.audio`: Raw audio data in bytes format
- `chunk.audio_transcript`: The transcript of the audio

This allows you to process both text and audio streams concurrently. Since audio data is received in chunks, you could technically begin playback before receiving the complete response.

!!! warning "Audio Playback Requirements"

    The example above uses `pydub` and `ffmpeg` for audio playback, but you can use any audio processing libraries or media players that can handle WAV format audio data. Choose the tools that best fit your needs and environment.

    If you decide to use pydub:
    - Install [pydub](https://github.com/jiaaro/pydub): `pip install pydub`
    - Install ffmpeg: Available from [ffmpeg.org](https://www.ffmpeg.org/) or through system package managers

!!! note "Voice Options"

    For providers that support audio outputs, refer to their documentation for available voice options and configurations:
    
    - OpenAI: [Text to Speech Guide](https://platform.openai.com/docs/guides/text-to-speech)


## Error Handling

Error handling in streams is similar to standard non-streaming calls. However, it's important to note that errors may occur during iteration rather than at the initial function call:

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="2 10 13"
                from mirascope.core import openai
                from openai import OpenAIError


                @openai.call(model="gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import mistral
                from mistralai import models


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import gemini


                @gemini.call(model="gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import groq


                @groq.call(model="llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import cohere


                @cohere.call(model="command-r-plus", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import litellm


                @litellm.call(model="gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import azure


                @azure.call(model="gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import vertex


                @vertex.call(model="gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import bedrock
                from botocore.exceptions import ClientError


                @bedrock.call(model="anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> str:
                    return f"Recommend a {genre} book"


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```


    === "Messages"

        === "OpenAI"

            ```python hl_lines="2 10 13"
                from mirascope.core import Messages, openai
                from openai import OpenAIError


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import Messages, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import Messages, mistral
                from mistralai import models


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import Messages, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import Messages, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import Messages, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import Messages, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import Messages, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import Messages, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import Messages, bedrock
                from botocore.exceptions import ClientError


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> Messages.Type:
                    return Messages.User(f"Recommend a {genre} book")


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```


    === "String Template"

        === "OpenAI"

            ```python hl_lines="2 10 13"
                from mirascope.core import openai, prompt_template
                from openai import OpenAIError


                @openai.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import anthropic, prompt_template


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import mistral, prompt_template
                from mistralai import models


                @mistral.call("mistral-large-latest", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import gemini, prompt_template


                @gemini.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import groq, prompt_template


                @groq.call("llama-3.1-70b-versatile", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import cohere, prompt_template


                @cohere.call("command-r-plus", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import litellm, prompt_template


                @litellm.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import azure, prompt_template


                @azure.call("gpt-4o-mini", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import prompt_template, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import bedrock, prompt_template
                from botocore.exceptions import ClientError


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                @prompt_template("Recommend a {genre} book")
                def recommend_book(genre: str): ...


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```


    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="2 10 13"
                from mirascope.core import BaseMessageParam, openai
                from openai import OpenAIError


                @openai.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except OpenAIError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Anthropic"

            ```python hl_lines="1 10 13"
                from anthropic import AnthropicError
                from mirascope.core import BaseMessageParam, anthropic


                @anthropic.call("claude-3-5-sonnet-20240620", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except AnthropicError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Mistral"

            ```python hl_lines="2 10 13 16"
                from mirascope.core import BaseMessageParam, mistral
                from mistralai import models


                @mistral.call("mistral-large-latest", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle e.data: models.HTTPValidationErrorData
                    raise (e)
                except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
                    # handle exception
                    raise (e)
            ```

        === "Gemini"

            ```python hl_lines="9 12"
                from mirascope.core import BaseMessageParam, gemini


                @gemini.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Groq"

            ```python hl_lines="1 10 13"
                from groq import GroqError
                from mirascope.core import BaseMessageParam, groq


                @groq.call("llama-3.1-70b-versatile", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except GroqError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Cohere"

            ```python hl_lines="1 10 13"
                from cohere.errors import BadRequestError
                from mirascope.core import BaseMessageParam, cohere


                @cohere.call("command-r-plus", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "LiteLLM"

            ```python hl_lines="1 10 13"
                from litellm.exceptions import BadRequestError
                from mirascope.core import BaseMessageParam, litellm


                @litellm.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except BadRequestError as e:
                    print(f"Error: {str(e)}")
            ```

        === "Azure AI"

            ```python hl_lines="9 12"
                from mirascope.core import BaseMessageParam, azure


                @azure.call("gpt-4o-mini", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Vertex AI"

            ```python hl_lines="9 12"
                from mirascope.core import BaseMessageParam, vertex


                @vertex.call("gemini-1.5-flash", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except Exception as e:
                    print(f"Error: {str(e)}")
            ```

        === "Bedrock"

            ```python hl_lines="1 10 13"
                from mirascope.core import BaseMessageParam, bedrock
                from botocore.exceptions import ClientError


                @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
                def recommend_book(genre: str) -> list[BaseMessageParam]:
                    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


                try:
                    for chunk, _ in recommend_book("fantasy"):
                        print(chunk.content, end="", flush=True)
                except ClientError as e:
                    print(f"Error: {str(e)}")
            ```



In these examples, we wrap the iteration loop in a try/except block to catch any errors that might occur during streaming.

!!! warning "When Errors Occur"

    The initial response when calling an LLM function with `stream=True` will return a generator. Any errors that may occur during streaming will not happen until you actually iterate through the generator. This is why we wrap the generation loop in the try/except block and not just the call to `recommend_book`.

## Next Steps

By leveraging streaming effectively, you can create more responsive and efficient LLM-powered applications with Mirascope's streaming capabilities.

Next, we recommend taking a look at the [Streams](./chaining.md) documentation, which shows you how to break tasks down into smaller, more directed calls and chain them togethder.
