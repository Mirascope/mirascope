"""Tests for the _internal utils module."""
from textwrap import dedent

import pytest

from mirascope.core._internal import utils


def test_format_prompt_template() -> None:
    """Tests the `format_prompt_template` function."""
    prompt_template = """
    Recommend a {empty_list} book.

    I like the following genres:
    {genres}

    Here are some of my favorite authors and their books:
    {authors_and_books}
    """

    empty_list = []
    genres = ["fantasy", "mystery"]
    authors_and_books = [
        ["The Name of the Wind", "The Wise Man's Fears"],
        ["The Da Vinci Code", "Angels & Demons"],
    ]
    attrs = {
        "empty_list": empty_list,
        "genres": genres,
        "authors_and_books": authors_and_books,
    }
    formatted_prompt_template = utils.format_prompt_template(prompt_template, attrs)
    assert (
        formatted_prompt_template
        == dedent(
            """
            Recommend a  book.

            I like the following genres:
            fantasy
            mystery

            Here are some of my favorite authors and their books:
            The Name of the Wind
            The Wise Man's Fears

            The Da Vinci Code
            Angels & Demons
            """
        ).strip()
    )


def test_parse_prompt_messages() -> None:
    """Tests the `parse_prompt_messages` function."""
    template = """
    SYSTEM: You are the world's greatest librarian.
    MESSAGES: {messages}
    USER: Recommend a book.
    """

    messages = [
        {"role": "user", "content": "Hi!"},
        {"role": "assistant", "content": "Hello!"},
    ]
    parsed_messages = utils.parse_prompt_messages(
        roles=["system", "user", "assistant"],
        template=template,
        attrs={"messages": messages},
    )
    assert parsed_messages == [
        {"role": "system", "content": "You are the world's greatest librarian."},
        {"role": "user", "content": "Hi!"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Recommend a book."},
    ]

    with pytest.raises(ValueError):
        utils.parse_prompt_messages(
            roles=["system"], template=template, attrs={"messages": None}
        )

    with pytest.raises(ValueError):
        utils.parse_prompt_messages(
            roles=["system"], template=template, attrs={"messages": "Hi!"}
        )
