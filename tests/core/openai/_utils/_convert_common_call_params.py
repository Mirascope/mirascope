from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.openai._utils._convert_common_call_params import (
    convert_common_call_params,
)


def test_openai_conversion_full():
    """Test full parameter conversion for OpenAI."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop": ["STOP", "END"],
    }
    result = convert_common_call_params(params)
    assert result == {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "seed": 42,
        "stop": ["STOP", "END"],
    }


def test_openai_conversion_empty():
    """Test empty parameters conversion for OpenAI."""
    result = convert_common_call_params({})
    assert result == {}
