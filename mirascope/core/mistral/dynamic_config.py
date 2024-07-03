"""This module defines the function return type for functions as LLM calls."""

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import MistralCallParams

MistralDynamicConfig = BaseDynamicConfig[BaseMessageParam, MistralCallParams]
'''The function return type for functions wrapped with the `mistral_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the Mistral API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the Mistral API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.mistral import MistralDynamicConfig, mistral_call

@mistral_call(model="gpt-4o")
def recommend_book(genre: str) -> MistralDynamicConfig:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''
