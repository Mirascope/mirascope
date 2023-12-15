"""A class for better prompting."""

from __future__ import annotations

import pickle
import re
from string import Formatter
from textwrap import dedent

from pydantic import BaseModel


class MirascopePrompt(BaseModel):
    """A Pydantic model for prompts."""

    @classmethod
    def template(cls) -> str:
        """Custom parsing functionality for docstring prompt.

        This function is the first step in formatting the prompt template docstring.
        For the default `MirascopePrompt`, this function dedents the docstring and
        replaces all repeated sequences of newlines with one fewer newline character.
        This enables writing blocks of text instead of really long single lines. To
        include any number of newline characters, simply include one extra.

        Raises:
            ValueError: If the docstring is empty.
        """
        if cls.__doc__ is None:
            raise ValueError("`MirascopePrompt` must have a prompt template docstring.")

        template = dedent(cls.__doc__).strip("\n")
        template = re.sub(
            "(\n+)", lambda x: x.group(0)[:-1] if len(x.group(0)) > 1 else " ", template
        )

        return template

    def __str__(self) -> str:
        """Returns the docstring prompt template formatted with all template variables."""
        template = self.template()
        template_vars = [
            var for _, var, _, _ in Formatter().parse(template) if var is not None
        ]
        return template.format(**{var: getattr(self, var) for var in template_vars})

    def save(self, filepath: str):
        """Saves the prompt to the given filepath."""
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str) -> MirascopePrompt:
        """Loads the prompt from the given filepath."""
        with open(filepath, "rb") as f:
            return pickle.load(f)
