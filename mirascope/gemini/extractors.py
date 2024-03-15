import logging
from typing import Any, ClassVar, Generic, TypeVar

from ..base import BaseExtractor, ExtractedType
from .calls import GeminiCall
from .tools import GeminiTool
from .types import GeminiCallParams

logger = logging.getLogger("mirascope")

T = TypeVar("T", bound=ExtractedType)


class GeminiExtractor(BaseExtractor[GeminiCall, GeminiTool, T], Generic[T]):
    '''A class for extracting structured information using Google's Gemini Chat models.

    Example:

    ```python
    from typing import Literal, Type
    from pydantic import BaseModel
    from mirascope.gemini import GeminiExtractor

    class TaskDetails(BaseModel):
        title: str
        priority: Literal["low", "normal", "high"]
        due_date: str

    class TaskExtractor(GeminiExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails

        prompt_template = """
        USER: I need to extract task details.
        MODEL: Sure, please provide the task description.
        USER: {task}
        """

        task: str

    task_description = "Prepare the budget report by next Monday. It's a high priority task."
    task = TaskExtractor(task=task_description).extract(retries=3)
    assert isinstance(task, TaskDetails)
    print(task)
    #> title='Prepare the budget report' priority='high' due_date='next Monday'
    ```
    '''

    call_params: ClassVar[GeminiCallParams] = GeminiCallParams()

    def extract(self, retries: int = 0, **kwargs: Any) -> T:
        """Extracts `extract_schema` from the Gemini call response.

        The `extract_schema` is converted into a `GeminiTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Gemini's tool/function calling functionality to extract
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
            GeminiError: raises any Gemini errors.
        """
        return self._extract(GeminiCall, GeminiTool, retries, **kwargs)

    async def extract_async(self, retries: int = 0, **kwargs: Any) -> T:
        """Asynchronously extracts `extract_schema` from the Gemini call response.

        The `extract_schema` is converted into a `GeminiTool`, complete with a
        description of the tool, all of the fields, and their types. This allows us to
        take advantage of Gemini's tool/function calling functionality to extract
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
            GeminiError: raises any Gemini errors.
        """
        return await self._extract_async(GeminiCall, GeminiTool, retries, **kwargs)
