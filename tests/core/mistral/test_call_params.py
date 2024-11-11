from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.mistral.call_params import get_mistral_call_params_from_common


def test_mistral_conversion_full():
    """Test Mistral parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
        "seed": 42,
    }
    result = get_mistral_call_params_from_common(params)
    expected = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
        "random_seed": 42,
    }
    for key, value in expected.items():
        assert result.get(key) == value


def test_mistral_conversion_empty():
    """Test Mistral parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_mistral_call_params_from_common(empty_params)
    assert dict(result) == {}


def test_mistral_conversion_partial():
    """Test Mistral parameter conversion with partial parameters."""
    partial_params: CommonCallParams = {
        "temperature": 0.7,
        "seed": 42,
    }
    result = get_mistral_call_params_from_common(partial_params)
    expected = {
        "temperature": 0.7,
        "random_seed": 42,
    }
    for key, value in expected.items():
        assert result.get(key) == value
