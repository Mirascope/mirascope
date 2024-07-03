"""This module defines the function return type for functions as LLM calls."""

from groq.types.chat import ChatCompletionMessageParam

from ..base import BaseDynamicConfig
from .call_params import GroqCallParams

GroqDynamicConfig = BaseDynamicConfig[ChatCompletionMessageParam, GroqCallParams]
'''The function return type for functions wrapped with the `groq_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the Groq API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the Groq API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.groq import GroqDynamicConfig, groq_call

@groq_call(model="gpt-4o")
def recommend_book(genre: str) -> GroqDynamicConfig:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''
