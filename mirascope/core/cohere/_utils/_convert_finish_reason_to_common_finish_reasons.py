from mirascope.core.base._utils._convert_provider_finish_reason_to_finish_reason import (
    FinishReasonMappingValue,
    _convert_finish_reasons_to_common_finish_reasons_from_mapping,
)
from mirascope.core.base.types import FinishReason

_FinishReasonMapping: dict[str, FinishReasonMappingValue] = {
    "COMPLETE": "stop",
    "STOP_SEQUENCE": "stop",
    "ERROR": "stop",
    "ERROR_TOXIC": "content_filter",
    "ERROR_LIMIT": "length",
    "USER_CANCEL": "stop",
    "MAX_TOKENS": "length",
}


def _convert_finish_reasons_to_common_finish_reasons(
    finish_reasons: list[str] | None,
) -> list[FinishReason] | None:
    """Provider-agnostic finish reasons."""
    return _convert_finish_reasons_to_common_finish_reasons_from_mapping(
        finish_reasons, _FinishReasonMapping
    )
