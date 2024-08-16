"""This module defines the function return type for functions as LLM calls.

usage docs: learn/dynamic_configuration.md#dynamic-configuration-options
"""

from anthropic.types import MessageParam

from ..base import BaseDynamicConfig
from .call_params import AnthropicCallParams

AnthropicDynamicConfig = BaseDynamicConfig[MessageParam, AnthropicCallParams]
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
