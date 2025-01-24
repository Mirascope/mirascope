from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.google._utils._convert_common_call_params import (
    convert_common_call_params,
)


def test_google_conversion_full():
    """Test full parameter conversion for Google."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
    }
    result = convert_common_call_params(params)
    assert result == {
        "generation_config": {
            "temperature": 0.7,
            "max_output_tokens": 100,
            "top_p": 0.9,
            "stop_sequences": ["STOP", "END"],
        }
    }


def test_google_conversion_single_stop():
    """Test single stop sequence conversion for Google."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "stop": "STOP",
    }
    result = convert_common_call_params(params)
    assert result == {
        "generation_config": {
            "temperature": 0.7,
            "stop_sequences": ["STOP"],
        }
    }


def test_google_conversion_empty():
    """Test empty parameters conversion for Google."""
    result = convert_common_call_params({})
    assert result == {}


def test_google_conversion_full_with_invalid_key():
    """Test full parameter conversion for Google."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
        "invalid": "invalid",  # pyright: ignore [reportAssignmentType]
    }
    result = convert_common_call_params(params)
    assert result == {
        "generation_config": {
            "temperature": 0.7,
            "max_output_tokens": 100,
            "top_p": 0.9,
            "stop_sequences": ["STOP", "END"],
        }
    }
