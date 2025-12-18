"""Tests for llm.StreamResponse class."""

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

import pytest
from inline_snapshot import snapshot

from mirascope import llm
from mirascope.llm.tools import FORMAT_TOOL_NAME


def create_sync_stream_response(
    chunks: Sequence[llm.StreamResponseChunk],
) -> llm.StreamResponse:
    """Create a llm.StreamResponse with a functioning iterator for testing."""

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
    )
    return response


def create_async_stream_response(
    chunks: Sequence[llm.StreamResponseChunk],
) -> llm.AsyncStreamResponse:
    """Create a llm.StreamResponse with a functioning iterator for testing."""

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
    )
    return response


@pytest.fixture
def example_text() -> llm.Text:
    return llm.Text(text="Hello world")


@pytest.fixture
def example_thought() -> llm.Thought:
    return llm.Thought(thought="Let me think...\nThis is interesting!")


@pytest.fixture
def example_tool_call() -> llm.ToolCall:
    return llm.ToolCall(
        id="tool_call_123",
        name="test_function",
        args='{"param1": "value1", "param2": 42}',
    )


@pytest.fixture
def example_text_chunks() -> Sequence[llm.StreamResponseChunk]:
    """Create a complete text chunk sequence for testing."""
    return [
        llm.TextStartChunk(),
        llm.TextChunk(delta="Hello"),
        llm.TextChunk(delta=" "),
        llm.TextChunk(delta="world"),
        llm.TextEndChunk(),
    ]


@pytest.fixture
def example_thought_chunks() -> Sequence[llm.StreamResponseChunk]:
    """Create a complete thought chunk sequence for testing."""
    return [
        llm.ThoughtStartChunk(),
        llm.ThoughtChunk(delta="Let me think..."),
        llm.ThoughtChunk(delta="\nThis is interesting!"),
        llm.ThoughtEndChunk(),
    ]


@pytest.fixture
def example_tool_call_chunks() -> Sequence[llm.StreamResponseChunk]:
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
    response: llm.StreamResponse | llm.AsyncStreamResponse,
    chunks: Sequence[llm.StreamResponseChunk],
    content: Sequence[llm.AssistantContentPart],
) -> None:
    assert response.chunks == [c for c in chunks if c.type != "finish_reason_chunk"], (
        "response.chunks"
    )
    assert response.content == content, "response.content"
    assert response.texts == [part for part in content if part.type == "text"], (
        "response.texts"
    )
    assert response.thoughts == [part for part in content if part.type == "thought"], (
        "response.thoughts"
    )
    assert response.tool_calls == [
        part for part in content if part.type == "tool_call"
    ], "response.tool_calls"
    assistant_message = response.messages[-1]
    assert assistant_message.role == "assistant", "assistant_message.role"
    assert assistant_message.content == content, "assistant_message.content"


def test_sync_initialization(
    example_text_chunks: Sequence[llm.StreamResponseChunk],
) -> None:
    """Test llm.StreamResponse initialization with sync iterator."""
    stream_response = create_sync_stream_response(example_text_chunks)

    assert stream_response.provider_id == "openai"
    assert stream_response.model_id == "openai/gpt-5-mini"
    assert stream_response.toolkit == llm.Toolkit(tools=[])
    assert stream_response.finish_reason is None
    assert not stream_response.consumed
    check_stream_response_consistency(stream_response, [], [])


@pytest.mark.asyncio
async def test_async_initialization(
    example_text_chunks: Sequence[llm.StreamResponseChunk],
) -> None:
    """Test llm.StreamResponse initialization with async iterator."""
    stream_response = create_async_stream_response(example_text_chunks)

    assert stream_response.provider_id == "openai"
    assert stream_response.model_id == "openai/gpt-5-mini"
    assert stream_response.toolkit == llm.AsyncToolkit(tools=[])
    assert stream_response.finish_reason is None
    assert not stream_response.consumed
    check_stream_response_consistency(stream_response, [], [])


