"""The `litellm_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ..openai._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
)
from ._utils import setup_call
from .call_params import LiteLLMCallParams
from .call_response import LiteLLMCallResponse
from .call_response_chunk import LiteLLMCallResponseChunk
from .stream import LiteLLMStream
from .tool import LiteLLMTool

litellm_call = call_factory(
    TCallResponse=LiteLLMCallResponse,
    TCallResponseChunk=LiteLLMCallResponseChunk,
    TToolType=LiteLLMTool,
    TStream=LiteLLMStream,
    default_call_params=LiteLLMCallParams(),
    setup_call=setup_call,  # pyright: ignore [reportArgumentType]
    get_json_output=get_json_output,
    handle_stream=handle_stream,  # pyright: ignore [reportArgumentType]
    handle_stream_async=handle_stream_async,  # pyright: ignore [reportArgumentType]
)
"""A decorator for calling the LiteLLM API with a typed function.

usage docs: learn/calls.md

This decorator is used to wrap a typed function that calls the LiteLLM API. It parses
the prompt template of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.litellm import litellm_call


@litellm_call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

Args:
    model (str): The model to use in the API call.
    stream (bool): Whether to stream the response from the API call.
    tools (list[BaseTool | Callable]): The tools to use in the API call.
    response_model (BaseModel | BaseType): The response model into which the response
        should be structured.
    output_parser (Callable[[OpenAICallResponse | ResponseModelT], Any]): A function for
        parsing the call response whose value will be returned in place of the original
        call response.
    json_mode (bool): Whether to use JSON Mode.
    client (None): LiteLLM does not support a custom client.
    call_params (OpenAICallParams): The `OpenAICallParams` call parameters to use in the
        API call.

Returns:
    decorator (Callable): The decorator for turning a typed function into a LiteLLM
        routed LLM API call.
"""
