"""Tests for the `prompts` module."""
from mirascope.prompts import MirascopePrompt


def test_mirascope_prompt_template():
    """Test that `MirascopePrompt` initializes properly."""

    class TestPrompt(MirascopePrompt):
        """{foo}"""

        foo: str

    assert TestPrompt.template() == "{foo}"