class TestChunkStream:
    """Test chunk streaming mechanics for both sync and async."""

    def test_sync_basic_streaming(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
        example_thought: llm.Thought,
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test streaming mixed chunk types with sync response."""
        chunks = [
            *example_text_chunks,
            *example_thought_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_sync_stream_response(chunks)

        stream_response.finish()

        check_stream_response_consistency(
            stream_response,
            chunks,
            [
                example_text,
                example_thought,
                example_tool_call,
            ],
        )
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_basic_streaming(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
        example_thought: llm.Thought,
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test streaming mixed chunk types with async response."""
        chunks = [
            *example_text_chunks,
            *example_thought_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_async_stream_response(chunks)

        await stream_response.finish()

        check_stream_response_consistency(
            stream_response,
            chunks,
            [
                example_text,
                example_thought,
                example_tool_call,
            ],
        )
        assert stream_response.consumed is True

    def test_sync_replay_functionality(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
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
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that streaming can be replayed from cache with async response."""
        stream_response = create_async_stream_response(example_text_chunks)

        first_stream = [chunk async for chunk in stream_response.chunk_stream()]
        second_stream = [chunk async for chunk in stream_response.chunk_stream()]

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert first_stream == example_text_chunks
        assert second_stream == example_text_chunks
        assert stream_response.consumed is True

    def test_sync_partial_iteration_and_resume(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
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
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test breaking iteration and resuming from cached state with async response."""
        stream_response = create_async_stream_response(example_text_chunks)

        # Partial iteration stopping early
        chunk_stream = stream_response.chunk_stream()
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
        example_text_chunks: Sequence[llm.StreamResponseChunk],
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
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test breaking iteration and restarting with async response."""
        stream_response = create_async_stream_response(example_text_chunks)

        # Partial iteration stopping early
        chunk_stream = stream_response.chunk_stream()
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
        chunks = [chunk async for chunk in stream_response.chunk_stream()]
        assert chunks[:2] == partial_chunks

        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert stream_response.consumed is True


@dataclass
class ChunkProcessingTestCase:
    chunks: Sequence[llm.StreamResponseChunk]
    expected_contents: Sequence[Sequence[llm.AssistantContentPart]]


CHUNK_PROCESSING_TEST_CASES: dict[str, ChunkProcessingTestCase] = {
    "empty_text": ChunkProcessingTestCase(
        chunks=[
            llm.TextStartChunk(),
            llm.TextEndChunk(),
        ],
        expected_contents=[[llm.Text(text="")], [llm.Text(text="")]],
    ),
    "text_with_deltas": ChunkProcessingTestCase(
        chunks=[
            llm.TextStartChunk(),
            llm.TextChunk(delta="Hello"),
            llm.TextChunk(delta=" world"),
            llm.TextEndChunk(),
        ],
        expected_contents=[
            [llm.Text(text="")],
            [llm.Text(text="Hello")],
            [llm.Text(text="Hello world")],
            [llm.Text(text="Hello world")],
        ],
    ),
    "empty_thought": ChunkProcessingTestCase(
        chunks=[
            llm.ThoughtStartChunk(content_type="thought"),
            llm.ThoughtEndChunk(content_type="thought"),
        ],
        expected_contents=[[llm.Thought(thought="")], [llm.Thought(thought="")]],
    ),
    "thought_with_deltas": ChunkProcessingTestCase(
        chunks=[
            llm.ThoughtStartChunk(content_type="thought"),
            llm.ThoughtChunk(content_type="thought", delta="Let me"),
            llm.ThoughtChunk(content_type="thought", delta=" think..."),
            llm.ThoughtEndChunk(content_type="thought"),
        ],
        expected_contents=[
            [llm.Thought(thought="")],
            [llm.Thought(thought="Let me")],
            [llm.Thought(thought="Let me think...")],
            [llm.Thought(thought="Let me think...")],
        ],
    ),
    "empty_tool_call": ChunkProcessingTestCase(
        chunks=[
            llm.ToolCallStartChunk(
                id="tool_123",
                name="empty_function",
            ),
            llm.ToolCallEndChunk(),
        ],
        expected_contents=[
            [],
            [llm.ToolCall(id="tool_123", name="empty_function", args="{}")],
        ],
    ),
    "tool_call_with_args": ChunkProcessingTestCase(
        chunks=[
            llm.ToolCallStartChunk(
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
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
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
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test tool call streaming functionality with async response."""
        stream_response = create_async_stream_response(example_tool_call_chunks)

        streamed_chunks = [chunk async for chunk in stream_response.chunk_stream()]

        check_stream_response_consistency(
            stream_response, example_tool_call_chunks, [example_tool_call]
        )
        assert len(streamed_chunks) == 4  # start + 2 deltas + end
        assert stream_response.consumed is True

    def test_sync_tool_call_partial_json_accumulation(self) -> None:
        """Test that partial JSON arguments are correctly accumulated."""
        chunks = [
            llm.ToolCallStartChunk(
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
        stream = stream_response.chunk_stream()
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
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that FinishReasonChunk sets the finish_reason on the response with sync response."""
        stream_response = create_sync_stream_response(example_text_chunks)

        assert stream_response.finish_reason is None

        streamed_chunks = list(stream_response.chunk_stream())

        assert stream_response.finish_reason is None
        check_stream_response_consistency(
            stream_response, example_text_chunks, [example_text]
        )
        assert len(streamed_chunks) == 5  # All the text chunks
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_finish_reason_chunk_processing(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that FinishReasonChunk sets the finish_reason on the response with async response."""
        chunks = example_text_chunks
        stream_response = create_async_stream_response(chunks)

        assert stream_response.finish_reason is None

        streamed_chunks = [chunk async for chunk in stream_response.chunk_stream()]

        assert stream_response.finish_reason is None
        check_stream_response_consistency(stream_response, chunks, [example_text])
        assert len(streamed_chunks) == 5  # all the text chunks
        assert stream_response.consumed is True

    def test_sync_response_consumed(self) -> None:
        """Test that response.consumed is set when the iterator is exhausted with sync response."""
        stream_response = create_sync_stream_response([])
        chunk_stream = stream_response.chunk_stream()

        assert stream_response.finish_reason is None
        assert stream_response.consumed is False

        with pytest.raises(StopIteration):
            next(chunk_stream)
        assert stream_response.finish_reason is None
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_response_consumed(self) -> None:
        """Test that response.consumed is set when the iterator is exhausted with async response."""
        stream_response = create_async_stream_response([])
        chunk_stream = stream_response.chunk_stream()

        assert stream_response.finish_reason is None
        assert stream_response.consumed is False

        with pytest.raises(StopAsyncIteration):
            await anext(chunk_stream)
        assert stream_response.finish_reason is None
        assert stream_response.consumed is True


@dataclass
class InvalidChunkSequenceTestCase:
    chunks: Sequence[llm.StreamResponseChunk]
    expected_error: str


INVALID_CHUNK_SEQUENCE_TEST_CASES: dict[str, InvalidChunkSequenceTestCase] = {
    "text_chunk_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.TextChunk(delta="Hello")],
        expected_error="Received text_chunk while not processing text",
    ),
    "text_end_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.TextEndChunk()],
        expected_error="Received text_end_chunk while not processing text",
    ),
    "thought_chunk_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.ThoughtChunk(content_type="thought", delta="Hello")],
        expected_error="Received thought_chunk while not processing thought",
    ),
    "thought_end_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.ThoughtEndChunk(content_type="thought")],
        expected_error="Received thought_end_chunk while not processing thought",
    ),
    "overlapping_text_then_thought": InvalidChunkSequenceTestCase(
        chunks=[
            llm.TextStartChunk(content_type="text"),
            llm.ThoughtStartChunk(content_type="thought"),
        ],
        expected_error="while processing another chunk",
    ),
    "overlapping_thought_then_text": InvalidChunkSequenceTestCase(
        chunks=[
            llm.ThoughtStartChunk(content_type="thought"),
            llm.TextStartChunk(content_type="text"),
        ],
        expected_error="while processing another chunk",
    ),
    "text_end_without_matching_start": InvalidChunkSequenceTestCase(
        chunks=[
            llm.ThoughtStartChunk(content_type="thought"),
            llm.ThoughtChunk(content_type="thought", delta="test"),
            llm.TextEndChunk(content_type="text"),
        ],
        expected_error="Received text_end_chunk while not processing text",
    ),
    "thought_end_without_matching_start": InvalidChunkSequenceTestCase(
        chunks=[
            llm.TextStartChunk(content_type="text"),
            llm.TextChunk(content_type="text", delta="test"),
            llm.ThoughtEndChunk(content_type="thought"),
        ],
        expected_error="Received thought_end_chunk while not processing thought",
    ),
    "tool_call_chunk_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.ToolCallChunk(delta='{"test": "value"}')],
        expected_error="Received tool_call_chunk while not processing tool call",
    ),
    "tool_call_end_without_start": InvalidChunkSequenceTestCase(
        chunks=[llm.ToolCallEndChunk()],
        expected_error="Received tool_call_end_chunk while not processing tool call",
    ),
    "overlapping_text_then_tool_call": InvalidChunkSequenceTestCase(
        chunks=[
            llm.TextStartChunk(),
            llm.ToolCallStartChunk(
                id="tool_123",
                name="test_function",
            ),
        ],
        expected_error="while processing another chunk",
    ),
    "overlapping_tool_call_then_text": InvalidChunkSequenceTestCase(
        chunks=[
            llm.ToolCallStartChunk(
                id="tool_123",
                name="test_function",
            ),
            llm.TextStartChunk(),
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
            [chunk async for chunk in stream_response.chunk_stream()]

    def test_sync_chunks_after_finish_reason(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that chunks after finish reason raise RuntimeError with sync response."""
        chunks = [
            *example_text_chunks,
            llm.responses.FinishReasonChunk(finish_reason=llm.FinishReason.REFUSAL),
            *example_thought_chunks,
        ]
        stream_response = create_sync_stream_response(chunks)

        with pytest.raises(RuntimeError):
            list(stream_response.chunk_stream())

        assert stream_response.finish_reason is llm.FinishReason.REFUSAL
        check_stream_response_consistency(stream_response, chunks[:6], [example_text])

    @pytest.mark.asyncio
    async def test_async_chunks_after_finish_reason(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that chunks after finish reason raise RuntimeError with async response."""
        chunks = [
            *example_text_chunks,
            llm.responses.FinishReasonChunk(finish_reason=llm.FinishReason.REFUSAL),
            *example_thought_chunks,
        ]
        stream_response = create_async_stream_response(chunks)

        with pytest.raises(RuntimeError):
            [chunk async for chunk in stream_response.chunk_stream()]

        assert stream_response.finish_reason is llm.FinishReason.REFUSAL
        check_stream_response_consistency(stream_response, chunks[:6], [example_text])


class TestPrettyStream:
    def test_sync_pretty_stream_text_only(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        stream_response = create_sync_stream_response(example_text_chunks)

        streamed_output = "".join(stream_response.pretty_stream())

        assert streamed_output == snapshot("Hello world")
        assert streamed_output == stream_response.pretty()

    @pytest.mark.asyncio
    async def test_async_pretty_stream_text_only(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        stream_response = create_async_stream_response(example_text_chunks)

        streamed_output = "".join(
            [part async for part in stream_response.pretty_stream()]
        )

        assert streamed_output == snapshot("Hello world")
        assert streamed_output == stream_response.pretty()

    def test_sync_pretty_stream_mixed_content(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        chunks = [
            *example_text_chunks,
            *example_thought_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_sync_stream_response(chunks)

        streamed_output = "".join(stream_response.pretty_stream())

        assert streamed_output == snapshot(
            """\
Hello world

**Thinking:**
  Let me think...
  This is interesting!

**ToolCall (test_function):** {"param1": "value1", "param2": 42}\
"""
        )
        assert streamed_output == stream_response.pretty()

    @pytest.mark.asyncio
    async def test_async_pretty_stream_mixed_content(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        chunks = [
            *example_text_chunks,
            *example_thought_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_async_stream_response(chunks)

        streamed_output = "".join(
            [part async for part in stream_response.pretty_stream()]
        )

        assert streamed_output == snapshot(
            """\
Hello world

**Thinking:**
  Let me think...
  This is interesting!

**ToolCall (test_function):** {"param1": "value1", "param2": 42}\
"""
        )
        assert streamed_output == stream_response.pretty()

    def test_sync_pretty_stream_empty_response(self) -> None:
        stream_response = create_sync_stream_response([])

        streamed_output = "".join(stream_response.pretty_stream())

        assert streamed_output == snapshot("**[No Content]**")
        assert streamed_output == stream_response.pretty()

    @pytest.mark.asyncio
    async def test_async_pretty_stream_empty_response(self) -> None:
        stream_response = create_async_stream_response([])

        streamed_output = "".join(
            [part async for part in stream_response.pretty_stream()]
        )

        assert streamed_output == snapshot("**[No Content]**")
        assert streamed_output == stream_response.pretty()


class TestRawChunkTracking:
    """Test chunk deduplication behavior."""

    def test_sync_raw_chunks_collection(self) -> None:
        """Test that raw chunks are collected."""
        raw1 = {"info": "a"}
        raw2 = {"info": "b"}
        chunk1 = llm.TextStartChunk()
        chunk2 = llm.TextChunk(delta="hi")
        chunk3 = llm.TextEndChunk()

        def chunk_iterator() -> llm.ChunkIterator:
            yield llm.responses.RawStreamEventChunk(raw_stream_event=raw1)
            yield chunk1
            yield chunk2
            yield llm.responses.RawStreamEventChunk(raw_stream_event=raw2)
            yield chunk3

        stream_response = llm.StreamResponse(
            provider_id="openai",
            model_id="openai/gpt-5-mini",
            provider_model_name="gpt-5-mini",
            params={},
            input_messages=[llm.messages.user("Test")],
            chunk_iterator=chunk_iterator(),
        )

        stream_response.finish()

        check_stream_response_consistency(
            stream_response, [chunk1, chunk2, chunk3], [llm.Text(text="hi")]
        )
        assert stream_response.raw_stream_events == [raw1, raw2]

    @pytest.mark.asyncio
    async def test_async_chunk_deduplication_with_same_raw(self) -> None:
        raw1 = {"info": "a"}
        raw2 = {"info": "b"}
        chunk1 = llm.TextStartChunk()
        chunk2 = llm.TextChunk(delta="hi")
        chunk3 = llm.TextEndChunk()

        async def chunk_iterator() -> llm.AsyncChunkIterator:
            yield llm.responses.RawStreamEventChunk(raw_stream_event=raw1)
            yield chunk1
            yield chunk2
            yield llm.responses.RawStreamEventChunk(raw_stream_event=raw2)
            yield chunk3

        stream_response = llm.AsyncStreamResponse(
            provider_id="openai",
            model_id="openai/gpt-5-mini",
            provider_model_name="gpt-5-mini",
            params={},
            input_messages=[llm.messages.user("Test")],
            chunk_iterator=chunk_iterator(),
        )

        await stream_response.finish()

        check_stream_response_consistency(
            stream_response, [chunk1, chunk2, chunk3], [llm.Text(text="hi")]
        )
        assert stream_response.raw_stream_events == [raw1, raw2]


class TestRawContentChunkTracking:
    """Test raw content chunk handling for provider-specific content reconstruction."""

    def test_sync_raw_content_chunks_update_assistant_message(self) -> None:
        """Test that raw content chunks update assistant message raw_content field.

        RawContentChunk is used to reconstruct provider-specific output format
        that can be passed directly back to the provider API without losing details.
        """
        # Simulate OpenAI responses output items structure
        raw_output_item = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "hello world"}],
        }

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta="hello world"),
            llm.TextEndChunk(),
            # Raw content chunks are emitted at end to reconstruct full output
            llm.RawMessageChunk(raw_message=raw_output_item),
        ]

        stream_response = create_sync_stream_response(chunks)
        stream_response.finish()

        check_stream_response_consistency(
            stream_response, chunks[:-1], [llm.Text(text="hello world")]
        )
        assistant_message = stream_response.messages[-1]
        assert assistant_message.role == "assistant"
        assert assistant_message.raw_message == raw_output_item

    @pytest.mark.asyncio
    async def test_async_raw_content_chunks_update_assistant_message(self) -> None:
        """Test that raw content chunks update assistant message in async context."""
        raw_output_item = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "hello world"}],
        }

        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta="hello world"),
            llm.TextEndChunk(),
            llm.RawMessageChunk(raw_message=raw_output_item),
        ]

        stream_response = create_async_stream_response(chunks)
        await stream_response.finish()

        check_stream_response_consistency(
            stream_response, chunks[:-1], [llm.Text(text="hello world")]
        )
        assistant_message = stream_response.messages[-1]
        assert assistant_message.role == "assistant"
        assert assistant_message.raw_message == raw_output_item

    def test_sync_no_raw_content_chunks_means_none(self) -> None:
        """Test that raw_content remains none when no raw content chunks are emitted."""
        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta="hello"),
            llm.TextEndChunk(),
        ]

        stream_response = create_sync_stream_response(chunks)
        stream_response.finish()

        check_stream_response_consistency(
            stream_response, chunks, [llm.Text(text="hello")]
        )
        assistant_message = stream_response.messages[-1]
        assert assistant_message.role == "assistant"
        assert assistant_message.raw_message is None

    @pytest.mark.asyncio
    async def test_async_no_raw_content_chunks_means_none(self) -> None:
        """Test that raw_content remains none in async when no raw content chunks."""
        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta="hello"),
            llm.TextEndChunk(),
        ]

        stream_response = create_async_stream_response(chunks)
        await stream_response.finish()

        check_stream_response_consistency(
            stream_response, chunks, [llm.Text(text="hello")]
        )
        assistant_message = stream_response.messages[-1]
        assert assistant_message.role == "assistant"
        assert assistant_message.raw_message is None


