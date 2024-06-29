"""The `anthropic_call_async` decorator for easy Anthropic API typed functions."""

from mirascope.core.anthropic.call_response_chunk import AnthropicCallResponseChunk

from ..base import call_async_factory, create_factory, extract_factory
from ._stream_async import AnthropicAsyncStream, stream_async_decorator
from ._structured_stream_async import structured_stream_async_decorator
from ._utils import anthropic_api_calculate_cost, get_json_output, setup_call
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .dynamic_config import AnthropicDynamicConfig
from .tool import AnthropicTool

anthropic_call_async = call_async_factory(
    TCallResponse=AnthropicCallResponse,
    TCallResponseChunk=AnthropicCallResponseChunk,
    TCallParams=AnthropicCallParams,
    TDynamicConfig=AnthropicDynamicConfig,
    TAsyncStream=AnthropicAsyncStream,
    create_async_decorator=create_factory(
        TBaseCallResponse=AnthropicCallResponse,
        setup_call=setup_call,
        calculate_cost=anthropic_api_calculate_cost,
    ),
    stream_async_decorator=stream_async_decorator,
    extract_async_decorator=extract_factory(
        TBaseCallResponse=AnthropicCallResponse,
        TToolType=AnthropicTool,
        setup_call=setup_call,
        get_json_output=get_json_output,
        calculate_cost=anthropic_api_calculate_cost,
    ),
    structured_stream_async_decorator=structured_stream_async_decorator,
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
