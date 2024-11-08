"""This module defines the function return type for functions as LLM calls."""

from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient as AsyncBedrockRuntimeClient,
)

from ..base import BaseDynamicConfig, BaseMessageParam
from ._types import InternalBedrockMessageParam
from .call_params import BedrockCallParams

AsyncBedrockDynamicConfig = BaseDynamicConfig[
    InternalBedrockMessageParam | BaseMessageParam,
    BedrockCallParams,
    AsyncBedrockRuntimeClient,
]
BedrockDynamicConfig = BaseDynamicConfig[
    InternalBedrockMessageParam | BaseMessageParam,
    BedrockCallParams,
    BedrockRuntimeClient,
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
