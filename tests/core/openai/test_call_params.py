from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.openai.call_params import get_openai_call_params_from_common


def test_openai_conversion_full():
    """Test OpenAI parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop": ["STOP", "END"],
    }
    result = get_openai_call_params_from_common(**params)
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


def test_openai_conversion_empty():
    """Test OpenAI parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_openai_call_params_from_common(**empty_params)
    assert dict(result) == {}


def test_openai_conversion_partial():
    """Test OpenAI parameter conversion with partial parameters."""
    partial_params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
    }
    result = get_openai_call_params_from_common(**partial_params)
    expected = {
        "temperature": 0.7,
        "max_tokens": 100,
    }
    for key, value in expected.items():
        assert result.get(key) == value
