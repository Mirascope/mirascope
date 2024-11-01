"""This module defines the function return type for functions as LLM calls."""

from groq import AsyncGroq, Groq
from groq.types.chat import ChatCompletionMessageParam

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import GroqCallParams

AsyncGroqDynamicConfig = BaseDynamicConfig[
    ChatCompletionMessageParam | BaseMessageParam, GroqCallParams, AsyncGroq
]
GroqDynamicConfig = BaseDynamicConfig[
    ChatCompletionMessageParam | BaseMessageParam, GroqCallParams, Groq
]
"""The function return type for functions wrapped with the `groq_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.groq import GroqDynamicConfig, groq_call


@groq_call("llama-3.1-8b-instant")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> GroqDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
