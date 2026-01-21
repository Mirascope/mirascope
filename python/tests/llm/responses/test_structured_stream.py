"""Unit tests for structured streaming with mocked chunks."""

from collections.abc import Sequence
from typing import Any, cast

import pytest
from inline_snapshot import snapshot
from pydantic import BaseModel

from mirascope import llm


def create_sync_stream_response_with_format(
    chunks: Sequence[llm.StreamResponseChunk],
    format: llm.Format[Any] | None = None,
) -> llm.StreamResponse[Any]:
    """Create a llm.StreamResponse with format for testing."""

    def sync_chunk_iter() -> llm.ChunkIterator:
        yield from chunks

    iterator = sync_chunk_iter()

    response = llm.StreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        input_messages=[llm.messages.user("Test")],
        chunk_iterator=iterator,
        format=format,
    )
    return response


def create_async_stream_response_with_format(
    chunks: Sequence[llm.StreamResponseChunk],
    format: llm.Format[Any] | None = None,
) -> llm.AsyncStreamResponse[Any]:
    """Create an async llm.StreamResponse with format for testing."""

    async def async_chunk_iter() -> llm.AsyncChunkIterator:
        for chunk in chunks:
            yield chunk

    iterator = async_chunk_iter()

    response = llm.AsyncStreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        input_messages=[llm.messages.user("Test")],
        chunk_iterator=iterator,
        format=format,
    )
    return response


class TestStructuredStreamSync:
    """Test synchronous structured streaming."""

    def test_structured_stream_basemodel(self) -> None:
        """Test partial structured streaming with BaseModel format."""

        class Book(BaseModel):
            title: str
            author: str

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"title": '),
            llm.TextChunk(delta='"The Name of the Wind"'),
            # Note: No author field, no closing brace, no TextEndChunk
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = []
        for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Should get partial results
        final_partial = partials[-1]
        assert final_partial is not None
        assert final_partial.title == "The Name of the Wind"
        assert final_partial.author is None  # Not received yet

    def test_structured_stream_nested_model(self) -> None:
        """Test partial structured streaming with nested BaseModel."""

        class Author(BaseModel):
            first_name: str
            last_name: str

        class Book(BaseModel):
            title: str
            author: Author

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"title": "The Name", '),
            llm.TextChunk(delta='"author": {"first_name": "Patrick"'),
            # Note: No last_name, no closing braces, no TextEndChunk
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = []
        for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Should get partial results
        final_partial = partials[-1]
        assert final_partial is not None
        assert final_partial.title == "The Name"
        assert final_partial.author is not None
        assert final_partial.author.first_name == "Patrick"
        assert final_partial.author.last_name is None  # Not received yet

    def test_structured_stream_primitive_type(self) -> None:
        """Test partial structured streaming with primitive type (unwrapped)."""

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"output": ['),
            llm.TextChunk(delta='"item1", '),
            llm.TextChunk(delta='"item2"'),
            # Note: No item3, no closing brackets, no TextEndChunk
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(list[str], mode="json")
        )

        partials = []
        for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Should get partial results
        final_partial = partials[-1]
        assert final_partial is not None
        assert isinstance(final_partial, list)
        assert len(final_partial) >= 2
        assert final_partial[0] == "item1"
        assert final_partial[1] == "item2"

    def test_structured_stream_with_tool_call_chunks(self) -> None:
        """Test partial structured streaming with tool call chunks (tool mode)."""

        class Book(BaseModel):
            title: str
            author: str

        chunks = [
            llm.ToolCallStartChunk(
                id="call_1", name="__mirascope_formatted_output_tool__"
            ),
            llm.ToolCallChunk(id="call_1", delta='{"title": '),
            llm.ToolCallChunk(id="call_1", delta='"The Name"'),
            # Note: No author field, no closing brace, no ToolCallEndChunk
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="tool")
        )

        partials = []
        for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Should get partial results
        final_partial = partials[-1]
        assert final_partial is not None
        assert final_partial.title == "The Name"
        assert final_partial.author is None  # Not received yet

    def test_structured_stream_no_format_raises(self) -> None:
        """Test that structured_stream raises when format is not set."""
        chunks = [llm.TextStartChunk(), llm.TextChunk(delta='{"test": "value"}')]

        response = create_sync_stream_response_with_format(chunks=chunks, format=None)

        with pytest.raises(ValueError, match="requires format parameter"):
            list(response.structured_stream())

    def test_structured_stream_output_parser_raises(self) -> None:
        """Test that structured_stream raises for OutputParser."""

        @llm.output_parser(formatting_instructions="CSV")
        def parse_csv(response: llm.AnyResponse) -> list[str]:
            return []

        chunks = [llm.TextStartChunk(), llm.TextChunk(delta="test")]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(parse_csv, mode="parser")
        )

        with pytest.raises(NotImplementedError, match="OutputParser"):
            list(response.structured_stream())


