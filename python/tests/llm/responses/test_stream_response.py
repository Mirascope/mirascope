"""Tests for llm.StreamResponse class."""

from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass

import pytest

from mirascope import llm


def create_sync_stream_response(
    chunks: list[llm.AssistantContentChunk],
) -> llm.StreamResponse[llm.Stream]:
    """Create a llm.StreamResponse with a functioning iterator for testing."""

    def sync_chunk_iter() -> llm.ChunkIterator:
        for chunk in chunks:
            yield chunk, f"raw_{chunk.type}"

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
            yield chunk, f"raw_{chunk.type}"

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


def check_stream_response_consistency(
    response: llm.StreamResponse[llm.Stream | llm.AsyncStream],
    chunks: list[llm.AssistantContentChunk],
    content: list[llm.AssistantContentPart],
) -> None:
    assert response.chunks == chunks, "response.chunks"
    expected_raw = [f"raw_{chunk.type}" for chunk in chunks]
    assert response.raw == expected_raw, "response.raw"
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
        example_text: llm.Text,
        example_thinking: llm.Thinking,
    ) -> None:
        """Test streaming mixed chunk types with sync response."""
        chunks = [*example_text_chunks, *example_thinking_chunks]
        stream_response = create_sync_stream_response(chunks)

        streamed_chunks = list(stream_response.chunk_stream())

        check_stream_response_consistency(
            stream_response, chunks, [example_text, example_thinking]
        )
        assert len(streamed_chunks) == 9
        assert stream_response.consumed is True

    @pytest.mark.asyncio
    async def test_async_basic_streaming(
        self,
        example_text_chunks: list[llm.AssistantContentChunk],
        example_thinking_chunks: list[llm.AssistantContentChunk],
        example_text: llm.Text,
        example_thinking: llm.Thinking,
    ) -> None:
        """Test streaming mixed chunk types with async response."""
        chunks = [*example_text_chunks, *example_thinking_chunks]
        stream_response = create_async_stream_response(chunks)

        streamed_chunks = [
            chunk async for chunk in await stream_response.chunk_stream()
        ]

        check_stream_response_consistency(
            stream_response, chunks, [example_text, example_thinking]
        )
        assert len(streamed_chunks) == 9
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
}


class ChunkProcessingFixtureRequest(pytest.FixtureRequest):
    param: str
    """The ID for the test case."""


@pytest.fixture(
    params=CHUNK_PROCESSING_TEST_CASES.keys(),
    ids=list(CHUNK_PROCESSING_TEST_CASES.keys()),
)
def chunk_processing_test_case(
    request: ChunkProcessingFixtureRequest,
) -> ChunkProcessingTestCase:
    return CHUNK_PROCESSING_TEST_CASES[request.param]


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


class TestErrorHandling:
    """Test error handling in chunk processing."""

    @pytest.fixture
    def invalid_chunk_sequences(
        self,
    ) -> list[tuple[list[llm.AssistantContentChunk], str]]:
        """Test cases for invalid chunk sequences."""
        return [
            # Text chunk without start
            (
                [llm.TextChunk(type="text_chunk", delta="Hello")],
                "Received text_chunk while not processing text",
            ),
            # Text end without start or delta
            (
                [llm.TextEndChunk(type="text_end_chunk")],
                "Received text_end_chunk while not processing text",
            ),
            # Thinking chunk without start
            (
                [llm.ThinkingChunk(type="thinking_chunk", delta="Hello")],
                "Received thinking_chunk while not processing thinking",
            ),
            # Thinking end without start or delta
            (
                [llm.ThinkingEndChunk(type="thinking_end_chunk", signature=None)],
                "Received thinking_end_chunk while not processing thinking",
            ),
            # Overlapping chunks - start text then start thinking
            (
                [
                    llm.TextStartChunk(type="text_start_chunk"),
                    llm.ThinkingStartChunk(type="thinking_start_chunk"),
                ],
                "while processing another chunk",
            ),
            # Overlapping chunks - start thinking then start text
            (
                [
                    llm.ThinkingStartChunk(type="thinking_start_chunk"),
                    llm.TextStartChunk(type="text_start_chunk"),
                ],
                "while processing another chunk",
            ),
            # Text end without matching start
            (
                [
                    llm.ThinkingStartChunk(type="thinking_start_chunk"),
                    llm.ThinkingChunk(type="thinking_chunk", delta="test"),
                    llm.TextEndChunk(type="text_end_chunk"),
                ],
                "Received text_end_chunk while not processing text",
            ),
            # Thinking end without matching start
            (
                [
                    llm.TextStartChunk(type="text_start_chunk"),
                    llm.TextChunk(type="text_chunk", delta="test"),
                    llm.ThinkingEndChunk(type="thinking_end_chunk", signature=None),
                ],
                "Received thinking_end_chunk while not processing thinking",
            ),
        ]

    def test_sync_invalid_chunk_sequences(
        self, invalid_chunk_sequences: list[tuple[list[llm.AssistantContentChunk], str]]
    ) -> None:
        """Test error handling for invalid chunk sequences with sync response."""
        for chunks, expected_error in invalid_chunk_sequences:
            stream_response = create_sync_stream_response(chunks)

            with pytest.raises(RuntimeError, match=expected_error):
                list(stream_response.chunk_stream())

    @pytest.mark.asyncio
    async def test_async_invalid_chunk_sequences(
        self, invalid_chunk_sequences: list[tuple[list[llm.AssistantContentChunk], str]]
    ) -> None:
        """Test error handling for invalid chunk sequences with async response."""
        for chunks, expected_error in invalid_chunk_sequences:
            stream_response = create_async_stream_response(chunks)

            with pytest.raises(RuntimeError, match=expected_error):
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
