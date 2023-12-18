"""Basic Prompt + LLM Example."""
from mirascope.prompt import MirascopePromptTemplate



class MyPrompt(MirascopePromptTemplate):
    """This is a prompt 0005. It has a {noun} and a {verb}."""

    noun: str
    verb: str
