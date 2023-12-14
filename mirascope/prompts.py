"""A class for better prompting."""

from __future__ import annotations
from pydantic import BaseModel
import pickle


class MirascopePrompt(BaseModel):
    """A Pydantic model for prompts."""

    @classmethod
    def template(cls):
        """Returns the docstring template."""
        return cls.__doc__

    def __str__(self):
        """Returns the formatted prompt."""
        return self.__doc__.strip().format(**self.__dict__)

    def save(self, filepath: str):
        """Saves the prompt to the given filepath."""
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str) -> MirascopePrompt:
        """Loads the prompt from the given filepath."""
        with open(filepath, "rb") as f:
            return pickle.load(f)
