import asyncio
import unittest.mock as mock
from collections.abc import Iterator

import pytest
from pydantic import BaseModel

from mirascope import llm


class MockChunk:
    """Mock chunk for streaming."""

    def __init__(self, content: str):
        self.content = content


class MockStream:
    """Simple mock for Stream."""

    def __init__(self, chunks: list[MockChunk]):
        self.chunks = chunks

    def __iter__(self) -> Iterator[tuple[MockChunk, str | None]]:
        for chunk in self.chunks:
            yield chunk, None

    async def __aiter__(self):
        for chunk in self.chunks:
            yield chunk, None


def test_prompt_decorator_requires_context():
    """Test that decorated functions can only be called within a context manager."""

    @llm.prompt()
    def hello_world():
        return "Hello, world!"

    with pytest.raises(ValueError) as excinfo:
        hello_world()

    assert "Prompt can only be called within a llm.context" in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_prompt_decorator_requires_context():
    """Test that async decorated functions can only be called within a context manager."""

    @llm.prompt()
    async def hello_world():
        return "Hello, world!"

    with pytest.raises(ValueError) as excinfo:
        await hello_world()

    assert "Prompt can only be called within a llm.context" in str(excinfo.value)


def test_prompt_with_context():
    """Test that we can call decorated functions within a context manager."""

    @llm.prompt()
    def hello_world() -> str:
        return "Hello, world!"

    # Create a mock for CallResponse
    mock_response = mock.MagicMock()
    mock_response.content = "Hello from the AI!"
    mock_response.finish_reasons = ["stop"]

    # Define patched provider call
    def patched_openai_call(**kwargs):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                return mock_response

            return wrapper

        return decorator

    # Setup the patch and context
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        llm.context(provider="openai", model="gpt-4o-mini"),
    ):
        # Call the prompt function
        response = hello_world()
        assert response.content == "Hello from the AI!"


@pytest.mark.asyncio
async def test_async_prompt_with_context():
    """Test that we can call async decorated functions within a context manager."""

    @llm.prompt()
    async def hello_world() -> str:
        return "Hello, world!"

    # Create a mock for CallResponse
    mock_response = mock.MagicMock()
    mock_response.content = "Hello from the AI!"
    mock_response.finish_reasons = ["stop"]

    # Define patched provider call
    def patched_openai_call(**kwargs):
        def decorator(fn):
            async def wrapper(*args, **kwargs):
                return mock_response

            return wrapper

        return decorator

    # Setup the patch and context
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        llm.context(provider="openai", model="gpt-4o-mini"),
    ):
        # Call the prompt function
        response = await hello_world()
        assert response.content == "Hello from the AI!"


def test_prompt_with_structural_args():
    """Test that we can use structural args with prompt."""

    class Response(BaseModel):
        message: str

    @llm.prompt(response_model=Response)
    def hello_world() -> str:
        return "Hello, world!"

    # Define patched provider call
    def patched_openai_call(**kwargs):
        # Verify that response_model was passed correctly
        assert kwargs.get("response_model") == Response

        def decorator(fn):
            def wrapper(*args, **kwargs):
                # Return a Response object directly
                return Response(message="Hello from the AI!")

            return wrapper

        return decorator

    # Setup the patch and context
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        llm.context(provider="openai", model="gpt-4o-mini"),
    ):
        # Call the prompt function
        response = hello_world()
        assert isinstance(response, Response)
        assert response.message == "Hello from the AI!"


@pytest.mark.asyncio
async def test_async_prompt_with_structural_args():
    """Test that we can use structural args with async prompt."""

    class Response(BaseModel):
        message: str

    @llm.prompt(response_model=Response)
    async def hello_world() -> str:
        return "Hello, world!"

    # Define patched provider call
    def patched_openai_call(**kwargs):
        # Verify that response_model was passed correctly
        assert kwargs.get("response_model") == Response

        def decorator(fn):
            async def wrapper(*args, **kwargs):
                # Return a Response object directly
                return Response(message="Hello from the AI!")

            return wrapper

        return decorator

    # Setup the patch and context
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        llm.context(provider="openai", model="gpt-4o-mini"),
    ):
        # Call the prompt function
        result = await hello_world()  # type: ignore[reportAwaitableType]
        assert isinstance(result, Response)
        assert result.message == "Hello from the AI!"


