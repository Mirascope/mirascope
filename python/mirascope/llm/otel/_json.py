"""JSON helpers for OTEL serialization."""

from __future__ import annotations

import json
from typing import Any


def json_dumps(data: Any) -> str:  # noqa: ANN401
    """Return a JSON string with consistent options for OTEL payloads."""

    return json.dumps(data, ensure_ascii=False)
