"""This module defines the function return type for functions as LLM calls."""

from vertexai.generative_models import (
    Content,
    GenerativeModel,
)

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import VertexCallParams

VertexDynamicConfig = BaseDynamicConfig[
    Content | BaseMessageParam, VertexCallParams, GenerativeModel
]
"""The function return type for functions wrapped with the `vertex_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.vertex import VertexDynamicConfig, vertex_call


@vertex_call("gemini-1.5-flash")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> VertexDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
