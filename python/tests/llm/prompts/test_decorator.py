"""Tests for the prompt decorator."""

import pytest

from mirascope import llm


@pytest.fixture
def mixed_content() -> list[llm.UserContent]:
    """Fixture for mixed user content."""
    return [
        "hi, can you help me interpret this?",
        llm.ToolOutput(
            id="long_running_computation",
            name="answer_to_life_the_universe_and_everything",
            type="tool_output",
            value="42",
        ),
    ]


@pytest.fixture
def expected_messages() -> list[llm.Message]:
    """Fixture for expected messages."""
    return [
        llm.messages.system("You are a helpful assistant who avoids situationshps."),
        llm.messages.user("Please be my AI soulmate."),
    ]


def test_decorator_call_patterns() -> None:
    def prompt() -> str:
        return "hello world"

    called_on_fn = llm.prompt(prompt)
    constructed_decorator = llm.prompt()(prompt)
    assert called_on_fn() == constructed_decorator()


class TestSyncPromptDecorator:
    def test_sync_prompt_with_string_return(
        self,
    ) -> None:
        """Test sync prompt decorator with string return value."""

        @llm.prompt
        def simple_prompt(name: str, *, title: str) -> str:
            return f"Hello {title} {name}, how are you?"

        result = simple_prompt("Alice", title="Miss")
        assert result == [llm.messages.user("Hello Miss Alice, how are you?")]

    def test_sync_prompt_with_mixed_return(
        self, mixed_content: llm.messages.UserContent
    ) -> None:
        """Test sync prompt decorator with mixed return value."""

        @llm.prompt
        def prompt() -> llm.messages.UserContent:
            return mixed_content

        result = prompt()
        assert result == [llm.messages.user(mixed_content)]

    def test_sync_prompt_with_messages_return(
        self, expected_messages: list[llm.Message]
    ) -> None:
        """Test sync prompt decorator with messages return value."""

        @llm.prompt
        def messages_prompt() -> list[llm.Message]:
            return expected_messages

        assert messages_prompt() == expected_messages


@pytest.mark.asyncio
class TestAsyncPromptDecorator:
    async def test_async_prompt_with_string_return(self) -> None:
        """Test async prompt decorator with string return value."""

        @llm.prompt
        async def simple_prompt(name: str, *, title: str) -> str:
            return f"Hello {title} {name}, how are you?"

        result = await simple_prompt("Alice", title="Miss")
        assert result == [llm.messages.user("Hello Miss Alice, how are you?")]

    async def test_async_prompt_with_mixed_return(
        self, mixed_content: llm.messages.UserContent
    ) -> None:
        """Test async prompt decorator with mixed return value."""

        @llm.prompt
        async def prompt() -> llm.messages.UserContent:
            return mixed_content

        result = await prompt()
        assert result == [llm.messages.user(mixed_content)]

    async def test_async_prompt_with_messages_return(
        self, expected_messages: list[llm.Message]
    ) -> None:
        """Test async prompt decorator with messages return value."""

        @llm.prompt
        async def messages_prompt() -> list[llm.Message]:
            return expected_messages

        assert await messages_prompt() == expected_messages


class TestValueErrorOnEmptyPrompts:
    @pytest.mark.parametrize("empty_value", [[], ""])
    def test_sync_prompt_with_empty_return(
        self, empty_value: llm.messages.UserContent
    ) -> None:
        """Test sync prompt decorator with empty return value."""

        @llm.prompt
        def empty_prompt() -> llm.messages.UserContent:
            return empty_value

        with pytest.raises(ValueError, match="Prompt returned empty content"):
            empty_prompt()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("empty_value", [[], ""])
    async def test_async_prompt_with_empty_return(
        self, empty_value: llm.messages.UserContent
    ) -> None:
        """Test async prompt decorator with empty return value."""

        @llm.prompt
        async def empty_prompt() -> llm.messages.UserContent:
            return empty_value

        with pytest.raises(ValueError, match="Prompt returned empty content"):
            await empty_prompt()


