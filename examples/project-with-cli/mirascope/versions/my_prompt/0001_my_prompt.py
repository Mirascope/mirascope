"""Basic Prompt + LLM Example."""
from mirascope.prompts import Prompt

prev_revision_id = "None"
revision_id = "0001"


class MyPrompt(Prompt):
    """This is a prompt 0001. It has a {noun} and a {verb}."""

    noun: str
    verb: str
