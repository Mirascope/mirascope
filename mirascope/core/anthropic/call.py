"""The `anthropic_call` decorator for functions as LLM calls."""

from anthropic.types import MessageParam

from ..base import call_factory
from ..base._stream import BaseStream
from ._structured_stream import structured_stream_decorator
from ._utils import (
    anthropic_api_calculate_cost,
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import AnthropicCallParams
from .call_response import AnthropicCallResponse
from .call_response_chunk import AnthropicCallResponseChunk
from .dynamic_config import AnthropicDynamicConfig
from .tool import AnthropicTool

AnthropicStream = BaseStream[
    AnthropicCallResponseChunk,
    MessageParam,
    MessageParam,
    MessageParam,
    AnthropicTool,
    AnthropicDynamicConfig,
]

anthropic_call = call_factory(
    TCallResponse=AnthropicCallResponse,
    TCallResponseChunk=AnthropicCallResponseChunk,
    TCallParams=AnthropicCallParams,
    TDynamicConfig=AnthropicDynamicConfig,
    TStream=AnthropicStream,
    TMessageParamType=MessageParam,
    TToolType=AnthropicTool,
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    calculate_cost=anthropic_api_calculate_cost,
    structured_stream_decorator=structured_stream_decorator,
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
