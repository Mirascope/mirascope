"""The `groq_call` decorator for functions as LLM calls."""

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base import call_factory
from ..base._stream import BaseStream
from ._utils import (
    calculate_cost,
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import GroqCallParams
from .call_response import GroqCallResponse
from .call_response_chunk import GroqCallResponseChunk
from .dynamic_config import GroqDynamicConfig
from .tool import GroqTool


class GroqStream(
    BaseStream[
        GroqCallResponse,
        GroqCallResponseChunk,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        GroqTool,
        GroqDynamicConfig,
        GroqCallParams,
    ]
): ...  # pragma: no cover


groq_call = call_factory(
    TCallResponse=GroqCallResponse,
    TCallResponseChunk=GroqCallResponseChunk,
    TDynamicConfig=GroqDynamicConfig,
    TMessageParamType=ChatCompletionAssistantMessageParam,
    TToolType=GroqTool,
    TStream=GroqStream,
    TCallParams=GroqCallParams,
    default_call_params=GroqCallParams(),
    setup_call=setup_call,  # type: ignore
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    calculate_cost=calculate_cost,
    provider="groq",
)
'''A decorator for calling the Groq API with a typed function.

This decorator is used to wrap a typed function that calls the Groq API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@groq_call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The Groq model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the Groq API call.
    **call_params: The `GroqCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an Groq API call.
'''
