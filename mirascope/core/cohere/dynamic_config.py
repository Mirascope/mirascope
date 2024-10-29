"""This module defines the function return type for functions as LLM calls."""

from cohere import (
    AsyncClient,
    Client,
)
from cohere.types.chat_message import ChatMessage

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import CohereCallParams

AsyncCohereDynamicConfig = BaseDynamicConfig[
    ChatMessage | BaseMessageParam, CohereCallParams, AsyncClient
]
CohereDynamicConfig = BaseDynamicConfig[
    ChatMessage | BaseMessageParam, CohereCallParams, Client
]
"""The function return type for functions wrapped with the `cohere_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.cohere import CohereDynamicConfig, cohere_call


@cohere_call("command-r-plus")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> CohereDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
