"""Utils associated with formatting."""

from typing import cast

from .decorator import format
from .types import (
    FormatInfo,
    FormatT,
    Formattable,
)


def ensure_formattable(
    formattable: type[FormatT],
) -> FormatInfo:
    """Ensures that a class is `Formattable`, and returns the format.

    This is intended to be used by final consumers of `FormatT` (e.g. the clients) where
    they need to ensure that the `FormatT` is `Formattable`, ie. that it has been decorated.

    The `FormatT` will be decorated into a `Formattable` if it wasn't already.
    """
    if isinstance(formattable, Formattable):
        return formattable.__mirascope_format_info__
    return cast(Formattable, format(formattable)).__mirascope_format_info__
