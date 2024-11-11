from mirascope.core.azure.call_params import (
    get_azure_call_params_from_common,
)
from mirascope.core.base.call_params import CommonCallParams


def test_azure_conversion_full():
    """Test Azure parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop": ["STOP", "END"],
    }
    result = get_azure_call_params_from_common(params)
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


def test_azure_conversion_empty():
    """Test Azure parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_azure_call_params_from_common(empty_params)
    assert dict(result) == {}
