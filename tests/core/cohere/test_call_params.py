from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.cohere.call_params import get_cohere_call_params_from_common


def test_cohere_conversion_full():
    """Test Cohere parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop": ["STOP", "END"],
    }
    result = get_cohere_call_params_from_common(params)
    expected = {
        "temperature": 0.7,
        "max_tokens": 100,
        "p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop_sequences": ["STOP", "END"],
    }
    for key, value in expected.items():
        assert result.get(key) == value


def test_cohere_conversion_empty():
    """Test Cohere parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_cohere_call_params_from_common(empty_params)
    assert dict(result) == {}
