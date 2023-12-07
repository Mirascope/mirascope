"""Basic Prompt + LLM Example."""
from mirascope.prompt import Prompt


class MyPrompt(Prompt):
    """This is a prompt. It has a {noun} and a {verb}."""

    noun: str
    verb: str
