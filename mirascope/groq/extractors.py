"""A module for extracting structured information using Groq's Cloud API."""

import logging
from typing import Any, ClassVar, Generic, TypeVar, Union

from tenacity import AsyncRetrying, Retrying

from ..base import BaseExtractor, ExtractedType
from .calls import GroqCall
from .tools import GroqTool
from .types import GroqCallParams

logger = logging.getLogger("mirascope")

T = TypeVar("T", bound=ExtractedType)


class GroqExtractor(BaseExtractor[GroqCall, GroqTool, Any, T], Generic[T]):
    '''A class for extracting structured information using Groq Cloud API.

    Example:

    ```python
    from mirascope.groq import GroqExtractor
    from pydantic import BaseModel
    from typing import Literal, Type

    class TaskDetails(BaseModel):
        title: str
        priority: Literal["low", "normal", "high"]
        due_date: str

    class TaskExtractor(GroqExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        call_params = GroqCallParams(model="mixtral-8x7b-32768")

        prompt_template = """
        Prepare the budget report by next Monday. It's a high priority task.
        """


    task = TaskExtractor().extract(retries=3)
    assert isinstance(task, TaskDetails)
    print(task)
    # > title='Prepare the budget report' priority='high' due_date='next Monday'
    ```
    '''

    call_params: ClassVar[GroqCallParams] = GroqCallParams()
    _provider: ClassVar[str] = "groq"

    def extract(self, retries: Union[int, Retrying] = 0, **kwargs: Any) -> T:
        """Extracts `extract_schema` from the Groq call response.

        The `extract_schema` is converted into an `GroqTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Groq's tool/function calling functionality to extract
        information from a prompt according to the context provided by the `BaseModel`
        schema.

        Args:
            retries: The maximum number of times to retry the query on validation error.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
        """
        return self._extract(GroqCall, GroqTool, retries, **kwargs)

    async def extract_async(
        self, retries: Union[int, AsyncRetrying] = 0, **kwargs: Any
    ) -> T:
        """Asynchronously extracts `extract_schema` from the Groq call response.

        The `extract_schema` is converted into an `GroqTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Groq's tool/function calling functionality to extract
        information from a prompt according to the context provided by the `BaseModel`
        schema.

        Args:
            retries: The maximum number of times to retry the query on validation error.
            **kwargs: Additional keyword arguments parameters to pass to the call. These
                will override any existing arguments in `call_params`.

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
        """
        return await self._extract_async(GroqCall, GroqTool, retries, **kwargs)
