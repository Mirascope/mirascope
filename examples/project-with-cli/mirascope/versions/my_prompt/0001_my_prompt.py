"""Basic Prompt + LLM Example."""
from mirascope.prompts import MirascopePrompt

prev_revision_id = "None"
revision_id = "0001"


class MyPrompt(MirascopePrompt):
    """This is a prompt 0001. It has a {noun} and a {verb}."""

    noun: str
    verb: str
