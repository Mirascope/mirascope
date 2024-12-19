from typing import Literal, TypeAlias, cast

from mirascope.core.base.types import FinishReason

FinishReasonMappingValue: TypeAlias = Literal[
    "stop", "length", "function_call", "tool_calls", "content_filter"
]


def _convert_finish_reasons_to_common_finish_reasons_from_mapping(
    finish_reasons: list[str], mapping: dict[str, FinishReasonMappingValue]
) -> list[FinishReason] | None:
    """Provider-agnostic finish reasons."""
    return [
        cast(FinishReason, mapping[reason])
        for reason in finish_reasons
        if reason in mapping
    ] or None
