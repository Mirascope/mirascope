"""The `gemini_call` decorator for functions as LLM calls."""

from ..base import call_factory, create_factory
from ._extract import extract_decorator
from ._stream import GeminiStream, stream_decorator
from ._structured_stream import structured_stream_decorator
from ._utils import setup_call
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .dynamic_config import GeminiDynamicConfig

gemini_call = call_factory(
    TCallResponse=GeminiCallResponse,
    TCallResponseChunk=GeminiCallResponseChunk,
    TCallParams=GeminiCallParams,
    TDynamicConfig=GeminiDynamicConfig,
    TStream=GeminiStream,
    create_decorator=create_factory(
        TBaseCallResponse=GeminiCallResponse,
        setup_call=setup_call,
        calculate_cost=lambda response, model: None,
    ),
    stream_decorator=stream_decorator,
    extract_decorator=extract_decorator,
    structured_stream_decorator=structured_stream_decorator,
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
