from typing import Any, Callable

from ...core.base import BaseCallResponse
from ...core.base._stream import BaseStream


def get_call_response_observation(result: BaseCallResponse, fn: Callable[..., Any]):
    metadata = fn.__annotations__.get("metadata", {})
    tags = getattr(metadata, "tags", {})
    return {
        "name": f"{fn.__name__} with {result.model}",
        "input": result.prompt_template,
        "metadata": result.response,
        "tags": tags,
        "model": result.model,
        "output": result.message_param.get("content", None),
    }


def get_stream_observation(stream: BaseStream, fn: Callable[..., Any]):
    return {
        "name": f"{fn.__name__} with {stream.model}",
        "input": stream.prompt_template,
        "tags": fn.__annotations__.get("tags", []),
        "model": stream.model,
        "output": stream.message_param.get("content", None),
    }
