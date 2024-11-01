"""This module defines the function return type for functions as LLM calls."""

from google.generativeai import GenerativeModel
from google.generativeai.types import ContentsType

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import GeminiCallParams

GeminiDynamicConfig = BaseDynamicConfig[
    ContentsType | BaseMessageParam, GeminiCallParams, GenerativeModel
]
"""The function return type for functions wrapped with the `gemini_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.gemini import GeminiDynamicConfig, gemini_call


@gemini_call("gemini-1.5-flash")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> GeminiDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
