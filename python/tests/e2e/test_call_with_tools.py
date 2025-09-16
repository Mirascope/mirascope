"""End-to-end tests for LLM tool usage, including parallel tool usage and continuation."""

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import response_snapshot_dict, stream_response_snapshot_dict

PASSWORD_MAP = {"mellon": "Welcome to Moria!", "radiance": "Life before Death"}

# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_sync(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous tool call without context."""

    @llm.tool
    def secret_retrieval_tool(password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return PASSWORD_MAP.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    def call(passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    response = call(["mellon", "radiance"])
    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

    assert response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_sync_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous tool call with context."""

    @llm.tool
    def secret_retrieval_tool(ctx: llm.Context[dict[str, str]], password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    def call(ctx: llm.Context[dict[str, str]], passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    ctx = llm.Context(deps=PASSWORD_MAP)
    response = call(ctx, ["mellon", "radiance"])
    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = response.execute_tools(
        ctx,
    )
    response = response.resume(ctx, tool_outputs)

    assert response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous tool call without context."""

    @llm.tool
    async def secret_retrieval_tool(password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return PASSWORD_MAP.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    async def call(passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    response = await call(["mellon", "radiance"])
    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = await response.execute_tools()
    response = await response.resume(tool_outputs)

    assert response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous tool call with context."""

    @llm.tool
    async def secret_retrieval_tool(
        ctx: llm.Context[dict[str, str]], password: str
    ) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    async def call(ctx: llm.Context[dict[str, str]], passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    ctx = llm.Context(deps=PASSWORD_MAP)
    response = await call(ctx, ["mellon", "radiance"])
    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = await response.execute_tools(ctx)
    response = await response.resume(ctx, tool_outputs)

    assert response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_stream(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming tool call without context."""

    @llm.tool
    def secret_retrieval_tool(password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return PASSWORD_MAP.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    def call(passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    response = call.stream(["mellon", "radiance"])

    for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

    for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_stream_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming tool call with context."""

    @llm.tool
    def secret_retrieval_tool(ctx: llm.Context[dict[str, str]], password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    def call(ctx: llm.Context[dict[str, str]], passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    ctx = llm.Context(deps=PASSWORD_MAP)
    response = call.stream(ctx, ["mellon", "radiance"])

    for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = response.execute_tools(ctx)
    response = response.resume(ctx, tool_outputs)

    for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async_stream(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming tool call without context."""

    @llm.tool
    async def secret_retrieval_tool(password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return PASSWORD_MAP.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    async def call(passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    response = await call.stream(["mellon", "radiance"])

    async for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = await response.execute_tools()
    response = await response.resume(tool_outputs)

    async for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async_stream_context(
    provider: llm.clients.Provider, model_id: llm.clients.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming tool call with context."""

    @llm.tool
    async def secret_retrieval_tool(
        ctx: llm.Context[dict[str, str]], password: str
    ) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.context_call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    async def call(ctx: llm.Context[dict[str, str]], passwords: list[str]) -> str:
        return f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"

    ctx = llm.Context(deps=PASSWORD_MAP)
    response = await call.stream(ctx, ["mellon", "radiance"])

    async for _ in response.chunk_stream():
        pass

    assert len(response.tool_calls) == 2, (
        f"Expected response to have two tool calls: {response.pretty()}"
    )

    tool_outputs = await response.execute_tools(ctx)
    response = await response.resume(ctx, tool_outputs)

    async for _ in response.chunk_stream():
        pass

    assert stream_response_snapshot_dict(response) == snapshot
    pretty = response.pretty()
    assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
    assert "Life before Death" in pretty, (
        f"Expected 'Life before Death' to be in response: {pretty}"
    )