def test_prompt_with_context_overrides():
    """Test that context overrides non-structural params."""

    @llm.prompt()
    def hello_world() -> str:
        return "Hello, world!"

    # Track which provider was used
    calls = []

    # Create mock responses
    openai_response = mock.MagicMock()
    openai_response.content = "Hello from OpenAI!"
    openai_response.finish_reasons = ["stop"]

    anthropic_response = mock.MagicMock()
    anthropic_response.content = "Hello from Anthropic!"
    anthropic_response.finish_reasons = ["stop"]

    # Create patched providers
    def patched_openai_call(**kwargs):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                calls.append("openai")
                return openai_response

            return wrapper

        return decorator

    def patched_anthropic_call(**kwargs):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                calls.append("anthropic")
                return anthropic_response

            return wrapper

        return decorator

    # Setup patches for both providers
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        mock.patch("mirascope.core.anthropic.anthropic_call", patched_anthropic_call),
    ):
        # First with OpenAI
        with llm.context(provider="openai", model="gpt-4o-mini"):
            response = hello_world()
            assert response.content == "Hello from OpenAI!"
            assert calls[-1] == "openai"

        # Then with Anthropic
        with llm.context(provider="anthropic", model="claude-3-opus-20240229"):
            response = hello_world()
            assert response.content == "Hello from Anthropic!"
            assert calls[-1] == "anthropic"


@pytest.mark.asyncio
async def test_async_prompt_with_context_overrides():
    """Test that context overrides non-structural params with async functions."""

    @llm.prompt()
    async def hello_world() -> str:
        return "Hello, world!"

    # Track which provider was used
    calls = []

    # Create mock responses
    openai_response = mock.MagicMock()
    openai_response.content = "Hello from OpenAI!"
    openai_response.finish_reasons = ["stop"]

    anthropic_response = mock.MagicMock()
    anthropic_response.content = "Hello from Anthropic!"
    anthropic_response.finish_reasons = ["stop"]

    # Create patched providers
    def patched_openai_call(**kwargs):
        def decorator(fn):
            async def wrapper(*args, **kwargs):
                calls.append("openai")
                return openai_response

            return wrapper

        return decorator

    def patched_anthropic_call(**kwargs):
        def decorator(fn):
            async def wrapper(*args, **kwargs):
                calls.append("anthropic")
                return anthropic_response

            return wrapper

        return decorator

    # Setup patches for both providers
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        mock.patch("mirascope.core.anthropic.anthropic_call", patched_anthropic_call),
    ):
        # First with OpenAI
        with llm.context(provider="openai", model="gpt-4o-mini"):
            response = await hello_world()
            assert response.content == "Hello from OpenAI!"
            assert calls[-1] == "openai"

        # Then with Anthropic
        with llm.context(provider="anthropic", model="claude-3-opus-20240229"):
            response = await hello_world()
            assert response.content == "Hello from Anthropic!"
            assert calls[-1] == "anthropic"


@pytest.mark.asyncio
async def test_async_prompt():
    """Test that async prompts work correctly."""

    @llm.prompt()
    async def hello_world() -> str:
        return "Hello, world!"

    # Create a mock response for async calls
    mock_response = mock.MagicMock()
    mock_response.content = "Hello from the AI!"
    mock_response.finish_reasons = ["stop"]

    # Define patched async provider call
    def patched_openai_call(**kwargs):
        def decorator(fn):
            async def async_wrapper(*args, **kwargs):
                return mock_response

            return async_wrapper

        return decorator

    # Setup the patch and context
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        llm.context(provider="openai", model="gpt-4o-mini"),
    ):
        # Call the async prompt function and await the result
        response = await hello_world()
        assert response.content == "Hello from the AI!"


