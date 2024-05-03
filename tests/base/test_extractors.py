"""Tests for the `BaseExtractor` class."""
from typing import Type
from unittest.mock import patch

from pydantic import BaseModel

from mirascope.base.calls import BaseCall
from mirascope.base.extractors import BaseExtractor
from mirascope.base.prompts import BasePrompt
from mirascope.base.tool_streams import BaseToolStream
from mirascope.base.tools import BaseTool
from mirascope.base.types import BaseCallParams


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
