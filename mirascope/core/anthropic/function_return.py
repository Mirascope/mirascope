"""This module defines the function return type for functions as LLM calls."""

from anthropic.types import MessageParam

from ..base import BaseDynamicConfig
from .call_params import AnthropicCallParams

AnthropicDynamicConfig = BaseDynamicConfig[MessageParam, AnthropicCallParams]
'''The function return type for functions wrapped with the `anthropic_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the Anthropic API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the Anthropic API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core import anthropic

@anthropic.call(model="gpt-4o")
def recommend_book(genre: str) -> anthropic.AnthropicDynamicConfig:
    """Recommend a {capitalized_genre} book."""
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''
