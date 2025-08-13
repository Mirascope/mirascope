"""Tests for llm.StreamResponse class."""

from collections.abc import AsyncIterator, Iterator, Sequence
from dataclasses import dataclass

import pytest

from mirascope import llm


def create_sync_stream_response(
    chunks: list[llm.AssistantContentChunk],
) -> llm.StreamResponse[llm.Stream]:
    """Create a llm.StreamResponse with a functioning iterator for testing."""

    def sync_chunk_iter() -> llm.ChunkIterator:
        yield from chunks

    iterator = sync_chunk_iter()

    response = llm.StreamResponse(
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[llm.messages.user("Test")],
        chunk_iterator=iterator,
    )
    return response


def create_async_stream_response(
    chunks: list[llm.AssistantContentChunk],
) -> llm.StreamResponse[llm.AsyncStream]:
    """Create a llm.StreamResponse with a functioning iterator for testing."""

    async def async_chunk_iter() -> llm.AsyncChunkIterator:
        for chunk in chunks:
            yield chunk

    iterator = async_chunk_iter()

    response = llm.StreamResponse[llm.AsyncStream](
        provider="openai",
        model="gpt-4o-mini",
        input_messages=[llm.messages.user("Test")],
        chunk_iterator=iterator,
    )
    return response


@pytest.fixture
def example_text() -> llm.Text:
    return llm.Text(text="Hello world")


@pytest.fixture
def example_thinking() -> llm.Thinking:
    return llm.Thinking(thinking="Let me think...", signature="reasoning")


@pytest.fixture
def example_tool_call() -> llm.ToolCall:
    return llm.ToolCall(
        id="tool_call_123",
        name="test_function",
        args='{"param1": "value1", "param2": 42}',
    )


@pytest.fixture
def example_text_chunks() -> list[llm.AssistantContentChunk]:
    """Create a complete text chunk sequence for testing."""
    return [
        llm.TextStartChunk(type="text_start_chunk"),
        llm.TextChunk(type="text_chunk", delta="Hello"),
        llm.TextChunk(type="text_chunk", delta=" "),
        llm.TextChunk(type="text_chunk", delta="world"),
        llm.TextEndChunk(type="text_end_chunk"),
    ]


@pytest.fixture
def example_thinking_chunks() -> list[llm.AssistantContentChunk]:
    """Create a complete thinking chunk sequence for testing."""
    return [
        llm.ThinkingStartChunk(type="thinking_start_chunk"),
        llm.ThinkingChunk(type="thinking_chunk", delta="Let me"),
        llm.ThinkingChunk(type="thinking_chunk", delta=" think..."),
        llm.ThinkingEndChunk(type="thinking_end_chunk", signature="reasoning"),
    ]


@pytest.fixture
def example_tool_call_chunks() -> list[llm.AssistantContentChunk]:
    """Create a complete tool call chunk sequence for testing."""
    return [
        llm.ToolCallStartChunk(
            type="tool_call_start_chunk", id="tool_call_123", name="test_function"
        ),
        llm.ToolCallChunk(type="tool_call_chunk", delta='{"param1": "value1", '),
        llm.ToolCallChunk(type="tool_call_chunk", delta='"param2": 42}'),
        llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
    ]


def check_stream_response_consistency(
    response: llm.StreamResponse[llm.Stream | llm.AsyncStream],
    chunks: Sequence[llm.AssistantContentChunk],
    content: Sequence[llm.AssistantContentPart],
) -> None:
    assert response.chunks == chunks, "response.chunks"
    assert response.content == content, "response.content"
    assert response.texts == [part for part in content if part.type == "text"], (
        "response.texts"
    )
    assert response.thinkings == [
        part for part in content if part.type == "thinking"
    ], "response.thinkings"
    assert response.tool_calls == [
        part for part in content if part.type == "tool_call"
    ], "response.tool_calls"
    assistant_message = response.messages[-1]
    assert assistant_message.role == "assistant", "assistant_message.role"
    assert assistant_message.content == content, "assistant_message.content"


