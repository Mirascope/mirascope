"""This module contains the Gemini `structured_stream_decorator` function."""

import json
from collections.abc import Generator
from functools import wraps
from typing import Callable, Generic, Iterable, ParamSpec, TypeVar

from google.generativeai import GenerativeModel  # type: ignore
from google.generativeai.types import GenerateContentResponse
from pydantic import BaseModel

from ..base import BaseStructuredStream, _utils
from ._utils import setup_extract
from .call_params import GeminiCallParams
from .function_return import GeminiCallFunctionReturn
from .tool import GeminiTool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


class GeminiStructuredStream(
    Generic[_ResponseModelT],
    BaseStructuredStream[GenerateContentResponse, _ResponseModelT],
):
    """A class for streaming structured outputs from Gemini's API."""

    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""
        json_output = ""
        for chunk in self.stream:
            if (
                self.json_mode
                and (content := chunk.candidates[0].content.parts[0].text) is not None
            ):
                print(content)
                json_output += content
            elif (
                tool_calls := chunk.candidates[0].content.parts[0].function_call
            ) and (arguments := tool_calls.args):
                json_output += json.dumps(dict(arguments))
            else:
                ValueError("No tool call or JSON object found in response.")
            if json_output:
                yield _utils.extract_tool_return(self.response_model, json_output, True)
        yield _utils.extract_tool_return(self.response_model, json_output, False)


def structured_stream_decorator(
    fn: Callable[_P, GeminiCallFunctionReturn],
    model: str,
    response_model: type[_ResponseModelT],
    call_params: GeminiCallParams,
) -> Callable[_P, Iterable[_ResponseModelT]]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, GeminiTool)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> Iterable[_ResponseModelT]:
        assert response_model is not None
        fn_args = _utils.get_fn_args(fn, args, kwargs)
        fn_return = fn(*args, **kwargs)
        json_mode, messages, call_kwargs = setup_extract(
            fn, fn_args, fn_return, tool, call_params
        )
        client = GenerativeModel(model_name=model)
        stream = client.generate_content(
            messages,
            stream=True,
            **call_kwargs,
        )
        return GeminiStructuredStream(
            stream=(chunk for chunk in stream),
            response_model=response_model,
            json_mode=json_mode,
        )

    return inner
