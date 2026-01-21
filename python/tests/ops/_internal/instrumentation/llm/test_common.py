"""Unit tests for common LLM instrumentation utilities."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mirascope.llm.content import Text
from mirascope.llm.messages import AssistantMessage, SystemMessage, UserMessage
from mirascope.llm.responses.usage import Usage
from mirascope.ops._internal.instrumentation.llm.common import (
    attach_response,
    attach_response_async,
)

if TYPE_CHECKING:
    pass


def _make_mock_span() -> MagicMock:
    """Create a mock OpenTelemetry span."""
    span = MagicMock()
    span.attributes = {}

    def set_attribute(key: str, value: object) -> None:
        span.attributes[key] = value

    span.set_attribute = MagicMock(side_effect=set_attribute)
    return span


def _make_mock_response(with_usage: bool = True) -> MagicMock:
    """Create a mock RootResponse for testing."""
    mock = MagicMock()
    mock.provider_id = "openai"
    mock.model_id = "openai/gpt-4o-mini"
    # finish_reason is None for normal completion (maps to "stop")
    mock.finish_reason = None
    mock.raw = MagicMock()
    mock.raw.id = "resp_123"
    mock.messages = [
        SystemMessage(content=Text(text="You are helpful.")),
        UserMessage(content=[Text(text="Hi")], name=None),
        AssistantMessage(
            content=[Text(text="Hello!")],
            name=None,
            provider_id="openai",
            model_id="openai/gpt-4o-mini",
            provider_model_name=None,
            raw_message=None,
        ),
    ]
    mock.content = [Text(text="Hello, world!")]
    if with_usage:
        mock.usage = Usage(input_tokens=100, output_tokens=50)
    else:
        mock.usage = None
    return mock


def _make_mock_cost_response(
    input_cost: float = 25.0,
    output_cost: float = 50.0,
    total_cost: float = 75.0,
    cache_read_cost: float | None = None,
    cache_write_cost: float | None = None,
) -> MagicMock:
    """Create a mock TokenCostCalculateResponse."""
    mock = MagicMock()
    mock.input_cost_centicents = input_cost
    mock.output_cost_centicents = output_cost
    mock.total_cost_centicents = total_cost
    mock.cache_read_cost_centicents = cache_read_cost
    mock.cache_write_cost_centicents = cache_write_cost
    return mock


class TestAttachResponse:
    """Tests for attach_response function."""

    def test_attach_response_with_cost(self) -> None:
        """Test attach_response sets cost when cost calculation succeeds."""
        span = _make_mock_span()
        response = _make_mock_response(with_usage=True)
        request_messages = [
            SystemMessage(content=Text(text="You are helpful.")),
            UserMessage(content=[Text(text="Hi")], name=None),
        ]
        mock_cost = _make_mock_cost_response(
            input_cost=25.0,
            output_cost=50.0,
            total_cost=75.0,
            cache_read_cost=5.0,
            cache_write_cost=10.0,
        )

        with patch(
            "mirascope.ops._internal.instrumentation.llm.common._calculate_cost_sync",
            return_value=mock_cost,
        ):
            attach_response(span, response, request_messages=request_messages)

        # Verify cost was attached
        assert "mirascope.response.cost" in span.attributes
        cost_json = span.attributes["mirascope.response.cost"]
        assert isinstance(cost_json, str)
        cost_data = json.loads(cost_json)
        assert cost_data["input_cost"] == 25.0
        assert cost_data["output_cost"] == 50.0
        assert cost_data["total_cost"] == 75.0
        assert cost_data["cache_read_cost"] == 5.0
        assert cost_data["cache_write_cost"] == 10.0

    def test_attach_response_without_usage(self) -> None:
        """Test attach_response when response has no usage."""
        span = _make_mock_span()
        response = _make_mock_response(with_usage=False)
        request_messages = [
            UserMessage(content=[Text(text="Hi")], name=None),
        ]

        with patch(
            "mirascope.ops._internal.instrumentation.llm.common._calculate_cost_sync",
        ) as mock_calc:
            attach_response(span, response, request_messages=request_messages)

        # Cost calculation should not be called when there's no usage
        mock_calc.assert_not_called()
        assert "mirascope.response.cost" not in span.attributes

    def test_attach_response_cost_calculation_returns_none(self) -> None:
        """Test attach_response when cost calculation returns None."""
        span = _make_mock_span()
        response = _make_mock_response(with_usage=True)
        request_messages = [
            UserMessage(content=[Text(text="Hi")], name=None),
        ]

        with patch(
            "mirascope.ops._internal.instrumentation.llm.common._calculate_cost_sync",
            return_value=None,
        ):
            attach_response(span, response, request_messages=request_messages)

        # Cost should not be attached when calculation returns None
        assert "mirascope.response.cost" not in span.attributes


class TestAttachResponseAsync:
    """Tests for attach_response_async function."""

    @pytest.mark.asyncio
    async def test_attach_response_async_with_cost(self) -> None:
        """Test attach_response_async sets cost when cost calculation succeeds."""
        span = _make_mock_span()
        response = _make_mock_response(with_usage=True)
        request_messages = [
            SystemMessage(content=Text(text="You are helpful.")),
            UserMessage(content=[Text(text="Hi")], name=None),
        ]
        mock_cost = _make_mock_cost_response(
            input_cost=30.0,
            output_cost=60.0,
            total_cost=90.0,
            cache_read_cost=8.0,
            cache_write_cost=12.0,
        )

        with patch(
            "mirascope.ops._internal.instrumentation.llm.common._calculate_cost_async",
            new_callable=AsyncMock,
            return_value=mock_cost,
        ):
            await attach_response_async(
                span, response, request_messages=request_messages
            )

        # Verify cost was attached
        assert "mirascope.response.cost" in span.attributes
        cost_json = span.attributes["mirascope.response.cost"]
        assert isinstance(cost_json, str)
        cost_data = json.loads(cost_json)
        assert cost_data["input_cost"] == 30.0
        assert cost_data["output_cost"] == 60.0
        assert cost_data["total_cost"] == 90.0
        assert cost_data["cache_read_cost"] == 8.0
        assert cost_data["cache_write_cost"] == 12.0

    @pytest.mark.asyncio
    async def test_attach_response_async_without_usage(self) -> None:
        """Test attach_response_async when response has no usage."""
        span = _make_mock_span()
        response = _make_mock_response(with_usage=False)
        request_messages = [
            UserMessage(content=[Text(text="Hi")], name=None),
        ]

        with patch(
            "mirascope.ops._internal.instrumentation.llm.common._calculate_cost_async",
            new_callable=AsyncMock,
        ) as mock_calc:
            await attach_response_async(
                span, response, request_messages=request_messages
            )

        # Cost calculation should not be called when there's no usage
        mock_calc.assert_not_called()
        assert "mirascope.response.cost" not in span.attributes

    @pytest.mark.asyncio
    async def test_attach_response_async_cost_calculation_returns_none(self) -> None:
        """Test attach_response_async when cost calculation returns None."""
        span = _make_mock_span()
        response = _make_mock_response(with_usage=True)
        request_messages = [
            UserMessage(content=[Text(text="Hi")], name=None),
        ]

        with patch(
            "mirascope.ops._internal.instrumentation.llm.common._calculate_cost_async",
            new_callable=AsyncMock,
            return_value=None,
        ):
            await attach_response_async(
                span, response, request_messages=request_messages
            )

        # Cost should not be attached when calculation returns None
        assert "mirascope.response.cost" not in span.attributes
