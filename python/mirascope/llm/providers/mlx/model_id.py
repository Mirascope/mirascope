from typing import TypeAlias

# TODO: Add more explicit literals
# TODO: Ensure automatic model downloads are supported.
# TODO: Ensure instructions are clear for examples that run as copied
MLXModelId: TypeAlias = str
"""The identifier of the MLX model to be loaded by the MLX client.

An MLX model identifier might be a local path to a model's file, or a huggingface
repository such as:
 - "mlx-community/Qwen3-8B-4bit-DWQ-053125"
 - "mlx-community/gpt-oss-20b-MXFP4-Q8"

For more details, see:
 - https://github.com/ml-explore/mlx-lm/?tab=readme-ov-file#supported-models
 - https://huggingface.co/mlx-community
"""


def model_name(model_id: MLXModelId) -> str:
    """Extract the mlx model name from the ModelId

    Args:
        model_id: Full model ID (e.g. "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125")

    Returns:
        Provider-specific model ID (e.g. "mlx-community/Qwen3-0.6B-4bit-DWQ-053125")
    """
    return model_id.removeprefix("mlx/")
