from typing import Any, cast
from unittest.mock import Mock

import pytest

from mirascope.core import BaseMessageParam
from mirascope.core.base import BaseDynamicConfig
from mirascope.core.base._utils._get_dynamic_configuration import (
    get_dynamic_configuration,
)


def test_get_dynamic_configuration_sync_returns_config():
    def fn(*args: Any, **kwargs: Any) -> BaseDynamicConfig:
        return cast(BaseDynamicConfig, {"metadata": {"some_key": "some_value"}})

    result = get_dynamic_configuration(fn, (), {})
    assert result == {"metadata": {"some_key": "some_value"}}


def test_get_dynamic_configuration_sync_returns_message_param_list():
    def fn(*args: Any, **kwargs: Any) -> list[BaseMessageParam]:
        return [BaseMessageParam(role="user", content="Hello, World!")]

    result = get_dynamic_configuration(fn, (), {})
    assert result == {
        "messages": [BaseMessageParam(role="user", content="Hello, World!")]
    }


def test_get_dynamic_configuration_sync_with_original_fn():
    def original_fn(*args: Any, **kwargs: Any) -> BaseDynamicConfig:
        return cast(BaseDynamicConfig, {"computed_fields": {"field1": "value1"}})

    fn = Mock()
    fn._original_fn = original_fn

    result = get_dynamic_configuration(fn, (), {})
    assert result == {"computed_fields": {"field1": "value1"}}


def test_get_dynamic_configuration_sync_with_original_fn_returns_message_param_list():
    def original_fn(*args: Any, **kwargs: Any) -> list[BaseMessageParam]:
        return [BaseMessageParam(role="assistant", content="How can I assist you?")]

    fn = Mock()
    fn._original_fn = original_fn

    result = get_dynamic_configuration(fn, (), {})
    assert result == {
        "messages": [
            BaseMessageParam(role="assistant", content="How can I assist you?")
        ]
    }


def test_get_dynamic_configuration_sync_passes_args_kwargs():
    def fn(*args: Any, **kwargs: Any) -> BaseDynamicConfig:
        assert args == (1, 2)
        assert kwargs == {"key": "value"}
        return cast(
            BaseDynamicConfig,
            {"metadata": {"args_received": args, "kwargs_received": kwargs}},
        )

    result = get_dynamic_configuration(fn, (1, 2), {"key": "value"})
    assert result == {
        "metadata": {
            "args_received": (1, 2),
            "kwargs_received": {"key": "value"},
        }
    }


@pytest.mark.asyncio
async def test_get_dynamic_configuration_async_returns_config():
    async def fn(*args: Any, **kwargs: Any) -> BaseDynamicConfig:
        return cast(BaseDynamicConfig, {"metadata": {"some_key": "some_value"}})

    result = await get_dynamic_configuration(fn, (), {})
    assert result == {"metadata": {"some_key": "some_value"}}


@pytest.mark.asyncio
async def test_get_dynamic_configuration_async_returns_message_param_list():
    async def fn(*args: Any, **kwargs: Any) -> list[BaseMessageParam]:
        return [BaseMessageParam(role="user", content="Hello, World!")]

    result = await get_dynamic_configuration(fn, (), {})
    assert result == {
        "messages": [BaseMessageParam(role="user", content="Hello, World!")]
    }


@pytest.mark.asyncio
async def test_get_dynamic_configuration_async_with_original_fn():
    async def original_fn(*args: Any, **kwargs: Any) -> BaseDynamicConfig:
        return cast(BaseDynamicConfig, {"computed_fields": {"field1": "value1"}})

    fn = Mock()
    fn._original_fn = original_fn

    result = await get_dynamic_configuration(fn, (), {})
    assert result == {"computed_fields": {"field1": "value1"}}


@pytest.mark.asyncio
async def test_get_dynamic_configuration_async_with_original_fn_returns_message_param_list():
    async def original_fn(*args: Any, **kwargs: Any) -> list[BaseMessageParam]:
        return [BaseMessageParam(role="assistant", content="How can I assist you?")]

    fn = Mock()
    fn._original_fn = original_fn

    result = await get_dynamic_configuration(fn, (), {})
    assert result == {
        "messages": [
            BaseMessageParam(role="assistant", content="How can I assist you?")
        ]
    }


@pytest.mark.asyncio
async def test_get_dynamic_configuration_async_passes_args_kwargs():
    async def fn(*args: Any, **kwargs: Any) -> BaseDynamicConfig:
        assert args == (1, 2)
        assert kwargs == {"key": "value"}
        return cast(
            BaseDynamicConfig,
            {"metadata": {"args_received": args, "kwargs_received": kwargs}},
        )

    result = await get_dynamic_configuration(fn, (1, 2), {"key": "value"})
    assert result == {
        "metadata": {
            "args_received": (1, 2),
            "kwargs_received": {"key": "value"},
        }
    }
