"""The `vertex_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._utils import get_json_output, handle_stream, handle_stream_async, setup_call
from .call_params import VertexCallParams
from .call_response import VertexCallResponse
from .call_response_chunk import VertexCallResponseChunk
from .stream import VertexStream
from .tool import VertexTool

vertex_call = call_factory(
    TCallResponse=VertexCallResponse,
    TCallResponseChunk=VertexCallResponseChunk,
    TStream=VertexStream,
    TToolType=VertexTool,
    default_call_params=VertexCallParams(),
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,  # pyright: ignore [reportArgumentType]
    handle_stream_async=handle_stream_async,  # pyright: ignore [reportArgumentType]
)
"""A decorator for calling the Vertex API with a typed function.

usage docs: learn/calls.md

This decorator is used to wrap a typed function that calls the Vertex API. It parses
the prompt template of the wrapped function as the messages array and templates the
input arguments for the function into each message's template.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.vertex import vertex_call


@vertex_call("gemini-1.5-flash")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
```

Args:
    model (str): The Vertex model to use in the API call.
    stream (bool): Whether to stream the response from the API call.
    tools (list[BaseTool | Callable]): The tools to use in the Vertex API call.
    response_model (BaseModel | BaseType): The response model into which the response
        should be structured.
    output_parser (Callable[[VertexCallResponse | ResponseModelT], Any]): A function
        for parsing the call response whose value will be returned in place of the
        original call response.
    json_modem (bool): Whether to use JSON Mode.
    client (object): An optional custom client to use in place of the default client.
    call_params (VertexCallParams): The `VertexCallParams` call parameters to use in the
        API call.

Returns:
    decorator (Callable): The decorator for turning a typed function into a Vertex API
        call.
"""