class TestStructuredStreamAsync:
    """Test asynchronous structured streaming."""

    @pytest.mark.asyncio
    async def test_structured_stream_async_basemodel(self) -> None:
        """Test async partial structured streaming with BaseModel format."""

        class Book(BaseModel):
            title: str
            author: str

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"title": '),
            llm.TextChunk(delta='"The Name of the Wind"'),
            # Note: No author field, no closing brace, no TextEndChunk
        ]

        response = create_async_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = []
        async for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Should get partial results
        final_partial = partials[-1]
        assert final_partial is not None
        assert final_partial.title == "The Name of the Wind"
        assert final_partial.author is None  # Not received yet

    @pytest.mark.asyncio
    async def test_structured_stream_async_primitive(self) -> None:
        """Test async partial structured streaming with primitive type."""

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"output": ['),
            llm.TextChunk(delta='"a", "b"'),
            # Note: No "c", no closing brackets, no TextEndChunk
        ]

        response = create_async_stream_response_with_format(
            chunks=chunks, format=llm.format(list[str], mode="json")
        )

        partials = []
        async for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Should get partial results
        final_partial = partials[-1]
        assert final_partial is not None
        assert isinstance(final_partial, list)
        assert len(final_partial) >= 2

    @pytest.mark.asyncio
    async def test_structured_stream_async_no_format_raises(self) -> None:
        """Test that async structured_stream raises when format is not set."""
        chunks = [llm.TextStartChunk(), llm.TextChunk(delta='{"test": "value"}')]

        response = create_async_stream_response_with_format(chunks=chunks, format=None)

        with pytest.raises(ValueError, match="requires format parameter"):
            _ = [p async for p in response.structured_stream()]


class TestStructuredStreamEdgeCases:
    """Test edge cases for structured streaming."""

    def test_structured_stream_empty_chunks(self) -> None:
        """Test structured streaming with no content chunks."""

        class Book(BaseModel):
            title: str

        chunks: list[llm.StreamResponseChunk] = []

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = list(response.structured_stream())

        # Should yield nothing for empty stream
        assert len(partials) == 0

    def test_structured_stream_malformed_json(self) -> None:
        """Test that malformed JSON chunks are skipped gracefully."""

        class Book(BaseModel):
            title: str

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta="{not valid json"),
            llm.TextChunk(delta="}"),
            llm.TextEndChunk(),
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        # Should not raise, just skip unparsable chunks
        for _ in response.structured_stream():
            pass
        # Streaming should complete without errors

    def test_structured_stream_preamble_in_same_chunk(self) -> None:
        """Test that preamble text in same chunk as JSON gets stripped."""

        class Book(BaseModel):
            title: str

        chunks = [
            llm.TextStartChunk(),
            # Single chunk with preamble AND JSON start
            llm.TextChunk(delta='Sure! Here: {"title": "The Name"'),
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = list(response.structured_stream())
        partials = [cast(Book, partial).model_dump_json() for partial in partials]
        assert partials == snapshot(['{"title":"The Name"}'])

    def test_structured_stream_only_preamble_no_json(self) -> None:
        """Test that only preamble text without any JSON characters is handled."""

        class Book(BaseModel):
            title: str

        chunks = [
            llm.TextStartChunk(),
            # Only preamble text with no { or [ characters
            llm.TextChunk(delta="Sure thing! "),
            llm.TextChunk(delta="I will help you. "),
            llm.TextChunk(delta="Let me process that..."),
            # Never send any JSON
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = []
        for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # All partials should be None since no JSON was ever sent
        assert all(p is None for p in partials)

    def test_parse_partial_during_stream(self) -> None:
        """Test calling parse(partial=True) with incomplete chunks."""

        class Book(BaseModel):
            title: str
            author: str
            year: int

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"title": '),
            llm.TextChunk(delta='"The Name of the Wind"'),
            llm.TextChunk(delta=', "author": "Patrick"'),
            # Note: No year field and no TextEndChunk - stream is incomplete
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = list(response.structured_stream())
        partials = [cast(Book, partial).model_dump_json() for partial in partials]
        assert partials == snapshot(
            [
                '{"title":null,"author":null,"year":null}',
                '{"title":"The Name of the Wind","author":null,"year":null}',
                '{"title":"The Name of the Wind","author":"Patrick","year":null}',
            ]
        )

    def test_parse_partial_nested_model(self) -> None:
        """Test partial parsing with nested models."""

        class Author(BaseModel):
            first_name: str
            last_name: str
            birth_year: int

        class Book(BaseModel):
            title: str
            author: Author

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"title": "The Name", '),
            llm.TextChunk(delta='"author": {"first_name": "Patrick"'),
            # Note: No last_name, birth_year, or closing braces - incomplete
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(Book, mode="json")
        )

        partials = []
        for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Get the most complete partial
        final_partial = partials[-1]
        assert final_partial is not None
        assert final_partial.title == "The Name"
        assert final_partial.author is not None
        assert final_partial.author.first_name == "Patrick"
        assert final_partial.author.last_name is None  # Not received yet
        assert final_partial.author.birth_year is None  # Not received yet

    def test_parse_partial_primitive_type(self) -> None:
        """Test partial parsing with primitive list type."""

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta='{"output": ['),
            llm.TextChunk(delta='"item1", '),
            llm.TextChunk(delta='"item2"'),
            # Note: No closing brackets - incomplete
        ]

        response = create_sync_stream_response_with_format(
            chunks=chunks, format=llm.format(list[str], mode="json")
        )

        partials = []
        for _ in response.structured_stream():
            partial = response.parse(partial=True)
            partials.append(partial)

        # Get the most complete partial
        final_partial = partials[-1]
        assert final_partial is not None
        assert isinstance(final_partial, list)
        # Should have at least the items we sent
        assert len(final_partial) >= 2
        assert final_partial[0] == "item1"
        assert final_partial[1] == "item2"
