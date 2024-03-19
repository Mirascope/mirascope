"""A class for extracting structured information using OpenAI chat models."""
from __future__ import annotations

import logging
from typing import Any, ClassVar, Generic, TypeVar

from ..base import BaseExtractor, ExtractedType
from .calls import OpenAICall
from .tools import OpenAITool
from .types import OpenAICallParams

logger = logging.getLogger("mirascope")

T = TypeVar("T", bound=ExtractedType)


class OpenAIExtractor(BaseExtractor[OpenAICall, OpenAITool, T], Generic[T]):
    '''A class for extracting structured information using OpenAI chat models.

    Example:

    ```python
    from typing import Literal, Type

    from mirascope.openai import OpenAIExtractor
    from pydantic import BaseModel


    class TaskDetails(BaseModel):
        title: str
        priority: Literal["low", "normal", "high"]
        due_date: str


    class TaskExtractor(OpenAIExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails

        prompt_template = """
        Please extract the task details:
        {task}
        """

        task: str


    task_description = "Submit quarterly report by next Friday. Task is high priority."
    task = TaskExtractor(task=task_description).extract(retries=3)
    assert isinstance(task, TaskDetails)
    print(task)
    #> title='Submit quarterly report' priority='high' due_date='next Friday'
    ```
    '''

    call_params: ClassVar[OpenAICallParams] = OpenAICallParams()

    def extract(self, retries: int = 0, **kwargs: Any) -> T:
        """Extracts `extract_schema` from the OpenAI call response.

        The `extract_schema` is converted into an `OpenAITool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of OpenAI's tool/function calling functionality to extract
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
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        return self._extract(OpenAICall, OpenAITool, retries, **kwargs)

    async def extract_async(self, retries: int = 0, **kwargs: Any) -> T:
        """Asynchronously extracts `extract_schema` from the OpenAI call response.

        The `extract_schema` is converted into an `OpenAITool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of OpenAI's tool/function calling functionality to extract
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
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        return await self._extract_async(OpenAICall, OpenAITool, retries, **kwargs)
