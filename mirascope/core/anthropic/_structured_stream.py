"""This module contains the Anthropic `structured_stream_decorator` function."""

from collections.abc import Generator
from functools import wraps
from typing import Callable, Generic, Iterable, ParamSpec, TypeVar

from anthropic import Anthropic
from anthropic._base_client import BaseClient
from anthropic.lib.streaming import MessageStreamEvent
from pydantic import BaseModel

from ..base import BaseStructuredStream, _utils

# from ._utils import setup_extract
from .call_params import AnthropicCallParams
from .dynamic_config import AnthropicDynamicConfig
from .tool import AnthropicTool

_P = ParamSpec("_P")
_ResponseModelT = TypeVar("_ResponseModelT", bound=BaseModel | _utils.BaseType)


class AnthropicStructuredStream(
    Generic[_ResponseModelT],
    BaseStructuredStream[MessageStreamEvent, _ResponseModelT],
):
    """A class for streaming structured outputs from Anthropic's API."""

    def __iter__(self) -> Generator[_ResponseModelT, None, None]:
        """Iterates over the stream and extracts structured outputs."""
        json_output = ""
        for chunk in self.stream:
            if chunk.type == "content_block_delta":
                if chunk.delta.type in ["text", "text_delta"]:
                    json_output += chunk.delta.text
                elif chunk.delta.type == "input_json_delta":
                    json_output += chunk.delta.partial_json
            if json_output:
                yield _utils.extract_tool_return(self.response_model, json_output, True)
        yield _utils.extract_tool_return(self.response_model, json_output, False)


def structured_stream_decorator(
    fn: Callable[_P, AnthropicDynamicConfig],
    model: str,
    response_model: type[_ResponseModelT],
    client: BaseClient | None,
    call_params: AnthropicCallParams,
) -> Callable[_P, Iterable[_ResponseModelT]]:
    assert response_model is not None
    tool = _utils.setup_extract_tool(response_model, AnthropicTool)

    @wraps(fn)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> Iterable[_ResponseModelT]:
        # assert response_model is not None
        # fn_args = _utils.get_fn_args(fn, args, kwargs)
        # fn_return = fn(*args, **kwargs)
        # json_mode, messages, call_kwargs = setup_extract(
        #     fn, fn_args, fn_return, tool, call_params
        # )
        # _client = client or Anthropic()
        # return AnthropicStructuredStream(
        #     stream=(
        #         chunk
        #         for chunk in _client.messages.create(
        #             model=model, stream=True, messages=messages, **call_kwargs
        #         )
        #     ),
        #     response_model=response_model,
        #     json_mode=json_mode,
        # )
        ...

    return inner
