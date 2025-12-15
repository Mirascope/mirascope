"""Together AI model ids and related utilities."""

from typing import TypeAlias

TogetherModelId: TypeAlias = str
"""Valid Together model IDs.

Together models are referenced via the Mirascope prefix:
  - "together/<provider-model-name>"

Examples:
  - "together/meta-llama/Llama-3.3-70B-Instruct-Turbo"
  - "together/Qwen/Qwen2.5-72B-Instruct-Turbo"
"""


def model_name(model_id: TogetherModelId) -> str:
    """Extract the Together model name from a full model ID.

    Args:
        model_id: Full model ID (e.g. "together/meta-llama/Llama-3.3-70B-Instruct-Turbo")

    Returns:
        Provider-specific model name (e.g. "meta-llama/Llama-3.3-70B-Instruct-Turbo")
    """
    return model_id.removeprefix("together/")
