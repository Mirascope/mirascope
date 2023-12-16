"""Basic Prompt + LLM Example."""
from mirascope.prompt import MirascopePromptTemplate


prev_revision_id = "0001"
revision_id = "0002"


class MyPrompt(MirascopePromptTemplate):
    """This is a prompt 0002. It has a {noun} and a {verb}."""

    noun: str
    verb: str
