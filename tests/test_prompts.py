"""Tests for deprecated `Prompt` class."""

from mirascope.prompts import Prompt, messages


@messages
class DecoratorMessagesPrompt(Prompt):
    """
    SYSTEM:
    This is the system message about {foo}.

        This is also the system message.

    USER:
    This is the user message about {bar}.

    TOOL:
    This is the output of calling a tool.

    ASSISTANT:
    This is an assistant message about {foobar}.
    This is also part of the assistant message.
    """

    foo: str
    bar: str

    @property
    def foobar(self) -> str:
        """Returns `foo` and `bar` concatenated."""
        return self.foo + self.bar


def test_messages(
    fixture_decorator_messages_prompt, fixture_expected_messages_prompt_messages
):
    """Tests that the messages decorator adds a function `messages` attribute."""
    assert (
        fixture_decorator_messages_prompt.messages
        == fixture_expected_messages_prompt_messages
    )
