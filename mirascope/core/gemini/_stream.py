import inspect
from functools import wraps
from typing import Callable, Generator, Generic, ParamSpec, TypeVar

from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import (  # type: ignore
    ContentDict,
    GenerateContentResponse,
)

from ..base import BaseStream, BaseTool, _utils
from ._utils import setup_call
from .call_params import GeminiCallParams
from .call_response_chunk import GeminiCallResponseChunk
from .function_return import GeminiCallFunctionReturn
from .tool import GeminiTool

_P = ParamSpec("_P")
_OutputT = TypeVar("_OutputT")


class GeminiStream(
    BaseStream[GeminiCallResponseChunk, ContentDict, ContentDict, GeminiTool, _OutputT],
    Generic[_OutputT],
):
    """A class for streaming responses from Google's Gemini API."""

    def __init__(self, stream: Generator[GeminiCallResponseChunk, None, None]):
        """Initializes an instance of `GeminiStream`."""
        super().__init__(stream, ContentDict)


def stream_decorator(
    fn: Callable[_P, GeminiCallFunctionReturn],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    output_parser: Callable[[GeminiCallResponseChunk], _OutputT] | None,
    call_params: GeminiCallParams,
) -> Callable[_P, GeminiStream[GenerateContentResponse | _OutputT]]:
    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> GeminiStream:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        _, messages, tool_types, call_kwargs = setup_call(
            fn, fn_args, fn_return, tools, call_params
        )
        client = GenerativeModel(model_name=model)
        stream = client.generate_content(
            messages,
            stream=True,
            tools=tools,
            **call_kwargs,
        )

        def generator():
            for chunk in stream:
                yield GeminiCallResponseChunk(
                    tags=fn.__annotations__.get("tags", []),
                    chunk=chunk,
                    user_message_param=messages[-1]
                    if messages[-1]["role"] == "user"
                    else None,
                    tool_types=tool_types,
                    cost=None,
                )

        return GeminiStream(generator(), output_parser)

    return inner
