"""End-to-end tests for a LLM call with all params set."""

from typing import get_type_hints

import pytest

from mirascope import llm
from tests.e2e.conftest import E2E_MODEL_IDS
from tests.utils import (
    Snapshot,
    response_snapshot_dict,
    snapshot_test,
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


@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
@pytest.mark.vcr
def test_call_with_params(
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test synchronous call with all parameters to verify param handling and logging."""

    @llm.call(model_id, **ALL_PARAMS)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot, caplog) as snap:
        response = add_numbers(4200, 42)
        snap["response"] = (response_snapshot_dict(response),)
