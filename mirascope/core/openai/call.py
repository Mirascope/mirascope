"""The `openai_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._create import create_decorator
from ._extract import extract_decorator
from ._stream import OpenAIStream, stream_decorator
from ._structured_stream import structured_stream_decorator
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .function_return import OpenAIDynamicConfig

openai_call = call_factory(
    OpenAICallResponse,
    OpenAICallResponseChunk,
    OpenAICallParams,
    OpenAIDynamicConfig,
    OpenAIStream,
    create_decorator,
    stream_decorator,
    extract_decorator,
    structured_stream_decorator,
)
'''A decorator for calling the OpenAI API with a typed function.

This decorator is used to wrap a typed function that calls the OpenAI API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@openai_call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The OpenAI model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the OpenAI API call.
    **call_params: The `OpenAICallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an OpenAI API call.
'''
