"""Tests the `_utils.get_prompt_template` module."""

import os

import pytest

from mirascope.core.base._utils._get_prompt_template import get_prompt_template
from mirascope.core.base.prompt import BasePrompt, prompt_template


def test_get_prompt_template() -> None:
    """Tests the `get_prompt_template` function."""

    class Prompt(BasePrompt): ...

    with pytest.raises(ValueError, match="No prompt template set!"):
        get_prompt_template(Prompt)

    assert get_prompt_template(prompt_template("prompt")(Prompt)) == "prompt"

    class PromptWithDocstring(BasePrompt):
        """docstring_prompt"""

    with pytest.raises(
        ValueError, match="You must explicitly enable docstring prompt templates."
    ):
        get_prompt_template(PromptWithDocstring)

    os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "ENABLED"
    assert get_prompt_template(PromptWithDocstring) == "docstring_prompt"
    os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "DISABLED"

    def fn() -> None: ...  # pragma: no cover

    with pytest.raises(ValueError, match="No prompt template set!"):
        get_prompt_template(fn)

    assert get_prompt_template(prompt_template("prompt")(fn)) == "prompt"

    def fn_with_docstring() -> None:
        """docstring_prompt"""

    with pytest.raises(
        ValueError, match="You must explicitly enable docstring prompt templates."
    ):
        get_prompt_template(fn_with_docstring)

    os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "ENABLED"
    assert get_prompt_template(fn_with_docstring) == "docstring_prompt"
    os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "DISABLED"
