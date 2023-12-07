"""A class for better prompting."""

from __future__ import annotations
from pydantic import BaseModel
import pickle


class MirascopePromptTemplate(BaseModel):
    """A Pydantic model for prompts."""

    @classmethod
    def template(cls):
        """Returns the docstring template."""
        return cls.__doc__

    def save(self, filepath: str):
        """Saves the prompt to the given filepath."""
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str) -> MirascopePromptTemplate:
        """Loads the prompt from the given filepath."""
        with open(filepath, "rb") as f:
            return pickle.load(f)

    def __str__(self):
        """Returns the formatted prompt."""
        return self.__doc__.strip().format(**self.__dict__)
