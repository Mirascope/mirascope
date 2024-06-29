"""The `openai_call` decorator for functions as LLM calls."""

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ..base import (
    BaseStream,
    call_factory,
    create_factory,
    extract_factory,
    stream_factory,
)
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
    create_decorator=create_factory(
        TBaseCallResponse=OpenAICallResponse,
        setup_call=setup_call,
        calculate_cost=openai_api_calculate_cost,
    ),
    stream_decorator=stream_factory(
        TBaseCallResponseChunk=OpenAICallResponseChunk,
        TStream=OpenAIStream,
        TMessageParamType=ChatCompletionAssistantMessageParam,
        setup_call=setup_call,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
    ),
    extract_decorator=extract_factory(
        TBaseCallResponse=OpenAICallResponse,
        TToolType=OpenAITool,
        setup_call=setup_call,
        get_json_output=get_json_output,
        calculate_cost=openai_api_calculate_cost,
    ),
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
