from typing import Any

from typing_extensions import NotRequired

from mirascope.core.base.call_params import (
    BaseCallParams,
    CommonCallParams,
    convert_params,
    convert_stop_to_list,
)


def test_convert_stop_to_list_string():
    """Test converting string to stop sequence list."""
    assert convert_stop_to_list("STOP") == ["STOP"]


def test_convert_stop_to_list_list():
    """Test converting list to stop sequence list."""
    stop_list = ["STOP", "END"]
    assert convert_stop_to_list(stop_list) == stop_list


def test_convert_stop_to_list_empty():
    """Test converting empty list."""
    empty_list: list[str] = []
    assert convert_stop_to_list(empty_list) == empty_list


class TestCallParams(BaseCallParams, total=False):
    """Test type for call params conversion."""

    temp: NotRequired[float]
    max_output: NotRequired[int]
    flag: NotRequired[bool]
    generation_config: NotRequired[dict[str, Any]]


def assert_call_params_equal(actual: TestCallParams, expected: TestCallParams) -> None:
    """Helper function to safely compare TestCallParams."""
    for key in expected:
        assert actual.get(key) == expected.get(key)
    for key in actual:
        assert actual.get(key) == expected.get(key)


def test_convert_params_basic():
    """Test basic parameter conversion."""
    common_params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
    }
    mapping = {
        "temperature": "temp",
        "max_tokens": "max_output",
    }
    result = convert_params(common_params, mapping, TestCallParams)
    assert_call_params_equal(result, TestCallParams(temp=0.7, max_output=100))


def test_convert_params_empty():
    """Test conversion with empty parameters."""
    common_params: CommonCallParams = {}
    mapping = {
        "temperature": "temp",
        "max_tokens": "max_output",
    }
    result = convert_params(common_params, mapping, TestCallParams)
    assert_call_params_equal(result, TestCallParams())


def test_convert_params_with_transforms():
    """Test conversion with transformations."""
    common_params: CommonCallParams = {
        "stop": "STOP",
    }
    mapping = {"stop": "flag"}
    transforms = [("stop", lambda x: True)]
    result = convert_params(common_params, mapping, TestCallParams, transforms)
    assert_call_params_equal(result, TestCallParams(flag=True))


def test_convert_params_wrap_in_config():
    """Test wrapping results in generation_config."""
    common_params: CommonCallParams = {
        "temperature": 0.7,
    }
    mapping = {"temperature": "temp"}
    result = convert_params(
        common_params,
        mapping,
        TestCallParams,
        wrap_in_config=True,
    )
    assert_call_params_equal(
        result,
        TestCallParams(generation_config={"temp": 0.7}),
    )


def test_convert_params_wrap_in_config_empty():
    """Test wrapping empty results in generation_config."""
    common_params: CommonCallParams = {}
    mapping = {"temperature": "temp"}
    result = convert_params(
        common_params,
        mapping,
        TestCallParams,
        wrap_in_config=True,
    )
    assert_call_params_equal(result, TestCallParams())
