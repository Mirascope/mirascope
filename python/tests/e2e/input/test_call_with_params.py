"""End-to-end tests for a LLM call with all params set."""

import logging
from typing import get_type_hints

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import (
    exception_snapshot_dict,
    response_snapshot_dict,
)

# ============= ALL PARAMS TESTS =============
ALL_PARAMS: llm.Params = {
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 0.3,
    "top_k": 50,
    "seed": 42,
    "stop_sequences": ["4242"],
    "thinking": False,
    "encode_thoughts_as_text": False,
}


def test_all_params_includes_every_param() -> None:
    """Verify that ALL_PARAMS includes every parameter defined in Params."""
    params_keys = set(get_type_hints(llm.Params).keys())
    all_params_keys = set(ALL_PARAMS.keys())
    assert params_keys == all_params_keys, (
        f"ALL_PARAMS is missing parameters: {params_keys - all_params_keys}"
    )


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_params(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test synchronous call with all parameters to verify param handling and logging."""

    @llm.call(provider=provider, model_id=model_id, **ALL_PARAMS)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    snapshot_data = {}
    with caplog.at_level(logging.WARNING):
        try:
            response = add_numbers(4200, 42)
            snapshot_data["response"] = (response_snapshot_dict(response),)
        except Exception as e:
            snapshot_data["exception"] = exception_snapshot_dict(e)

        snapshot_data["logging"] = [
            record.message
            for record in caplog.records
            if record.levelno >= logging.WARNING
        ]
        assert snapshot_data == snapshot
