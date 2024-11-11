"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from typing_extensions import NotRequired
from vertexai.generative_models import GenerationConfig, SafetySetting, ToolConfig

from ..base import BaseCallParams
from ..base.call_params import CommonCallParams, convert_params, convert_stop_to_list


class VertexCallParams(BaseCallParams):
    """The parameters to use when calling the Vertex API.

    [Vertex API Reference](https://cloud.google.com/python/docs/reference/aiplatform/latest)

    Attributes:
        generation_config: ...
        safety_settings: ...
        tool_config: ...
    """

    generation_config: NotRequired[GenerationConfig]
    safety_settings: NotRequired[SafetySetting]
    tool_config: NotRequired[ToolConfig]


def get_vertex_call_params_from_common(params: CommonCallParams) -> VertexCallParams:
    """Converts common call parameters to Vertex AI-specific call parameters."""
    mapping = {
        "temperature": "temperature",
        "max_tokens": "max_output_tokens",
        "top_p": "top_p",
        "stop": "stop_sequences",
    }
    transforms = [
        ("stop", convert_stop_to_list),
    ]
    return convert_params(
        params, mapping, VertexCallParams, transforms=transforms, wrap_in_config=True
    )
