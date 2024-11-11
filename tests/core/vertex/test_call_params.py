from mirascope.core.base.call_params import CommonCallParams
from mirascope.core.vertex.call_params import (
    get_vertex_call_params_from_common,
)


def test_vertex_conversion_full():
    """Test Vertex parameter conversion with all parameters."""
    params: CommonCallParams = {
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 0.9,
        "stop": ["STOP", "END"],
    }
    result = get_vertex_call_params_from_common(**params)
    assert result == {
        "generation_config": {
            "temperature": 0.7,
            "max_output_tokens": 100,
            "top_p": 0.9,
            "stop_sequences": ["STOP", "END"],
        }
    }


def test_vertex_conversion_empty():
    """Test Vertex parameter conversion with empty parameters."""
    empty_params: CommonCallParams = {}
    result = get_vertex_call_params_from_common(**empty_params)
    assert dict(result) == {}
