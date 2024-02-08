"""Tests for the `prompts` module."""
from unittest.mock import patch

import pytest

from mirascope.prompts import Prompt, messages


class FooBarPrompt(Prompt):
    """
    This is a test prompt about {foobar}.
    This should be on the same line in the template.

        This should be indented on a new line in the template.
    """

    foo: str
    bar: str

    @property
    def foobar(self) -> str:
        """Returns `foo` and `bar` concatenated."""
        return self.foo + self.bar


@messages
class MessagesPrompt(Prompt):
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


def test_template():
    """Test that `Prompt` initializes properly."""
    assert (
        FooBarPrompt.template() == "This is a test prompt about {foobar}. "
        "This should be on the same line in the template."
        "\n    This should be indented on a new line in the template."
    )


@patch.object(Prompt, "template", return_value="{foo}{bar}")
def test_str_uses_template(mock_template, fixture_foobar_prompt):
    """Tests that the `__str__` method uses the `template` method."""
    str(fixture_foobar_prompt)
    mock_template.assert_called_once()


def test_str(fixture_foobar_prompt, fixture_expected_foobar_prompt_str):
    """Test that the `__str__` method properly formats the template."""
    assert str(fixture_foobar_prompt) == fixture_expected_foobar_prompt_str


def test_save_and_load(fixture_foobar_prompt, tmpdir):
    """Test that `Prompt` can be saved and loaded."""
    filepath = f"{tmpdir}/test_prompt.pkl"
    fixture_foobar_prompt.save(filepath)
    assert FooBarPrompt.load(filepath) == fixture_foobar_prompt


def test_messages(fixture_messages_prompt, fixture_expected_messages_prompt_messages):
    """Tests that the messages decorator adds a function `messages` attribute."""
    assert hasattr(fixture_messages_prompt, "messages")
    assert fixture_messages_prompt.messages == fixture_expected_messages_prompt_messages


@messages
class NoDocstringPrompt(Prompt):
    param: str


def test_no_docstr():
    """Tests that `Prompt` throws a value error if it doesn't have a docstring."""
    with pytest.raises(ValueError):
        NoDocstringPrompt.template()

    with pytest.raises(ValueError):
        NoDocstringPrompt().messages
