"""Basic Prompt + LLM Example."""
from mirascope.prompts import MirascopePrompt


class MyPrompt(MirascopePrompt):
    """This is a prompt 0002. It has a {noun} and a {verb}."""

    noun: str
    verb: str
