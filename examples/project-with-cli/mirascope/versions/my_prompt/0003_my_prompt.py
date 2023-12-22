"""Basic Prompt + LLM Example."""
from mirascope.prompts import Prompt

prev_revision_id = "0001"
revision_id = "0003"


class MyPrompt(Prompt):
    """This is a prompt 0003. It has a {noun} and a {verb}."""

    noun: str
    verb: str
