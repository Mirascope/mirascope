"""Google message types."""

from typing import TypeAlias

from google.genai.types import ContentDict, FunctionResponse

from ...messages import Message

GoogleMessage: TypeAlias = Message | ContentDict | FunctionResponse
