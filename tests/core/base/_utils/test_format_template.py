"""Tests the `_utils.format_template` module."""

from textwrap import dedent

from mirascope.core.base._utils.format_template import format_template


def test_format_template() -> None:
    """Tests the `format_template` function."""
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
    formatted_prompt_template = format_template(prompt_template, attrs)
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
