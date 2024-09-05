"""usage docs: learn/calls.md#provider-specific-parameters"""

from __future__ import annotations

from google.cloud.aiplatform_v1beta1.types import GenerationConfig
from typing_extensions import NotRequired
from vertexai.generative_models import SafetySetting, ToolConfig

from ..base import BaseCallParams


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
