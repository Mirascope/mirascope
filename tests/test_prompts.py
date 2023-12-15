"""Tests for the `prompts` module."""
from mirascope.prompts import MirascopePrompt


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
    print(FooPrompt.template())
    assert (
        FooPrompt.template() == "This is a test prompt about {foobar}. "
        "This should be on the same line in the template."
        "\n    This should be indented on a new line in the template."
    )


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
