from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.mistral._utils._convert_common_call_params import (
    convert_common_call_params,
)


def test_mistral_conversion_full():
    """Test full parameter conversion for Mistral."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "seed": 42,
        "stop": ["STOP", "END"],
    }
    result = convert_common_call_params(params)
    assert result == {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "random_seed": 42,
        "stop": ["STOP", "END"],
    }


def test_mistral_conversion_empty():
    """Test empty parameters conversion for Mistral."""
    result = convert_common_call_params({})
    assert result == {}
