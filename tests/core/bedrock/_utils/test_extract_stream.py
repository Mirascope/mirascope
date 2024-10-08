from unittest.mock import AsyncMock, MagicMock

import pytest

from mirascope.core.bedrock._utils._extract_stream import (
    _extract_async_stream_fn,
    _extract_sync_stream_fn,
)


def test_extract_sync_stream_fn():
    mock_fn = MagicMock()
    mock_fn.return_value = {
        "ResponseMetadata": {"RequestId": "123"},
        "stream": [
            {
                "contentBlockDelta": {"delta": [{"text": "Hello"}]},
            },
            {
                "contentBlockDelta": {"delta": [{"text": "World"}]},
            },
        ],
    }

    extracted_fn = _extract_sync_stream_fn(mock_fn, "test-model")
    result = list(extracted_fn())

    assert len(result) == 2
    assert result[0]["contentBlockDelta"]["delta"][0]["text"] == "Hello"  # pyright: ignore [reportTypedDictNotRequiredAccess, reportGeneralTypeIssues]
    assert result[1]["contentBlockDelta"]["delta"][0]["text"] == "World"  # pyright: ignore [reportTypedDictNotRequiredAccess, reportGeneralTypeIssues]
    assert all(chunk["responseMetadata"] == {"RequestId": "123"} for chunk in result)
    assert all(chunk["model"] == "test-model" for chunk in result)


@pytest.mark.asyncio
async def test_extract_async_stream_fn():
    async def async_generator():
        yield {"chunk1": "async_data1"}
        yield {"chunk2": "async_data2"}

    mock_fn = AsyncMock()
    mock_fn.return_value = {
        "ResponseMetadata": {"RequestId": "456"},
        "stream": async_generator(),
    }

    extracted_fn = _extract_async_stream_fn(mock_fn, "test-async-model")
    result = [chunk async for chunk in extracted_fn()]

    assert len(result) == 2
    assert result[0]["chunk1"] == "async_data1"  # pyright: ignore [reportGeneralTypeIssues]
    assert result[1]["chunk2"] == "async_data2"  # pyright: ignore [reportGeneralTypeIssues]
    assert all(chunk["responseMetadata"] == {"RequestId": "456"} for chunk in result)
    assert all(chunk["model"] == "test-async-model" for chunk in result)
