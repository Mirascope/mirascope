"""Basic Prompt + LLM Example."""
from mirascope.prompts import MirascopePrompt


class MyPrompt(MirascopePrompt):
    """This is a prompt 0005. It has a {noun} and a {verb}."""

    noun: str
    verb: str
