"""The `mistral_call` decorator for functions as LLM calls."""

from ..base import BaseMessageParam, call_factory
from ..base._stream import BaseStream
from ._utils import (
    calculate_cost,
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import MistralCallParams
from .call_response import MistralCallResponse
from .call_response_chunk import MistralCallResponseChunk
from .dynamic_config import MistralDynamicConfig
from .tool import MistralTool


class MistralStream(
    BaseStream[
        MistralCallResponse,
        MistralCallResponseChunk,
        BaseMessageParam,
        BaseMessageParam,
        BaseMessageParam,
        MistralTool,
        MistralDynamicConfig,
        MistralCallParams,
    ]
): ...  # pragma: no cover


mistral_call = call_factory(
    TCallResponse=MistralCallResponse,
    TCallResponseChunk=MistralCallResponseChunk,
    TDynamicConfig=MistralDynamicConfig,
    TMessageParamType=BaseMessageParam,
    TToolType=MistralTool,
    TStream=MistralStream,
    TCallParams=MistralCallParams,
    default_call_params=MistralCallParams(),
    setup_call=setup_call,  # type: ignore
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    calculate_cost=calculate_cost,
)
'''A decorator for calling the Mistral API with a typed function.

This decorator is used to wrap a typed function that calls the Mistral API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@mistral_call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The Mistral model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the Mistral API call.
    **call_params: The `MistralCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an Mistral API call.
'''