@pytest.mark.asyncio
async def test_async_prompt_with_gather():
    """Test that context is properly applied in async functions when using asyncio.gather."""

    @llm.prompt()
    async def hello_world() -> str:
        return "Hello, world!"

    # Track which provider was used for each call
    calls = []

    # Create mock responses for different providers
    openai_response = mock.MagicMock()
    openai_response.content = "Hello from OpenAI!"
    openai_response.finish_reasons = ["stop"]

    anthropic_response = mock.MagicMock()
    anthropic_response.content = "Hello from Anthropic!"
    anthropic_response.finish_reasons = ["stop"]

    # Create patched providers that track which provider was used
    def patched_openai_call(**kwargs):
        model = kwargs.get("model", "unknown")

        def decorator(fn):
            async def wrapper(*args, **kwargs):
                calls.append(("openai", model))
                return openai_response

            return wrapper

        return decorator

    def patched_anthropic_call(**kwargs):
        model = kwargs.get("model", "unknown")

        def decorator(fn):
            async def wrapper(*args, **kwargs):
                calls.append(("anthropic", model))
                return anthropic_response

            return wrapper

        return decorator

    # Setup patches for both providers
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        mock.patch("mirascope.core.anthropic.anthropic_call", patched_anthropic_call),
    ):
        # Create the first future with OpenAI context
        with llm.context(provider="openai", model="gpt-4o-mini"):
            future1 = hello_world()

        # Create the second future with Anthropic context
        with llm.context(provider="anthropic", model="claude-3-opus-20240229"):
            future2 = hello_world()

        # Await both futures together
        results = await asyncio.gather(future1, future2)

        # Check that we have results from both providers
        assert len(results) == 2
        assert results[0].content == "Hello from OpenAI!"
        assert results[1].content == "Hello from Anthropic!"

        # Check that the correct providers and models were used
        assert len(calls) == 2
        assert calls[0] == ("openai", "gpt-4o-mini")
        assert calls[1] == ("anthropic", "claude-3-opus-20240229")


def test_prompt_with_streaming():
    """Test that streaming works correctly."""

    @llm.prompt(stream=True)
    def hello_world() -> str:
        return "Hello, world!"

    # Create chunks and mock stream
    chunks = [MockChunk("Hello "), MockChunk("from the AI!")]
    mock_stream = MockStream(chunks)

    # Define patched streaming provider call
    def patched_openai_call(**kwargs):
        # Verify that stream was passed correctly
        assert kwargs.get("stream") is True

        def decorator(fn):
            def wrapper(*args, **kwargs):
                return mock_stream

            return wrapper

        return decorator

    # Setup the patch and context
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        llm.context(provider="openai", model="gpt-4o-mini"),
    ):
        # Call the streaming prompt function
        stream = hello_world()

        # Test iteration over the stream
        collected_chunks = []
        for chunk, _ in stream:
            collected_chunks.append(chunk.content)

        assert collected_chunks == ["Hello ", "from the AI!"]
        assert "".join(collected_chunks) == "Hello from the AI!"


@pytest.mark.asyncio
async def test_async_prompt_with_streaming():
    """Test that streaming works correctly with async prompts."""

    @llm.prompt(stream=True)
    async def hello_world() -> str:
        return "Hello, world!"

    # Create chunks and mock stream
    chunks = [MockChunk("Hello "), MockChunk("from the AI!")]
    mock_stream = MockStream(chunks)

    # Define patched streaming provider call
    def patched_openai_call(**kwargs):
        # Verify that stream was passed correctly
        assert kwargs.get("stream") is True

        def decorator(fn):
            async def wrapper(*args, **kwargs):
                return mock_stream

            return wrapper

        return decorator

    # Setup the patch and context
    with (
        mock.patch("mirascope.core.openai.openai_call", patched_openai_call),
        llm.context(provider="openai", model="gpt-4o-mini"),
    ):
        # Call the streaming prompt function
        stream = await hello_world()

        # Test iteration over the stream
        collected_chunks = []
        async for chunk, _ in stream:
            collected_chunks.append(chunk.content)

        assert collected_chunks == ["Hello ", "from the AI!"]
        assert "".join(collected_chunks) == "Hello from the AI!"
