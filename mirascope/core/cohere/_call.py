"""The `cohere_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import CohereCallParams
from .call_response import CohereCallResponse
from .call_response_chunk import CohereCallResponseChunk
from .dynamic_config import CohereDynamicConfig
from .stream import CohereStream
from .tool import CohereTool

cohere_call = call_factory(
    TCallResponse=CohereCallResponse,
    TCallResponseChunk=CohereCallResponseChunk,
    TDynamicConfig=CohereDynamicConfig,
    TToolType=CohereTool,
    TStream=CohereStream,
    TCallParams=CohereCallParams,
    default_call_params=CohereCallParams(),
    setup_call=setup_call,  # type: ignore
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
)
'''A decorator for calling the Cohere API with a typed function.

This decorator is used to wrap a typed function that calls the Cohere API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@cohere_call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The Cohere model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the Cohere API call.
    **call_params: The `CohereCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an Cohere API call.
'''