def test_sync_initialization(
    example_text_chunks: list[llm.AssistantContentChunk],
) -> None:
    """Test llm.StreamResponse initialization with sync iterator."""
    stream_response = create_sync_stream_response(example_text_chunks)

    assert stream_response.provider == "openai"
    assert stream_response.model == "gpt-4o-mini"
    assert stream_response.finish_reason is None
    assert isinstance(stream_response._chunk_iterator, Iterator)
    assert stream_response._current_content is None
    assert not stream_response.consumed
    check_stream_response_consistency(stream_response, [], [])


@pytest.mark.asyncio
async def test_async_initialization(
    example_text_chunks: list[llm.AssistantContentChunk],
) -> None:
    """Test llm.StreamResponse initialization with async iterator."""
    stream_response = create_async_stream_response(example_text_chunks)

    assert stream_response.provider == "openai"
    assert stream_response.model == "gpt-4o-mini"
    assert stream_response.finish_reason is None
    assert isinstance(stream_response._chunk_iterator, AsyncIterator)
    assert stream_response._current_content is None
    assert not stream_response.consumed
    check_stream_response_consistency(stream_response, [], [])


class TestChunkStream:
    """Test chunk streaming mechanics for both sync and async."""

    def test_sync_basic_streaming(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_thinking_chunks: list[llm.AssistantContentChunk],
        example_tool_call_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
        example_thinking: llm.Thinking,
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test streaming mixed chunk types with sync response."""
        chunks = [
            *example_text_chunks,
            *example_thinking_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_sync_stream_response(chunks)

        streamed_chunks = list(stream_response.chunk_stream())

        check_stream_response_consistency(
            stream_response, chunks, [example_text, example_thinking, example_tool_call]
        )
        assert len(streamed_chunks) == 13  # 5 text + 4 thinking + 4 tool_call
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_basic_streaming(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_thinking_chunks: list[llm.AssistantContentChunk],
        example_tool_call_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
        example_thinking: llm.Thinking,
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test streaming mixed chunk types with async response."""
        chunks = [
            *example_text_chunks,
            *example_thinking_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_async_stream_response(chunks)

        streamed_chunks = [
            chunk async for chunk in await stream_response.chunk_stream()
        ]

        check_stream_response_consistency(
            stream_response, chunks, [example_text, example_thinking, example_tool_call]
        )
        assert len(streamed_chunks) == 13  # 5 text + 4 thinking + 4 tool_call
        assert stream_response.consumed is True

    def test_sync_replay_functionality(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that streaming can be replayed from cache with sync response."""
        stream_response = create_sync_stream_response(example_text_chunks)

        first_stream = list(stream_response.chunk_stream())
        second_stream = list(stream_response.chunk_stream())

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert first_stream == example_text_chunks
        assert second_stream == example_text_chunks
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_replay_functionality(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that streaming can be replayed from cache with async response."""
        stream_response = create_async_stream_response(example_text_chunks)

        first_stream = [chunk async for chunk in await stream_response.chunk_stream()]
        second_stream = [chunk async for chunk in await stream_response.chunk_stream()]

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert first_stream == example_text_chunks
        assert second_stream == example_text_chunks
        assert stream_response.consumed is True

    def test_sync_partial_iteration_and_resume(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test breaking iteration and resuming from cached state with sync response."""
        stream_response = create_sync_stream_response(example_text_chunks)

        # Partial iteration stopping early
        chunk_stream = stream_response.chunk_stream()
        partial_chunks = []
        for chunk in chunk_stream:
            partial_chunks.append(chunk)
            break

        check_stream_response_consistency(
            stream_response, partial_chunks, [llm.Text(text="")]
        )
        assert stream_response.consumed is False

        # Resume iteration from the same iterator
        for chunk in chunk_stream:
            partial_chunks.append(chunk)

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert stream_response.consumed is True
        assert partial_chunks == example_text_chunks

    @pytest.mark.asyncio
    async def test_async_partial_iteration_and_resume(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test breaking iteration and resuming from cached state with async response."""
        stream_response = create_async_stream_response(example_text_chunks)

        # Partial iteration stopping early
        chunk_stream = await stream_response.chunk_stream()
        partial_chunks = []
        async for chunk in chunk_stream:
            partial_chunks.append(chunk)
            break

        check_stream_response_consistency(
            stream_response, partial_chunks, [llm.Text(text="")]
        )
        assert stream_response.consumed is False

        # Resume iteration from the same iterator
        async for chunk in chunk_stream:
            partial_chunks.append(chunk)

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert stream_response.consumed is True
        assert partial_chunks == example_text_chunks

    def test_sync_partial_iteration_and_restart(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test breaking iteration and restarting with sync response."""
        stream_response = create_sync_stream_response(example_text_chunks)

        # Partial iteration stopping early
        chunk_stream = stream_response.chunk_stream()
        partial_chunks = []
        for i, chunk in enumerate(chunk_stream):
            partial_chunks.append(chunk)
            if i == 2:
                break

        check_stream_response_consistency(
            stream_response, partial_chunks, [llm.Text(text="Hello ")]
        )
        assert stream_response.consumed is False

        # Restart iteration from the beginning
        chunks = list(stream_response.chunk_stream())
        assert chunks[:3] == partial_chunks

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_partial_iteration_and_restart(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test breaking iteration and restarting with async response."""
        stream_response = create_async_stream_response(example_text_chunks)

        # Partial iteration stopping early
        chunk_stream = await stream_response.chunk_stream()
        partial_chunks = []
        i = 0
        async for chunk in chunk_stream:
            partial_chunks.append(chunk)
            i += 1
            if i == 2:
                break

        check_stream_response_consistency(
            stream_response, partial_chunks, [llm.Text(text="Hello")]
        )
        assert stream_response.consumed is False

        # Restart iteration from the beginning
        chunks = [chunk async for chunk in await stream_response.chunk_stream()]
        assert chunks[:2] == partial_chunks

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert stream_response.consumed is True


@dataclass
class ChunkProcessingTestCase:
    chunks: list[llm.AssistantContentChunk]
    expected_contents: list[list[llm.AssistantContentPart]]


CHUNK_PROCESSING_TEST_CASES: dict[str, ChunkProcessingTestCase] = {
    "empty_text": ChunkProcessingTestCase(
        chunks=[
            llm.TextStartChunk(type="text_start_chunk"),
            llm.TextEndChunk(type="text_end_chunk"),
        ],
        expected_contents=[[llm.Text(text="")], [llm.Text(text="")]],
    ),
    "text_with_deltas": ChunkProcessingTestCase(
        chunks=[
            llm.TextStartChunk(type="text_start_chunk"),
            llm.TextChunk(type="text_chunk", delta="Hello"),
            llm.TextChunk(type="text_chunk", delta=" world"),
            llm.TextEndChunk(type="text_end_chunk"),
        ],
        expected_contents=[
            [llm.Text(text="")],
            [llm.Text(text="Hello")],
            [llm.Text(text="Hello world")],
            [llm.Text(text="Hello world")],
        ],
    ),
    "empty_thinking": ChunkProcessingTestCase(
        chunks=[
            llm.ThinkingStartChunk(type="thinking_start_chunk"),
            llm.ThinkingEndChunk(type="thinking_end_chunk", signature="thoughts"),
        ],
        expected_contents=[[], [llm.Thinking(thinking="", signature="thoughts")]],
    ),
    "thinking_with_deltas": ChunkProcessingTestCase(
        chunks=[
            llm.ThinkingStartChunk(type="thinking_start_chunk"),
            llm.ThinkingChunk(type="thinking_chunk", delta="Let me"),
            llm.ThinkingChunk(type="thinking_chunk", delta=" think..."),
            llm.ThinkingEndChunk(type="thinking_end_chunk", signature="reasoning"),
        ],
        expected_contents=[
            [],
            [],
            [],
            [llm.Thinking(thinking="Let me think...", signature="reasoning")],
        ],
    ),
    "empty_tool_call": ChunkProcessingTestCase(
        chunks=[
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="tool_123",
                name="empty_function",
            ),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
        ],
        expected_contents=[
            [],
            [llm.ToolCall(id="tool_123", name="empty_function", args="{}")],
        ],
    ),
    "tool_call_with_args": ChunkProcessingTestCase(
        chunks=[
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="tool_456",
                name="test_function",
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"key": '),
            llm.ToolCallChunk(type="tool_call_chunk", delta='"value"}'),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
        ],
        expected_contents=[
            [],
            [],
            [],
            [
                llm.ToolCall(
                    id="tool_456", name="test_function", args='{"key": "value"}'
                )
            ],
        ],
    ),
}


class TestToolCallSupport:
    """Test tool call specific functionality."""

    def test_sync_tool_call_streaming(
        self,
        example_tool_call_chunks: list[llm.AssistantContentChunk],
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test tool call streaming functionality with sync response."""
        stream_response = create_sync_stream_response(example_tool_call_chunks)

        streamed_chunks = list(stream_response.chunk_stream())

        check_stream_response_consistency(
            stream_response, example_tool_call_chunks, [example_tool_call]
        )
        assert len(streamed_chunks) == 4  # start + 2 deltas + end
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_tool_call_streaming(
        self,
        example_tool_call_chunks: list[llm.AssistantContentChunk],
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test tool call streaming functionality with async response."""
        stream_response = create_async_stream_response(example_tool_call_chunks)

        streamed_chunks = [
            chunk async for chunk in await stream_response.chunk_stream()
        ]

        check_stream_response_consistency(
            stream_response, example_tool_call_chunks, [example_tool_call]
        )
        assert len(streamed_chunks) == 4  # start + 2 deltas + end
        assert stream_response.consumed is True

    def test_sync_tool_call_partial_json_accumulation(self) -> None:
        """Test that partial JSON arguments are correctly accumulated."""
        chunks = [
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="tool_complex",
                name="complex_function",
            ),
            llm.ToolCallChunk(type="tool_call_chunk", delta='{"nested":'),
            llm.ToolCallChunk(type="tool_call_chunk", delta=' {"key": "value"},'),
            llm.ToolCallChunk(type="tool_call_chunk", delta=' "array": [1, 2, 3]}'),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
        ]

        stream_response = create_sync_stream_response(chunks)

        list(stream_response.chunk_stream())

        assert len(stream_response.tool_calls) == 1
        tool_call = stream_response.tool_calls[0]
        assert tool_call.id == "tool_complex"
        assert tool_call.name == "complex_function"
        assert tool_call.args == '{"nested": {"key": "value"}, "array": [1, 2, 3]}'


class ChunkProcessingFixtureRequest(pytest.FixtureRequest):
    param: ChunkProcessingTestCase
    """The chunk processing test case."""


@pytest.fixture(
    params=list(CHUNK_PROCESSING_TEST_CASES.values()),
    ids=list(CHUNK_PROCESSING_TEST_CASES.keys()),
)
def chunk_processing_test_case(
    request: ChunkProcessingFixtureRequest,
) -> ChunkProcessingTestCase:
    return request.param


class TestChunkProcessing:
    """Test chunk processing with various content types and states."""

    def test_sync_chunk_processing(
        self, chunk_processing_test_case: ChunkProcessingTestCase
    ) -> None:
        chunks = chunk_processing_test_case.chunks
        stream_response = create_sync_stream_response(chunks)
        stream = stream_response.chunk_stream()
        check_stream_response_consistency(stream_response, [], [])
        for i, expected_content in enumerate(
            chunk_processing_test_case.expected_contents
        ):
            next(stream)
            check_stream_response_consistency(
                stream_response, chunks[: i + 1], expected_content
            )

    @pytest.mark.asyncio
    async def test_async_chunk_processing(
        self, chunk_processing_test_case: ChunkProcessingTestCase
    ) -> None:
        chunks = chunk_processing_test_case.chunks
        stream_response = create_async_stream_response(chunks)
        stream = await stream_response.chunk_stream()
        check_stream_response_consistency(stream_response, [], [])
        for i, expected_content in enumerate(
            chunk_processing_test_case.expected_contents
        ):
            await anext(stream)
            check_stream_response_consistency(
                stream_response, chunks[: i + 1], expected_content
            )

    def test_sync_finish_reason_chunk_processing(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that FinishReasonChunk sets the finish_reason on the response with sync response."""
        chunks = [
            *example_text_chunks,
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
        ]
        stream_response = create_sync_stream_response(chunks)

        assert stream_response.finish_reason is None

        streamed_chunks = list(stream_response.chunk_stream())

        assert stream_response.finish_reason == llm.FinishReason.END_TURN
        check_stream_response_consistency(stream_response, chunks, [example_text])
        assert len(streamed_chunks) == 6  # 5 text chunks + 1 finish reason chunk
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_finish_reason_chunk_processing(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that FinishReasonChunk sets the finish_reason on the response with async response."""
        chunks = [
            *example_text_chunks,
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
        ]
        stream_response = create_async_stream_response(chunks)

        assert stream_response.finish_reason is None

        streamed_chunks = [
            chunk async for chunk in await stream_response.chunk_stream()
        ]

        assert stream_response.finish_reason == llm.FinishReason.END_TURN
        check_stream_response_consistency(stream_response, chunks, [example_text])
        assert len(streamed_chunks) == 6  # 5 text chunks + 1 finish reason chunk
        assert stream_response.consumed is True

    def test_sync_response_consumed(self) -> None:
        """Test that response.consumed is set when the iterator is exhausted with sync response."""
        stream_response = create_sync_stream_response(
            [llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN)]
        )
        chunk_stream = stream_response.chunk_stream()

        assert stream_response.finish_reason is None
        assert stream_response.consumed is False

        next(chunk_stream)
        assert stream_response.finish_reason == llm.FinishReason.END_TURN
        assert stream_response.consumed is False

        with pytest.raises(StopIteration):
            next(chunk_stream)
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_response_consumed(self) -> None:
        """Test that response.consumed is set when the iterator is exhausted with async response."""
        stream_response = create_async_stream_response(
            [llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN)]
        )
        chunk_stream = await stream_response.chunk_stream()

        assert stream_response.finish_reason is None
        assert stream_response.consumed is False

        await anext(chunk_stream)
        assert stream_response.finish_reason == llm.FinishReason.END_TURN
        assert stream_response.consumed is False

        with pytest.raises(StopAsyncIteration):
            await anext(chunk_stream)
        assert stream_response.consumed is True


@dataclass
class InvalidChunkSequenceTestCase:
    chunks: list[llm.AssistantContentChunk]
    expected_error: str


INVALID_CHUNK_SEQUENCE_TEST_CASES: dict[str, InvalidChunkSequenceTestCase] = {
    "text_chunk_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.TextChunk(type="text_chunk", delta="Hello")],
        expected_error="Received text_chunk while not processing text",
    ),
    "text_end_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.TextEndChunk(type="text_end_chunk")],
        expected_error="Received text_end_chunk while not processing text",
    ),
    "thinking_chunk_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.ThinkingChunk(type="thinking_chunk", delta="Hello")],
        expected_error="Received thinking_chunk while not processing thinking",
    ),
    "thinking_end_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.ThinkingEndChunk(type="thinking_end_chunk", signature=None)],
        expected_error="Received thinking_end_chunk while not processing thinking",
    ),
    "overlapping_text_then_thinking": InvalidChunkSequenceTestCase(
        chunks=[
            llm.TextStartChunk(type="text_start_chunk"),
            llm.ThinkingStartChunk(type="thinking_start_chunk"),
        ],
        expected_error="while processing another chunk",
    ),
    "overlapping_thinking_then_text": InvalidChunkSequenceTestCase(
        chunks=[
            llm.ThinkingStartChunk(type="thinking_start_chunk"),
            llm.TextStartChunk(type="text_start_chunk"),
        ],
        expected_error="while processing another chunk",
    ),
    "text_end_without_matching_start": InvalidChunkSequenceTestCase(
        chunks=[
            llm.ThinkingStartChunk(type="thinking_start_chunk"),
            llm.ThinkingChunk(type="thinking_chunk", delta="test"),
            llm.TextEndChunk(type="text_end_chunk"),
        ],
        expected_error="Received text_end_chunk while not processing text",
    ),
    "thinking_end_without_matching_start": InvalidChunkSequenceTestCase(
        chunks=[
            llm.TextStartChunk(type="text_start_chunk"),
            llm.TextChunk(type="text_chunk", delta="test"),
            llm.ThinkingEndChunk(type="thinking_end_chunk", signature=None),
        ],
        expected_error="Received thinking_end_chunk while not processing thinking",
    ),
    "tool_call_chunk_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.ToolCallChunk(type="tool_call_chunk", delta='{"test": "value"}')],
        expected_error="Received tool_call_chunk while not processing tool call",
    ),
    "tool_call_end_without_start": InvalidChunkSequenceTestCase(
        chunks=[
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call")
        ],
        expected_error="Received tool_call_end_chunk while not processing tool call",
    ),
    "overlapping_text_then_tool_call": InvalidChunkSequenceTestCase(
        chunks=[
            llm.TextStartChunk(type="text_start_chunk"),
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="tool_123",
                name="test_function",
            ),
        ],
        expected_error="while processing another chunk",
    ),
    "overlapping_tool_call_then_text": InvalidChunkSequenceTestCase(
        chunks=[
            llm.ToolCallStartChunk(
                type="tool_call_start_chunk",
                id="tool_123",
                name="test_function",
            ),
            llm.TextStartChunk(type="text_start_chunk"),
        ],
        expected_error="while processing another chunk",
    ),
    "tool_call_end_without_matching_start": InvalidChunkSequenceTestCase(
        chunks=[
            llm.TextStartChunk(type="text_start_chunk"),
            llm.TextChunk(type="text_chunk", delta="test"),
            llm.ToolCallEndChunk(type="tool_call_end_chunk", content_type="tool_call"),
        ],
        expected_error="Received tool_call_end_chunk while not processing tool call",
    ),
}


