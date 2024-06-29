"""The `gemini_call_async` decorator for easy Gemini API typed functions."""

from google.generativeai.types import ContentDict

from ..base import call_async_factory
from ..base._stream import BaseStream
from ._structured_stream_async import structured_stream_async_decorator
from ._utils import (
    gemini_api_calculate_cost,
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool

GeminiAsyncStream = BaseStream[
    GeminiCallResponseChunk,
    ContentDict,
    ContentDict,
    ContentDict,
    GeminiTool,
    GeminiDynamicConfig,
]

gemini_call_async = call_async_factory(
    TCallResponse=GeminiCallResponse,
    TCallResponseChunk=GeminiCallResponseChunk,
    TCallParams=GeminiCallParams,
    TDynamicConfig=GeminiDynamicConfig,
    TStream=GeminiAsyncStream,
    TMessageParamType=ContentDict,
    TToolType=GeminiTool,
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    calculate_cost=gemini_api_calculate_cost,
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
