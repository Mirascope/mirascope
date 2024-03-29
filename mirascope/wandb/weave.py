"""Integration with Weave from Weights & Biases"""
from typing import Type, TypeVar, overload

import weave

from mirascope.base import BaseCall, BaseExtractor

BaseCallT = TypeVar("BaseCallT", bound=BaseCall)
BaseExtractorT = TypeVar("BaseExtractorT", bound=BaseExtractor)


@overload
def with_weave(cls: Type[BaseCallT]) -> Type[BaseCallT]:
    ...  # pragma: no cover


@overload
def with_weave(cls: Type[BaseExtractorT]) -> Type[BaseExtractorT]:
    ...  # pragma: no cover


def with_weave(cls):
    """Wraps `BaseCall` and `BaseExtractor` functions to automatically use weave."""
    if hasattr(cls, "call"):
        setattr(cls, "call", weave.op()(cls.call))
    if hasattr(cls, "call_async"):
        setattr(cls, "call_async", weave.op()(cls.call_async))

    # It appears Weave does not yet support streaming or does it in a different way? :(
    # Our calls will be tracked, but the sub-calls don't since the streaming happens
    # when iterating through the generator after the call.
    if hasattr(cls, "stream"):
        setattr(cls, "stream", weave.op()(cls.stream))
    if hasattr(cls, "stream_async"):
        setattr(cls, "stream_async", weave.op()(cls.stream_async))

    # BUG https://github.com/wandb/weave/issues/1408 prevents extract + weave working
    # if hasattr(cls, "extract"):
    #     setattr(cls, "extract", weave.op()(cls.extract))
    # if hasattr(cls, "extract_async"):
    #     setattr(cls, "extract_async", weave.op()(cls.extract_async))

    cls.call_params.weave = weave.op()
    return cls
