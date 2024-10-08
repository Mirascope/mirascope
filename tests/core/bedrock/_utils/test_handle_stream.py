from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest

from mirascope.core.bedrock._utils._handle_stream import (
    handle_stream,
    handle_stream_async,
)
from mirascope.core.bedrock.call_response_chunk import BedrockCallResponseChunk
from mirascope.core.bedrock.tool import BedrockTool


class MockRecommendBook(BedrockTool):
    def call(self, *args: Any, **kwargs: Any) -> Any: ...

    genre: str
    title: str
    author: str

    @classmethod
    def _name(cls) -> str:
        return "RecommendBook"


class MockAnotherTool(BedrockTool):
    def call(self, *args: Any, **kwargs: Any) -> Any: ...

    @classmethod
    def _name(cls) -> str:
        return "AnotherTool"


@pytest.fixture
def mock_response_text_with_tool():
    return [
        {"messageStart": {"role": "assistant"}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": "Here"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " is"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " a"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " book"}}},
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"text": " recommendation"},
            }
        },
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " for"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " a"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " fantasy"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " book"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": ":"}}},
        {"contentBlockStop": {"contentBlockIndex": 0}},
        {
            "contentBlockStart": {
                "contentBlockIndex": 1,
                "start": {
                    "toolUse": {
                        "name": "RecommendBook",
                        "toolUseId": "tooluse_VQy5Xa-oTXqjpQTf4q6LVg",
                    }
                },
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": ""}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": '{"genre": "f'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": 'antasy"'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": ', "tit'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": 'le": '}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": '"T'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": "he "}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": "Name of"}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": " the"}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": ' Wind"'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": ', "auth'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": 'or": "Patri'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": "ck Rothfu"}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 1,
                "delta": {"toolUse": {"input": 'ss"}'}},
            }
        },
        {"contentBlockStop": {"contentBlockIndex": 1}},
        {"messageStop": {"stopReason": "tool_use"}},
        {
            "metadata": {
                "metrics": {"latencyMs": 1063},
                "usage": {"inputTokens": 395, "outputTokens": 85, "totalTokens": 480},
            }
        },
    ]


@pytest.fixture
def mock_response_only_tool():
    return [
        {"messageStart": {"role": "assistant"}},
        {
            "contentBlockStart": {
                "contentBlockIndex": 0,
                "start": {
                    "toolUse": {
                        "name": "RecommendBook",
                        "toolUseId": "tooluse_Z3qh_1hxSoCzEIw5yBiVpQ",
                    }
                },
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": ""}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": '{"g'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": 'enre": "'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": 'fantasy"'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": ', "title": '}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": '"The Way'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": ' of Kings"'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": ", "}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": '"author": "'}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": "Brandon "}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": "Sand"}},
            }
        },
        {
            "contentBlockDelta": {
                "contentBlockIndex": 0,
                "delta": {"toolUse": {"input": 'erson"}'}},
            }
        },
        {"contentBlockStop": {"contentBlockIndex": 0}},
        {"messageStop": {"stopReason": "tool_use"}},
        {
            "metadata": {
                "metrics": {"latencyMs": 876},
                "usage": {"inputTokens": 385, "outputTokens": 74, "totalTokens": 459},
            }
        },
    ]


@pytest.fixture
def mock_response_without_tool():
    return [
        {"messageStart": {"role": "assistant"}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": "Hello"}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": " world"}}},
        {"contentBlockStop": {"contentBlockIndex": 0}},
        {"messageStop": {"stopReason": "end_turn"}},
        {
            "metadata": {
                "metrics": {"latencyMs": 100},
                "usage": {"inputTokens": 10, "outputTokens": 2, "totalTokens": 12},
            }
        },
    ]


def test_handle_stream_with_text_and_tool(mock_response_text_with_tool):
    def mock_stream() -> Generator[dict, None, None]:
        yield from mock_response_text_with_tool

    tool_types = [MockRecommendBook]
    results = list(handle_stream(mock_stream(), tool_types))  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert isinstance(results[-2][1], MockRecommendBook)
    assert results[-2][1].genre == "fantasy"
    assert results[-2][1].title == "The Name of the Wind"
    assert results[-2][1].author == "Patrick Rothfuss"


@pytest.mark.asyncio
async def test_handle_stream_async_with_text_and_tool(mock_response_text_with_tool):
    async def mock_stream() -> AsyncGenerator[dict, None]:
        for chunk in mock_response_text_with_tool:
            yield chunk

    tool_types = [MockRecommendBook]
    results = tuple([c async for c in handle_stream_async(mock_stream(), tool_types)])  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert isinstance(results[-2][1], MockRecommendBook)
    assert results[-2][1].genre == "fantasy"
    assert results[-2][1].title == "The Name of the Wind"
    assert results[-2][1].author == "Patrick Rothfuss"


def test_handle_stream_with_only_tool(mock_response_only_tool):
    def mock_stream() -> Generator[dict, None, None]:
        yield from mock_response_only_tool

    tool_types = [MockRecommendBook]
    results = list(handle_stream(mock_stream(), tool_types))  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert isinstance(results[2][1], MockRecommendBook)
    assert results[2][1].genre == "fantasy"
    assert results[2][1].title == "The Way of Kings"
    assert results[2][1].author == "Brandon Sanderson"


def test_handle_stream_without_tools(mock_response_without_tool):
    def mock_stream() -> Generator[dict, None, None]:
        yield from mock_response_without_tool

    results = list(handle_stream(mock_stream(), None))  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert all(tool is None for chunk, tool in results)


def test_handle_stream_with_mismatched_tool_name(mock_response_text_with_tool):
    def mock_stream() -> Generator[dict, None, None]:
        yield from mock_response_text_with_tool

    tool_types = [MockAnotherTool]
    results = list(handle_stream(mock_stream(), tool_types))  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert all(tool is None for chunk, tool in results)


def test_handle_stream_with_multiple_tool_types(mock_response_text_with_tool):
    def mock_stream() -> Generator[dict, None, None]:
        yield from mock_response_text_with_tool

    tool_types = [MockAnotherTool, MockRecommendBook]
    results = list(handle_stream(mock_stream(), tool_types))  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert isinstance(results[-2][1], MockRecommendBook)
    assert results[-2][1].genre == "fantasy"
    assert results[-2][1].title == "The Name of the Wind"
    assert results[-2][1].author == "Patrick Rothfuss"


@pytest.mark.asyncio
async def test_handle_stream_async_with_mismatched_tool_name(
    mock_response_text_with_tool,
):
    async def mock_stream() -> AsyncGenerator[dict, None]:
        for chunk in mock_response_text_with_tool:
            yield chunk

    tool_types = [MockAnotherTool]
    results = [c async for c in handle_stream_async(mock_stream(), tool_types)]  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert all(tool is None for chunk, tool in results)


@pytest.mark.asyncio
async def test_handle_stream_async_with_multiple_tool_types(
    mock_response_text_with_tool,
):
    async def mock_stream() -> AsyncGenerator[dict, None]:
        for chunk in mock_response_text_with_tool:
            yield chunk

    tool_types = [MockAnotherTool, MockRecommendBook]
    results = [c async for c in handle_stream_async(mock_stream(), tool_types)]  # pyright: ignore [reportArgumentType]

    assert all(isinstance(chunk, BedrockCallResponseChunk) for chunk, tool in results)
    assert isinstance(results[-2][1], MockRecommendBook)
    assert results[-2][1].genre == "fantasy"
    assert results[-2][1].title == "The Name of the Wind"
    assert results[-2][1].author == "Patrick Rothfuss"
