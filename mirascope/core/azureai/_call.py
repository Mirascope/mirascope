"""The `azureai_call` decorator for functions as LLM calls."""

from ..base import call_factory
from ._utils import (
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import AzureAICallParams
from .call_response import AzureAICallResponse
from .call_response_chunk import AzureAICallResponseChunk
from .dynamic_config import AzureAIDynamicConfig
from .stream import AzureAIStream
from .tool import AzureAITool

azureai_call = call_factory(
    TCallResponse=AzureAICallResponse,
    TCallResponseChunk=AzureAICallResponseChunk,
    TDynamicConfig=AzureAIDynamicConfig,
    TToolType=AzureAITool,
    TStream=AzureAIStream,
    TCallParams=AzureAICallParams,
    default_call_params=AzureAICallParams(),
    setup_call=setup_call,
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
)
"""A decorator for calling the AzureAI API with a typed function.

usage docs: learn/calls.md

This decorator is used to wrap a typed function that calls the AzureAI API. It parses
the prompt template of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.azureai import azureai_call


@azureai_call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

response = recommend_book("fantasy")
print(response.content)
```

Args:
    model (str): The AzureAI model to use in the API call.
    stream (bool): Whether to stream the response from the API call.
    tools (list[BaseTool | Callable]): The tools to use in the AzureAI API call.
    response_model (BaseModel | BaseType): The response model into which the response
        should be structured.
    output_parser (Callable[[AzureAICallResponse | ResponseModelT], Any]): A function for 
        parsing the call response whose value will be returned in place of the original
        call response.
    json_mode (bool): Whether to use JSON Mode.
    client (object): An optional custom client to use in place of the default client.
    call_params (AzureAICallParams): The `AzureAICallParams` call parameters to use in the
        API call.

Returns:
    decorator (Callable): The decorator for turning a typed function into an AzureAI API
        call.
"""