class TestSyncContextPromptDecorator:
    def test_context_decorator_call_patterns(self) -> None:
        """Test that context_prompt decorator can be called with and without parentheses."""

        def context_prompt_fn(ctx: llm.Context[None], name: str) -> str:
            return f"Hello {name}"

        called_on_fn = llm.prompt(context_prompt_fn)
        constructed_decorator = llm.prompt()(context_prompt_fn)

        context = llm.Context(deps=None)
        assert called_on_fn(context, "Alice") == constructed_decorator(context, "Alice")

    def test_sync_context_prompt_with_string_return(self) -> None:
        """Test sync context prompt decorator with string return value."""

        @llm.prompt
        def simple_context_prompt(
            ctx: llm.Context[None], name: str, *, title: str
        ) -> str:
            return f"Hello {title} {name}, how are you?"

        context = llm.Context(deps=None)
        result = simple_context_prompt(context, "Alice", title="Miss")
        assert result == [llm.messages.user("Hello Miss Alice, how are you?")]

    def test_sync_context_prompt_with_mixed_return(
        self, mixed_content: llm.messages.UserContent
    ) -> None:
        """Test sync context prompt decorator with mixed return value."""

        @llm.prompt
        def context_prompt(ctx: llm.Context[None]) -> llm.messages.UserContent:
            return mixed_content

        context = llm.Context(deps=None)
        result = context_prompt(context)
        assert result == [llm.messages.user(mixed_content)]

    def test_sync_context_prompt_with_messages_return(
        self, expected_messages: list[llm.Message]
    ) -> None:
        """Test sync context prompt decorator with messages return value."""

        @llm.prompt
        def messages_context_prompt(ctx: llm.Context[None]) -> list[llm.Message]:
            return expected_messages

        context = llm.Context(deps=None)
        assert messages_context_prompt(context) == expected_messages

    def test_sync_context_prompt_with_deps(self) -> None:
        """Test sync context prompt decorator with context dependencies."""

        @llm.prompt
        def context_prompt_with_deps(
            ctx: llm.Context[dict[str, str]], query: str
        ) -> str:
            user_id = ctx.deps["user_id"]
            return f"User {user_id} asks: {query}"

        context = llm.Context(deps={"user_id": "12345"})
        result = context_prompt_with_deps(context, "How are you?")
        assert result == [llm.messages.user("User 12345 asks: How are you?")]


@pytest.mark.asyncio
class TestAsyncContextPromptDecorator:
    async def test_async_context_prompt_with_string_return(self) -> None:
        """Test async context prompt decorator with string return value."""

        @llm.prompt
        async def simple_context_prompt(
            ctx: llm.Context[None], name: str, *, title: str
        ) -> str:
            return f"Hello {title} {name}, how are you?"

        context = llm.Context(deps=None)
        result = await simple_context_prompt(context, "Alice", title="Miss")
        assert result == [llm.messages.user("Hello Miss Alice, how are you?")]

    async def test_async_context_prompt_with_mixed_return(
        self, mixed_content: llm.messages.UserContent
    ) -> None:
        """Test async context prompt decorator with mixed return value."""

        @llm.prompt
        async def context_prompt(ctx: llm.Context[None]) -> llm.messages.UserContent:
            return mixed_content

        context = llm.Context(deps=None)
        result = await context_prompt(context)
        assert result == [llm.messages.user(mixed_content)]

    async def test_async_context_prompt_with_messages_return(
        self, expected_messages: list[llm.Message]
    ) -> None:
        """Test async context prompt decorator with messages return value."""

        @llm.prompt
        async def messages_context_prompt(ctx: llm.Context[None]) -> list[llm.Message]:
            return expected_messages

        context = llm.Context(deps=None)
        assert await messages_context_prompt(context) == expected_messages

    async def test_async_context_prompt_with_deps(self) -> None:
        """Test async context prompt decorator with context dependencies."""

        @llm.prompt
        async def context_prompt_with_deps(
            ctx: llm.Context[dict[str, str]], query: str
        ) -> str:
            user_id = ctx.deps["user_id"]
            return f"User {user_id} asks: {query}"

        context = llm.Context(deps={"user_id": "12345"})
        result = await context_prompt_with_deps(context, "How are you?")
        assert result == [llm.messages.user("User 12345 asks: How are you?")]


class TestValueErrorOnEmptyContextPrompts:
    @pytest.mark.parametrize("empty_value", [[], ""])
    def test_sync_context_prompt_with_empty_return(
        self, empty_value: llm.messages.UserContent
    ) -> None:
        """Test sync context prompt decorator with empty return value."""

        @llm.prompt
        def empty_context_prompt(ctx: llm.Context[None]) -> llm.messages.UserContent:
            return empty_value

        context = llm.Context(deps=None)
        with pytest.raises(ValueError, match="Prompt returned empty content"):
            empty_context_prompt(context)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("empty_value", [[], ""])
    async def test_async_context_prompt_with_empty_return(
        self, empty_value: llm.messages.UserContent
    ) -> None:
        """Test async context prompt decorator with empty return value."""

        @llm.prompt
        async def empty_context_prompt(
            ctx: llm.Context[None],
        ) -> llm.messages.UserContent:
            return empty_value

        context = llm.Context(deps=None)
        with pytest.raises(ValueError, match="Prompt returned empty content"):
            await empty_context_prompt(context)