@pytest.fixture
def example_format_tool_chunks() -> Sequence[llm.StreamResponseChunk]:
    return [
        llm.ToolCallStartChunk(
            id="call_format_123",
            name=FORMAT_TOOL_NAME,
        ),
        llm.ToolCallChunk(delta='{"title": "The Hobbit"'),
        llm.ToolCallChunk(delta=', "author": "Tolkien"}'),
        llm.ToolCallEndChunk(),
    ]


@pytest.fixture
def example_format_tool_chunks_processed() -> Sequence[llm.AssistantContentChunk]:
    return [
        llm.TextStartChunk(),
        llm.TextChunk(delta='{"title": "The Hobbit"'),
        llm.TextChunk(delta=', "author": "Tolkien"}'),
        llm.TextEndChunk(),
    ]


@pytest.fixture
def example_format_tool_chunks_mixed() -> Sequence[llm.StreamResponseChunk]:
    return [
        llm.ToolCallStartChunk(id="call_007", name="ring_tool"),
        llm.ToolCallChunk(delta='{"ring_purpose": "to_rule_them_all"}'),
        llm.ToolCallEndChunk(),
        llm.ToolCallStartChunk(
            id="call_format_123",
            name=FORMAT_TOOL_NAME,
        ),
        llm.ToolCallChunk(delta='{"title": "The Hobbit"'),
        llm.ToolCallChunk(delta=', "author": "Tolkien"}'),
        llm.ToolCallEndChunk(),
        llm.TextStartChunk(),
        llm.TextChunk(delta="A wizard is never late."),
        llm.TextEndChunk(),
    ]


