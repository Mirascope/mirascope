"""This module defines the function return type for functions as LLM calls."""

from google.generativeai.types import ContentsType  # type: ignore

from ..base import BaseFunctionReturn
from .call_params import GeminiCallParams

GeminiCallFunctionReturn = BaseFunctionReturn[ContentsType, GeminiCallParams]
'''The function return type for functions wrapped with the `gemini_call` decorator.

Attributes:
    computed_fields: The computed fields to use in the prompt template.
    messages: The messages to send to the Gemini API. If provided, `computed_fields`
        will be ignored.
    call_params: The call parameters to use when calling the Gemini API. These will
        override any call parameters provided to the decorator.

Example:

```python
from mirascope.core.gemini import GeminiCallFunctionReturn, gemini_call

@gemini_call(model="gemini-pro")
def recommend_book(genre: str) -> GeminiCallFunctionReturn:
    """Recommend a {capitalized_genre} book."""
    reeturn {"computed_fields": {"capitalized_genre": genre.capitalize()}}
```
'''
