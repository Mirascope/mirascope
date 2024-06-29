"""The `openai_call_async` decorator for easy OpenAI API typed functions."""

from mirascope.core.openai.call_response_chunk import OpenAICallResponseChunk

from ..base import call_async_factory, create_factory
from ._extract_async import extract_async_decorator
from ._stream_async import OpenAIAsyncStream, stream_async_decorator
from ._structured_stream_async import structured_stream_async_decorator
from ._utils import openai_api_calculate_cost, setup_call
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .dyanmic_config import OpenAIDynamicConfig

openai_call_async = call_async_factory(
    TCallResponse=OpenAICallResponse,
    TCallResponseChunk=OpenAICallResponseChunk,
    TCallParams=OpenAICallParams,
    TDynamicConfig=OpenAIDynamicConfig,
    TAsyncStream=OpenAIAsyncStream,
    create_async_decorator=create_factory(
        TBaseCallResponse=OpenAICallResponse,
        setup_call=setup_call,
        calculate_cost=openai_api_calculate_cost,
    ),
    stream_async_decorator=stream_async_decorator,
    extract_async_decorator=extract_async_decorator,
    structured_stream_async_decorator=structured_stream_async_decorator,
)
'''A decorator for calling the AsyncOpenAI API with a typed function.

This decorator is used to wrap a typed function that calls the OpenAI API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@openai_call_async(model="gpt-4o")
async def recommend_book(genre: str):
    """Recommend a {genre} book."""

async def run():
    response = await recommend_book("fantasy")

asyncio.run(run())
```

Args:
    model: The OpenAI model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the OpenAI API call.
    **call_params: The `OpenAICallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an AsyncOpenAI API call.
'''
