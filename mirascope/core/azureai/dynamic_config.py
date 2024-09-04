"""This module defines the function return type for functions as LLM calls.

usage docs: learn/dynamic_configuration.md#dynamic-configuration-options
"""

from azure.ai.inference.models import (
    ChatRequestMessage,
)

from ..base import BaseDynamicConfig
from .call_params import AzureAICallParams

AzureAIDynamicConfig = BaseDynamicConfig[ChatRequestMessage, AzureAICallParams]
"""The function return type for functions wrapped with the `azureai_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.azureai import AzureAIDynamicConfig, azureai_call


@azureai_call("gpt-4o-mini")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> AzureAIDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
