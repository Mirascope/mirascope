"""The `gemini_call_async` decorator for easy Gemini API typed functions."""

from ..base import call_async_factory, create_factory, extract_factory
from ._stream_async import GeminiAsyncStream, stream_async_decorator
from ._structured_stream_async import structured_stream_async_decorator
from ._utils import gemini_api_calculate_cost, get_json_output, setup_call
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool

gemini_call_async = call_async_factory(
    TCallResponse=GeminiCallResponse,
    TCallResponseChunk=GeminiCallResponseChunk,
    TCallParams=GeminiCallParams,
    TDynamicConfig=GeminiDynamicConfig,
    TAsyncStream=GeminiAsyncStream,
    create_async_decorator=create_factory(
        TBaseCallResponse=GeminiCallResponse,
        setup_call=setup_call,
        calculate_cost=gemini_api_calculate_cost,
    ),
    stream_async_decorator=stream_async_decorator,
    extract_async_decorator=extract_factory(
        TBaseCallResponse=GeminiCallResponse,
        TToolType=GeminiTool,
        setup_call=setup_call,
        get_json_output=get_json_output,
        calculate_cost=gemini_api_calculate_cost,
    ),
    structured_stream_async_decorator=structured_stream_async_decorator,
)
'''A decorator for calling the Gemini API with a typed function.

This decorator is used to wrap a typed function that calls the Gemini API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@gemini_call(model="gemini-1.5-pro")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The Gemini model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the Gemini API call.
    **call_params: The `GeminiCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an Gemini API call.
'''
