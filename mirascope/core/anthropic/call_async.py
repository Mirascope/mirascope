"""The `anthropic_call_async` decorator for easy Anthropic API typed functions."""

from mirascope.core.anthropic.call_response_chunk import AnthropicCallResponseChunk

from ..base import call_async_factory
from ._create_async import create_async_decorator
from ._extract_async import extract_async_decorator
from ._stream_async import AnthropicAsyncStream, stream_async_decorator
from ._structured_stream_async import structured_stream_async_decorator
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .function_return import AnthropicCallFunctionReturn

anthropic_call_async = call_async_factory(
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
    AnthropicCallParams,
    AnthropicCallFunctionReturn,
    AnthropicAsyncStream,
    create_async_decorator,
    stream_async_decorator,
    extract_async_decorator,
    structured_stream_async_decorator,
)
'''A decorator for calling the AsyncAnthropic API with a typed function.

This decorator is used to wrap a typed function that calls the Anthropic API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@anthropic_call_async(model="claude-3-5-sonnet-20240620")
async def recommend_book(genre: str):
    """Recommend a {genre} book."""

async def run():
    response = await recommend_book("fantasy")

asyncio.run(run())
```

Args:
    model: The Anthropic model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the Anthropic API call.
    **call_params: The `AnthropicCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an AsyncAnthropic API call.
'''
