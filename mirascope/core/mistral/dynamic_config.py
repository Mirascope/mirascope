"""This module defines the function return type for functions as LLM calls."""

from mistralai import Mistral
from mistralai.models import (
    AssistantMessage,
    SystemMessage,
    ToolMessage,
    UserMessage,
)

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import MistralCallParams

MistralDynamicConfig = BaseDynamicConfig[
    AssistantMessage | SystemMessage | ToolMessage | UserMessage | BaseMessageParam,
    MistralCallParams,
    Mistral,
]
"""The function return type for functions wrapped with the `mistral_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.mistral import MistralDynamicConfig, mistral_call


@mistral_call("mistral-large-latest")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> MistralDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
