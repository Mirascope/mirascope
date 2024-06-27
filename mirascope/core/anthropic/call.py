"""The `anthropic_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._create import create_decorator
from ._extract import extract_decorator
from ._stream import AnthropicStream, stream_decorator
from ._structured_stream import structured_stream_decorator
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .function_return import AnthropicCallFunctionReturn

anthropic_call = call_factory(
    AnthropicCallResponse,
    AnthropicCallResponseChunk,
    AnthropicCallParams,
    AnthropicCallFunctionReturn,
    AnthropicStream,
    create_decorator,
    stream_decorator,
    extract_decorator,
    structured_stream_decorator,
)
'''A decorator for calling the Anthropic API with a typed function.

This decorator is used to wrap a typed function that calls the Anthropic API. It
parses the docstring of the wrapped function as the messages array and templates the
input arguments for the function into each message's template.

Example:

```python
@anthropic_call(model="claude-3-5-sonnet-20240620")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The Anthropic model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the Anthropic API call.
    **call_params: The `AnthropicCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an Anthropic API call.
'''