@pytest.fixture
def example_format_tool_chunks_mixed_processed() -> Sequence[llm.AssistantContentChunk]:
    return [
        llm.ToolCallStartChunk(id="call_007", name="ring_tool"),
        llm.ToolCallChunk(delta='{"ring_purpose": "to_rule_them_all"}'),
        llm.ToolCallEndChunk(),
        llm.TextStartChunk(),
        llm.TextChunk(delta='{"title": "The Hobbit"'),
        llm.TextChunk(delta=', "author": "Tolkien"}'),
        llm.TextEndChunk(),
        llm.TextStartChunk(),
        llm.TextChunk(delta="A wizard is never late."),
        llm.TextEndChunk(),
    ]


@pytest.fixture
def example_format_tool_chunks_max_tokens() -> Sequence[llm.StreamResponseChunk]:
    return [
        llm.ToolCallStartChunk(
            id="call_format_123",
            name=FORMAT_TOOL_NAME,
        ),
        llm.ToolCallEndChunk(),
        llm.responses.FinishReasonChunk(finish_reason=llm.FinishReason.MAX_TOKENS),
    ]


@pytest.fixture
def example_format_tool_chunks_max_tokens_processed() -> Sequence[
    llm.AssistantContentChunk
]:
    return [
        llm.TextStartChunk(),
        llm.TextEndChunk(),
    ]


