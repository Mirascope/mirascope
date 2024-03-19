"""A class for extracting structured information using Anthropic Claude models."""
from __future__ import annotations

import logging
from typing import Any, ClassVar, Generic, TypeVar

from ..base import BaseExtractor, ExtractedType
from .calls import AnthropicCall
from .tools import AnthropicTool
from .types import AnthropicCallParams

logger = logging.getLogger("mirascope")

T = TypeVar("T", bound=ExtractedType)


class AnthropicExtractor(BaseExtractor[AnthropicCall, AnthropicTool, T], Generic[T]):
    '''A class for extracting structured information using Anthropic Claude models.

    Example:

    ```python
    from typing import Literal, Type

    from mirascope.anthropic import AnthropicExtractor
    from pydantic import BaseModel


    class TaskDetails(BaseModel):
        title: str
        priority: Literal["low", "normal", "high"]
        due_date: str


    class TaskExtractor(AnthropicExtractor[TaskDetails]):
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

    call_params: ClassVar[AnthropicCallParams] = AnthropicCallParams()

    def extract(self, retries: int = 0, **kwargs: Any) -> T:
        """Extracts `extract_schema` from the Anthropic call response.

        The `extract_schema` is converted into an `AnthropicTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Anthropics's tool/function calling functionality to extract
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
        return self._extract(AnthropicCall, AnthropicTool, retries, **kwargs)

    async def extract_async(self, retries: int = 0, **kwargs: Any) -> T:
        """Asynchronously extracts `extract_schema` from the Anthropic call response.

        The `extract_schema` is converted into an `AnthropicTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Anthropic's tool/function calling functionality to extract
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
        return await self._extract_async(
            AnthropicCall, AnthropicTool, retries, **kwargs
        )
