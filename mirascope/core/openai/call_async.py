"""The `openai_call_async` decorator for easy OpenAI API typed functions."""

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base import call_async_factory
from ..base._stream import BaseStream
from ._structured_stream_async import structured_stream_async_decorator
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

OpenAIAsyncStream = BaseStream[
    OpenAICallResponseChunk,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    OpenAITool,
    OpenAIDynamicConfig,
]


openai_call_async = call_async_factory(
    TCallResponse=OpenAICallResponse,
    TCallResponseChunk=OpenAICallResponseChunk,
    TCallParams=OpenAICallParams,
    TDynamicConfig=OpenAIDynamicConfig,
    TStream=OpenAIAsyncStream,
    TMessageParamType=ChatCompletionAssistantMessageParam,
    TToolType=OpenAITool,
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    calculate_cost=openai_api_calculate_cost,
    structured_stream_async_decorator=structured_stream_async_decorator,
)
'''A decorator for calling the AsyncOpenAI API with a typed function.

This decorator is used to wrap a typed function that calls the OpenAI API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@openai_call_async(model="gpt-4o")
async def recommend_book(genre: str):
    """Recommend a {genre} book."""

async def run():
    response = await recommend_book("fantasy")

asyncio.run(run())
```

Args:
    model: The OpenAI model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the OpenAI API call.
    **call_params: The `OpenAICallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an AsyncOpenAI API call.
'''
