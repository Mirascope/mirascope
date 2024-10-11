"""This module defines the function return type for functions as LLM calls."""

from ..base import BaseDynamicConfig, BaseMessageParam
from ._types import InternalBedrockMessageParam
from .call_params import BedrockCallParams

BedrockDynamicConfig = BaseDynamicConfig[
    InternalBedrockMessageParam | BaseMessageParam, BedrockCallParams
]
"""The function return type for functions wrapped with the `bedrock_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.bedrock import BedrockDynamicConfig, bedrock_call


@bedrock_call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> BedrockDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
