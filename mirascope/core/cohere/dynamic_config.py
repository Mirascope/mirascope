"""This module defines the function return type for functions as LLM calls."""

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import CohereCallParams

CohereDynamicConfig = BaseDynamicConfig[BaseMessageParam, CohereCallParams]
'''The function return type for functions wrapped with the `cohere_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the Cohere API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the Cohere API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.cohere import CohereDynamicConfig, cohere_call

@cohere_call(model="gpt-4o")
def recommend_book(genre: str) -> CohereDynamicConfig:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''
