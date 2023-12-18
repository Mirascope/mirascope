"""Tests for the `prompts` module."""
from unittest.mock import MagicMock, patch

from mirascope.prompts import MirascopePrompt, messages


class FooPrompt(MirascopePrompt):
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


def test_template():
    """Test that `MirascopePrompt` initializes properly."""
    assert (
        FooPrompt.template() == "This is a test prompt about {foobar}. "
        "This should be on the same line in the template."
        "\n    This should be indented on a new line in the template."
    )


@patch.object(MirascopePrompt, "__str__", return_value="str")
def test_str_uses_template(mock_str: MagicMock):
    """Tests that the `__str__` method uses the `template` method."""
    str(FooPrompt(foo="foo", bar="bar"))
    mock_str.assert_called_once()


def test_str():
    """Test that the `__str__` method properly formats the template."""
    assert (
        str(FooPrompt(foo="foo", bar="bar")) == "This is a test prompt about foobar. "
        "This should be on the same line in the template."
        "\n    This should be indented on a new line in the template."
    )


def test_save_and_load(tmpdir):
    """Test that `MirascopePrompt` can be saved and loaded."""
    prompt = FooPrompt(foo="foo", bar="bar")
    filepath = f"{tmpdir}/test_prompt.pkl"
    prompt.save(filepath)
    assert FooPrompt.load(filepath) == prompt


@messages
class MessagesPrompt(MirascopePrompt):
    """
    SYSTEM:
    This is the system message about {foo}.

        This is also the system message.

    USER:
    This is the user message about {bar}.

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


def test_messages():
    """Tests that the messages decorator adds a function `messages` attribute."""
    prompt = MessagesPrompt(foo="foo", bar="bar")
    assert isinstance(prompt, MirascopePrompt)
    assert MessagesPrompt(foo="foo", bar="bar").messages() == [
        (
            "system",
            "This is the system message about foo.\n    This is also the system message.",
        ),
        ("user", "This is the user message about bar."),
        (
            "assistant",
            "This is an assistant message about foobar. This is also part of the assistant message.",
        ),
    ]
