"""Tests the `_utils.get_template_variables` module."""

from mirascope.core.base._utils.get_template_variables import get_template_variables


def test_get_template_variables() -> None:
    """Test the get_template_variables function."""
    template = "This is a {variable} template with {multiple} variables."
    assert get_template_variables(template) == ["variable", "multiple"]
