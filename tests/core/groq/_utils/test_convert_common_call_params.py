from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.groq._utils._convert_common_call_params import (
    convert_common_call_params,
)


def test_groq_conversion_full():
    """Test full parameter conversion for Groq."""
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


def test_groq_conversion_empty():
    """Test empty parameters conversion for Groq."""
    result = convert_common_call_params({})
    assert result == {}


def test_groq_conversion_none_values():
    """Test None values conversion for Groq."""
    params: CommonCallParams = {
        "temperature": None,
        "max_tokens": None,
    }
    result = convert_common_call_params(params)
    assert result == {}
