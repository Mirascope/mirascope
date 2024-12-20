from typing import Literal, TypeAlias, cast

from mirascope.core.base.types import FinishReason

FinishReasonMappingValue: TypeAlias = Literal[
    "stop", "length", "tool_calls", "content_filter"
]


def _convert_finish_reasons_to_common_finish_reasons_from_mapping(
    finish_reasons: list[str] | None, mapping: dict[str, FinishReasonMappingValue]
) -> list[FinishReason] | None:
    """Provider-agnostic finish reasons."""
    if not finish_reasons:
        return None
    return [
        cast(FinishReason, mapping[reason])
        for reason in finish_reasons
        if reason in mapping
    ] or None
