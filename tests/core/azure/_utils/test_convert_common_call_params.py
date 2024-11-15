from mirascope.core.azure._utils._convert_common_call_params import (
    convert_common_call_params,
)
from mirascope.core.base.call_params import CommonCallParams


def test_azure_conversion_full():
    """Test full parameter conversion for Azure."""
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


def test_azure_conversion_single_stop():
    """Test single stop sequence conversion for Azure."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "stop": "STOP",
    }
    result = convert_common_call_params(params)
    assert result == {
        "temperature": 0.7,
        "stop": ["STOP"],
    }


def test_azure_conversion_empty():
    """Test empty parameters conversion for Azure."""
    result = convert_common_call_params({})
    assert result == {}
