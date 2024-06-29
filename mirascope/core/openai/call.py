"""The `openai_call` decorator for functions as LLM calls."""

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base import call_factory
from ..base._stream import BaseStream
from ._structured_stream import structured_stream_decorator
from ._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
    openai_api_calculate_cost,
    setup_call,
)
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dyanmic_config import OpenAIDynamicConfig
from .tool import OpenAITool

OpenAIStream = BaseStream[
    OpenAICallResponseChunk,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    OpenAITool,
    OpenAIDynamicConfig,
]

openai_call = call_factory(
    TCallResponse=OpenAICallResponse,
    TCallResponseChunk=OpenAICallResponseChunk,
    TCallParams=OpenAICallParams,
    TDynamicConfig=OpenAIDynamicConfig,
    TStream=OpenAIStream,
    TMessageParamType=ChatCompletionAssistantMessageParam,
    TToolType=OpenAITool,
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    calculate_cost=openai_api_calculate_cost,
    # TO BE REFACTORED
    structured_stream_decorator=structured_stream_decorator,
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