class InvalidChunkSequenceFixtureRequest(pytest.FixtureRequest):
    param: InvalidChunkSequenceTestCase
    """The invalid chunk sequence test case."""


@pytest.fixture(
    params=list(INVALID_CHUNK_SEQUENCE_TEST_CASES.values()),
    ids=list(INVALID_CHUNK_SEQUENCE_TEST_CASES.keys()),
)
def invalid_chunk_sequence_test_case(
    request: InvalidChunkSequenceFixtureRequest,
) -> InvalidChunkSequenceTestCase:
    return request.param


class TestErrorHandling:
    """Test error handling in chunk processing."""

    def test_sync_invalid_chunk_sequence(
        self, invalid_chunk_sequence_test_case: InvalidChunkSequenceTestCase
    ) -> None:
        """Test error handling for invalid chunk sequences with sync response."""
        stream_response = create_sync_stream_response(
            invalid_chunk_sequence_test_case.chunks
        )

        with pytest.raises(
            RuntimeError, match=invalid_chunk_sequence_test_case.expected_error
        ):
            list(stream_response.chunk_stream())

    @pytest.mark.asyncio
    async def test_async_invalid_chunk_sequence(
        self, invalid_chunk_sequence_test_case: InvalidChunkSequenceTestCase
    ) -> None:
        """Test error handling for invalid chunk sequences with async response."""
        stream_response = create_async_stream_response(
            invalid_chunk_sequence_test_case.chunks
        )

        with pytest.raises(
            RuntimeError, match=invalid_chunk_sequence_test_case.expected_error
        ):
            [chunk async for chunk in await stream_response.chunk_stream()]

    def test_sync_chunks_after_finish_reason(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_thinking_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that chunks after finish reason raise RuntimeError with sync response."""
        chunks = [
            *example_text_chunks,
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
            *example_thinking_chunks,
        ]
        stream_response = create_sync_stream_response(chunks)

        with pytest.raises(RuntimeError):
            list(stream_response.chunk_stream())

        assert stream_response.finish_reason == llm.FinishReason.END_TURN
        check_stream_response_consistency(stream_response, chunks[:6], [example_text])

    @pytest.mark.asyncio
    async def test_async_chunks_after_finish_reason(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_thinking_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that chunks after finish reason raise RuntimeError with async response."""
        chunks = [
            *example_text_chunks,
            llm.FinishReasonChunk(finish_reason=llm.FinishReason.END_TURN),
            *example_thinking_chunks,
        ]
        stream_response = create_async_stream_response(chunks)

        with pytest.raises(RuntimeError):
            [chunk async for chunk in await stream_response.chunk_stream()]

        assert stream_response.finish_reason == llm.FinishReason.END_TURN
        check_stream_response_consistency(stream_response, chunks[:6], [example_text])


class TestRawChunkTracking:
    """Test chunk deduplication behavior."""

    def test_sync_raw_chunks_collection(self) -> None:
        """Test that raw chunks are collected."""
        raw1 = {"info": "a"}
        raw2 = {"info": "b"}
        chunk1 = llm.TextStartChunk(type="text_start_chunk", content_type="text")
        chunk2 = llm.TextChunk(type="text_chunk", content_type="text", delta="hi")
        chunk3 = llm.TextEndChunk(type="text_end_chunk", content_type="text")

        def chunk_iterator() -> llm.ChunkIterator:
            yield llm.responses.RawChunk(raw=raw1)
            yield chunk1
            yield chunk2
            yield llm.responses.RawChunk(raw=raw2)
            yield chunk3

        stream_response = llm.StreamResponse(
            provider="openai",
            model="gpt-4o-mini",
            input_messages=[llm.messages.user("Test")],
            chunk_iterator=chunk_iterator(),
        )

        for _ in stream_response.chunk_stream():
            ...

        check_stream_response_consistency(
            stream_response, [chunk1, chunk2, chunk3], [llm.Text(text="hi")]
        )
        assert stream_response.raw == [raw1, raw2]

    @pytest.mark.asyncio
    async def test_async_chunk_deduplication_with_same_raw(self) -> None:
        raw1 = {"info": "a"}
        raw2 = {"info": "b"}
        chunk1 = llm.TextStartChunk(type="text_start_chunk", content_type="text")
        chunk2 = llm.TextChunk(type="text_chunk", content_type="text", delta="hi")
        chunk3 = llm.TextEndChunk(type="text_end_chunk", content_type="text")

        async def chunk_iterator() -> llm.AsyncChunkIterator:
            yield llm.responses.RawChunk(raw=raw1)
            yield chunk1
            yield chunk2
            yield llm.responses.RawChunk(raw=raw2)
            yield chunk3

        stream_response = llm.StreamResponse[llm.AsyncStream](
            provider="openai",
            model="gpt-4o-mini",
            input_messages=[llm.messages.user("Test")],
            chunk_iterator=chunk_iterator(),
        )

        async for _ in await stream_response.chunk_stream():
            ...

        check_stream_response_consistency(
            stream_response, [chunk1, chunk2, chunk3], [llm.Text(text="hi")]
        )
        assert stream_response.raw == [raw1, raw2]
