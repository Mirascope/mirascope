"""A base abstract interface for extracting structured information using LLMs."""
from abc import ABC, abstractmethod
from typing import Callable, ClassVar, Generic, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from .prompts import BasePrompt
from .tools import BaseType
from .types import BaseCallParams

ExtractionTypeT = TypeVar("ExtractionTypeT", bound=Union[BaseType, BaseModel, Callable])


class BaseExtractor(BasePrompt, Generic[ExtractionTypeT], ABC):
    """The base abstract interface for extracting structured information using LLMs."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None

    extract_schema: ClassVar[Type[ExtractionTypeT]]  # type: ignore
    call_params: ClassVar[BaseCallParams]

    @abstractmethod
    def extract(self, retries: int = 0) -> ExtractionTypeT:
        """Extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover

    @abstractmethod
    async def extract_async(self, retries: int = 0) -> ExtractionTypeT:
        """Asynchronously extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover
