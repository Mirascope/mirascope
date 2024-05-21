"""Fixtures for Mirascope's base module tests."""
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel, ConfigDict

from mirascope.base.ops_utils import wrap_mirascope_class_functions
from mirascope.openai.calls import OpenAICall


def with_saving(cls):
    """Test decorator for saving."""

    def handle_after_call(
        self: BaseModel,
        fn: Callable[..., Any],
        result: Any,
        before_result: Any,
        **kwargs: dict[str, Any],
    ):
        pass

    handle_after_call_mock = MagicMock(wraps=handle_after_call)
    wrap_mirascope_class_functions(cls, None, handle_after_call_mock)
    cls.handle_after_call = handle_after_call_mock
    return cls


@pytest.fixture()
def fixture_with_saving() -> type[OpenAICall]:
    @with_saving
    class TestModel(OpenAICall):
        prompt_template = """
        Test
        """
        api_key = "Test"
        model_config = ConfigDict(ignored_types=(MagicMock,))
        handle_after_call = MagicMock()

    return TestModel
