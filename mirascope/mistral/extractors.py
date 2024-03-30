"""A class for extracting structured information using Mistral chat models."""
import logging
from typing import Any, ClassVar, Generic, TypeVar

from ..base import BaseExtractor, ExtractedType
from .calls import MistralCall
from .tools import MistralTool
from .types import MistralCallParams

logger = logging.getLogger("mirascope")

T = TypeVar("T", bound=ExtractedType)


class MistralExtractor(BaseExtractor[MistralCall, MistralTool, T], Generic[T]):
    '''A class for extracting structured information using Mistral Chat models.

    Example:

    ```python
    from mirascope.mistral import MistralExtractor
    from pydantic import BaseModel
    from typing import Literal, Type

    class TaskDetails(BaseModel):
        title: str
        priority: Literal["low", "normal", "high"]
        due_date: str

    class TaskExtractor(MistralExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        call_params = MistralCallParams(model="mistral-large-latest")

        prompt_template = """
        Prepare the budget report by next Monday. It's a high priority task.
        """


    task = TaskExtractor().extract(retries=3)
    assert isinstance(task, TaskDetails)
    print(task)
    # > title='Prepare the budget report' priority='high' due_date='next Monday'
    ```
    '''

    call_params: ClassVar[MistralCallParams] = MistralCallParams()

    def extract(self, retries: int = 0, **kwargs: Any) -> T:
        """Extracts `extract_schema` from the Mistral call response.

        The `extract_schema` is converted into an `MistralTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Mistrals's tool/function calling functionality to extract
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
            MistralException: raises any Mistral exceptions, see:
                https://github.com/mistralai/client-python/blob/main/src/mistralai/exceptions.py
        """
        return self._extract(MistralCall, MistralTool, retries, **kwargs)

    async def extract_async(self, retries: int = 0, **kwargs: Any) -> T:
        """Asynchronously extracts `extract_schema` from the Mistral call response.

        The `extract_schema` is converted into an `MistralTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Mistrals's tool/function calling functionality to extract
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
            MistralException: raises any Mistral exceptions, see:
                https://github.com/mistralai/client-python/blob/main/src/mistralai/exceptions.py
        """
        return await self._extract_async(MistralCall, MistralTool, retries, **kwargs)
