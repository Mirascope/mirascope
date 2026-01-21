"""Azure model identifiers."""

from typing import TypeAlias

AzureModelId: TypeAlias = str
"""Model IDs for Azure OpenAI (e.g. "azure/openai/<deployment_name>")."""


def model_name(model_id: AzureModelId) -> str:
    """Extract the Azure deployment name from a full model ID.

    Args:
        model_id: Full model ID (e.g. "azure/openai/gpt-5-mini")

    Returns:
        Azure deployment name (e.g. "gpt-5-mini")
    """
    return model_id.removeprefix("azure/openai/")
