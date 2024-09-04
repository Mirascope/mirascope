"""This module defines the function return type for functions as LLM calls.

usage docs: learn/dynamic_configuration.md#dynamic-configuration-options
"""

from vertexai.generative_models import Content

from ..base import BaseDynamicConfig
from .call_params import VertexCallParams

VertexDynamicConfig = BaseDynamicConfig[Content, VertexCallParams]
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
