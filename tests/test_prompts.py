"""Tests for the `prompts` module."""
from typing import Any, Optional
from unittest.mock import patch

import pytest

from mirascope.prompts import OpenAICallParams, Prompt, messages, tags


class FooBarPrompt(Prompt):
    """
    This is a test prompt about {foobar}.
    This should be on the same line in the template.

        This should be indented on a new line in the template.
    """

    foo: str
    bar: str
    _call_params: OpenAICallParams = OpenAICallParams(model="gpt-3.5-turbo-1106")

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


@tags(["test_tag"])
class TagPrompt(Prompt):
    """This is a test prompt with a tag."""


@tags(["multiple", "tags"])
class TagsPrompt(Prompt):
    """This is a test prompt with multiple tags."""


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


@pytest.mark.parametrize(
    "prompt,expected_messages",
    [
        ("fixture_foobar_prompt", "fixture_expected_foobar_prompt_messages"),
        ("fixture_messages_prompt", "fixture_expected_messages_prompt_messages"),
    ],
)
def test_messages(prompt, expected_messages, request):
    """Tests that the messages decorator adds a function `messages` attribute."""
    prompt = request.getfixturevalue(prompt)
    expected_messages = request.getfixturevalue(expected_messages)
    assert prompt.messages == expected_messages


@pytest.mark.parametrize(
    "prompt, expected_tags",
    [
        ("fixture_foobar_prompt", []),
        ("fixture_tag_prompt", ["test_tag"]),
        ("fixture_tags_prompt", ["multiple", "tags"]),
    ],
)
def test_tags(prompt, expected_tags, request):
    """Tests that the tags decorator adds a `tags` attribute."""
    prompt = request.getfixturevalue(prompt)
    assert hasattr(prompt, "_tags")
    assert prompt.tags() == expected_tags


@pytest.mark.parametrize(
    "completion,expected", [(None, {}), ({"hello": "world"}, {"hello": "world"})]
)
def test_prompt_dump(
    completion: Optional[dict[str, Any]],
    expected: dict[str, Any],
    fixture_foobar_prompt: FooBarPrompt,
):
    """Tests that `Prompt.dump` returns the expected string."""
    foobar_prompt_random_json = fixture_foobar_prompt.dump(completion)
    assert foobar_prompt_random_json["template"] == fixture_foobar_prompt.template()
    for key, value in expected.items():
        assert (
            key in foobar_prompt_random_json and foobar_prompt_random_json[key] == value
        )


@messages
class NoDocstringPrompt(Prompt):
    param: str


def test_no_docstr():
    """Tests that `Prompt` throws a value error if it doesn't have a docstring."""
    with pytest.raises(ValueError):
        NoDocstringPrompt.template()

    with pytest.raises(ValueError):
        NoDocstringPrompt().messages
