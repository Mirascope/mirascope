from typing import ClassVar

from pydantic import BaseModel

from mirascope.base.types import BaseChunkerParams


class BaseChunker(BaseModel):
    chunker_params: ClassVar[BaseChunkerParams] = BaseChunkerParams()
