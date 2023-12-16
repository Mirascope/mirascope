"""Basic Prompt + LLM Example."""
from mirascope.prompt import MirascopePromptTemplate
import os
from datetime import datetime

prev_revision_id = "0002"
revision_id = "0003"


class MyPrompt(MirascopePromptTemplate):
    """This is a prompt 0003. It has a {noun} and a {verb}."""

    noun: str
    verb: str
