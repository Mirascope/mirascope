"""This module defines the function return type for functions as LLM calls."""

from google.genai import Client
from google.genai.types import ContentListUnion, ContentListUnionDict

from ..base import BaseDynamicConfig, BaseMessageParam
from .call_params import GoogleCallParams

GoogleDynamicConfig = BaseDynamicConfig[
    ContentListUnion | ContentListUnionDict | BaseMessageParam, GoogleCallParams, Client
]
"""The function return type for functions wrapped with the `google_call` decorator.

Example:

```python
from mirascope.core import prompt_template
from mirascope.core.google import GoogleDynamicConfig, google_call


@google_call("google-1.5-flash")
@prompt_template("Recommend a {capitalized_genre} book")
def recommend_book(genre: str) -> GoogleDynamicConfig:
    return {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
"""
