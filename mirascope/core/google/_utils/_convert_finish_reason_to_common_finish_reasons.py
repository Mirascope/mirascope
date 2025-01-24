from mirascope.core.base._utils._convert_provider_finish_reason_to_finish_reason import (
    FinishReasonMappingValue,
    _convert_finish_reasons_to_common_finish_reasons_from_mapping,
)
from mirascope.core.base.types import FinishReason

_FinishReasonMapping: dict[str, FinishReasonMappingValue] = {
    "FINISH_REASON_UNSPECIFIED": "stop",
    "STOP": "stop",
    "MAX_TOKENS": "length",
    "SAFETY": "content_filter",
    "RECITATION": "stop",
    "OTHER": "stop",
    "BLOCKLIST": "stop",
    "PROHIBITED_CONTENT": "stop",
    "SPII": "stop",
    "MALFORMED_FUNCTION_CALL": "stop",
}


def _convert_finish_reasons_to_common_finish_reasons(
    finish_reasons: list[str],
) -> list[FinishReason] | None:
    """Provider-agnostic finish reasons."""
    return _convert_finish_reasons_to_common_finish_reasons_from_mapping(
        finish_reasons, _FinishReasonMapping
    )
