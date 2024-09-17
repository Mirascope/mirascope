# Streams

??? api "API Documentation"

    [`mirascope.core.anthropic.stream`](../api/core/anthropic/stream.md)

    [`mirascope.core.cohere.stream`](../api/core/cohere/stream.md)

    [`mirascope.core.gemini.stream`](../api/core/gemini/stream.md)

    [`mirascope.core.groq.stream`](../api/core/groq/stream.md)

    [`mirascope.core.mistral.stream`](../api/core/mistral/stream.md)

    [`mirascope.core.openai.stream`](../api/core/openai/stream.md)

Streaming is a powerful feature when using LLMs that allows you to process LLM responses in real-time as they are generated. This can be particularly useful for long-running tasks, providing immediate feedback to users, or implementing more responsive applications.

## What is Streaming?

Streaming in the context of LLMs refers to the process of receiving and processing the model's output in chunks as it's being generated, rather than waiting for the entire response to be completed. This approach offers several benefits:

1. Immediate feedback to users
2. Reduced latency for long responses
3. Ability to process partial results
4. Efficient use of resources

Here's a diagram illustrating the difference between standard and streaming responses:

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

## Basic Usage and Syntax

To use streaming with Mirascope, you simply need to set the `stream` parameter to `True` in your [`call`](./calls.md) decorator. Here's a basic example:

```python hl_lines="4 10"
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
```

In this example:

1. We use the `@openai.call` decorator with `stream=True` to enable streaming.
2. The `recommend_book` function now returns a generator that yields chunks of the response.
3. We iterate over the chunks, printing each one as it's received.

The `end=""` and `flush=True` parameters in the print function ensure that the output is displayed in real-time without line breaks.

!!! info "Supported Providers"

    Mirascope supports standard streaming (without tools) for all supported providers. While we use OpenAI in this example, the interface is the same across all supported providers.

## Handling Streamed Responses

??? api "API Documentation"

    [`mirascope.core.base.call_response_chunk`](../api/core/base/call_response_chunk.md)

    [`mirascope.core.anthropic.call_response_chunk`](../api/core/anthropic/call_response_chunk.md)

    [`mirascope.core.cohere.call_response_chunk`](../api/core/cohere/call_response_chunk.md) 

    [`mirascope.core.gemini.call_response_chunk`](../api/core/gemini/call_response_chunk.md)

    [`mirascope.core.groq.call_response_chunk`](../api/core/groq/call_response_chunk.md) 

    [`mirascope.core.mistral.call_response_chunk`](../api/core/mistral/call_response_chunk.md)

    [`mirascope.core.openai.call_response_chunk`](../api/core/openai/call_response_chunk.md) 

When streaming, the initial response will be a provider-specific `BaseStream` instance (e.g. `OpenAIStream`), which is a generator that yields tuples `(chunk, tool)` where `chunk` is a provider-specific `BaseCallResponseChunk` (e.g. `OpenAICallResponseChunk`) that wraps the original chunk in the provider's response. These objects provide a consistent interface across providers while still allowing access to provider-specific details.

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

### Provider-Specific Response Details

While Mirascope provides a consistent interface, you can also always access the full, provider-specific response object if needed. This is available through the `chunk` property of the `BaseCallResponseChunk` object.

```python
# Accessing OpenAI-specific chat completion details
completion_chunk = chunk.chunk
print(f"Content: {completion_chunk.choices[0].delta.content}")
```

!!! note "Reasoning For Provider-Specific `BaseCallResponseChunk` Objects"

    The reason that we have provider-specific response objects (e.g. `OpenAICallResponseChunk`) is to provide proper type hints and safety when accessing the original response.

### Common Stream Properties and Methods