class TestFormatToolHandling:
    """Test format tool handling in stream responses."""

    def test_sync_format_tool_conversion(
        self,
        example_format_tool_chunks: Sequence[llm.StreamResponseChunk],
        example_format_tool_chunks_processed: Sequence[llm.AssistantContentChunk],
    ) -> None:
        """Test that FORMAT_TOOL_NAME tool calls are converted to text."""
        stream_response = create_sync_stream_response(example_format_tool_chunks)
        streamed_chunks = list(stream_response.chunk_stream())

        assert streamed_chunks == example_format_tool_chunks_processed
        assert stream_response.content == snapshot(
            [llm.Text(text='{"title": "The Hobbit", "author": "Tolkien"}')]
        )
        assert stream_response.messages[-1].content == stream_response.content

        assert stream_response.finish_reason is None

    def test_sync_mixed_regular_and_format_tools(
        self,
        example_format_tool_chunks_mixed: Sequence[llm.StreamResponseChunk],
        example_format_tool_chunks_mixed_processed: Sequence[llm.AssistantContentChunk],
    ) -> None:
        """Test streaming with both regular and format tools."""
        stream_response = create_sync_stream_response(example_format_tool_chunks_mixed)
        streamed_chunks = list(stream_response.chunk_stream())

        assert streamed_chunks == example_format_tool_chunks_mixed_processed
        assert stream_response.content == snapshot(
            [
                llm.ToolCall(
                    id="call_007",
                    name="ring_tool",
                    args='{"ring_purpose": "to_rule_them_all"}',
                ),
                llm.Text(text='{"title": "The Hobbit", "author": "Tolkien"}'),
                llm.Text(text="A wizard is never late."),
            ]
        )
        assert stream_response.messages[-1].content == stream_response.content
        assert stream_response.finish_reason is None

    def test_sync_format_tool_no_finish_reason_change(
        self,
        example_format_tool_chunks_max_tokens: Sequence[llm.StreamResponseChunk],
        example_format_tool_chunks_max_tokens_processed: Sequence[
            llm.AssistantContentChunk
        ],
    ) -> None:
        """Test that format tool doesn't change non-TOOL_USE finish reasons."""
        stream_response = create_sync_stream_response(
            example_format_tool_chunks_max_tokens
        )
        streamed_chunks = list(stream_response.chunk_stream())

        assert streamed_chunks == example_format_tool_chunks_max_tokens_processed
        assert len(stream_response.texts) == 1
        assert stream_response.texts[0].text == ""
        assert len(stream_response.tool_calls) == 0
        assert stream_response.finish_reason == llm.FinishReason.MAX_TOKENS

    @pytest.mark.asyncio
    async def test_async_format_tool_conversion(
        self,
        example_format_tool_chunks: Sequence[llm.StreamResponseChunk],
        example_format_tool_chunks_processed: Sequence[llm.AssistantContentChunk],
    ) -> None:
        """Test that FORMAT_TOOL_NAME tool calls are converted to text in async."""
        stream_response = create_async_stream_response(example_format_tool_chunks)
        streamed_chunks = [chunk async for chunk in stream_response.chunk_stream()]

        assert streamed_chunks == example_format_tool_chunks_processed
        assert stream_response.content == snapshot(
            [llm.Text(text='{"title": "The Hobbit", "author": "Tolkien"}')]
        )
        assert stream_response.messages[-1].content == stream_response.content
        assert stream_response.finish_reason is None

    @pytest.mark.asyncio
    async def test_async_mixed_regular_and_format_tools(
        self,
        example_format_tool_chunks_mixed: Sequence[llm.StreamResponseChunk],
        example_format_tool_chunks_mixed_processed: Sequence[llm.StreamResponseChunk],
    ) -> None:
        """Test streaming with both regular and format tools in async."""
        stream_response = create_async_stream_response(example_format_tool_chunks_mixed)
        streamed_chunks = [chunk async for chunk in stream_response.chunk_stream()]

        assert streamed_chunks == example_format_tool_chunks_mixed_processed
        assert stream_response.content == snapshot(
            [
                llm.ToolCall(
                    id="call_007",
                    name="ring_tool",
                    args='{"ring_purpose": "to_rule_them_all"}',
                ),
                llm.Text(text='{"title": "The Hobbit", "author": "Tolkien"}'),
                llm.Text(text="A wizard is never late."),
            ]
        )
        assert stream_response.messages[-1].content == stream_response.content
        assert stream_response.finish_reason is None

    @pytest.mark.asyncio
    async def test_async_format_tool_no_finish_reason_change(
        self,
        example_format_tool_chunks_max_tokens: Sequence[llm.StreamResponseChunk],
        example_format_tool_chunks_max_tokens_processed: Sequence[
            llm.AssistantContentChunk
        ],
    ) -> None:
        """Test that format tool doesn't change non-TOOL_USE finish reasons in async."""
        stream_response = create_async_stream_response(
            example_format_tool_chunks_max_tokens
        )
        streamed_chunks = [chunk async for chunk in stream_response.chunk_stream()]

        assert streamed_chunks == example_format_tool_chunks_max_tokens_processed
        assert len(stream_response.texts) == 1
        assert stream_response.texts[0].text == ""
        assert len(stream_response.tool_calls) == 0
        assert stream_response.finish_reason == llm.FinishReason.MAX_TOKENS


