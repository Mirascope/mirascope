"""This module defines the function return type for functions as LLM calls.

usage docs: learn/dynamic_configuration.md#dynamic-configuration-options
"""

from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseDynamicConfig
from .call_params import OpenAICallParams

OpenAIDynamicConfig = BaseDynamicConfig[ChatCompletionMessageParam, OpenAICallParams]
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
