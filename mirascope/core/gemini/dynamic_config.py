"""This module defines the function return type for functions as LLM calls.

usage docs: learn/dynamic_configuration.md#dynamic-configuration-options
"""

from google.generativeai.types import ContentsType  # type: ignore

from ..base import BaseDynamicConfig
from .call_params import GeminiCallParams

GeminiDynamicConfig = BaseDynamicConfig[ContentsType, GeminiCallParams]
"""The function return type for functions wrapped with the `gemini_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.gemini import GeminiDynamicConfig, gemini_call


@gemini_call("gemini-flash-1.5")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> GeminiDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
