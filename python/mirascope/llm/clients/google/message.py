"""Google message types."""

from typing import TypeAlias

from google.genai.types import ContentDict, FunctionResponse

GoogleMessage: TypeAlias = ContentDict | FunctionResponse
