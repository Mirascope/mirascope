"""A class for extracting structured information using OpenAI chat models."""
from typing import Callable, Generic, TypeVar, Union

from pydantic import BaseModel

from ..base import BaseExtractor, BaseType

_T = TypeVar("_T", bound=Union[BaseType, BaseModel, Callable])


class OpenAIExtractor(BaseExtractor[_T], Generic[_T]):
    '''A class for extracting structured information using OpenAI chat models.

    Example:

    ```python
    from typing import Literal

    from mirascope.openai import OpenAIExtractor
    from pydantic import BaseModel


    class TaskDetails(BaseModel):
        title: str
        priority: Literal["low", "normal", "high"]
        due_date: str


    class TaskExtractor(OpenAIExtractor[TaskDetails]):
        extract_schema = TaskDetails

        template = """\\
            Please extract the task details:
            {task}
        """

        task: str


    task_description = "Submit quarterly report by next Friday. Task is high priority."
    task = TaskExtractor(task=task).extract(retries=3)
    assert isinstance(task, TaskDetails)
    print(task)
    #> title='Submit quarterly report' priority='high' due_date='next Friday'
    ```
    '''

    def extract(self, retries: int = 0) -> _T:
        """Extracts `extract_schema` from the OpenAI call response.

        The `extract_schema` is converted into an `OpenAITool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of OpenAI's tool/function calling functionality to extract
        information from a prompt according to the context provided by the `BaseModel`
        schema.

        Args:
            retries: The maximum number of times to retry the query on validation error.

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        raise NotImplementedError()

    async def extract_async(self, retries: int = 0) -> _T:
        """Asynchronously extracts `extract_schema` from the OpenAI call response.

        The `extract_schema` is converted into an `OpenAITool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of OpenAI's tool/function calling functionality to extract
        information from a prompt according to the context provided by the `BaseModel`
        schema.

        Args:
            retries: The maximum number of times to retry the query on validation error.

        Returns:
            The `Schema` instance extracted from the completion.

        Raises:
            AttributeError: if there is no tool in the call creation.
            ValidationError: if the schema cannot be instantiated from the completion.
            OpenAIError: raises any OpenAI errors, see:
                https://platform.openai.com/docs/guides/error-codes/api-errors
        """
        raise NotImplementedError()
