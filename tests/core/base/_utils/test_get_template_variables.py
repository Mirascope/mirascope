"""Tests the `_utils.get_template_variables` module."""

from mirascope.core.base._utils._get_template_variables import get_template_variables


def test_get_template_variables() -> None:
    """Test the `get_template_variables` function."""
    template = "This is a {variable} template with {multiple:spec} variables."
    assert get_template_variables(template, False) == ["variable", "multiple"]
    assert get_template_variables(template, True) == [
        ("variable", ""),
        ("multiple", "spec"),
    ]
