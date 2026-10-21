"""Failed Responses streams must not look like successful empty responses."""

from unittest.mock import patch

import pytest
from openai.types.responses import ResponseStreamEvent
from pydantic import TypeAdapter

from mirascope import llm

_EVENT_ADAPTER: TypeAdapter[ResponseStreamEvent] = TypeAdapter(ResponseStreamEvent)


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            {"code": "server_error", "message": "The model crashed."},
            "server_error: The model crashed.",
        ),
        (None, "unknown_error: no error message"),
    ],
)
def test_failed_responses_stream_raises_api_error(
    error: dict[str, str] | None, expected: str
) -> None:
    event = _EVENT_ADAPTER.validate_python(
        {
            "type": "response.failed",
            "sequence_number": 1,
            "response": {
                "id": "resp_1",
                "object": "response",
                "created_at": 1,
                "status": "failed",
                "error": error,
                "incomplete_details": None,
                "model": "gpt-5.6-terra",
                "output": [],
                "parallel_tool_calls": True,
                "tool_choice": "auto",
                "tools": [],
            },
        }
    )

    model = llm.Model("openai/gpt-5.6-terra:responses")
    with patch(
        "openai.resources.responses.Responses.create", return_value=iter([event])
    ):
        response = model.stream("Say hi")
        with pytest.raises(llm.APIError, match=expected) as exc_info:
            response.finish()

    assert exc_info.value.provider == "openai"
