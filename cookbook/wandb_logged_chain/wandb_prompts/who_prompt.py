"""Prompt to ask who I am."""
from pydantic import BaseModel

from .trace_prompt import TracePrompt


class Person(BaseModel):
    """Person model."""

    person: str


class WhoPrompt(TracePrompt):
    """Who is {person}?"""

    person: str
