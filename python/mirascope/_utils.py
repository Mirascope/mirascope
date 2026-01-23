"""Shared internal utilities for mirascope."""

from typing import Any

# Attributes to copy from wrapped functions (matches functools.WRAPPER_ASSIGNMENTS)
WRAPPER_ASSIGNMENTS = (
    "__module__",
    "__name__",
    "__qualname__",
    "__annotations__",
    "__doc__",
)


def copy_function_metadata(target: Any, source: Any) -> None:  # noqa: ANN401
    """Copy standard function metadata from source to target.

    Copies __module__, __name__, __qualname__, __annotations__, __doc__
    from source to target, and sets __wrapped__ to source.

    This enables decorator stacking by preserving the original function's
    metadata on wrapper objects.

    Args:
        target: The wrapper object to copy metadata to
        source: The original function to copy metadata from
    """
    for attr in WRAPPER_ASSIGNMENTS:
        try:
            value = getattr(source, attr)
            object.__setattr__(target, attr, value)
        except AttributeError:
            pass
    object.__setattr__(target, "__wrapped__", source)
