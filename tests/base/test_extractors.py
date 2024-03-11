"""Tests for the `BaseExtractor` class."""
from unittest.mock import patch

from pydantic import BaseModel

from mirascope.base.extractors import BaseExtractor
from mirascope.base.prompts import BasePrompt
from mirascope.base.types import BaseCallParams


@patch.multiple(BaseExtractor, __abstractmethods__=set())
@patch.multiple(BaseCallParams, __abstractmethods__=set())
def test_base_call() -> None:
    """Tests the `BaseExtractor` interface."""
    model = "gpt-3.5-turbo-1106"

    class Task(BaseModel):
        title: str
        details: str

    class Extractor(BaseExtractor):
        extract_schema = Task
        call_params = BaseCallParams(model=model)

    extractor = Extractor()  # type: ignore
    assert isinstance(extractor, BasePrompt)
    assert extractor.call_params.model == model
