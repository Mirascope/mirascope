from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.bedrock._utils._convert_common_call_params import (
    convert_common_call_params,
)


def test_bedrock_conversion_full():
    """Test full parameter conversion for Bedrock."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
    }
    result = convert_common_call_params(params)
    assert result == {
        "inferenceConfig": {
            "temperature": 0.7,
            "maxTokens": 100,
            "topP": 0.9,
            "stopSequences": ["STOP", "END"],
        }
    }


def test_bedrock_conversion_single_stop():
    """Test single stop sequence conversion for Bedrock."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "stop": "STOP",
    }
    result = convert_common_call_params(params)
    assert result == {
        "inferenceConfig": {
            "temperature": 0.7,
            "stopSequences": ["STOP"],
        }
    }


def test_bedrock_conversion_empty():
    """Test empty parameters conversion for Bedrock."""
    result = convert_common_call_params({})
    assert result == {}


def test_bedrock_conversion_full_with_invalid_key():
    """Test full parameter conversion for Bedrock."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
        "invalid": "invalid",  # pyright: ignore [reportAssignmentType]
    }
    result = convert_common_call_params(params)
    assert result == {
        "inferenceConfig": {
            "temperature": 0.7,
            "maxTokens": 100,
            "topP": 0.9,
            "stopSequences": ["STOP", "END"],
        }
    }
