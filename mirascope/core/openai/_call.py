"""The `openai_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .stream import OpenAIStream
from .tool import OpenAITool

openai_call = call_factory(
    TCallResponse=OpenAICallResponse,
    TCallResponseChunk=OpenAICallResponseChunk,
    TToolType=OpenAITool,
    TStream=OpenAIStream,
    default_call_params=OpenAICallParams(),
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
)
"""A decorator for calling the OpenAI API with a typed function.

usage docs: learn/calls.md

This decorator is used to wrap a typed function that calls the OpenAI API. It parses
the prompt template of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.openai import openai_call


@openai_call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

Args:
    model (str): The OpenAI model to use in the API call.
    stream (bool): Whether to stream the response from the API call.
    tools (list[BaseTool | Callable]): The tools to use in the OpenAI API call.
    response_model (BaseModel | BaseType): The response model into which the response
        should be structured.
    output_parser (Callable[[OpenAICallResponse | ResponseModelT], Any]): A function for 
        parsing the call response whose value will be returned in place of the original
        call response.
    json_mode (bool): Whether to use JSON Mode.
    client (object): An optional custom client to use in place of the default client.
    call_params (OpenAICallParams): The `OpenAICallParams` call parameters to use in the
        API call.

Returns:
    decorator (Callable): The decorator for turning a typed function into an OpenAI API
        call.
"""
