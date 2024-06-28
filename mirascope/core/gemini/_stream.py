from functools import wraps
from typing import Any, Callable, Generator, ParamSpec

from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import ContentDict  # type: ignore

from ..base import BaseStream, BaseTool, _utils
from ._utils import setup_call
from .call_params import GeminiCallParams
from .call_response_chunk import GeminiCallResponseChunk
from .function_return import GeminiDynamicConfig
from .tool import GeminiTool

_P = ParamSpec("_P")


class GeminiStream(
    BaseStream[GeminiCallResponseChunk, ContentDict, ContentDict, GeminiTool],
):
    """A class for streaming responses from Google's Gemini API."""

    provider: str = "gemini"

    def __init__(
        self,
        stream: Generator[GeminiCallResponseChunk, None, None],
        prompt_template: str,
        fn_args: dict[str, Any],
        call_params: GeminiCallParams,
    ):
        """Initializes an instance of `GeminiStream`."""
        super().__init__(stream, ContentDict, prompt_template, fn_args, call_params)


def stream_decorator(
    fn: Callable[_P, GeminiDynamicConfig],
    model: str,
    tools: list[type[BaseTool] | Callable] | None,
    call_params: GeminiCallParams,
) -> Callable[_P, GeminiStream]:
    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> GeminiStream:
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        prompt_template, messages, tool_types, call_kwargs = setup_call(
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

        return GeminiStream(generator(), prompt_template, fn_args, call_params)

    return inner