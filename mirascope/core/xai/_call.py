"""The `xai_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ..openai._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
)
from ._utils import setup_call
from .call_params import XAICallParams
from .call_response import XAICallResponse
from .call_response_chunk import XAICallResponseChunk
from .stream import XAIStream
from .tool import XAITool

xai_call = call_factory(
    TCallResponse=XAICallResponse,
    TCallResponseChunk=XAICallResponseChunk,
    TToolType=XAITool,
    TStream=XAIStream,
    default_call_params=XAICallParams(),
    setup_call=setup_call,  # pyright: ignore [reportArgumentType]
    get_json_output=get_json_output,
    handle_stream=handle_stream,  # pyright: ignore [reportArgumentType]
    handle_stream_async=handle_stream_async,  # pyright: ignore [reportArgumentType]
)
"""A decorator for calling the xAI API with a typed function.

usage docs: learn/calls.md

This decorator is used to wrap a typed function that calls the xAI API. It parses
the prompt template of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.xai import xai_call


@xai_call("grok-2-latest")
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
    client (None): xAI does not support a custom client.
    call_params (OpenAICallParams): The `OpenAICallParams` call parameters to use in the
        API call.

Returns:
    decorator (Callable): The decorator for turning a typed function into a xAI
        routed LLM API call.
"""
