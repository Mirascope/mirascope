"""CloudGPU provider implementation."""

from __future__ import annotations

from typing import ClassVar

from ..openai.completions._utils import CompletionsModelFeatureInfo
from ..openai.completions.base_provider import BaseOpenAICompletionsProvider


class CloudGPUProvider(BaseOpenAICompletionsProvider):
    """Provider for CloudGPU's OpenAI-compatible API.

    Inherits from BaseOpenAICompletionsProvider with CloudGPU-specific configuration:
    - Uses CloudGPU's API endpoint
    - Requires CLOUDGPU_API_KEY

    CloudGPU model IDs are unprefixed (e.g. "deepseek-v4-flash", "glm-5.3").
    The full list is returned by GET https://cloudgpu.app/v1/models.

    Usage:
        Use the "cloudgpu/" prefix for CloudGPU models:

        ```python
        from mirascope import llm

        llm.register_provider("cloudgpu", scope="cloudgpu/")

        @llm.call("cloudgpu/deepseek-v4-flash")
        def my_prompt():
            return [llm.messages.user("Hello!")]
        ```
    """

    id: ClassVar[str] = "cloudgpu"
    default_scope: ClassVar[str | list[str]] = []
    default_base_url: ClassVar[str | None] = "https://cloudgpu.app/v1"
    api_key_env_var: ClassVar[str] = "CLOUDGPU_API_KEY"
    api_key_required: ClassVar[bool] = True
    provider_name: ClassVar[str | None] = "CloudGPU"

    def _model_name(self, model_id: str) -> str:
        """Strip 'cloudgpu/' prefix from model ID for the CloudGPU API."""
        return model_id.removeprefix("cloudgpu/")

    def _model_feature_info(self, model_id: str) -> CompletionsModelFeatureInfo:
        """Return empty feature info.

        CloudGPU model IDs (e.g. "deepseek-v4-flash") are not OpenAI API models,
        so OpenAI's per-model feature table does not apply to them.
        """
        return CompletionsModelFeatureInfo()
