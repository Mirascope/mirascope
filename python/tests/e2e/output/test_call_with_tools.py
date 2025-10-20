"""End-to-end tests for LLM tool usage, including parallel tool usage and continuation."""

import pytest

from mirascope import llm
from tests.e2e.conftest import PROVIDER_MODEL_ID_PAIRS, Snapshot
from tests.utils import (
    exception_snapshot_dict,
    response_snapshot_dict,
    stream_response_snapshot_dict,
)

PASSWORD_MAP = {"mellon": "Welcome to Moria!", "radiance": "Life before Death"}

# ============= SYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_sync(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
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
    def call(passwords: list[str]) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        response = call(["mellon", "radiance"])
        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = response.execute_tools()
        response = response.resume(tool_outputs)

        snapshot_data["response"] = response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_sync_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test synchronous tool call with context."""

    @llm.tool
    def secret_retrieval_tool(ctx: llm.Context[dict[str, str]], password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    def call(
        ctx: llm.Context[dict[str, str]], passwords: list[str]
    ) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        ctx = llm.Context(deps=PASSWORD_MAP)
        response = call(ctx, ["mellon", "radiance"])
        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = response.execute_tools(
            ctx,
        )
        response = response.resume(ctx, tool_outputs)

        snapshot_data["response"] = response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


# ============= ASYNC TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
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
    async def call(passwords: list[str]) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        response = await call(["mellon", "radiance"])
        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = await response.execute_tools()
        response = await response.resume(tool_outputs)

        snapshot_data["response"] = response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test asynchronous tool call with context."""

    @llm.tool
    async def secret_retrieval_tool(
        ctx: llm.Context[dict[str, str]], password: str
    ) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    async def call(
        ctx: llm.Context[dict[str, str]], passwords: list[str]
    ) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        ctx = llm.Context(deps=PASSWORD_MAP)
        response = await call(ctx, ["mellon", "radiance"])
        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = await response.execute_tools(ctx)
        response = await response.resume(ctx, tool_outputs)

        snapshot_data["response"] = response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


# ============= STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
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
    def call(passwords: list[str]) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        response = call.stream(["mellon", "radiance"])
        response.finish()

        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = response.execute_tools()
        response = response.resume(tool_outputs)
        response.finish()

        snapshot_data["response"] = stream_response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
def test_call_with_tools_stream_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test streaming tool call with context."""

    @llm.tool
    def secret_retrieval_tool(ctx: llm.Context[dict[str, str]], password: str) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    def call(
        ctx: llm.Context[dict[str, str]], passwords: list[str]
    ) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        ctx = llm.Context(deps=PASSWORD_MAP)
        response = call.stream(ctx, ["mellon", "radiance"])
        response.finish()

        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = response.execute_tools(ctx)
        response = response.resume(ctx, tool_outputs)
        response.finish()

        snapshot_data["response"] = stream_response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


# ============= ASYNC STREAM TESTS =============


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async_stream(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
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
    async def call(passwords: list[str]) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        response = await call.stream(["mellon", "radiance"])
        await response.finish()

        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = await response.execute_tools()
        response = await response.resume(tool_outputs)
        await response.finish()

        snapshot_data["response"] = stream_response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot


@pytest.mark.parametrize("provider, model_id", PROVIDER_MODEL_ID_PAIRS)
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_call_with_tools_async_stream_context(
    provider: llm.Provider, model_id: llm.ModelId, snapshot: Snapshot
) -> None:
    """Test async streaming tool call with context."""

    @llm.tool
    async def secret_retrieval_tool(
        ctx: llm.Context[dict[str, str]], password: str
    ) -> str:
        """A tool that requires a password to retrieve a secret."""
        return ctx.deps.get(password, "Invalid password!")

    @llm.call(
        provider=provider,
        model_id=model_id,
        tools=[secret_retrieval_tool],
    )
    async def call(
        ctx: llm.Context[dict[str, str]], passwords: list[str]
    ) -> list[llm.Message]:
        return [
            llm.messages.system("Use parallel tool calling."),
            llm.messages.user(
                f"Please retrieve the secrets associated with each of these passwords: {','.join(passwords)}"
            ),
        ]

    snapshot_data = {}
    try:
        ctx = llm.Context(deps=PASSWORD_MAP)
        response = await call.stream(ctx, ["mellon", "radiance"])
        await response.finish()

        assert len(response.tool_calls) == 2, (
            f"Expected response to have two tool calls: {response.pretty()}"
        )

        tool_outputs = await response.execute_tools(ctx)
        response = await response.resume(ctx, tool_outputs)
        await response.finish()

        snapshot_data["response"] = stream_response_snapshot_dict(response)
        pretty = response.pretty()
        assert "Moria" in pretty, f"Expected 'Moria' to be in response: {pretty}"
        assert "Life before Death" in pretty, (
            f"Expected 'Life before Death' to be in response: {pretty}"
        )
    except Exception as e:
        snapshot_data["exception"] = exception_snapshot_dict(e)

    assert snapshot_data == snapshot
