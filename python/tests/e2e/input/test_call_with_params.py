"""End-to-end tests for a LLM call with all params set."""

from typing import get_type_hints

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS
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


def get_test_params(model_id: llm.ModelId) -> llm.Params:
    """Get appropriate test parameters for the given provider and model."""

    # Anthropic Bedrock / Vertex variants do not allow configuring temperature and top_p together.
    if model_id in {
        "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "claude-haiku-4-5@20251001",
    }:
        params = ALL_PARAMS.copy()
        params.pop("top_p", None)
        return params

    return ALL_PARAMS


@pytest.mark.parametrize("provider,model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_params(
    provider: llm.Provider,
    model_id: llm.ModelId,
    snapshot: Snapshot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test synchronous call with all parameters to verify param handling and logging."""

    params = get_test_params(model_id)

    @llm.call(provider=provider, model_id=model_id, **params)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    with snapshot_test(snapshot, caplog) as snap:
        response = add_numbers(4200, 42)
        snap["response"] = (response_snapshot_dict(response),)
