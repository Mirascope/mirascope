"""MLX error handling utilities."""

from collections.abc import Generator
from contextlib import contextmanager

from huggingface_hub.errors import LocalEntryNotFoundError

from ...exceptions import NotFoundError


def handle_mlx_error(e: Exception) -> None:
    """Convert MLX/HuggingFace Hub errors to Mirascope errors.

    Args:
        e: The exception to handle.

    Raises:
        NotFoundError: If the error is a model not found error.
        Exception: Re-raises the original exception if not handled.
    """
    # HuggingFace Hub raises LocalEntryNotFoundError when model files are not found
    if isinstance(e, LocalEntryNotFoundError):
        raise NotFoundError(str(e)) from e
    raise e  # pragma: no cover


@contextmanager
def wrap_mlx_errors() -> Generator[None, None, None]:
    """Context manager that wraps MLX/HuggingFace Hub errors.

    Usage:
        with wrap_mlx_errors():
            model, tokenizer = mlx_load(model_id)
    """
    try:
        yield
    except Exception as e:
        handle_mlx_error(e)
