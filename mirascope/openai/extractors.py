"""A class for extracting structured information using OpenAI chat models."""
import logging
from enum import Enum
from inspect import isclass
from typing import (
    Annotated,
    Any,
    ClassVar,
    Generic,
    Literal,
    TypeVar,
    Union,
    get_origin,
)

from pydantic import ValidationError

from ..base import BaseExtractor, ExtractionType
from .calls import OpenAICall
from .tools import OpenAITool
from .types import OpenAICallParams

logger = logging.getLogger("mirascope")

T = TypeVar("T", bound=ExtractionType)


def _is_base_type(type_: Any) -> bool:
    """Check if a type is a base type."""
    base_types = {str, int, float, bool, list, set, tuple}
    return (
        (isclass(type_) and issubclass(type_, Enum))
        or type_ in base_types
        or get_origin(type_) in base_types.union({Literal, Union, Annotated})
    )


class OpenAIExtractor(BaseExtractor, Generic[T]):
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

    call_params: ClassVar[OpenAICallParams] = OpenAICallParams(
        model="gpt-3.5-turbo-0125"
    )

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
        kwargs, return_tool = self._setup(kwargs)

        class TempCall(OpenAICall):
            template = self.template

            call_params = self.call_params

        response = TempCall(**self.model_dump()).call(**kwargs)
        try:
            tool = response.tool
            if tool is None:
                raise AttributeError("No tool found in the completion.")
            if return_tool:
                return tool  # type: ignore
            if _is_base_type(self.extract_schema):
                return tool.value  # type: ignore
            model = self.extract_schema(**response.tool.model_dump())  # type: ignore
            model._completion = response  # type: ignore
            return model  # type: ignore
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                return self.extract(retries - 1, **kwargs)
            raise  # re-raise if we have no retries left

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
        kwargs, return_tool = self._setup(kwargs)

        class TempCall(OpenAICall):
            template = self.template

            call_params = OpenAICallParams(**self.call_params.model_dump())

        response = await TempCall(**self.model_dump()).call_async(**kwargs)
        try:
            tool = response.tool
            if tool is None:
                raise AttributeError("No tool found in the completion.")
            if return_tool:
                return tool  # type: ignore
            if _is_base_type(self.extract_schema):
                return tool.value  # type: ignore
            model = self.extract_schema(**response.tool.model_dump())  # type: ignore
            model._completion = response  # type: ignore
            return model  # type: ignore
        except (AttributeError, ValueError, ValidationError) as e:
            if retries > 0:
                logging.info(f"Retrying due to exception: {e}")
                # TODO: include failure in retry prompt.
                return await self.extract_async(retries - 1, **kwargs)
            raise  # re-raise if we have no retries left
        raise NotImplementedError()

    ############################## PRIVATE METHODS ###################################

    def _setup(self, kwargs: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        return_tool = True
        openai_tool = self.extract_schema
        if _is_base_type(self.extract_schema):
            openai_tool = OpenAITool.from_base_type(self.extract_schema)  # type: ignore
            return_tool = False
        elif not isclass(self.extract_schema):
            openai_tool = OpenAITool.from_fn(self.extract_schema)
        elif not issubclass(self.extract_schema, OpenAITool):
            openai_tool = OpenAITool.from_model(self.extract_schema)
            return_tool = False
        kwargs["tools"] = [openai_tool]
        return kwargs, return_tool
