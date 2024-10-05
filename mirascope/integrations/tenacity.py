"""DEPRECATED."""

import inspect
import warnings

from ..retries.tenacity import collect_errors

warnings.warn(
    inspect.cleandoc("""
    The import `mirascope.integrations.tenacity` is deprecated in versions `>=1.3`.
    Please instead use the `mirascope.retries.tenacity` import.
    """)
)
__all__ = ["collect_errors"]