All `BaseStream` objects share the same [common properties and methods](./calls.md#common-response-properties-and-methods) as `BaseCallResponse` except for `usage`, `tools`, `tool`, and `__str__`. You can access these properties by using the additional shared method `construct_call_response` to reconstruct a `BaseCallResponse` instance.

!!! note "Not Necessarily 1:1"

    While we try our best to reconstruct the `BaseCallResponse` instance from the stream, there is always a chance that some information that may have been present in a standard call is missing from the stream.

### Error Handling

Error handling in streams is the same as standard non-streaming calls:

```python
stream = recommend_book("fantasy")
response = stream.construct_call_response()
print(response.model_dump())
```

!!! note "Reconstructed Response Limitations"

    While we try our best to reconstruct the `BaseCallResponse` instance from the stream, there's always a chance that some information present in a standard call might be missing from the stream.

## Error Handling

Error handling in streams is similar to standard non-streaming calls. However, it's important to note that errors may occur during iteration rather than at the initial function call:

```python hl_lines="11 14-15"
from openai import OpenAIError
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except OpenAIError as e:
    print(f"\nStreaming Error: {str(e)}")
```

!!! info "When The Error Will Occur"

    The initial response when calling an LLM function with `stream=True` will return a generator. This means that any errors that may occur during streaming will not occur until you actually iterate through the generator, which is why we wrap the generation loop in the try/except and not just the call to `recommend_book`.

### Type Safety with Streams

Mirascope's `call` decorator provides proper type hints and safety when working with streams. When you enable streaming, the return type of your function will accurately reflect the stream type:

```python
@openai.call(model="gpt-4o-mini", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> openai.OpenAIStream:
    ...

stream = recommend_book("fantasy")
# Your IDE will provide autocompletion for stream methods and properties
```

This type safety ensures that your IDE can provide appropriate autocompletion and type checking for the stream's methods and properties, improving your development experience when working with streamed LLM responses.

## Best Practices

When working with streaming in Mirascope, consider the following best practices:

1. **Real-time Feedback**: Use streaming for applications where users benefit from seeing results immediately, such as chatbots or writing assistants.

   ```python
   @openai.call(model="gpt-4o-mini", stream=True)
   @prompt_template("Write a short story about {topic}")
   def write_story(topic: str):
       ...

   print("Generating story...")
   for chunk, _ in write_story("a magical forest"):
       print(chunk.content, end="", flush=True)
   ```

2. **Progress Indicators**: Implement progress bars or loading animations that update based on the streamed response, improving user experience for longer generations.

   ```python
   from tqdm import tqdm

   @openai.call(model="gpt-4o-mini", stream=True)
   @prompt_template("Summarize the following text: {text}")
   def summarize_text(text: str):
       ...

   text = "..." # Long text to summarize
   with tqdm(total=100, desc="Summarizing") as pbar:
       for i, (chunk, _) in enumerate(summarize_text(text)):
           print(chunk.content, end="", flush=True)
           pbar.update(1)  # Update progress bar
   ```

3. **Incremental Processing**: Process streamed content incrementally for large outputs, reducing memory usage and allowing for early termination if needed.

   ```python
   @openai.call(model="gpt-4o-mini", stream=True)
   @prompt_template("Generate a list of {n} random words")
   def generate_words(n: int):
       ...

   word_count = 0
   for chunk, _ in generate_words(1000):
       words = chunk.content.split()
       word_count += len(words)
       process_words(words)  # Some processing function
       if word_count >= 1000:
           break  # Early termination
   ```

4. **Timeout Handling**: Implement timeouts for streamed responses to handle cases where the LLM might take too long to generate content.

   ```python
   import asyncio
   from asyncio import TimeoutError

   @openai.call(model="gpt-4o-mini", stream=True)
   @prompt_template("Write a detailed essay about {topic}")
   async def write_essay(topic: str):
       ...

   async def stream_with_timeout(topic: str, timeout: float):
       try:
           async for chunk, _ in asyncio.wait_for(write_essay(topic), timeout):
               print(chunk.content, end="", flush=True)
       except TimeoutError:
           print("\nGeneration timed out")

   asyncio.run(stream_with_timeout("artificial intelligence", 30.0))
   ```

By leveraging streaming effectively, you can create more responsive and efficient LLM-powered applications with Mirascope's streaming capabilities.

## Conclusion

Streaming in Mirascope offers a powerful way to handle real-time LLM responses, enabling more responsive and efficient applications. By understanding the basics of streaming, how to handle streamed responses, and following best practices, you can significantly enhance the user experience of your LLM-powered applications.

For more advanced usage of streaming, including combining streaming with tools or response models, refer to the [Tools](./tools.md) and [Response Models](./response_models.md) documentation.
