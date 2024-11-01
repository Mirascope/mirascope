"""This module defines the function return type for functions as LLM calls."""

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import OpenAICallParams

AsyncOpenAIDynamicConfig = BaseDynamicConfig[
    ChatCompletionMessageParam | BaseMessageParam,
    OpenAICallParams,
    AsyncOpenAI | AsyncAzureOpenAI,
]

OpenAIDynamicConfig = BaseDynamicConfig[
    ChatCompletionMessageParam | BaseMessageParam,
    OpenAICallParams,
    OpenAI | AzureOpenAI,
]
"""The function return type for functions wrapped with the `openai_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.openai import OpenAIDynamicConfig, openai_call


@openai_call("gpt-4o-mini")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> OpenAIDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
