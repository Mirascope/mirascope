"""This module defines the function return type for functions as LLM calls."""

from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseFunctionReturn
from .call_params import OpenAICallParams

OpenAICallFunctionReturn = BaseFunctionReturn[
    ChatCompletionMessageParam, OpenAICallParams
]
'''The function return type for functions wrapped with the `openai_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the OpenAI API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the OpenAI API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.openai import OpenAICallFunctionReturn, openai_call

@openai_call(model="gpt-4o")
def recommend_book(genre: str) -> OpenAICallFunctionReturn:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''
