"""End-to-end tests for OpenAI-compatible providers (together, ollama, etc.)."""

import os

import pytest

from mirascope import llm
from mirascope.llm.providers.azure import AzureProvider
from tests.utils import (
    Snapshot,
    response_snapshot_dict,
    snapshot_test,
    stream_response_snapshot_dict,
)

TOGETHER_MODEL_IDS = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
]


@pytest.mark.parametrize("model_id", TOGETHER_MODEL_IDS)
@pytest.mark.vcr
def test_together_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Together provider works correctly."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    llm.register_provider(
        "together", "meta-llama/", api_key=os.getenv("TOGETHER_API_KEY", "test")
    )

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == "together"
        assert response.provider_model_name == "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


def test_together_provider_missing_api_key() -> None:
    """Test that Together provider raises clear error when API key is missing."""
    from mirascope.llm.providers.together import TogetherProvider

    original_key = os.environ.pop("TOGETHER_API_KEY", None)
    try:
        with pytest.raises(ValueError) as exc_info:
            TogetherProvider()
        assert "Together API key is required" in str(exc_info.value)
        assert "TOGETHER_API_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ["TOGETHER_API_KEY"] = original_key


OLLAMA_MODEL_IDS = [
    "ollama/gemma3:4b",
]


@pytest.mark.parametrize("model_id", OLLAMA_MODEL_IDS)
@pytest.mark.vcr
def test_ollama_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Ollama provider works correctly."""
    # Clear OLLAMA_BASE_URL to ensure consistent cassette matching
    original_base_url = os.environ.pop("OLLAMA_BASE_URL", None)
    try:

        @llm.call(model_id)
        def add_numbers(a: int, b: int) -> str:
            return f"What is {a} + {b}?"

        llm.register_provider("ollama")

        with snapshot_test(snapshot) as snap:
            response = add_numbers(4200, 42)
            assert response.provider_id == "ollama"
            assert response.provider_model_name == "gemma3:4b"
            snap.set_response(response)
            assert "4242" in response.pretty(), (
                f"Expected '4242' in response: {response.pretty()}"
            )
    finally:
        if original_base_url is not None:
            os.environ["OLLAMA_BASE_URL"] = original_base_url


AZURE_MODEL_IDS = [
    "azure/openai/gpt-5-mini",
]


def _register_azure_provider() -> None:
    llm.register_provider(
        "azure",
        "azure/openai/",
        api_key=os.getenv("AZURE_OPENAI_API_KEY", "test"),
        base_url=os.getenv(
            "AZURE_OPENAI_ENDPOINT",
            "https://dummy.openai.azure.com/",
        ),
    )


@pytest.mark.parametrize("model_id", AZURE_MODEL_IDS)
@pytest.mark.vcr
def test_azure_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Azure OpenAI provider works correctly."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    _register_azure_provider()

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == "azure"
        assert response.provider_model_name == "gpt-5-mini"
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", AZURE_MODEL_IDS)
@pytest.mark.vcr
def test_azure_openai_sync_call_and_stream(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test sync call + stream paths for Azure OpenAI (with and without context)."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    @llm.call(model_id)
    def add_numbers_ctx(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    _register_azure_provider()

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        snap["call"] = response_snapshot_dict(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )

        ctx = llm.Context(deps=4200)
        response_ctx = add_numbers_ctx(ctx, 42)
        snap["context_call"] = response_snapshot_dict(response_ctx)
        assert "4242" in response_ctx.pretty(), (
            f"Expected '4242' in response: {response_ctx.pretty()}"
        )

        stream = add_numbers.stream(4200, 42)
        stream.finish()
        snap["stream"] = stream_response_snapshot_dict(stream)
        assert "4242" in stream.pretty(), (
            f"Expected '4242' in response: {stream.pretty()}"
        )

        stream_ctx = add_numbers_ctx.stream(ctx, 42)
        stream_ctx.finish()
        snap["context_stream"] = stream_response_snapshot_dict(stream_ctx)
        assert "4242" in stream_ctx.pretty(), (
            f"Expected '4242' in response: {stream_ctx.pretty()}"
        )


@pytest.mark.parametrize("model_id", AZURE_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_azure_openai_async_call_and_stream(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async call + stream paths for Azure OpenAI (with and without context)."""

    @llm.call(model_id)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    @llm.call(model_id)
    async def add_numbers_ctx(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    _register_azure_provider()

    with snapshot_test(snapshot) as snap:
        response = await add_numbers(4200, 42)
        snap["async_call"] = response_snapshot_dict(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )

        ctx = llm.Context(deps=4200)
        response_ctx = await add_numbers_ctx(ctx, 42)
        snap["async_context_call"] = response_snapshot_dict(response_ctx)
        assert "4242" in response_ctx.pretty(), (
            f"Expected '4242' in response: {response_ctx.pretty()}"
        )

        stream = await add_numbers.stream(4200, 42)
        await stream.finish()
        snap["async_stream"] = stream_response_snapshot_dict(stream)
        assert "4242" in stream.pretty(), (
            f"Expected '4242' in response: {stream.pretty()}"
        )

        stream_ctx = await add_numbers_ctx.stream(ctx, 42)
        await stream_ctx.finish()
        snap["async_context_stream"] = stream_response_snapshot_dict(stream_ctx)
        assert "4242" in stream_ctx.pretty(), (
            f"Expected '4242' in response: {stream_ctx.pretty()}"
        )


AZURE_ANTHROPIC_MODEL_NAME = (
    "azureml://registries/azureml-anthropic/models/claude-haiku-4-5/versions/20251001"
)
AZURE_ANTHROPIC_MODEL_IDS = [f"azure/{AZURE_ANTHROPIC_MODEL_NAME}"]


@pytest.mark.skipif(
    not os.getenv("AZURE_ANTHROPIC_DEPLOYED"),
    reason="Azure Anthropic not yet deployed - set AZURE_ANTHROPIC_DEPLOYED=1 to enable",
)
@pytest.mark.parametrize("model_id", AZURE_ANTHROPIC_MODEL_IDS)
@pytest.mark.vcr
def test_azure_anthropic_provider(
    model_id: llm.ModelId,
    snapshot: Snapshot,
) -> None:
    """Test that Azure Anthropic provider is wired for Foundry models."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    provider = AzureProvider(
        api_key=os.getenv("AZURE_OPENAI_API_KEY", "test"),
        base_url=os.getenv(
            "AZURE_OPENAI_ENDPOINT",
            "https://dummy.openai.azure.com/",
        ),
        anthropic_api_key=os.getenv("AZURE_ANTHROPIC_API_KEY", "test"),
        anthropic_base_url=os.getenv(
            "AZURE_AI_ANTHROPIC_ENDPOINT",
            "https://dummy.services.ai.azure.com/anthropic/",
        ),
    )
    llm.register_provider(provider, "azure/")

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == "azure"
        assert response.provider_model_name == AZURE_ANTHROPIC_MODEL_NAME
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


# =============================================================================
# Bedrock Anthropic Provider Tests
# =============================================================================

BEDROCK_ANTHROPIC_MODEL_IDS = ["bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0"]


def _register_bedrock_provider() -> None:
    llm.register_provider("bedrock", "bedrock/")


@pytest.mark.parametrize("model_id", BEDROCK_ANTHROPIC_MODEL_IDS)
@pytest.mark.vcr
def test_bedrock_anthropic_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Bedrock Anthropic provider works correctly."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    _register_bedrock_provider()

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == "bedrock"
        assert (
            response.provider_model_name
            == "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        )
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", BEDROCK_ANTHROPIC_MODEL_IDS)
@pytest.mark.vcr
def test_bedrock_anthropic_sync_call_and_stream(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test sync call + stream paths for Bedrock Anthropic (with and without context)."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    @llm.call(model_id)
    def add_numbers_ctx(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    _register_bedrock_provider()

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        snap["call"] = response_snapshot_dict(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )

        ctx = llm.Context(deps=4200)
        response_ctx = add_numbers_ctx(ctx, 42)
        snap["context_call"] = response_snapshot_dict(response_ctx)
        assert "4242" in response_ctx.pretty(), (
            f"Expected '4242' in response: {response_ctx.pretty()}"
        )

        stream = add_numbers.stream(4200, 42)
        stream.finish()
        snap["stream"] = stream_response_snapshot_dict(stream)
        assert "4242" in stream.pretty(), (
            f"Expected '4242' in response: {stream.pretty()}"
        )

        stream_ctx = add_numbers_ctx.stream(ctx, 42)
        stream_ctx.finish()
        snap["context_stream"] = stream_response_snapshot_dict(stream_ctx)
        assert "4242" in stream_ctx.pretty(), (
            f"Expected '4242' in response: {stream_ctx.pretty()}"
        )


@pytest.mark.parametrize("model_id", BEDROCK_ANTHROPIC_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_bedrock_anthropic_async_call_and_stream(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async call + stream paths for Bedrock Anthropic (with and without context)."""

    @llm.call(model_id)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    @llm.call(model_id)
    async def add_numbers_ctx(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    _register_bedrock_provider()

    with snapshot_test(snapshot) as snap:
        response = await add_numbers(4200, 42)
        snap["async_call"] = response_snapshot_dict(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )

        ctx = llm.Context(deps=4200)
        response_ctx = await add_numbers_ctx(ctx, 42)
        snap["async_context_call"] = response_snapshot_dict(response_ctx)
        assert "4242" in response_ctx.pretty(), (
            f"Expected '4242' in response: {response_ctx.pretty()}"
        )

        stream = await add_numbers.stream(4200, 42)
        await stream.finish()
        snap["async_stream"] = stream_response_snapshot_dict(stream)
        assert "4242" in stream.pretty(), (
            f"Expected '4242' in response: {stream.pretty()}"
        )

        stream_ctx = await add_numbers_ctx.stream(ctx, 42)
        await stream_ctx.finish()
        snap["async_context_stream"] = stream_response_snapshot_dict(stream_ctx)
        assert "4242" in stream_ctx.pretty(), (
            f"Expected '4242' in response: {stream_ctx.pretty()}"
        )


# =============================================================================
# Bedrock OpenAI Provider Tests
# =============================================================================

BEDROCK_OPENAI_MODEL_IDS = ["bedrock/openai.gpt-oss-20b-1:0"]


@pytest.mark.parametrize("model_id", BEDROCK_OPENAI_MODEL_IDS)
@pytest.mark.vcr
def test_bedrock_openai_provider(model_id: llm.ModelId, snapshot: Snapshot) -> None:
    """Test that Bedrock OpenAI provider works correctly."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    _register_bedrock_provider()

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        assert response.provider_id == "bedrock"
        assert response.provider_model_name == "openai.gpt-oss-20b-1:0"
        snap.set_response(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )


@pytest.mark.parametrize("model_id", BEDROCK_OPENAI_MODEL_IDS)
@pytest.mark.vcr
def test_bedrock_openai_sync_call_and_stream(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test sync call + stream paths for Bedrock OpenAI (with and without context)."""

    @llm.call(model_id)
    def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    @llm.call(model_id)
    def add_numbers_ctx(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    _register_bedrock_provider()

    with snapshot_test(snapshot) as snap:
        response = add_numbers(4200, 42)
        snap["call"] = response_snapshot_dict(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )

        ctx = llm.Context(deps=4200)
        response_ctx = add_numbers_ctx(ctx, 42)
        snap["context_call"] = response_snapshot_dict(response_ctx)
        assert "4242" in response_ctx.pretty(), (
            f"Expected '4242' in response: {response_ctx.pretty()}"
        )

        stream = add_numbers.stream(4200, 42)
        stream.finish()
        snap["stream"] = stream_response_snapshot_dict(stream)
        assert "4242" in stream.pretty(), (
            f"Expected '4242' in response: {stream.pretty()}"
        )

        stream_ctx = add_numbers_ctx.stream(ctx, 42)
        stream_ctx.finish()
        snap["context_stream"] = stream_response_snapshot_dict(stream_ctx)
        assert "4242" in stream_ctx.pretty(), (
            f"Expected '4242' in response: {stream_ctx.pretty()}"
        )


@pytest.mark.parametrize("model_id", BEDROCK_OPENAI_MODEL_IDS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_bedrock_openai_async_call_and_stream(
    model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async call + stream paths for Bedrock OpenAI (with and without context)."""

    @llm.call(model_id)
    async def add_numbers(a: int, b: int) -> str:
        return f"What is {a} + {b}?"

    @llm.call(model_id)
    async def add_numbers_ctx(ctx: llm.Context[int], b: int) -> str:
        return f"What is {ctx.deps} + {b}?"

    _register_bedrock_provider()

    with snapshot_test(snapshot) as snap:
        response = await add_numbers(4200, 42)
        snap["async_call"] = response_snapshot_dict(response)
        assert "4242" in response.pretty(), (
            f"Expected '4242' in response: {response.pretty()}"
        )

        ctx = llm.Context(deps=4200)
        response_ctx = await add_numbers_ctx(ctx, 42)
        snap["async_context_call"] = response_snapshot_dict(response_ctx)
        assert "4242" in response_ctx.pretty(), (
            f"Expected '4242' in response: {response_ctx.pretty()}"
        )

        stream = await add_numbers.stream(4200, 42)
        await stream.finish()
        snap["async_stream"] = stream_response_snapshot_dict(stream)
        assert "4242" in stream.pretty(), (
            f"Expected '4242' in response: {stream.pretty()}"
        )

        stream_ctx = await add_numbers_ctx.stream(ctx, 42)
        await stream_ctx.finish()
        snap["async_context_stream"] = stream_response_snapshot_dict(stream_ctx)
        assert "4242" in stream_ctx.pretty(), (
            f"Expected '4242' in response: {stream_ctx.pretty()}"
        )
