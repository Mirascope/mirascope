"""This module defines the function return type for functions as LLM calls."""

from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    AsyncAnthropic,
    AsyncAnthropicBedrock,
    AsyncAnthropicVertex,
)
from anthropic.types import MessageParam

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import AnthropicCallParams

AnthropicDynamicConfig = BaseDynamicConfig[
    MessageParam | BaseMessageParam,
    AnthropicCallParams,
    Anthropic | AnthropicBedrock | AnthropicVertex,
]
AsyncAnthropicDynamicConfig = BaseDynamicConfig[
    MessageParam | BaseMessageParam,
    AnthropicCallParams,
    AsyncAnthropic | AsyncAnthropicBedrock | AsyncAnthropicVertex,
]
"""The function return type for functions wrapped with the `anthropic_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.anthropic import AnthropicDynamicConfig, anthropic_call


@anthropic_call("claude-3-5-sonnet-20240620")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> AnthropicDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
