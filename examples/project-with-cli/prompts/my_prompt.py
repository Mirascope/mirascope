"""Basic Prompt + LLM Example."""
from mirascope.prompts import Prompt


class MyPrompt(Prompt):
    """This is a prompt 0002. It has a {noun} and a {verb}."""

    noun: str
    verb: str
