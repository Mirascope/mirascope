from mirascope.core.anthropic.call_params import (
    get_anthropic_call_params_from_common,
)
from mirascope.core.base.call_params import CommonCallParams


def test_anthropic_conversion_single_stop():
    """Test Anthropic parameter conversion with single stop sequence."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": "STOP",
    }
    result = get_anthropic_call_params_from_common(**params)
    expected = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop_sequences": ["STOP"],
    }
    for key, value in expected.items():
        assert result.get(key) == value


def test_anthropic_conversion_multiple_stops():
    """Test Anthropic parameter conversion with multiple stop sequences."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
    }
    result = get_anthropic_call_params_from_common(**params)
    expected = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop_sequences": ["STOP", "END"],
    }
    for key, value in expected.items():
        assert result.get(key) == value


def test_anthropic_conversion_empty():
    """Test Anthropic parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_anthropic_call_params_from_common(**empty_params)
    assert dict(result) == {}


def test_anthropic_conversion_partial():
    """Test Anthropic parameter conversion with partial parameters."""
    partial_params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
    }
    result = get_anthropic_call_params_from_common(**partial_params)
    expected = {
        "temperature": 0.7,
        "max_tokens": 100,
    }
    for key, value in expected.items():
        assert result.get(key) == value
