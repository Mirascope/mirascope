"""Context management utilities for distributed tracing."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import ExitStack, contextmanager
from typing import Any

from opentelemetry import context as otel_context
from opentelemetry.context import Context

from .propagation import extract_context
from .session import extract_session_id, session


@contextmanager
def propagated_context(
    *,
    parent: Context | None = None,
    extract_from: Mapping[str, Any] | None = None,
) -> Iterator[None]:
    """Attach a parent context or extract context from carrier headers.

    This context manager is used to establish trace context continuity,
    typically on the server side when receiving requests. It either extracts
    context from incoming headers or attaches a pre-existing context.

    Args:
        parent: Pre-existing OTEL context to attach. Mutually exclusive with extract_from.
        extract_from: Dictionary of headers to extract context from (e.g., request.headers).
            Mutually exclusive with parent.

    Raises:
        ValueError: If both parent and extract_from are provided, or if neither is provided.

    Example:
        Server-side context extraction from FastAPI request:

        ```python
        @app.post("/endpoint")
        async def endpoint(request: Request):
            with propagated_context(extract_from=dict(request.headers)):
                result = process_request()
            return result
        ```

        Using a pre-existing context:

        ```python
        with propagated_context(parent=existing_context):
            do_work()
        ```
    """
    if parent is not None and extract_from is not None:
        raise ValueError("Cannot specify both 'parent' and 'extract_from' parameters")

    if parent is None and extract_from is None:
        raise ValueError("Must specify either 'parent' or 'extract_from' parameter")

    if extract_from is not None:
        with ExitStack() as stack:
            session_id = extract_session_id(extract_from)
            if session_id:
                stack.enter_context(session(id=session_id))

            extracted_context = extract_context(extract_from)
            token = otel_context.attach(extracted_context)
            stack.callback(otel_context.detach, token)

            yield
    elif parent is not None:
        token = otel_context.attach(parent)
        try:
            yield
        finally:
            otel_context.detach(token)
