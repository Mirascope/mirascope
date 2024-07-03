"""This module defines the function return type for functions as LLM calls."""

from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseDynamicConfig
from .call_params import LiteLLMCallParams

LiteLLMDynamicConfig = BaseDynamicConfig[ChatCompletionMessageParam, LiteLLMCallParams]
'''The function return type for functions wrapped with the `litellm_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the LiteLLM API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the LiteLLM API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.litellm import LiteLLMDynamicConfig, litellm_call

@litellm_call(model="gpt-4o")
def recommend_book(genre: str) -> LiteLLMDynamicConfig:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''
