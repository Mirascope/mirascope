from typing import cast

from vertexai.generative_models import GenerationConfig

from ...base.call_params import CommonCallParams
from ..call_params import VertexCallParams

VERTEX_PARAM_MAPPING = {
    "temperature": "temperature",
    "max_tokens": "max_output_tokens",
    "top_p": "top_p",
    "stop": "stop_sequences",
}


def convert_common_call_params(common_params: CommonCallParams) -> VertexCallParams:
    """Convert CommonCallParams to Vertex parameters."""
    generation_config = {}

    for key, value in common_params.items():
        if key not in VERTEX_PARAM_MAPPING or value is None:
            continue

        if key == "stop":
            generation_config["stop_sequences"] = (
                [value] if isinstance(value, str) else value
            )
        else:
            generation_config[VERTEX_PARAM_MAPPING[key]] = value

    if not generation_config:
        return cast(VertexCallParams, {})

    return cast(
        VertexCallParams,
        {"generation_config": cast(GenerationConfig, generation_config)},
    )
