"""The `anthropic_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .dynamic_config import AnthropicDynamicConfig
from .stream import AnthropicStream
from .tool import AnthropicTool

anthropic_call = call_factory(
    TCallResponse=AnthropicCallResponse,
    TCallResponseChunk=AnthropicCallResponseChunk,
    TDynamicConfig=AnthropicDynamicConfig,
    TStream=AnthropicStream,
    TToolType=AnthropicTool,
    TCallParams=AnthropicCallParams,
    default_call_params=AnthropicCallParams(max_tokens=1000),
    setup_call=setup_call,  # type: ignore
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
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
