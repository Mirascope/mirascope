"""Tests for the prompt decorator."""

import pytest
from inline_snapshot import snapshot

from mirascope import llm


@pytest.fixture
def mixed_content() -> list:
    """Fixture for mixed user content."""
    return [
        "hi, can you help me interpret this?",
        llm.ToolOutput(
            content_type="tool_output",
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


class TestSyncPromptDecorator:
    def test_sync_prompt_with_string_return(
        self,
    ) -> None:
        """Test sync prompt decorator with string return value."""

        @llm.prompt()
        def simple_prompt(name: str, *, title: str) -> str:
            return f"Hello {title} {name}, how are you?"

        result = simple_prompt("Alice", title="Miss")
        assert result == [llm.messages.user("Hello Miss Alice, how are you?")]

    def test_sync_prompt_with_mixed_return(
        self, mixed_content: llm.messages.UserContent
    ) -> None:
        """Test sync prompt decorator with mixed return value."""

        @llm.prompt()
        def prompt() -> llm.messages.UserContent:
            return mixed_content

        result = prompt()
        assert result == [llm.messages.user(mixed_content)]

    def test_sync_prompt_with_messages_return(
        self, expected_messages: list[llm.Message]
    ) -> None:
        """Test sync prompt decorator with messages return value."""

        @llm.prompt()
        def messages_prompt() -> list[llm.Message]:
            return expected_messages

        assert messages_prompt() == expected_messages

    def test_sync_prompt_with_empty_list(
        self,
    ) -> None:
        """Test sync prompt decorator with empty return value."""

        @llm.prompt()
        def empty_prompt() -> llm.messages.UserContent:
            return []

        result = empty_prompt()
        assert result == []

    def test_sync_prompt_with_empty_string(
        self,
    ) -> None:
        """Test sync prompt decorator with empty return value."""

        @llm.prompt()
        def empty_string_prompt() -> llm.messages.UserContent:
            return ""

        result = empty_string_prompt()
        assert result == [llm.messages.user("")]


@pytest.mark.asyncio
class TestAsyncPromptDecorator:
    async def test_async_prompt_with_string_return(self) -> None:
        """Test async prompt decorator with string return value."""

        @llm.prompt()
        async def simple_prompt(name: str, *, title: str) -> str:
            return f"Hello {title} {name}, how are you?"

        result = await simple_prompt("Alice", title="Miss")
        assert result == [llm.messages.user("Hello Miss Alice, how are you?")]

    async def test_async_prompt_with_mixed_return(
        self, mixed_content: llm.messages.UserContent
    ) -> None:
        """Test async prompt decorator with mixed return value."""

        @llm.prompt()
        async def prompt() -> llm.messages.UserContent:
            return mixed_content

        result = await prompt()
        assert result == [llm.messages.user(mixed_content)]

    async def test_async_prompt_with_messages_return(
        self, expected_messages: list[llm.Message]
    ) -> None:
        """Test async prompt decorator with messages return value."""

        @llm.prompt()
        async def messages_prompt() -> list[llm.Message]:
            return expected_messages

        assert await messages_prompt() == expected_messages

    async def test_async_prompt_with_empty_return(self) -> None:
        """Test async prompt decorator with empty return value."""

        @llm.prompt()
        async def empty_prompt() -> llm.messages.UserContent:
            return []

        result = await empty_prompt()
        assert result == []

    async def test_async_prompt_with_empty_string(
        self,
    ) -> None:
        """Test sync prompt decorator with empty return value."""

        @llm.prompt()
        async def empty_string_prompt() -> llm.messages.UserContent:
            return ""

        result = await empty_string_prompt()
        assert result == [llm.messages.user("")]


class TestErrorCases:
    """Test behavior when the decorated prompt is not a proper prompt.

    These are type errors and will not happen if users are properly using the type hints.
    Included for documentation purposes.
    """

    def test_mismatched_message_first(self) -> None:
        bad_contents = [llm.messages.user("hello there"), "so uncivilized"]

        @llm.prompt()  # pyright: ignore[reportArgumentType, reportCallIssue]
        def bad_prompt() -> list[llm.Message | str]:
            return bad_contents

        assert bad_prompt() == bad_contents

    def test_mismatched_str_first(self) -> None:
        bad_contents = ["so uncivilized", llm.messages.user("hello there")]

        @llm.prompt()  # pyright: ignore[reportArgumentType, reportCallIssue]
        def bad_prompt() -> list[llm.Message | str]:
            return bad_contents

        assert bad_prompt() == snapshot(
            [
                llm.UserMessage(
                    content=[
                        llm.Text(text="so uncivilized"),
                        llm.UserMessage(content=[llm.Text(text="hello there")]),  # pyright: ignore[reportArgumentType]
                    ]
                )
            ]
        )
        assert bad_prompt() == [llm.messages.user(bad_contents)]
