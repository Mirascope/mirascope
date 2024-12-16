"""Utility for pulling the `prompt_template` from a call or `BasePrompt`."""

import os
from collections.abc import Callable
from textwrap import dedent

from pydantic import BaseModel


def get_prompt_template(fn: Callable | BaseModel) -> str:
    """Get the metadata from the function and merge with any dynamic metadata."""

    prompt_template = getattr(fn, "prompt_template", None) or getattr(
        fn, "_prompt_template", None
    )
    if prompt_template:
        return prompt_template

    docstring_prompt_enabled = os.getenv("MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE")
    doc = fn.__doc__
    if not doc:
        raise ValueError("No prompt template set!")
    if docstring_prompt_enabled != "ENABLED":
        raise ValueError(
            "You must explicitly enable docstring prompt templates by setting "
            "`MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE=ENABLED` in your environment."
        )
    return dedent(doc).strip()
