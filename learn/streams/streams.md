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
    {% for provider in supported_llm_providers %}
    {% if provider == 'LiteLLM' %}
    [`mirascope.core.litellm.stream`](../api/core/openai/stream.md)
    {% else %}
    [`mirascope.core.{{ provider | provider_dir }}.stream`](../api/core/{{ provider | provider_dir}}/stream.md)
    {% endif %}
    {% endfor %}

## Basic Usage and Syntax

To use streaming, simply set the `stream` parameter to `True` in your [`call`](calls.md) decorator:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="4 9-11"
            --8<-- "build/snippets/learn/streams/basic_usage/{{ provider | provider_dir }}/{{ method }}.py::11"
            ```

        {% endfor %}

    {% endfor %}

In this example:

1. We use the `call` decorator with `stream=True` to enable streaming.
2. The `recommend_book` function now returns a generator that yields `(chunk, tool)` tuples of the response.
3. We iterate over the chunks, printing each one as it's received.
4. We use `end=""` and `flush=True` parameters in the print function to ensure that the output is displayed in real-time without line breaks.

## Handling Streamed Responses

??? api "API Documentation"

    [`mirascope.core.base.call_response_chunk`](../api/core/base/call_response_chunk.md)
    {% for provider in supported_llm_providers %}
    {% if provider == 'LiteLLM' %}
    [`mirascope.core.litellm.call_response_chunk`](../api/core/openai/call_response_chunk.md)
    {% else %}
    [`mirascope.core.{{ provider | provider_dir }}.call_response_chunk`](../api/core/{{ provider | provider_dir }}/call_response_chunk.md)
    {% endif %}
    {% endfor %} 

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

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="13"
            --8<-- "build/snippets/learn/streams/basic_usage/{{ provider | provider_dir }}/{{ method }}.py::13"
            ```

        {% endfor %}

    {% endfor %}

You can access the additional missing properties by using the method `construct_call_response` to reconstruct a provider-specific `BaseCallResponse` instance:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="15-16"
            --8<-- "build/snippets/learn/streams/basic_usage/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}

    {% endfor %}

!!! warning "Reconstructed Response Limitations"

    While we try our best to reconstruct the `BaseCallResponse` instance from the stream, there's always a chance that some information present in a standard call might be missing from the stream.

### Provider-Specific Response Details

While Mirascope provides a consistent interface, you can always access the full, provider-specific response object if needed. This is available through the `chunk` property of the `BaseCallResponseChunk` object:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="11"
            --8<-- "build/snippets/learn/streams/basic_usage/{{ provider | provider_dir }}/{{ method }}.py::10"
                print(f"Original chunk: {chunk.chunk}")
            --8<-- "build/snippets/learn/streams/basic_usage/{{ provider | provider_dir }}/{{ method }}.py:11:11"
            ```

        {% endfor %}

    {% endfor %}

!!! note "Reasoning For Provider-Specific `BaseCallResponseChunk` Objects"

    The reason that we have provider-specific response objects (e.g. `OpenAICallResponseChunk`) is to provide proper type hints and safety when accessing the original response chunk.


## Multi-Modal Outputs

While most LLM providers focus on text streaming, some providers support streaming additional output modalities like audio. The availability of multi-modal streaming varies among providers:

| Provider      | Text | Audio | Image |
|---------------|------|-------|-------|
| OpenAI        | ✓    | ✓     | -     |
| Anthropic     | ✓    | -     | -     |
| Mistral       | ✓    | -     | -     |
| Google Gemini | ✓    | -     | -     |
| Groq          | ✓    | -     | -     |
| Cohere        | ✓    | -     | -     |
| LiteLLM       | ✓    | -     | -     |
| Azure AI      | ✓    | -     | -     |

Legend: ✓ (Supported), - (Not Supported)

### Audio Streaming

For providers that support audio outputs, you can stream both text and audio responses simultaneously:

!!! mira "" 

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider == "OpenAI" %}
            ```python hl_lines="17 18 20 31-34"
            {% else %}
            ```python
            {% endif %}
            --8<-- "examples/learn/streams/multi_modal_outputs/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}
    {% endfor %}


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

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider in ["Google", "Azure AI"] %}
            ```python hl_lines="9 12"
            {% elif provider == "Mistral" %}
            ```python hl_lines="2 10 13 16"
            {% elif provider == "OpenAI" %}
            ```python hl_lines="2 10 13"
            {% else %}
            ```python hl_lines="1 10 13"
            {% endif %}
            --8<-- "build/snippets/learn/streams/error_handling/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}

    {% endfor %}

In these examples we show provider-specific error handling, though you can also catch generic exceptions.

Note how we wrap the iteration loop in a try/except block to catch any errors that might occur during streaming.

!!! warning "When Errors Occur"

    The initial response when calling an LLM function with `stream=True` will return a generator. Any errors that may occur during streaming will not happen until you actually iterate through the generator. This is why we wrap the generation loop in the try/except block and not just the call to `recommend_book`.

## Next Steps

By leveraging streaming effectively, you can create more responsive and efficient LLM-powered applications with Mirascope's streaming capabilities.

Next, we recommend taking a look at the [Streams](./chaining.md) documentation, which shows you how to break tasks down into smaller, more directed calls and chain them togethder.
