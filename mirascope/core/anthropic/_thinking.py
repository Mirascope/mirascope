"""Centralized thinking-related imports and compatibility handling for Anthropic."""

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel
from typing_extensions import TypedDict


# Always define the stubs with underscore names
class _ThinkingConfigParam(TypedDict):
    type: Literal["enabled"]
    budget_tokens: int


class _ThinkingBlock(BaseModel):
    signature: str
    thinking: str
    type: Literal["thinking"]


class _ThinkingDelta(BaseModel):
    thinking: str
    type: Literal["thinking_delta"]


class _SignatureDelta(BaseModel):
    signature: str
    type: Literal["signature_delta"]


HAS_THINKING_SUPPORT = True

# Define the public names based on what's available
if TYPE_CHECKING:
    # For static analysis, always use our stubs so types are consistent
    ThinkingConfigParam = _ThinkingConfigParam
    ThinkingBlock = _ThinkingBlock
    ThinkingDelta = _ThinkingDelta
    SignatureDelta = _SignatureDelta
else:
    # At runtime, use real types if available, otherwise stubs
    try:
        from anthropic.types import (  # pyright: ignore [reportAttributeAccessIssue]
            ThinkingBlock,
            ThinkingDelta,
        )
        from anthropic.types.signature_delta import (
            SignatureDelta,  # pyright: ignore [reportMissingImports]
        )
        from anthropic.types.thinking_config_param import (
            ThinkingConfigParam,  # pyright: ignore [reportMissingImports]
        )

        HAS_THINKING_SUPPORT = True

    except ImportError:  # pragma: no cover
        ThinkingConfigParam = _ThinkingConfigParam
        ThinkingBlock = _ThinkingBlock
        ThinkingDelta = _ThinkingDelta
        SignatureDelta = _SignatureDelta
        HAS_THINKING_SUPPORT = False


__all__ = [
    "HAS_THINKING_SUPPORT",
    "SignatureDelta",
    "ThinkingBlock",
    "ThinkingConfigParam",
    "ThinkingDelta",
]
