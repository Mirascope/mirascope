"""Fixtures for Mirascope's base module tests."""

from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, ConfigDict

from mirascope.base.ops_utils import wrap_mirascope_class_functions
from mirascope.openai.calls import OpenAICall


def with_saving(include_async: bool):
    def inner_with_saving(cls):
        """Test decorator for saving."""

        def handle_before_call(
            self: BaseModel,
            fn: Callable[..., Any],
            **kwargs: dict[str, Any],
        ):
            pass

        async def handle_before_call_async(
            self: BaseModel,
            fn: Callable[..., Any],
            **kwargs: dict[str, Any],
        ):
            pass

        def handle_after_call(
            self: BaseModel,
            fn: Callable[..., Any],
            result: Any,
            before_result: Any,
            **kwargs: dict[str, Any],
        ):
            pass

        async def handle_after_call_async(
            self: BaseModel,
            fn: Callable[..., Any],
            result: Any,
            before_result: Any,
            **kwargs: dict[str, Any],
        ):
            pass

        handle_before_call_mock = MagicMock(wraps=handle_before_call)
        handle_before_call_async_mock = AsyncMock(wraps=handle_before_call_async)
        handle_after_call_mock = MagicMock(wraps=handle_after_call)
        handle_after_call_async_mock = AsyncMock(wraps=handle_after_call_async)
        kwargs = {
            "handle_before_call": handle_before_call_mock,
            "handle_after_call": handle_after_call_mock,
        }
        if include_async:
            kwargs.update(
                {
                    "handle_before_call_async": handle_before_call_async_mock,
                    "handle_after_call_async": handle_after_call_async_mock,
                }
            )
        wrap_mirascope_class_functions(cls, **kwargs)
        cls.handle_before_call = handle_before_call_mock
        cls.handle_before_call_async = handle_before_call_async_mock
        cls.handle_after_call = handle_after_call_mock
        cls.handle_after_call_async = handle_after_call_async_mock
        return cls

    return inner_with_saving


@pytest.fixture()
def fixture_with_saving() -> type[OpenAICall]:
    @with_saving(include_async=True)
    class TestModel(OpenAICall):
        prompt_template = """
        Test
        """
        api_key = "Test"
        model_config = ConfigDict(
            ignored_types=(
                MagicMock,
                AsyncMock,
            )
        )
        handle_before_call = MagicMock()
        handle_before_call_async = AsyncMock()
        handle_after_call = MagicMock()
        handle_after_call_async = AsyncMock()

    return TestModel


@pytest.fixture()
def fixture_with_saving_without_async() -> type[OpenAICall]:
    @with_saving(include_async=False)
    class TestModel(OpenAICall):
        prompt_template = """
        Test
        """
        api_key = "Test"
        model_config = ConfigDict(ignored_types=(MagicMock,))
        handle_before_call = MagicMock()
        handle_after_call = MagicMock()

    return TestModel
