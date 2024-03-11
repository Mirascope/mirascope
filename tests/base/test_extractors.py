"""Tests for the `BaseExtractor` class."""
from unittest.mock import patch

from mirascope.base.extractors import BaseExtractor
from mirascope.base.prompts import BasePrompt


@patch.multiple(BaseExtractor, __abstractmethods__=set())
def test_base_call() -> None:
    """Tests the `BaseExtractor` interface."""
    model = "gpt-3.5-turbo-1106"

    class Extractor(BaseExtractor):
        extract_params = BaseExtractor.ExtractParams(model=model)

    extractor = Extractor()  # type: ignore
    assert isinstance(extractor, BasePrompt)
    assert extractor.extract_params.model == model
