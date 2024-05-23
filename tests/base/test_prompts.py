"""Tests for the `BasePrompt` class."""

from textwrap import dedent
from typing import Any

import pytest
from pydantic import ConfigDict

from mirascope.base.prompts import BasePrompt, tags
from mirascope.base.types import Message


def test_tags_decorator() -> None:
    """Tests the `tags` decorator on a BasePrompt."""

    @tags(["test"])
    class MyPrompt(BasePrompt):
        prompt_template = "test"

    assert MyPrompt.tags == ["test"]


@pytest.mark.parametrize(
    "prompt_tags,prompt_template_str,prompt_data,expected_str,expected_messages,"
    "expected_dump",
    [
        (
            ["version:0001"],
            "Single user message",
            {},
            "Single user message",
            [{"role": "user", "content": "Single user message"}],
            {
                "tags": ["version:0001"],
                "template": "Single user message",
                "inputs": {},
            },
        ),
        (
            ["multiple", "different", "tags"],
            dedent(
                """
                SYSTEM: system message
                USER: user message about {topic}
                """
            ),
            {"topic": "testing"},
            "SYSTEM: system message\nUSER: user message about testing",
            [
                {"role": "system", "content": "system message"},
                {"role": "user", "content": "user message about testing"},
            ],
            {
                "tags": ["multiple", "different", "tags"],
                "template": "SYSTEM: system message\nUSER: user message about {topic}",
                "inputs": {"topic": "testing"},
            },
        ),
    ],
)
def test_base_prompt(
    prompt_tags: list[str],
    prompt_template_str: str,
    prompt_data: dict[str, Any],
    expected_str: str,
    expected_messages: list[Message],
    expected_dump: dict[str, Any],
) -> None:
    """Tests various different subclasses of `BasePrompt`."""

    class Prompt(BasePrompt):
        tags = prompt_tags
        prompt_template = prompt_template_str

        model_config = ConfigDict(extra="allow")

    prompt = Prompt(**prompt_data)
    assert str(prompt) == expected_str
    assert prompt.messages() == expected_messages
    assert prompt.dump() == expected_dump


def test_base_prompt_allow_any_keyword() -> None:
    """Tests that a any non-role keyword is parsed correctly."""

    class Prompt(BasePrompt):
        prompt_template = """
        USER:
        KEYWORD: allow this
        """

    messages = Prompt().messages()

    assert len(messages) == 1
    assert messages[0] == {"role": "user", "content": "KEYWORD: allow this"}


def test_base_prompt_messages_injection() -> None:
    """Tests injecting messages into the prompt."""

    class MyPrompt(BasePrompt):
        prompt_template = """
        SYSTEM: System message
        MESSAGES: {history}
        USER: User message
        MESSAGES: {context}
        USER: User message
        """

        history: list[Message]
        context: list[Message]

    history: list[Message] = [
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Assistant message"},
    ]
    context: list[Message] = [{"role": "user", "content": "Context message"}]
    messages = MyPrompt(history=history, context=context).messages()
    assert messages == [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Assistant message"},
        {"role": "user", "content": "User message"},
        {"role": "user", "content": "Context message"},
        {"role": "user", "content": "User message"},
    ]


def test_base_prompt_messages_injection_empty_list() -> None:
    """Tests that an empty messages array works properly."""

    class MyPrompt(BasePrompt):
        prompt_template = """
        MESSAGES: {history}

        USER:
        user message
        """

        history: list[Message]

    messages = MyPrompt(history=[]).messages()
    assert messages == [{"role": "user", "content": "user message"}]


def test_base_prompt_messages_injection_wrong_type() -> None:
    """Tests that an error is raised if trying to inject a non-list type."""

    class MyPrompt(BasePrompt):
        prompt_template = """
        MESSAGES: {bad}
        """

        bad: int

    with pytest.raises(ValueError):
        MyPrompt(bad=1).messages()


def test_base_prompt_list_attribute() -> None:
    """Tests that attributes of type list are properly injected."""

    class MyPrompt(BasePrompt):
        prompt_template = """
        {my_list}
        {my_list_of_lists}
        """

        my_list: list[str]
        my_list_of_lists: list[list[str]]

    my_list = ["my", "list"]
    my_list_of_lists = [my_list, my_list]
    prompt = MyPrompt(my_list=my_list, my_list_of_lists=my_list_of_lists)
    assert str(prompt) == "my\nlist\nmy\nlist\n\nmy\nlist"


def test_messages_property_called_once() -> None:
    """Tests that the messages property is called once."""

    class MyPrompt(BasePrompt):
        prompt_template = """
        MESSAGES: 
        {history}
        """
        count: int = 0

        @property
        def history(self) -> list[Message]:
            self.count += 1
            return [{"role": "user", "content": "foo"}]

    my_prompt = MyPrompt()
    my_prompt.messages()
    assert my_prompt.count == 1
