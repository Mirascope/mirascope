"""Tests for the `BaseExtractor` class."""

from typing import Literal, Type
from unittest.mock import patch

from pydantic import BaseModel

from mirascope.anthropic.extractors import AnthropicExtractor
from mirascope.anthropic.types import AnthropicCallParams
from mirascope.base.calls import BaseCall
from mirascope.base.extractors import BaseExtractor
from mirascope.base.prompts import BasePrompt
from mirascope.base.tool_streams import BaseToolStream
from mirascope.base.tools import BaseTool
from mirascope.base.types import BaseCallParams
from mirascope.openai.extractors import OpenAIExtractor


@patch.multiple(BaseExtractor, __abstractmethods__=set())
@patch.multiple(BaseCallParams, __abstractmethods__=set())
def test_base_extractor() -> None:
    """Tests the `BaseExtractor` interface."""
    model = "gpt-3.5-turbo-1106"

    class Task(BaseModel):
        title: str
        details: str

    class Extractor(BaseExtractor[BaseCall, BaseTool, BaseToolStream, Type[Task]]):
        extract_schema: Type[Task] = Task
        call_params = BaseCallParams(model=model)

    extractor = Extractor()  # type: ignore
    assert isinstance(extractor, BasePrompt)
    assert extractor.call_params.model == model


def test_create_extractor() -> None:
    """Tests the `create_extractor` function."""

    class TaskDetails(BaseModel):
        description: str
        due_date: str
        priority: Literal["low", "normal", "high"]

    class NewTaskDetails(TaskDetails):
        points: int

    class TaskExtractor(OpenAIExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        prompt_template = """
        Extract the task details from the following task:
        {task}
        """

        task: str

    new_task_extractor = AnthropicExtractor.from_extractor(
        TaskExtractor,
        AnthropicCallParams(model="claude-3-haiku-20240307"),
    )
    anthropic_task_extractor = new_task_extractor(
        task="Submit quarterly report by next Friday. Task is high priority. Points: 10"
    )
    assert isinstance(anthropic_task_extractor, AnthropicExtractor[TaskDetails])  # type: ignore
    assert anthropic_task_extractor.call_params.model == "claude-3-haiku-20240307"

    new_task_extractor_with_extract_schema = AnthropicExtractor.from_extractor(
        TaskExtractor,
        AnthropicCallParams(model="claude-3-haiku-20240307"),
        extract_schema=NewTaskDetails,
    )
    anthropic_task_extractor_with_extract_schema = new_task_extractor_with_extract_schema(
        task="Submit quarterly report by next Friday. Task is high priority. Points: 10"
    )
    assert isinstance(
        anthropic_task_extractor_with_extract_schema,
        AnthropicExtractor[NewTaskDetails],
    )
