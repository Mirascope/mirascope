from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.gemini.call_params import (
    get_gemini_call_params_from_common,
)


def test_gemini_conversion_full():
    """Test Gemini parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
    }
    result = get_gemini_call_params_from_common(**params)
    assert result == {
        "generation_config": {
            "temperature": 0.7,
            "max_output_tokens": 100,
            "top_p": 0.9,
            "stop_sequences": ["STOP", "END"],
        }
    }


def test_gemini_conversion_single_stop():
    """Test Gemini parameter conversion with single stop sequence."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "stop": "STOP",
    }
    result = get_gemini_call_params_from_common(**params)
    assert result == {
        "generation_config": {
            "temperature": 0.7,
            "stop_sequences": ["STOP"],
        }
    }


def test_gemini_conversion_empty():
    """Test Gemini parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_gemini_call_params_from_common(*empty_params)
    assert dict(result) == {}
