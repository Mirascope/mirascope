from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.litellm.call_params import get_litellm_call_params_from_common


def test_litellm_conversion_full():
    """Test LiteLLM parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop": ["STOP", "END"],
    }
    result = get_litellm_call_params_from_common(params)
    expected = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop": ["STOP", "END"],
    }
    for key, value in expected.items():
        assert result.get(key) == value


def test_litellm_conversion_empty():
    """Test LiteLLM parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_litellm_call_params_from_common(empty_params)
    assert dict(result) == {}
