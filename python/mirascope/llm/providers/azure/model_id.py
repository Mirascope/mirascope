"""Azure model ids, and related utilities."""

from typing import TypeAlias

AzureModelId: TypeAlias = str
"""Valid Azure model IDs.

Azure models use the format 'azure/<model-name>', e.g., 'azure/gpt-4o'.
The model name is passed directly to the Azure OpenAI API after stripping the prefix.
"""
