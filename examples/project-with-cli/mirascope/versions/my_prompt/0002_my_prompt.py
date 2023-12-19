"""Basic Prompt + LLM Example."""
from mirascope.prompts import MirascopePrompt


prev_revision_id = "0001"
revision_id = "0002"


class MyPrompt(MirascopePrompt):
    """This is a prompt 0002. It has a {noun} and a {verb}."""

    noun: str
    verb: str