def test_stream_response_execute_tools() -> None:
    """Test execute_tools with multiple tool calls."""

    @llm.tool
    def tool_one(x: int) -> int:
        return x * 2

    @llm.tool
    def tool_two(y: str) -> str:
        return y.upper()

    tool_call_chunks = [
        llm.ToolCallStartChunk(id="call_1", name="tool_one"),
        llm.ToolCallChunk(delta='{"x": 5}'),
        llm.ToolCallEndChunk(),
        llm.ToolCallStartChunk(id="call_2", name="tool_two"),
        llm.ToolCallChunk(delta='{"y": "hello"}'),
        llm.ToolCallEndChunk(),
    ]

    stream_response = llm.StreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[tool_one, tool_two],
        input_messages=[],
        chunk_iterator=iter(tool_call_chunks),
    )

    list(stream_response.chunk_stream())

    outputs = stream_response.execute_tools()
    assert len(outputs) == 2
    assert outputs[0].value == 10
    assert outputs[1].value == "HELLO"


@pytest.mark.asyncio
async def test_async_stream_response_execute_tools() -> None:
    """Test async execute_tools with multiple tool calls executing concurrently."""

    @llm.tool
    async def tool_one(x: int) -> int:
        return x * 2

    @llm.tool
    async def tool_two(y: str) -> str:
        return y.upper()

    tool_call_chunks = [
        llm.ToolCallStartChunk(id="call_1", name="tool_one"),
        llm.ToolCallChunk(delta='{"x": 5}'),
        llm.ToolCallEndChunk(),
        llm.ToolCallStartChunk(id="call_2", name="tool_two"),
        llm.ToolCallChunk(delta='{"y": "hello"}'),
        llm.ToolCallEndChunk(),
    ]

    async def async_chunk_iter() -> AsyncIterator[llm.AssistantContentChunk]:
        for chunk in tool_call_chunks:
            yield chunk

    stream_response = llm.AsyncStreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        tools=[tool_one, tool_two],
        input_messages=[],
        chunk_iterator=async_chunk_iter(),
    )

    [chunk async for chunk in stream_response.chunk_stream()]

    outputs = await stream_response.execute_tools()
    assert len(outputs) == 2
    assert outputs[0].value == 10
    assert outputs[1].value == "HELLO"


def test_response_toolkit_initialization() -> None:
    """Initialize `StreamResponse` and `AsyncStreamResponse` with tools."""

    def chunk_iter() -> llm.ChunkIterator: ...

    def async_chunk_iter() -> llm.AsyncChunkIterator: ...

    response = llm.StreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        input_messages=[],
        chunk_iterator=chunk_iter(),
    )
    assert isinstance(response.toolkit, llm.Toolkit)

    response = llm.AsyncStreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        input_messages=[],
        chunk_iterator=async_chunk_iter(),
    )
    assert isinstance(response.toolkit, llm.AsyncToolkit)

    response = llm.ContextStreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        input_messages=[],
        chunk_iterator=chunk_iter(),
    )
    assert isinstance(response.toolkit, llm.ContextToolkit)

    response = llm.AsyncContextStreamResponse(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        provider_model_name="gpt-5-mini",
        params={},
        input_messages=[],
        chunk_iterator=async_chunk_iter(),
    )
    assert isinstance(response.toolkit, llm.AsyncContextToolkit)


