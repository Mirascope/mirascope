"""A base abstract interface for extracting structured information using LLMs."""
from abc import ABC, abstractmethod
from typing import Callable, ClassVar, Generic, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from .calls import BaseCall
from .prompts import BasePrompt
from .types import BaseType

_T = TypeVar("_T", bound=Union[BaseType, BaseModel, Callable])


class BaseExtractor(BasePrompt, Generic[_T], ABC):
    """The base abstract interface for extracting structured information using LLMs."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None

    class ExtractParams(BaseCall.CallParams):
        """The parameters used for extract when calling the LLM."""

    extract_params: ClassVar[ExtractParams]
    extract_schema: ClassVar[Type[_T]]  # type: ignore

    @abstractmethod
    def extract(self, retries: int = 0) -> _T:
        """Extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover

    @abstractmethod
    async def extract_async(self, retries: int = 0) -> _T:
        """Asynchronously extracts the `extraction_schema` from an LLM call."""
        ...  # pragma: no cover
