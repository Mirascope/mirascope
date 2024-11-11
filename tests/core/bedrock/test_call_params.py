from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.bedrock.call_params import (
    get_bedrock_call_params_from_common,
)


def test_bedrock_conversion_full():
    """Test Bedrock parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
    }
    result = get_bedrock_call_params_from_common(params)
    assert result == {
        "inferenceConfig": {
            "temperature": 0.7,
            "maxTokens": 100,
            "topP": 0.9,
            "stopSequences": ["STOP", "END"],
        }
    }


def test_bedrock_conversion_single_stop():
    """Test Bedrock parameter conversion with single stop sequence."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "stop": "STOP",
    }
    result = get_bedrock_call_params_from_common(params)
    assert result == {
        "inferenceConfig": {
            "temperature": 0.7,
            "stopSequences": ["STOP"],
        }
    }


def test_bedrock_conversion_empty():
    """Test Bedrock parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_bedrock_call_params_from_common(empty_params)
    assert dict(result) == {}