class TestUsageTracking:
    """Test usage tracking in streams."""

    def test_sync_usage_accumulation(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        """Test that usage deltas are accumulated correctly in sync streams."""
        chunks = [
            *example_text_chunks,
            llm.UsageDeltaChunk(input_tokens=10, output_tokens=5),
            llm.UsageDeltaChunk(output_tokens=3, reasoning_tokens=2),
            llm.UsageDeltaChunk(cache_read_tokens=100),
        ]
        stream_response = create_sync_stream_response(chunks)

        assert stream_response.usage is None

        stream_response.finish()

        assert stream_response.usage is not None
        assert stream_response.usage.input_tokens == 10
        assert stream_response.usage.output_tokens == 8
        assert stream_response.usage.cache_read_tokens == 100
        assert stream_response.usage.cache_write_tokens == 0
        assert stream_response.usage.reasoning_tokens == 2

    @pytest.mark.asyncio
    async def test_async_usage_accumulation(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        """Test that usage deltas are accumulated correctly in async streams."""
        chunks = [
            *example_text_chunks,
            llm.UsageDeltaChunk(input_tokens=10, output_tokens=5),
            llm.UsageDeltaChunk(output_tokens=3, reasoning_tokens=2),
            llm.UsageDeltaChunk(cache_read_tokens=100),
        ]
        stream_response = create_async_stream_response(chunks)

        assert stream_response.usage is None

        await stream_response.finish()

        assert stream_response.usage is not None
        assert stream_response.usage.input_tokens == 10
        assert stream_response.usage.output_tokens == 8
        assert stream_response.usage.cache_read_tokens == 100
        assert stream_response.usage.cache_write_tokens == 0
        assert stream_response.usage.reasoning_tokens == 2

    def test_sync_no_usage_chunks_means_none(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        """Test that usage remains None when no usage chunks are emitted."""
        stream_response = create_sync_stream_response(example_text_chunks)

        stream_response.finish()

        assert stream_response.usage is None

    @pytest.mark.asyncio
    async def test_async_no_usage_chunks_means_none(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
    ) -> None:
        """Test that usage remains None in async when no usage chunks are emitted."""
        stream_response = create_async_stream_response(example_text_chunks)

        await stream_response.finish()

        assert stream_response.usage is None

    def test_sync_usage_with_all_fields(self) -> None:
        """Test accumulating usage with all possible fields."""
        chunks = [
            llm.TextStartChunk(),
            llm.TextChunk(delta="test"),
            llm.TextEndChunk(),
            llm.UsageDeltaChunk(
                input_tokens=100,
                output_tokens=50,
                cache_read_tokens=25,
                cache_write_tokens=10,
                reasoning_tokens=15,
            ),
            llm.UsageDeltaChunk(
                input_tokens=5,
                output_tokens=10,
                cache_read_tokens=5,
                cache_write_tokens=2,
                reasoning_tokens=3,
            ),
        ]
        stream_response = create_sync_stream_response(chunks)

        stream_response.finish()

        assert stream_response.usage is not None
        assert stream_response.usage.input_tokens == 105
        assert stream_response.usage.output_tokens == 60
        assert stream_response.usage.cache_read_tokens == 30
        assert stream_response.usage.cache_write_tokens == 12
        assert stream_response.usage.reasoning_tokens == 18


class TestStreams:
    """Test streams() method that yields content-part streams."""

    def test_sync_streams_single_text(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test streams() yields a single TextStream for text content."""
        stream_response = create_sync_stream_response(example_text_chunks)

        streams_iter = stream_response.streams()
        stream = next(streams_iter)

        assert isinstance(stream, llm.TextStream)
        assert stream.content_type == "text"
        assert stream.partial_text == ""

        deltas_and_partials = []
        for delta in stream:
            deltas_and_partials.append((delta, stream.partial_text))
        assert deltas_and_partials == snapshot(
            [("Hello", "Hello"), (" ", "Hello "), ("world", "Hello world")]
        )

        assert stream.collect() == example_text

        try:
            next(streams_iter)
            assert False, "Expected StopIteration"
        except StopIteration:
            pass

        assert stream_response.consumed is True

    def test_sync_streams_outer_iteration_consumes(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that iterating the outer streams() iterator consumes each stream."""
        chunks = [*example_text_chunks, *example_text_chunks]
        stream_response = create_sync_stream_response(chunks)

        streams_iter = stream_response.streams()

        # Get first stream but don't iterate it
        first_stream = next(streams_iter)
        assert isinstance(first_stream, llm.TextStream)
        assert first_stream.partial_text == ""

        # Getting the second stream should have auto-consumed the first
        second_stream = next(streams_iter)
        assert isinstance(second_stream, llm.TextStream)
        assert first_stream.partial_text == example_text.text
        assert second_stream.partial_text == ""

        try:
            next(streams_iter)
            assert False, "Expected StopIteration"
        except StopIteration:
            pass

        # Both streams should be consumed
        assert first_stream.partial_text == example_text.text
        assert second_stream.partial_text == example_text.text
        assert stream_response.consumed is True

    def test_sync_streams_replay_semantics(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that calling streams() multiple times replays from cache."""
        stream_response = create_sync_stream_response(example_text_chunks)

        first_streams = list(stream_response.streams())
        assert len(first_streams) == 1
        assert first_streams[0].collect() == example_text
        assert stream_response.consumed is True

        second_streams = list(stream_response.streams())
        assert len(second_streams) == 1
        assert second_streams[0].collect() == example_text

    def test_sync_streams_single_thought(
        self,
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_thought: llm.Thought,
    ) -> None:
        """Test streams() yields a ThoughtStream for a single thought content part."""
        stream_response = create_sync_stream_response(example_thought_chunks)

        streams_iter = stream_response.streams()
        stream = next(streams_iter)

        assert isinstance(stream, llm.ThoughtStream)
        assert stream.content_type == "thought"
        assert stream.partial_thought == ""

        deltas_and_partials = []
        for delta in stream:
            deltas_and_partials.append((delta, stream.partial_thought))
        assert deltas_and_partials == snapshot(
            [
                ("Let me think...", "Let me think..."),
                ("\nThis is interesting!", "Let me think...\nThis is interesting!"),
            ]
        )

        assert stream.collect() == example_thought

        try:
            next(streams_iter)
            assert False, "Expected StopIteration"
        except StopIteration:
            pass

        assert stream_response.consumed is True

    def test_sync_streams_single_tool_call(
        self,
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test streams() yields a ToolCallStream for a single tool call content part."""
        stream_response = create_sync_stream_response(example_tool_call_chunks)

        streams_iter = stream_response.streams()
        stream = next(streams_iter)

        assert isinstance(stream, llm.ToolCallStream)
        assert stream.content_type == "tool_call"
        assert stream.tool_id == "tool_call_123"
        assert stream.tool_name == "test_function"
        assert stream.partial_args == ""

        deltas_and_partials = []
        for delta in stream:
            deltas_and_partials.append((delta, stream.partial_args))
        assert deltas_and_partials == snapshot(
            [
                ('{"param1": "value1", ', '{"param1": "value1", '),
                ('"param2": 42}', '{"param1": "value1", "param2": 42}'),
            ]
        )

        assert stream.collect() == example_tool_call

        try:
            next(streams_iter)
            assert False, "Expected StopIteration"
        except StopIteration:
            pass

        assert stream_response.consumed is True

    def test_sync_streams_mixed_content(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
        example_thought: llm.Thought,
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test streams() yields TextStream, ThoughtStream, and ToolCallStream in order."""
        chunks = [
            *example_text_chunks,
            *example_thought_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_sync_stream_response(chunks)

        streams = list(stream_response.streams())

        assert len(streams) == 3
        assert isinstance(streams[0], llm.TextStream)
        assert isinstance(streams[1], llm.ThoughtStream)
        assert isinstance(streams[2], llm.ToolCallStream)

        assert streams[0].collect() == example_text
        assert streams[1].collect() == example_thought
        assert streams[2].collect() == example_tool_call

        assert stream_response.consumed is True
        assert stream_response.texts == [example_text]
        assert stream_response.thoughts == [example_thought]
        assert stream_response.tool_calls == [example_tool_call]


@pytest.mark.asyncio
class TestAsyncStreams:
    """Test async streams() method that yields content-part streams."""

    async def test_async_streams_single_text(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test async streams() yields a single AsyncTextStream for text content."""
        stream_response = create_async_stream_response(example_text_chunks)

        streams_iter = stream_response.streams()
        stream = await anext(streams_iter)

        assert isinstance(stream, llm.AsyncTextStream)
        assert stream.content_type == "text"
        assert stream.partial_text == ""

        deltas_and_partials = []
        async for delta in stream:
            deltas_and_partials.append((delta, stream.partial_text))
        assert deltas_and_partials == snapshot(
            [("Hello", "Hello"), (" ", "Hello "), ("world", "Hello world")]
        )

        assert await stream.collect() == example_text

        try:
            await anext(streams_iter)
            assert False, "Expected StopAsyncIteration"
        except StopAsyncIteration:
            pass

        assert stream_response.consumed is True

    async def test_async_streams_outer_iteration_consumes(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that iterating the outer async streams() iterator consumes each stream."""
        chunks = [*example_text_chunks, *example_text_chunks]
        stream_response = create_async_stream_response(chunks)

        streams_iter = stream_response.streams()

        # Get first stream but don't iterate it
        first_stream = await anext(streams_iter)
        assert isinstance(first_stream, llm.AsyncTextStream)
        assert first_stream.partial_text == ""

        # Getting the second stream should have auto-consumed the first
        second_stream = await anext(streams_iter)
        assert isinstance(second_stream, llm.AsyncTextStream)
        assert first_stream.partial_text == example_text.text
        assert second_stream.partial_text == ""

        try:
            await anext(streams_iter)
            assert False, "Expected StopAsyncIteration"
        except StopAsyncIteration:
            pass

        # Both streams should be consumed
        assert first_stream.partial_text == example_text.text
        assert second_stream.partial_text == example_text.text
        assert stream_response.consumed is True

    async def test_async_streams_replay_semantics(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
    ) -> None:
        """Test that calling async streams() multiple times replays from cache."""
        stream_response = create_async_stream_response(example_text_chunks)

        first_streams = [stream async for stream in stream_response.streams()]
        assert len(first_streams) == 1
        assert await first_streams[0].collect() == example_text
        assert stream_response.consumed is True

        second_streams = [stream async for stream in stream_response.streams()]
        assert len(second_streams) == 1
        assert await second_streams[0].collect() == example_text

    async def test_async_streams_single_thought(
        self,
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_thought: llm.Thought,
    ) -> None:
        """Test async streams() yields an AsyncThoughtStream for a single thought content part."""
        stream_response = create_async_stream_response(example_thought_chunks)

        streams_iter = stream_response.streams()
        stream = await anext(streams_iter)

        assert isinstance(stream, llm.AsyncThoughtStream)
        assert stream.content_type == "thought"
        assert stream.partial_thought == ""

        deltas_and_partials = []
        async for delta in stream:
            deltas_and_partials.append((delta, stream.partial_thought))
        assert deltas_and_partials == snapshot(
            [
                ("Let me think...", "Let me think..."),
                ("\nThis is interesting!", "Let me think...\nThis is interesting!"),
            ]
        )

        assert await stream.collect() == example_thought

        try:
            await anext(streams_iter)
            assert False, "Expected StopAsyncIteration"
        except StopAsyncIteration:
            pass

        assert stream_response.consumed is True

    async def test_async_streams_single_tool_call(
        self,
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test async streams() yields an AsyncToolCallStream for a single tool call content part."""
        stream_response = create_async_stream_response(example_tool_call_chunks)

        streams_iter = stream_response.streams()
        stream = await anext(streams_iter)

        assert isinstance(stream, llm.AsyncToolCallStream)
        assert stream.content_type == "tool_call"
        assert stream.tool_id == "tool_call_123"
        assert stream.tool_name == "test_function"
        assert stream.partial_args == ""

        deltas_and_partials = []
        async for delta in stream:
            deltas_and_partials.append((delta, stream.partial_args))
        assert deltas_and_partials == snapshot(
            [
                ('{"param1": "value1", ', '{"param1": "value1", '),
                ('"param2": 42}', '{"param1": "value1", "param2": 42}'),
            ]
        )

        assert await stream.collect() == example_tool_call

        try:
            await anext(streams_iter)
            assert False, "Expected StopAsyncIteration"
        except StopAsyncIteration:
            pass

        assert stream_response.consumed is True

    async def test_async_streams_mixed_content(
        self,
        example_text_chunks: Sequence[llm.StreamResponseChunk],
        example_thought_chunks: Sequence[llm.StreamResponseChunk],
        example_tool_call_chunks: Sequence[llm.StreamResponseChunk],
        example_text: llm.Text,
        example_thought: llm.Thought,
        example_tool_call: llm.ToolCall,
    ) -> None:
        """Test async streams() yields AsyncTextStream, AsyncThoughtStream, and AsyncToolCallStream in order."""
        chunks = [
            *example_text_chunks,
            *example_thought_chunks,
            *example_tool_call_chunks,
        ]
        stream_response = create_async_stream_response(chunks)

        streams = [stream async for stream in stream_response.streams()]

        assert len(streams) == 3
        assert isinstance(streams[0], llm.AsyncTextStream)
        assert isinstance(streams[1], llm.AsyncThoughtStream)
        assert isinstance(streams[2], llm.AsyncToolCallStream)

        assert await streams[0].collect() == example_text
        assert await streams[1].collect() == example_thought
        assert await streams[2].collect() == example_tool_call

        assert stream_response.consumed is True
        assert stream_response.texts == [example_text]
        assert stream_response.thoughts == [example_thought]
        assert stream_response.tool_calls == [example_tool_call]
